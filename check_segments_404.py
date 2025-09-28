import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Optional, Set, Tuple

try:
    # Prefer stdlib to avoid external deps; requests is optional
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except Exception:  # pragma: no cover - very unlikely on CPython
    urllib_request = None  # type: ignore
    urllib_error = None  # type: ignore


BO_TOC_PATH_DEFAULT = "/Users/tenzintsering/Desktop/my-work/Scripts/bo_choejug_toc.json"
ZH_TOC_PATH_DEFAULT = "/Users/tenzintsering/Desktop/my-work/Scripts/zh_choejug_toc.json"

# You can override the base URL via the SEGMENT_API_BASE env var if needed
SEGMENT_API_BASE = os.environ.get(
    "SEGMENT_API_BASE",
    "https://pecha-backend-12341825340-1fb0112.onrender.com/api/v1/segments",
)


def load_segment_ids_from_toc(toc_file_path: str) -> List[str]:
    with open(toc_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        return []

    root = data[0]
    sections = root.get("sections", [])
    segment_ids: List[str] = []
    for section in sections:
        for segment in section.get("segments", []):
            segment_id = segment.get("segment_id")
            if isinstance(segment_id, str) and segment_id:
                segment_ids.append(segment_id)
    return segment_ids


def build_segment_url(segment_id: str) -> str:
    return f"{SEGMENT_API_BASE}/{segment_id}?text_details=false"


def http_get_status(url: str, timeout_seconds: float = 10.0) -> Tuple[int, Optional[str]]:
    if urllib_request is None:
        raise RuntimeError("urllib is unavailable in this environment")

    request = urllib_request.Request(url, headers={"accept": "application/json"})
    try:
        with urllib_request.urlopen(request, timeout=timeout_seconds) as response:
            return response.getcode(), None
    except urllib_error.HTTPError as http_err:  # type: ignore[attr-defined]
        # Return HTTP status code with reason
        return http_err.code, getattr(http_err, "reason", None)
    except urllib_error.URLError as url_err:  # type: ignore[attr-defined]
        # Network-level error (DNS, TLS, connection refused, etc.)
        return -1, str(url_err.reason)
    except Exception as unexpected:
        return -1, str(unexpected)


def check_segment_ids_for_404(segment_ids: Iterable[str], max_workers: int = 16) -> Dict[str, List[str]]:
    missing_404: List[str] = []
    other_errors: List[str] = []

    def _worker(seg_id: str) -> Tuple[str, int, Optional[str]]:
        status_code, reason = http_get_status(build_segment_url(seg_id))
        return seg_id, status_code, reason

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(_worker, seg_id): seg_id for seg_id in segment_ids}
        for future in as_completed(future_to_id):
            seg_id, status_code, reason = future.result()
            if status_code == 404:
                missing_404.append(seg_id)
            elif status_code != 200:
                # Track any non-200, non-404 issues for visibility
                suffix = f" (status {status_code}{': ' + reason if reason else ''})"
                other_errors.append(seg_id + suffix)

    return {
        "missing_404": missing_404,
        "other_errors": other_errors,
    }


def main() -> None:
    bo_toc_path = os.environ.get("BO_TOC_PATH", BO_TOC_PATH_DEFAULT)
    zh_toc_path = os.environ.get("ZH_TOC_PATH", ZH_TOC_PATH_DEFAULT)

    bo_segment_ids = load_segment_ids_from_toc(bo_toc_path)
    zh_segment_ids = load_segment_ids_from_toc(zh_toc_path)

    # Optionally de-duplicate to avoid repeated requests
    bo_unique_ids: List[str] = list(dict.fromkeys(bo_segment_ids))
    zh_unique_ids: List[str] = list(dict.fromkeys(zh_segment_ids))

    print(f"BO total IDs: {len(bo_segment_ids)} (unique: {len(bo_unique_ids)})")
    print(f"ZH total IDs: {len(zh_segment_ids)} (unique: {len(zh_unique_ids)})")

    bo_result = check_segment_ids_for_404(bo_unique_ids)
    zh_result = check_segment_ids_for_404(zh_unique_ids)

    report = {
        "api_base": SEGMENT_API_BASE,
        "bo": {
            "total_ids": len(bo_segment_ids),
            "unique_ids": len(bo_unique_ids),
            "missing_404_count": len(bo_result["missing_404"]),
            "missing_404": bo_result["missing_404"],
            "other_errors_count": len(bo_result["other_errors"]),
            "other_errors": bo_result["other_errors"],
        },
        "zh": {
            "total_ids": len(zh_segment_ids),
            "unique_ids": len(zh_unique_ids),
            "missing_404_count": len(zh_result["missing_404"]),
            "missing_404": zh_result["missing_404"],
            "other_errors_count": len(zh_result["other_errors"]),
            "other_errors": zh_result["other_errors"],
        },
    }

    # Print a concise summary
    print("\nSummary:")
    print(
        f"BO 404s: {report['bo']['missing_404_count']}, Other errors: {report['bo']['other_errors_count']}"
    )
    print(
        f"ZH 404s: {report['zh']['missing_404_count']}, Other errors: {report['zh']['other_errors_count']}"
    )

    # Persist full report for inspection
    output_path = "/Users/tenzintsering/Desktop/my-work/Scripts/segments_404_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nFull report written to: {output_path}")


if __name__ == "__main__":
    main()






