# Task 4 — Evidence-Based UCI Online Retail Analysis

**Submission report:** [Google Docs](https://docs.google.com/document/d/19-aivT1f8sQqmu4zjRhoA4kZIc4NtnE-v2sI8ceSOLE/edit) · [Word master](https://drive.google.com/file/d/12UGKoGWLT0XeweG9mqwoVWq4BAY87jQh/view)  
**Project repository:** https://github.com/appureddy1102-cloud/online-retail-task4-evidence-based-analysis


**Author:** T. Aparna Reddy  
**Deliverable:** YuvaIntern — Real-World Dataset Analysis Project, revised submission  
**Report date:** 7 November 2026

This is the revised **Task 4**, built on the genuine, unchanged UCI Online Retail workbook. It addresses the five supplied reviewer criticisms: too few numerical examples, missing worked calculations, limited original interpretation, incomplete sections and unsupported findings. The completed Task 5 project is separate and unchanged.

## Main deliverables

- **Word report:** [`reports/YuvaIntern_Task4_Real_World_Dataset_Analysis_Revised.docx`](reports/YuvaIntern_Task4_Real_World_Dataset_Analysis_Revised.docx)
- **Readable report:** [`reports/Task4_Real_World_Dataset_Analysis.md`](reports/Task4_Real_World_Dataset_Analysis.md)
- **Executed notebook:** [`notebooks/Task4_Online_Retail_Evidence_Based_Analysis.ipynb`](notebooks/Task4_Online_Retail_Evidence_Based_Analysis.ipynb)
- **Review and corrections:** [`REVIEW_AND_CORRECTIONS.md`](REVIEW_AND_CORRECTIONS.md)
- **Executed technical checks:** [`reports/VALIDATION.md`](reports/VALIDATION.md), [`reports/QA_REPORT.json`](reports/QA_REPORT.json)
- **Separate submission description:** [`SUBMISSION_DESCRIPTION.md`](SUBMISSION_DESCRIPTION.md), more than 200 words
- **Publication status and verified links:** [`SUBMISSION_LINKS.md`](SUBMISSION_LINKS.md)

The report has **19 requested parts, 14 fully worked calculations, 15 figures, 12 substantive findings and 8 measurable recommendations**. Figures include bar, histogram, time line, scatter, box plot, heatmap and count plot, with both Matplotlib and Seaborn.

## Dataset authenticity

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5BW33](https://doi.org/10.24432/C5BW33). Dataset licence: **CC BY 4.0**.

- Official page: <https://archive.ics.uci.edu/dataset/352/online+retail>
- Official archive: <https://archive.ics.uci.edu/static/public/352/online+retail.zip>
- Workbook: `data/Online Retail.xlsx`, sheet `Online Retail`
- Original dimensions: **541,909 × 8**
- Original bytes: **23,715,344**
- SHA-256: `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`
- Window: **1 December 2010–9 December 2011**; the final month is partial.

The script stops on a checksum mismatch. If the workbook is absent, it downloads the same official archive and verifies its bytes before analysis. The full project archive includes the unchanged original and both complete cleaned exports; the fallback download is only for a deliberately missing workbook. No substitute dataset or synthetic records are used.

## Reproduce the analysis

Tested with **Python 3.13.16**. Exact installed library versions are in `requirements.txt`.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell alternative: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/analyze.py
python scripts/make_charts.py
python scripts/run_notebook.py
python tests/validate_outputs.py
```

The analysis generates all CSV/JSON evidence and full cleaned-data exports. On a memory-constrained machine, close Writer before notebook execution/validation; the notebook releases temporary analysis frames before continuing. The notebook re-executes the analysis and figures; `allow_errors=False` prevents silently retaining failed cells. For a fresh Excel import, remove the optional local `.cache/*_raw.pkl` first. The independent validator always reads Excel directly and does **not** trust that cache.

### Regenerate the Word report

```bash
python scripts/build_report.py
```

This writes `.cache/Task4_draft.docx`, the Markdown report and `outputs/report_manifest.json`. Open the draft in Word/Writer, refresh the contents and page fields and save to the final report path. For the tested Linux route, install LibreOffice Writer, `python3-uno`, Carlito/Liberation fonts and the optional packages in `requirements-publishing.txt`, then run a headless service and formatter:

```bash
libreoffice -env:UserInstallation="file://$(pwd)/.cache/lo-profile" \
  --headless '--accept=pipe,name=task4lo;urp;StarOffice.ServiceManager' \
  --norestore --nodefault --nofirststartwizard
# In another terminal, from the project root:
/usr/bin/python3 scripts/format_document.py
python tests/validate_outputs.py
```

The final OOXML Word was rendered in LibreOffice for layout verification. Microsoft Word itself was not available for direct testing. The layout-check PDF is internal, not a replacement submission master. Publication is separate from numerical reproduction and requires the relevant account authorization.

## Cleaned data and scopes

| View | Rows | Columns | Treatment |
|---|---:|---:|---|
| Original workbook | 541,909 | 8 | Unchanged |
| `cleaned_all_records.csv.gz` | 536,641 | 16 | Exact duplicates removed; normalized labels/types; all transaction classes retained |
| `qualified_sales.csv.gz` | 524,878 | 16 | Separate positive-quantity, positive-price, non-credit view |
| Qualified invoice summary | 19,960 | See CSV | One invoice at earliest qualified timestamp |
| Identified purchasers | 4,338 | See CSV | Only customer-level outputs require a present ID |

The 16 cleaned fields are the eight originals, `SourceRow` and seven derived fields: `IsCredit`, `IsNonProduct`, `IsOtherNegativeMovement`, `HasCustomerID`, `IsQualifiedSale`, `LineValue` and `Month`.

```python
import pandas as pd
clean = pd.read_csv('data/cleaned_all_records.csv.gz',
    dtype={'InvoiceNo':'string', 'StockCode':'string', 'CustomerID':'Int64',
           'IsQualifiedSale':'boolean'}, parse_dates=['InvoiceDate'])
sales = clean.loc[clean.IsQualifiedSale].copy()
```

`SourceRow` is the original Excel row, including the header offset. Missing IDs stay missing. `UNKNOWN` is a missing-description sentinel, not an inferred product label. `data/cleaned_data_manifest.json` records row counts, sizes and SHA-256 values. Prices as small as £0.001 remain positive; source precision is preserved and monetary presentation is rounded at the end.

### Cleaning decisions that matter

- **5,268 exact duplicates** are removed under an assumption, not proved duplicate business events. No-dedup sales are £10,666,684.54; the difference is £24,573.74.
- **135,037 missing CustomerIDs** remain in the complete cleaned data. Anonymous qualified sales of **£1,754,901.91** remain in business totals.
- **1,454 missing descriptions** receive `UNKNOWN`; **112,371** edge-whitespace labels are trimmed without changing money or rows.
- **Outliers are flagged and retained**: 27,111 quantity and 37,827 unit-amount flags. Winsorisation is a separately labelled sensitivity only.
- All **9,251 C-credit lines**, **1,336 other negative-quantity movements** and **1,176 remaining lines** stay in cleaned-all.
- **42 split-timestamp invoices** are assigned once to their earliest time, correcting noon starts to **3,219**.
- **Eight customers span country labels**; first observed country is a disclosed customer-level convention, not a verified residence correction.
- The configured non-product code list is explicit in `scripts/verified_core.py`; it affects only the merchandise view, not all-sales totals.

## Selected computed results

| Metric | Actual result | Scope |
|---|---:|---|
| Sales before credits | £10,642,110.80 | Qualified lines; includes positive non-product activity |
| Recorded C-credit value | £893,979.73 | Absolute signed C-credit total |
| Credit-adjusted transaction value | £9,748,131.07 | Sales less C-credit value |
| All-line signed transaction value | £9,726,006.95 | Also includes −£22,124.12 other adjustments |
| Mean / median invoice value | £533.17 / £303.30 | Qualified invoice grain |
| UK share | 84.59% | Qualified sales value |
| Known-sales coverage | 83.51% | Identifiable purchaser sales / all sales |
| Observed repeat share | 65.58% | 2,845 of 4,338 identified purchasers; not cohort retention |
| November sales / invoices | £1,503,866.78 / 2,769 | Full November 2011 |

Two directly inspected extreme sale–credit pairs completely offset **£245,653.20**, or **27.48% of recorded credit value**. The Netherlands leads non-UK sales, but its largest account represents **98.16% of identified country sales**. November sales growth is **30.63%**, decomposing into **35.74% more invoices** and **3.76% lower AOV**.

## Evidence and project structure

```text
scripts/          verified core, exploration/cleaning, charts, Word and notebook utilities
notebooks/        executed analysis with actual outputs and 15 plot displays
data/             unchanged original, two complete gzip exports and provenance manifests
outputs/          full numerical evidence, worked tables, exceptions and report register
visualizations/   15 high-resolution, labelled PNG figures
reports/          final Word, Markdown, technical QA, hashes and layout verification
references/       preserved prior Task 4 results for 24 exact baseline reconciliations
tests/            independent workbook-backed validator
```

## Interpretation boundaries

This historical case study does not identify profit, current performance, causal drivers, fraud, campaign uplift or forecast recoveries. Country groups are observational; customer invoices and time periods are dependent. Customer-level Welch and rank tests are exploratory and conditional, not a remedy for non-random coverage. The final month is partial; RFM is gross-value, quintile/tie-dependent and not lifetime value. Every recommendation specifies a problem, evidence, proposed action, expected mechanism and measurement, not an invented outcome.

Technical validation and rubric review are not an official internship grade. A 90+/100 evaluation is an aim, not a guarantee.

## Licensing and security

Original analysis code: MIT, T. Aparna Reddy. Source/derived UCI data: CC BY 4.0 with attribution and changes in `DATA_LICENSE.md`. Do not commit credentials or personal operational data. If any GitHub token was exposed in conversation, revoke it and use a newly authorized, least-privilege method outside the report and repository. No credentials are included in this project.
