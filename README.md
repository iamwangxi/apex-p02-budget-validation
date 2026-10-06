**English** | [简体中文](README.zh-CN.md)

# Apex paper 02: exhaustive six-point Budget validation

This focused package supports a finite audit of Lemmas 9.11, 9.14, 9.15 and Corollary 9.16 of Apex Intelligence's [*The complex of curves pairwise intersecting at most once is contractible in genus two*](https://math.apexin.net/papers/curve-complex-genus-two.pdf), dated 11 September 2026. Corollary 9.13 is also checked as an auxiliary predicate. The target PDF has 35 pages and SHA-256 `d1eadd01f94e9af17ee9f5fb2ee1b05b326430f37296309fd9417340ea366fd4`.

The contribution is the exhaustive combinatorial audit and its reproducibility evidence. The paper's Budget statements and standard surface-topology inputs are not claimed as new theorems. The submission text is version **v1.3**; it cites repository snapshot **v1.2** of [apex-p02-budget-validation](https://github.com/iamwangxi/apex-p02-budget-validation). The `v1.2` tag fixes that snapshot. Later text or documentation changes require a new commit and a new version; the existing tag must not be moved.

## Contents

- [Submission text](proof/submission.md): the exact bytes of the separately maintained official-form Markdown, including the full finite reconstruction specification and AI disclosure. Its first line is the proposed title; the remaining text is the submission body. It identifies the repository URL and the `v1.2` snapshot separately from submission version `v1.3`.
- [Reproduction instructions](REPRODUCE.md): executable commands, expected counts and the distinction between quick integrity checks and full recomputation.
- [Packaging and provenance](PACKAGING.md): the extraction boundary and verification of unchanged scientific files.
- [Code](code/): host generation, independent host comparison, region predicates, enumeration, record inspection and audit utilities, plus two separately written cross-model checks (`claude_host_census.py`, `claude_budget_check.py`).
- [Certificates](certificates/): 191 hosts, 658 type records, all 72 statistical strata, software-audit evidence and the recorded output of the cross-model checks (`claude-crosscheck.txt`).
- [SHA-256 manifest](MANIFEST.sha256): every intended release file except the manifest itself.
- Simplified Chinese translations: [README](README.zh-CN.md), [reproduction instructions](REPRODUCE.zh-CN.md), [packaging note](PACKAGING.zh-CN.md) and [submission text](proof/submission.zh-CN.md). They were produced by OpenAI Codex (GPT); the English files are authoritative.

Tag `v1.0` was the snapshot cited by submission text v1.2. Tag `v1.1` added the Chinese translations and language-switch lines, updated the version notes in this README and `PACKAGING.md`, and corrected one label in `REPRODUCE.md`, where Corollary 9.13 had been called a lemma. It also clarified that pure badness is recomputed for all 782,145 candidate subsets and the Budget assertions are checked on the 11,504 purely bad witnesses. At tag `v1.1`, the submission text, code and certificates remained byte-identical to `v1.0`. Tag `v1.2` replaces the submission with text v1.3, synchronizes its Chinese translation, updates the version notes and adds the host-certificate reading guide below. Code and certificates are byte-identical across all three tags.

## Exact scope

The 658 nonempty purely bad arc-system types are classified up to orientation-preserving homeomorphism of a six-marked sphere, allowing permutation of the marked labels. Mirrors are not deliberately identified. The computation does not enumerate the infinitely many isotopy classes with individually fixed marks.

Completeness depends on embedded arc-system representatives, standard essentiality/empty-disc isotopy facts, the independent edge bound `E <= 12`, and generalized-triangulation extension. These reduction arguments appear in the submission; the truncated finite computation does not independently establish its own cutoff or certify all dimensions of the arc complex.

| Audit quantity | Result |
|---|---:|
| Tree/stem constructions | 60,060 |
| Oriented triangular hosts | 191 |
| Nonempty host subsets | 782,145 |
| Rejected solely as not purely bad | 770,641 |
| Purely bad host witnesses | 11,504 |
| Oriented types | 658 |
| Predicate-field comparisons before deduplication | 115,040 |
| Failed Budget predicates | 0 |

The host comparison uses a separate Whitehead-move closure from an explicit octahedron. The second predicate implementation uses dual-graph BFS instead of the main union-find regions. Both share the mathematical encoding model and definitions. The supplementary audit calls these implementations; it is not a third independent predicate implementation. A third implementation, written separately by Claude from the paper's definitions, reproduces all 11,504 purely bad witnesses with zero predicate failures; a generator-independent census shows that the 191 hosts weighted by 24/|Aut+| sum to 4096, the number of rooted planar cubic maps with eight vertices (OEIS A002005). Both use only the standard library and import no other module of this package.

This package does not validate the original spectral sequence, the full contractibility theorem, the hyperelliptic dictionary, the intersection-number formula, or the geometric Cone lemma. Experiment 1B was not performed: zero new exact intersection-number samples. No other proof route is needed or claimed here.

## Reading the host certificate

`alpha` pairs darts into edges. The six cycles of `sigma` are the marked vertices; the eight triangular face cycles follow `d -> sigma[alpha[d]]`, as checked by `validate_map` in `code/triangulations.py`.

These hosts are generalized triangulations. A marked vertex of degree 1 lies inside a self-folded triangle; triangles bounded by three loops based at the same marked point also occur.

All these hosts are legal. The recorded cross-model output contains 1,465 direct legality tests and 0 violations (`certificates/claude-crosscheck.txt`).

## Reproduction and provenance

The copied scientific files preserve the already verified packaged implementation and certificates byte-for-byte. A complete packaged rerun took place on 29 September 2026. For this focused extraction, the SHA-256 bindings and standard-library quick verifier were checked; no unnecessary new full enumeration was run. The quick verifier checks recorded evidence and integrity, not mathematical completeness or fresh execution of every predicate.

Mathematical drafting and prior checking used GPT-6 Astra and Claude Opus 5.5. GPT-based agents produced and reviewed the finite reduction, code and software audits. Claude reviewed version v1.1 of the focused submission and added the two cross-model checks. A new GPT session reviewed the v1.2 changes and their affected context. For tag v1.1, OpenAI Codex (GPT) produced the Chinese translations and a fresh GPT session checked them against the English sources. For tag v1.2, a DeepSeek-based agent reviewed the text, Claude and GPT adjudicated the wording points, Codex made the changes, and a fresh GPT session reviewed them. AI review, executable results and finite certificates are distinct evidence; none is human expert endorsement or formal verification.

Python 3.9 or later and `pynauty==2.8.8.1` support the full workflow. Code is MIT-licensed; original prose and the generated certificate collection are offered under CC BY 4.0 to the extent applicable rights exist. The inherited attribution is retained in [LICENSE](LICENSE). Third-party works and dependencies retain their own licenses; external PDFs are linked rather than bundled.

## Revision note

This revision differs from `36532d51356aa235bd2fe15c56540751bb7a01c6` only in how formulas are written. GitHub's Markdown processing removed backslash escapes such as `\{` and `\,` inside `$...$` and did not recognise some formulas, so every formula now uses GitHub's literal math syntax. No mathematical text was changed.
