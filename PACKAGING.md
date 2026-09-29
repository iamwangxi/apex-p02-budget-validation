# Focused extraction and provenance

This package extracts only the finite six-point Budget verification from the previously audited `apex-p02-validation` package. It supports Lemmas 9.11, 9.14, 9.15 and Corollary 9.16, with auxiliary Corollary 9.13. It does not carry the broader validation of the original spectral sequence, geometric dictionary, Cone lemma or whole main theorem.

## Copied scientific files

The eight files in `code/` and six files in `certificates/` were copied by an explicit whitelist and matched the prior release manifest before copying. Every source and scientific certificate byte is unchanged. The existing software audit therefore continues to bind the same code and result hashes. No enumeration, geometric predicate, canonicalization rule, identifier, statistical cell, audit flag or timing field was changed.

The docstring of `code/triangulations.py` still refers to `proof/expanded-validation.md` from the earlier package. That file is not included here; the completeness argument it refers to is Section 2 of `proof/submission.md`. The code bytes were left unchanged because the software audit binds their hashes.

`LICENSE` and `.gitignore` were copied without alteration. `REPRODUCE.md` was copied with only its final scope paragraph changed: the obsolete expanded-proof link now points to the focused submission, and the paragraph limits its claim to the Budget reduction and algorithms. All executable reproduction commands and numerical acceptance criteria are unchanged.

The prior package's documentation records that its English packaging translated comments and diagnostics, made output paths explicit, and added a standard-library verifier without changing the mathematical algorithms. That packaged implementation was fully rerun on 29 September 2026: 191 hosts, 782,145 candidates, 11,504 pure witnesses and 658 types, with 115,040 predicate-field comparisons, 658 reconstructions, 658 relabelings and five legality examples. This focused extraction preserves those actual results; it does not imply a new complete run.

## New focused documents

`README.md`, this file and `proof/submission.md` were prepared for this single contribution. No expanded proof is included: the submission itself gives the completeness inputs, host construction, region atoms, exact predicates and deduplication specification. The source paper is identified by its URL and SHA-256 in both the README and submission.

`proof/submission.md` is byte-identical to the separately maintained official-form Markdown, submission version **v1.2**. Its first line is the proposed English title; its remaining text is the form body. The entire file, including title and whitespace, is 18,953 UTF-16 code units, below 20,000. Its SHA-256 is recorded in `MANIFEST.sha256`.

The repository URL is [apex-p02-budget-validation](https://github.com/iamwangxi/apex-p02-budget-validation), and the repository snapshot version is **v1.0**. Submission version `v1.2` and repository version `v1.0` identify different artifacts. The `v1.0` tag fixes this snapshot; later changes to the submission or documentation require a new commit and a new version, without moving the existing tag. Commit and manifest hashes are recorded in the external verification record. The reconstruction specification can be read independently of repository availability.

This revision changes only `proof/submission.md`, `README.md`, this packaging note and `MANIFEST.sha256`. All existing scientific files, including the two cross-model scripts and their recorded output, retain their exact bytes. Proof/form synchronization and the form limit are checked before regenerating the manifest.

## Verification of this extraction

The explicit whitelist contains eight code files, six certificate files, the license and ignore file, and reproduction instructions. The new focused README, packaging note and proof bring the manifest to 20 entries. On 29 September 2026 Claude added two cross-model scripts in `code/` and their recorded output in `certificates/`, bringing the manifest to 23 entries; the fourteen originally copied scientific files are unchanged. All release files are covered except the manifest itself. A SHA-256 manifest check and the standard-library quick verifier pass in this focused directory. The quick verifier validates counts, record metadata, comparison flags and the hashes bound by the software audit; it does not rerun every topological predicate.

The type-record SHA-256 remains `bc1a30fe32b3f357a3c94688e69e3a36979c60cd103017e0a4c1dd3f30244b4a`; the complete 72-cell CSV SHA-256 remains `11da4b46f89c08e1e614eefd87878737d30cde9d2bfb17e2c066d34dac809bde`.

No `.git`, `.local-validation`, environment, cache, previous whole-route proof, third-party PDF, conversation transcript or private machine path was copied. The release inventory consists only of the 23 manifest entries and `MANIFEST.sha256` itself.
