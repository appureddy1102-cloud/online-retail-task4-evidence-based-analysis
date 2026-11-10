# Strict Task 4 Review and Corrections

**Author:** T. Aparna Reddy  
**Review basis:** the five reviewer criticisms supplied in the current request; the exact 19-part structure; and the ten requested evaluation criteria.  
**Status:** internal evidence/readiness review, not an independent human assessment or an official internship score.

## 1. Reviewer feedback: correction and evidence

| Criticism | Correction made | Evidence in final submission |
|---|---|---|
| Lack of specific numerical examples | Actual source-row examples, full invoice reconstruction, complete monthly/country/SKU tables and explicit KPI denominators | Report Sections 8–12; `outputs/worked_*.csv`; full aggregate CSVs |
| Missing worked examples and calculations | Fourteen examples each show formula, actual values, arithmetic, result and interpretation | Section 11; manual SD, Pearson, Welch and chi-square code; independent checks |
| Insufficient original interpretation | Inspect exactly offset sale/credit records; decompose November sales growth; contrast country value with account concentration; qualify gross RFM with credits | Sections 10, 12 and 13; `extreme_transaction_pairs.csv`; country and customer summaries |
| Sections too short or incomplete | All nineteen parts are substantive; eight analytical questions; every original variable defined; complete cleaning, limitations, future scope and source appendix | Contents and all numbered sections; `report_manifest.json` |
| Findings not supported by actual evidence | Twelve findings each include numerical evidence, comparison, meaning, importance, recommended response and evidence filename | Section 13 and machine-readable finding register |

## 2. Ten-criterion evaluator-style review

| Criterion | Evidence / assessment | Remaining reservation |
|---|---|---|
| Dataset authenticity | Original 541,909 × 8 workbook; SHA-256 verified; official DOI/source/licence; independent validator re-reads Excel | Source catalogue's “no missing” flag is contradicted by actual rows and explicitly corrected |
| Section completeness | Exact 19-part order; full data dictionary, objectives, methodology, exploration, cleaning, EDA, statistics, visuals, insights, recommendations and appendices | Long report is necessary partly because full executable source is included; navigate through the real TOC |
| Calculation accuracy | Twenty-four baseline reconciliations; independent line/invoice/customer arithmetic; manual calculations checked against SciPy; financial identities | Financial presentation rounds pennies; source sub-penny values and floating-point tolerances must remain explicit |
| Cleaning quality | Each operation has issue/code/before/after/reason/effect; complete cleaned-all and separate sales exports; source-row trace; no arbitrary outlier deletion | Exact-duplicate removal and merchandise taxonomy remain disclosed assumptions, not verified business facts |
| EDA depth | Raw/valid numeric profiles, category frequencies, temporal group-bys, products, customer concentration, RFM × country and correlations | One retailer/year limits generalisation; some operational explanations are unidentifiable |
| Visual quality | Fifteen labelled Matplotlib/Seaborn figures cover every required type; log axes retain extreme observations; numerical interpretations and business implications | Log scales require care; box-plot fences are original-scale, not log-space fences |
| Numerical/ worked examples | Fourteen fully worked examples use actual workbook records and substituted values, including small-sample SD/Pearson and full-customer Welch | First-five subsets illustrate arithmetic only and are explicitly not random business samples |
| Original insights | Twelve evidence-backed insights include extreme offsets, volume/AOV decomposition, value-coverage denominators and account-dependent countries | No causal or current-business claim is possible from this historical extract |
| Practical recommendations | Eight actions state problem/evidence, proposed owner, action, expected mechanism and measurable decision gate | Benefits, ROI, current baselines and uplift are not observed; several pilots need fresh cost, identity or operational data |
| Reproducibility | Complete computational code appears in report and project; executed notebook saves outputs; original/cleaned data manifests, exact versions, source licence and executable validator | Optional Word pagination needs Writer/UNO or manual Word field refresh; public GitHub publication requires working authorization |

**Readiness conclusion:** the report is designed to meet the substantive evidence requirements of a 90+/100 submission. No official score exists and no grade is guaranteed. Technical checks establish reproducibility and consistency, not an external evaluator's judgement.

## 3. Specific issues caught and corrected during this revision

1. **Financial labels:** sales before credits are not called net revenue. The £10,642,110.80 → £9,748,131.07 → £9,726,006.95 bridge explicitly separates credits and bad-debt adjustments.
2. **Credit denominator ambiguity:** 16.12% document share, 8.40% credit-value/sales ratio, 14.81% share of raw IDs and legacy 7.75% absolute-activity share are distinguished. None is a linked-order cancellation probability.
3. **Time double counting:** 42 invoices span line timestamps. Earliest-invoice-time allocation produces 3,219 noon invoices, not 3,220; hourly counts sum exactly to 19,960.
4. **Country ranking:** Netherlands, not Germany, leads non-UK gross sales. Country breadth and 98.16% top-account concentration are reported separately.
5. **RFM denominators:** Champions represent 64.47% of identified sales and 53.84% of all sales, not interchangeable “revenue shares”. RFM tie-breaking and gross-value limits are stated.
6. **Zero-balance float artefacts:** classification uses penny-rounded credit-adjusted balances. Twenty-one accounts are non-positive at that presentation basis; unrounded floating-point comparisons would undercount near-zero balances.
7. **Chi-square effect convention:** the reported 2×2 test uses Yates correction, while standard Cramér's V is based on uncorrected Pearson chi-square (0.00141765). They are no longer conflated.
8. **Skew/mean interpretation:** repeat vs one-time mean AOV is not significantly different under Welch, while rank distributions differ; this is not labelled contradictory evidence or equivalence.
9. **Outliers:** the IQR flag count is evidence for inspection, not a deletion list. The 99th-percentile cap is a sensitivity, never the published cleaned total.
10. **Precision:** UK share and other substituted percentages are recalculated rather than copied from rounded summaries. Source £0.001 values remain positive, and totals are rounded only for display.
11. **Figure consistency:** output filenames and report figure captions now run sequentially from 01–15. Required Seaborn box and count plots are added without fabricating inputs.
12. **Source appendix:** every line of the three computational scripts is checked against the final DOCX after LibreOffice formatting; no truncated or pseudo-code-only appendix is accepted.

13. **Mixed Description type:** independent checking found one integer-valued Description (20713 at Excel row 420393). String normalization preserves it as text. Whitespace is counted only after lossless text handling, rather than letting object `.str.strip()` manufacture a missing value. The actual trimmed count remains 112,371.
14. **OOXML attribution:** LibreOffice emitted a non-canonical core-properties relationship, hiding otherwise present metadata from a standard reader. The formatter canonicalizes that relationship and restores author/title fields without changing layout; final checks enforce the correct author and title.

## 4. Verification and handoff boundary

- `reports/QA_REPORT.json` and `reports/VALIDATION.md` contain the actual executed check counts and individual results.
- `reports/layout_verification.json` records page/figure/table/code-layout checks and the final Word hash.
- The Word was rendered in LibreOffice; direct Microsoft Word application testing was not performed.
- The executed notebook stops on errors and embeds all fifteen chart outputs.
- Publication status, anonymous-link verification and any remaining GitHub authorization blocker are reported truthfully in `SUBMISSION_LINKS.md` and `PUBLICATION.json`.
- Task 5 is unchanged; the revised Task 4 is a separate project. Credentials are never part of report, notebook, code, commit or submission description.
