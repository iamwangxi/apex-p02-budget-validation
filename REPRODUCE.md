**English** | [简体中文](REPRODUCE.zh-CN.md)

# Reproduce the finite Budget audit

Run every command below from the root of this package. Python 3.9 or later is required. The release was tested on Python 3.9.6, macOS arm64, with `pynauty==2.8.8.1`. `triangulations.py` and `verify_certificates.py` use only the standard library; the other full-enumeration and audit commands use pynauty. Installation may require a C compiler if a wheel is unavailable. Do not use Python's `-O` option: assertions are part of the checks.

## Check the shipped files

On macOS:

```sh
shasum -a 256 -c MANIFEST.sha256
```

On Linux with GNU coreutils, use `sha256sum -c MANIFEST.sha256`. The manifest checks byte integrity, not mathematical validity. It excludes itself, environments, caches, local validation logs, and user reruns.

The quick standard-library check validates reported counts, type metadata, agreement flags, and the hashes bound by the software audit:

```sh
python3 -B code/verify_certificates.py
```

For actual recomputation of every pure witness and every certificate record, install the dependency and run the supplementary audit:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements.txt
.venv/bin/python -B code/independent_predicates.py
.venv/bin/python -B code/audit_checks.py --results certificates
```

The audit is read-only unless `--output` is supplied. It checks 11,504 pre-deduplication witnesses against both predicate implementations, atom conservation, Euler relations, all 658 record reconstructions and identifiers, 658 deterministic random dart relabelings, and five hand-built positive/negative legality examples. It shares `Host` and the separate predicate checker; it does not independently regenerate hosts.

Inspect a single record using a one-based line number, or substitute an identifier prefix:

```sh
.venv/bin/python -B code/inspect_case.py --line 1
.venv/bin/python -B code/inspect_case.py --line 658
```

## Cross-model checks (standard library only)

Two separately written scripts need no dependency and import no other module of this package:

```sh
python3 -B code/claude_host_census.py --small-cases
python3 -B code/claude_budget_check.py
```

The first validates the 191 hosts, confirms they are pairwise non-isomorphic, and checks that the automorphism-weighted count of 24/|Aut+| over all hosts equals 4096 = A002005 a(4); `--small-cases` brute-forces a(1) = 4 and a(2) = 32 on the same map family. The second recomputes pure badness for all 782,145 subsets, checks Lemmas 9.11, 9.14 and 9.15, Corollary 9.16 and auxiliary Corollary 9.13 on the 11,504 purely bad witnesses, rechecks host legality and prints sensitivity controls. Both exit with status zero and end with `passed=True`; the recorded output is `certificates/claude-crosscheck.txt`. The second script took about a minute in the recorded environment.

## Rebuild the complete finite computation

Choose a fresh output directory for each run. These commands write to `reproduced/`; repeating them overwrites files in that directory. They do not change the shipped `certificates/` directory. No network is used after dependency installation.

```sh
mkdir reproduced
.venv/bin/python -B code/triangulations.py --output reproduced/hosts.json
.venv/bin/python -B code/flip_crosscheck.py --hosts reproduced/hosts.json --output reproduced/host-crosscheck.json
.venv/bin/python -B code/independent_predicates.py
.venv/bin/python -B code/subsets.py --hosts reproduced/hosts.json --out reproduced
.venv/bin/python -B code/audit_checks.py --results reproduced --output reproduced/software-audit.json
.venv/bin/python -B code/verify_certificates.py --results reproduced --export-strata reproduced/strata.csv --compare certificates
```

The full release rerun took approximately 27 seconds in the recorded local environment; this is an observation, not a runtime guarantee. Do not use `--limit` for a complete run. Prefix diagnostics are explicitly marked incomplete.

## Acceptance criteria

All commands must exit with status zero. The expected results are:

| Check | Expected result |
|---|---|
| Host generation | `complete=true`, 60,060 constructions, 191 hosts |
| Flip cross-check | `complete=true`, 191 hosts, 1,924 transitions, both set differences zero, `agree=true` |
| Subsets | `complete=true`, 782,145 candidates, 770,641 not pure, 11,504 pure witnesses, 658 unique, no failures |
| Full audit | `passed=true`, 115,040 field comparisons, 658 record reconstructions, 658 relabelings, 5 legality examples |
| Unique types by edge count 1-12 | `2,10,26,69,114,164,142,95,30,6,0,0` |
| Unique types by used-mark count 1-6 | `32,238,303,85,0,0` |
| Candidates using 5 and 6 marks | 295,711 and 165,188; both ranges were tested |
| Final comparison | `stable_rerun_comparison=true` |

`strata.csv` contains all 72 edge-count/used-mark cells, including zero cells omitted from the sparse JSON statistics. `types.jsonl` contains one representative per oriented type; each record includes the host permutations, selected-edge mask, embedding/region data, main predicates, separate predicates, and gap data.

For this pinned implementation and tested architecture, the regenerated `types.jsonl` agrees byte-for-byte with the shipped records. Timing fields naturally change, and audit hashes that bind files with timings change with them. The comparison excludes only `seconds`, `elapsed_seconds`, and the audit hash mapping from structural comparison; each mapping is still checked against the corresponding files. Canonical certificate bytes and derived identifiers may depend on pynauty/nauty version and architecture. A different platform can preserve the same mathematical class set and counts without reproducing those identifiers; a byte-comparison failure then needs investigation, not dismissal.

The numerical checks do not independently verify the geometric completeness inputs, the full hyperelliptic correspondence, the intersection formula, or the geometric Cone lemma. Read the [Budget submission](proof/submission.md) for the finite reduction, reconstruction specification and precise scope. Arguments about the paper's other proof routes are outside this package.
