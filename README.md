# Strategic Override Research Studio

**Knowing when to disagree with AI.** This repository reproduces the paper's behavioral analyses and validates the Managerial Strategic Override Dataset (MSOD) v1.0 experimental design.

## One-click GitHub reproduction
Open **Actions → Reproduce Complete Strategic Override Study → Run workflow**. It installs dependencies, runs all tests, regenerates every table and figure, validates MSOD, audits FiFAR, and uploads `strategic-override-complete-results`.

## Bundled resources
- **Loan human-AI experiment:** 2,810 decisions from 281 participants.
- **Chess human-AI experiment:** 3,000 decisions from 100 participants.
- **FiFAR:** structural benchmark audit of a 1,000,000-record fraud base dataset and 50 synthetic experts. FiFAR is not human behavioral evidence.
- **MSOD v1.0:** 10 strategic cases × 8 conditions = 80 stimuli. It contains no collected manager responses. DOI: `10.5281/zenodo.21930342`.

## Central diagnostic
`OSI = P(override | human initially correct, AI wrong) - P(override | human initially wrong, AI correct)`

Positive OSI means disagreement is allocated more often to human-advantage conflicts. Negative OSI means people override more often when correct AI could have corrected an initial human error. OSI is not a universal intelligence score, causal effect, or proof of private information.

## Local run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python reproduce.py
python app.py
```

## Five-state outcome decomposition
The behavioral analysis distinguishes five mutually exclusive outcomes: appropriate reliance, justified override/rescue, automation failure, unjustified override, and non-rescue override. The last category captures a multiclass case in which the AI recommendation is wrong, the human rejects it, but the final human action is also criterion-incorrect. The software verifies that the five shares sum to 1 separately for Loan and Chess. In the bundled data, non-rescue override is 0.0% for Loan and 17.3% for Chess; the exhaustive Chess unjustified-override share is 19.2%.

## Reproducibility folder
The `reproducibility/` folder contains the expected primary results and an independent verification script. GitHub Actions runs this check after regenerating all outputs.

## Future MSOD response analysis

The web app includes a dedicated tab for **genuine collected MSOD response CSVs** using the bundled response schema. It derives override, accuracy, justified/unjustified override, factorial-cell summaries, and a selective-override contrast. It never simulates missing manager responses.

## Research-integrity boundary
Behavioral findings use only the loan and chess human-participant datasets. FiFAR's experts are synthetic. MSOD v1.0 is a prospective experimental instrument. This software never fabricates manager responses.

## License
Software copyright © 2026 Mohammad Amir Khusru Akhtar. Apache License 2.0. Third-party datasets retain their original licenses. MSOD dataset/text materials are CC BY 4.0.
