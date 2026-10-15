"""Create the course's reproducible 4% record sample without publishing post text.

Usage: python prepare_weibo_sample.py SOURCE_CSV --output SAMPLE_CSV
The source is read twice; source records are sampled before quality filtering.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import sys


SOURCE_FIELDS = [
    "用户ID", "性别", "地点类型", "经度", "纬度", "发布时间", "微博文本", "年份", "月份"
]
OUTPUT_FIELDS = ["匿名用户ID", "发布时间", "经度", "纬度", "年份", "月份"]
SEED = 20261016
RATE = 0.04


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Quality:
    def __init__(self):
        self.n = 0
        self.date_min = None
        self.date_max = None
        self.months = collections.Counter()
        self.year_months = collections.Counter()
        self.issues = collections.Counter()
        self.lon_min = math.inf
        self.lon_max = -math.inf
        self.lat_min = math.inf
        self.lat_max = -math.inf

    def add(self, row):
        self.n += 1
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"CSV column count mismatch at record {self.n}")
        raw_time = row["发布时间"].strip()
        try:
            timestamp = dt.datetime.fromisoformat(raw_time)
        except ValueError:
            self.issues["invalid_timestamp"] += 1
        else:
            stamp = timestamp.isoformat(sep=" ")
            self.date_min = stamp if self.date_min is None else min(self.date_min, stamp)
            self.date_max = stamp if self.date_max is None else max(self.date_max, stamp)
            self.months[stamp[:7]] += 1
            if not (2020 <= timestamp.year <= 2025):
                self.issues["timestamp_outside_2020_2025"] += 1
            try:
                matches = (int(float(row["年份"])) == timestamp.year and
                           int(float(row["月份"])) == timestamp.month)
            except (ValueError, OverflowError):
                matches = False
            if not matches:
                self.issues["source_year_month_disagrees_with_timestamp"] += 1
        self.year_months[f'{row["年份"]}-{row["月份"]}'] += 1
        if not row["用户ID"].strip():
            self.issues["missing_user_id"] += 1
        try:
            lon, lat = float(row["经度"]), float(row["纬度"])
        except ValueError:
            self.issues["nonnumeric_coordinate"] += 1
            return
        if not (math.isfinite(lon) and math.isfinite(lat)):
            self.issues["nonfinite_coordinate"] += 1
            return
        self.lon_min, self.lon_max = min(self.lon_min, lon), max(self.lon_max, lon)
        self.lat_min, self.lat_max = min(self.lat_min, lat), max(self.lat_max, lat)
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            self.issues["coordinate_outside_world_bounds"] += 1
        if lon == 0 or lat == 0:
            self.issues["zero_coordinate_component"] += 1
        # Diagnostic envelope only; it is not the Shanghai study boundary.
        if not (120.5 <= lon <= 122.5 and 30.5 <= lat <= 32.0):
            self.issues["outside_broad_shanghai_screening_box"] += 1

    def export(self):
        return {
            "records": self.n,
            "timestamp_min": self.date_min,
            "timestamp_max": self.date_max,
            "records_by_month": dict(sorted(self.months.items())),
            "source_year_month_counts": dict(sorted(self.year_months.items())),
            "observed_month_count": len(self.months),
            "coordinate_range": {
                "longitude": [self.lon_min, self.lon_max],
                "latitude": [self.lat_min, self.lat_max],
            },
            "issues": dict(sorted(self.issues.items())),
            "screening_box": {"longitude": [120.5, 122.5], "latitude": [30.5, 32.0]},
            "screening_box_note": "Diagnostic only; no record is filtered before sampling.",
        }


def records(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != SOURCE_FIELDS:
            raise ValueError("Unexpected source schema; inspect before running this script.")
        yield from reader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    csv.field_size_limit(64 * 1024 * 1024)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    source_stat = args.source.stat()
    source_quality = Quality()
    for row in records(args.source):
        source_quality.add(row)
    total = source_quality.n
    target = total * 4 // 100  # floor(N * 0.04), using exact integer arithmetic.
    selected_indices = sorted(random.Random(args.seed).sample(range(total), target))
    sample_quality = Quality()
    user_map = {}
    missing_id_count = 0
    next_index = iter(selected_indices)
    selected_index = next(next_index, None)
    temp_path = args.output.with_suffix(".csv.new")
    with temp_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        for index, row in enumerate(records(args.source)):
            if index != selected_index:
                continue
            sample_quality.add(row)
            raw_id = row["用户ID"].strip()
            if raw_id:
                if raw_id not in user_map:
                    user_map[raw_id] = f"u{len(user_map) + 1:06d}"
                anonymous_id = user_map[raw_id]
            else:
                anonymous_id = ""
                missing_id_count += 1
            writer.writerow({
                "匿名用户ID": anonymous_id,
                "发布时间": row["发布时间"],
                "经度": row["经度"],
                "纬度": row["纬度"],
                "年份": row["年份"],
                "月份": row["月份"],
            })
            selected_index = next(next_index, None)
    if args.source.stat().st_size != source_stat.st_size or args.source.stat().st_mtime_ns != source_stat.st_mtime_ns:
        raise RuntimeError("The source changed while sampling; output not replaced.")
    if sample_quality.n != target:
        raise RuntimeError("Sample size does not match exact target.")
    temp_path.replace(args.output)
    index_path = args.output.with_name("weibo_sample_4pct_record_indices.json")
    index_path.write_text(json.dumps({
        "index_origin": 0, "source_csv_header_excluded": True,
        "csv_records_not_physical_lines": True, "indices": selected_indices
    }), encoding="utf-8")
    manifest = {
        "created_date": "2026-10-16",
        "source_file": args.source.name,
        "source_bytes": source_stat.st_size,
        "source_sha256": sha256(args.source),
        "source_encoding": "UTF-8 with BOM; strict decoding",
        "source_crs": "WGS84, as confirmed by the data provider",
        "source_fields": SOURCE_FIELDS,
        "sampling_unit": "CSV record (header excluded)",
        "sampling_method": "Simple random sample without replacement over all records; no prefiltering or deduplication",
        "sampling_fraction_requested": RATE,
        "sampling_seed": args.seed,
        "sampling_implementation": f"Python {platform.python_version()} random.Random.sample; sorted source record indices retained locally",
        "sampling_target": target,
        "sampling_fraction_actual": target / total,
        "anonymous_id_method": "Sample-local sequential codes in sampled source order, consistent for the same nonmissing source user ID; no source-to-code mapping exported",
        "distinct_sample_user_codes": len(user_map),
        "missing_sample_user_ids": missing_id_count,
        "output_file": args.output.name,
        "output_encoding": "UTF-8 with BOM",
        "output_fields": OUTPUT_FIELDS,
        "output_bytes": args.output.stat().st_size,
        "output_sha256": sha256(args.output),
        "record_indices_file": index_path.name,
        "record_indices_sha256": sha256(index_path),
        "source_quality": source_quality.export(),
        "sample_quality": sample_quality.export(),
        "excluded_columns": ["用户ID", "性别", "地点类型", "微博文本"],
        "limitations": [
            "The filename and observed coverage do not independently prove completeness of all Shanghai Weibo posts.",
            "A 4% record sample is not a 4% user sample and does not correct platform or collection bias.",
            "Sequential user coding is pseudonymization; precise coordinates and timestamps may still carry reidentification risk.",
            "Source data rights and redistribution permission must be checked by the data provider; no third-party license is inferred."
        ],
    }
    manifest_path = args.output.with_name("weibo_sample_4pct_manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "records": total, "sample_records": target, "sample_sha256": manifest["output_sha256"],
        "timestamp_min": manifest["source_quality"]["timestamp_min"],
        "timestamp_max": manifest["source_quality"]["timestamp_max"],
        "source_issues": manifest["source_quality"]["issues"],
        "sample_issues": manifest["sample_quality"]["issues"],
        "output": str(args.output), "manifest": str(manifest_path)
    }, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
