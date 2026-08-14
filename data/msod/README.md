# Managerial Strategic Override Dataset (MSOD) v1.0

## Experimental benchmark and data-collection instrument

**Creator:** Mohammad Amir Khusru Akhtar  
**Affiliation:** Usha Martin University, Ranchi–834001, Jharkhand, India  
**Contact:** akakhtar.2024@gmail.com  
**Version:** 1.0  
**Release date:** 14 August 2026  
**Resource type:** Dataset  
**DOI:** 10.5281/zenodo.21930342  
**Persistent link:** https://doi.org/10.5281/zenodo.21930342

MSOD v1.0 is an open, reusable experimental benchmark for studying when people should accept or override AI recommendations in strategic decisions. It contains **10 controlled strategic cases crossed with a 2 × 2 × 2 design**, producing **80 unique experimental stimuli**.

The three factors are:

1. candidate problem representation: `low_qc_candidate` vs `high_qc_candidate`;
2. human-only decision-relevant information: `absent` vs `present`;
3. AI recommendation correctness: `correct` vs `incorrect`.

## Critical status statement

**MSOD v1.0 contains no collected human-participant responses.** It is a stimulus dataset, experimental instrument, response schema, codebook, randomisation specification, and analysis specification. It must not be described as evidence from 600 managers.

The labels `high_qc_candidate` and `low_qc_candidate` are **candidate DPT-inspired representation manipulations**. They are not validated empirical measurements of formal Question Compression. The supplied pretest instrument should be used before confirmatory claims.

A later empirical release may add de-identified participant responses after ethics approval, informed consent, preregistration, power analysis, quality control, and disclosure-risk review.

## Why the dataset exists

Existing human–AI datasets often capture a human choice, AI advice and a later choice, but they do not jointly manipulate strategic problem representation, exclusive human information, and AI correctness. MSOD is designed to make those factors experimentally separable.

## Files

- `data/msod_case_master.csv` — 10 master strategic cases.
- `data/condition_matrix.csv` — the eight factorial conditions.
- `data/msod_stimulus_bank_80.csv` — 80 ready-to-present case-condition stimuli.
- `data/msod_response_template.csv` — header-only schema for future human data.
- `data/codebook.csv` — variable definitions and coding rules.
- `data/analysis_variable_spec.csv` — derived-variable definitions.
- `data/qc_pretest_instrument.csv` — manipulation-pretest items.
- `docs/CASEBOOK.md` — human-readable case descriptions.
- `docs/DATA_DICTIONARY.md` — detailed field documentation.
- `docs/EXPERIMENT_PROTOCOL.md` — four-stage administration protocol.
- `docs/PREREGISTRATION_TEMPLATE.md` — confirmatory hypotheses and exclusions template.
- `docs/ETHICS_AND_PRIVACY.md` — human-subject and public-release safeguards.
- `docs/ZENODO_UPLOAD.md` — publication-ready Zenodo metadata.
- `code/generate_randomization.py` — reproducible balanced assignment generator.
- `code/derive_variables.py` — creates trial-level derived outcomes after data collection.
- `code/validate_package.py` — package integrity checks.

## Core experimental sequence

Each trial follows four stages:

1. **Common evidence** → initial decision + confidence.
2. **AI recommendation** → displayed recommendation + confidence.
3. **Additional evidence** → human-only evidence present or absent.
4. **Final decision** → decision + confidence + short reason.

The declared criterion key is provided for reproducible analysis. Researchers may create alternative criterion frameworks, but they should version and document them instead of silently changing the supplied key.

## Main derived outcomes

`override = 1(final_decision != ai_recommendation)`

`decision_accuracy = 1(final_decision == criterion_correct_final_decision)`

`justified_override = override × decision_accuracy`

`unjustified_override = override × (1 - decision_accuracy)`

`OSI = override rate when AI is incorrect - override rate when AI is correct`

OSI lies in [-1,1]. Higher values indicate more selective override. It is not a probability of expertise and should be reported with uncertainty.

## Decision Answerability

The randomized human-information factor permits a counterfactual contrast between decisions when critical evidence is present and absent. Researchers should estimate the contrast using the randomized design and suitable participant/case clustering or multilevel models. The package does not pretend that a single difference-in-means is the complete mathematical Experience Architecture object.

## Recommended empirical sample

A planning target of 500–800 working managers is reasonable, but **the final sample size must be justified by a preregistered multilevel power analysis** after pilot estimates of effect size and participant/case dependence. Ten repeated trials per participant are not ten independent participants.

## Reuse

The cases are deliberately generic and controlled. Researchers may:
- use the 80 stimuli unchanged;
- translate them with back-translation and measurement checks;
- replace currency while preserving relative magnitudes;
- adapt domains while retaining the factorial structure;
- use the schema for other human–AI strategic decisions.

All changes should be documented and versioned.

## Licensing

The **dataset, case texts and documentation** are released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.  
The **code files** are released under the **Apache License 2.0**.

See `LICENSE_DATA.txt` and `LICENSE_CODE.txt`.

## Citation

Until a Zenodo DOI is assigned:

Akhtar, M. A. K. (2026). *Managerial Strategic Override Dataset (MSOD) v1.0: Experimental benchmark and data-collection instrument*. Version 1.0.

After publication, replace the provisional citation with the Zenodo-generated DOI.

