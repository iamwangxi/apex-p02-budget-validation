"""Verify shipped counts and optional rerun equivalence without third-party imports.

This is an integrity/count checker, not an independent topological proof.
Use audit_checks.py for full witness and certificate reconstruction.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["candidates", "legal", "not_pure", "pure", "duplicates", "unique", "checked"]


def load(directory, name):
    return json.loads((directory / name).read_text(encoding="utf-8"))


def strata_csv(stats):
    rows = {(r["E"], r["V"]): r for r in stats["strata"]}
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(["E", "V_prime", *FIELDS])
    for edges in range(1, 13):
        for vertices in range(1, 7):
            row = rows.get((edges, vertices), {})
            writer.writerow([edges, vertices, *(row.get(key, 0) for key in FIELDS)])
    return output.getvalue()


def stable(value):
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items()
                if key not in {"seconds", "elapsed_seconds", "sha256"}}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def verify(directory):
    hosts = load(directory, "hosts.json")
    stats = load(directory, "statistics.json")
    flip = load(directory, "host-crosscheck.json")
    audit = load(directory, "software-audit.json")
    assert hosts["stats"]["complete"] and stats["complete"]
    assert hosts["stats"]["processed_raw_constructions"] == 60060
    assert len(hosts["hosts"]) == hosts["stats"]["canonical_oriented_hosts"] == 191
    assert flip["complete"] and flip["agree"] and flip["hosts"] == 191
    assert flip["transitions"] == 1924 and flip["only_main"] == flip["only_flip"] == 0
    assert stats["unique"] == 658 and stats["failures"] == []
    total = Counter()
    by_edges = Counter()
    by_vertices = Counter()
    candidates_by_vertices = Counter()
    for row in stats["strata"]:
        total.update({key: row.get(key, 0) for key in FIELDS})
        by_edges[row["E"]] += row.get("unique", 0)
        by_vertices[row["V"]] += row.get("unique", 0)
        candidates_by_vertices[row["V"]] += row.get("candidates", 0)
    assert total["candidates"] == 782145 and total["not_pure"] == 770641
    assert total["pure"] == 11504 and total["unique"] == 658
    assert total["duplicates"] == 10846 and total["checked"] == 658
    assert [by_edges[e] for e in range(1, 13)] == [2, 10, 26, 69, 114, 164, 142, 95, 30, 6, 0, 0]
    assert [by_vertices[v] for v in range(1, 7)] == [32, 238, 303, 85, 0, 0]
    assert candidates_by_vertices[5] == 295711 and candidates_by_vertices[6] == 165188
    records = [json.loads(line) for line in
               (directory / "types.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(records) == len({record["id"] for record in records}) == 658
    record_edges = Counter(len(record["selected_edges"]) for record in records)
    record_vertices = Counter(record["checks"]["V"] for record in records)
    assert record_edges == +by_edges and record_vertices == +by_vertices
    for record in records:
        assert all(record["checks"][key] == record["independent"][key]
                   for key in record["checks"])
        assert all(record["checks"][key]
                   for key in ["9.11", "9.11_disjoint", "9.11_faces", "9.13", "9.14", "9.15", "9.16"])
    assert audit["passed"]
    expected_audit = dict(all_pure_witnesses=11504, all_candidates=782145,
                          unique=658, checked_record_ids=658,
                          full_record_reconstructions=658,
                          random_dart_relabelings=658,
                          all_subpredicate_comparisons=115040,
                          legal_positive_negative_examples=5)
    assert audit["counts"] == expected_audit
    for name, expected in audit["sha256"].items():
        prefix, basename = name.split("/", 1)
        path = ROOT / "code" / basename if prefix == "code" else directory / basename
        assert prefix in {"code", "results"}
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
    return stats, dict(passed=True, hosts=191, candidates=782145,
                      pure_witnesses=11504, types=658,
                      checked_record_metadata=658)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "certificates")
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--export-strata", type=Path)
    args = parser.parse_args()
    stats, result = verify(args.results)
    csv_text = strata_csv(stats)
    existing_csv = args.results / "strata.csv"
    if existing_csv.exists():
        assert existing_csv.read_bytes() == csv_text.encode("utf-8")
    if args.export_strata:
        args.export_strata.write_bytes(csv_text.encode("utf-8"))
    if args.compare:
        verify(args.compare)
        for name in ["hosts.json", "statistics.json", "host-crosscheck.json", "software-audit.json"]:
            assert stable(load(args.results, name)) == stable(load(args.compare, name)), name
        assert (args.results / "types.jsonl").read_bytes() == (args.compare / "types.jsonl").read_bytes()
        result["stable_rerun_comparison"] = True
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
