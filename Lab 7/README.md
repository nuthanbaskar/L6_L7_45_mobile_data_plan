# Lab 7 - Fuzz Testing for Input Validation Bugs

This folder adapts the three functions from the Lab 6 mobile data plan app to
the requested `processor.py` and `test_processor.py` filenames.

## Run

From this folder, install the test dependencies and run:

```powershell
python -m pip install pytest hypothesis
python -m pytest -v
```

Hypothesis generates inputs for all three functions. The tests verify each
function's calculation and exercise invalid boundary values, including negative
recharge values, malformed data usage, and invalid day counts.
The execution evidence and both requested source files are included in
`Submission_Report.pdf`. The generated report is accompanied by the captured
console output and screenshots. To rebuild the PDF from those files, install
`reportlab` and `pillow`, then run `python make_report.py`.

## Input rules

- Data usage and recharge amounts must be finite, non-negative numbers.
- Recharge counts and days remaining must be integers; days remaining may be
  negative to represent grace or expired status.
- Boolean flags must be booleans.
- Plan names must be `basic`, `standard`, or `premium`.

The corrected functions reject inputs outside these rules with `ValueError`.
