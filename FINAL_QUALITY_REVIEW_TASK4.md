# Historical pre-correction quality review — YuvaIntern Task 4

> Historical snapshot: this review applied to the earlier Word SHA shown below. The numerical, wording and validator corrections were subsequently applied; do not interpret its earlier GitHub-pending status as the present publication status. See `SUBMISSION_LINKS.md` for the current report.

**Report reviewed:** `reports/YuvaIntern_Task4_Real_World_Dataset_Analysis_Revised.docx`, by T. Aparna Reddy.  
**Reviewed version:** SHA-256 `1db4ea87c9616c6729a134ce7a151ba2eca38eeca67ec3e1384f4a879d05465f`; 73 pages in the LibreOffice rendering.  
**Scope:** all report pages, including the complete computational appendix; all 15 chart images; selected rendered pages across the report; independently recalculated key figures; rerun of the workbook-backed validation suite; inspection of publication and package evidence.  
**Page references:** original Word master as rendered in LibreOffice. Google Docs or Word may paginate differently. This review is an estimate, not an official evaluator decision.

## 1. Overall assessment

**Verdict: NOT READY TO SUBMIT against the full original submission requirements.** The analytical report is substantially complete and no critical data or statistical error was found in the checks performed. However, the requested new GitHub repository has not been created or published, and there is a small actual arithmetic transcription error and a reproducibility-test defect to correct. If the evaluator explicitly waives the GitHub requirement, the analysis is close to ready after the targeted corrections below; no wholesale rewrite is needed.

**Completion estimate: 93% — 13 of the 14 high-level checklist items below are substantially present.** This is a simple checklist-based estimate, not a measure of calculation correctness. “Present” does not mean flawless; the remaining report and technical defects are recorded below.

**Estimated score: 89/100**, under this reviewer's provisional rubric. The official rubric and evaluator's decision are unknown. The score is an estimate, not a result from YuvaIntern.

| Area | Estimate | Reason |
|---|---:|---|
| Dataset authenticity and context | 19/20 | Official, fingerprinted source and all variables explained; catalogue-versus-file discrepancy acknowledged. |
| Cleaning and traceability | 14/15 | Source rows, code and sensitivity documented; duplicate removal remains an assumption rather than verified duplicate events. |
| Exploratory analysis | 14/15 | Broad and grain-aware; some findings recur in multiple sections. |
| Calculations and statistical interpretation | 13/15 | Strong worked examples and caveats; one high-precision ratio in §11.5 is incorrect; tests are exploratory and not all are equally robust to the heavy tail. |
| Visualizations and readability | 9/10 | Fifteen appropriate and interpreted visuals; several dense plot labels and appendix text are small in the paginated master. |
| Insights and actionable recommendations | 9/10 | Claims are tied to historical evidence and measurement plans; some wording could more carefully avoid suggesting true retention or demand. |
| Reporting and reproducibility | 8/10 | Comprehensive appendix and working notebook, but the validator hard-codes its date and rejects an arbitrary valid date string; direct Microsoft Word rendering was not tested. |
| Full submission and publication | 3/5 | Google Doc, original Word, ZIP and description exist; required new GitHub repository is still pending. |
| **Total** | **89/100** | **Provisional reviewer estimate.** |

## 2. Previous reviewer feedback

| Feedback | Status | Evidence and reservation |
|---|---|---|
| Lack of specific numerical examples | **Corrected** | Actual five source rows on p. 10; source-derived profiles on pp. 9–12; complete seven-line invoice on p. 21; numeric evidence throughout pp. 17–51. |
| Missing worked calculations and original analysis | **Corrected, with one minor arithmetic transcription to repair** | §11.1–11.14, pp. 21–28, include formulas, substituted values and interpretations. §11.5 has an incorrect extra-precision mean/median ratio; the 75.79% conclusion remains correct. Extreme credit-pair and October–November decompositions go beyond generic description. |
| Thin, incomplete or missing sections | **Corrected** | All 19 requested sections are present and substantive, including dictionary, cleaning, EDA, statistical examples, business actions, limitations, references and full code. |
| Insufficient interpretation | **Corrected** | Examples contain interpretation, 15 figures have observed numbers and business implications, and findings connect data, importance and action. |
| Repetitive explanations | **Partially corrected** | Interpretations are tailored, but the same gross/credit bridge, RFM shares and offset examples recur in the summary, EDA, charts, findings, recommendations and conclusion. Some recurrence supports traceability; a concise cross-reference can replace a few repeated caveats without removing analysis. |
| Lack of practical business implications | **Corrected** | Eight recommendations on pp. 48–51 name actions, proposed owners and measures. They correctly avoid claiming that outcomes were achieved. |

## 3. Full section-by-section review

| Sections / pages | Assessment and exact action |
|---|---|
| **1 Cover, p. 1; 2 Abstract, p. 3** | Title, author, date, historical window and key denominators are explicit. Dashboard and summary agree with checked outputs. Date 7 November 2026 is the stated report date, not the dataset period. |
| **3 Introduction, p. 4** | States context, original reviewer concerns and historical decision boundary. Table 2 maps fixes to evidence. The new repetition concern merits the targeted cross-reference edits listed below. |
| **4 Source and description, pp. 5–6** | Official UCI DOI, workbook checksum, licence and all eight fields are documented; customer residence is not incorrectly called shipping destination. Missing-field evidence correctly overrides the catalogue's missingness flag for this file. |
| **5 Objectives, p. 7** | Eight clear analytical questions link methods and decisions. |
| **6 Tools and 7 Methodology, p. 8** | Versions, analysis sequence, grains and validation approach are recorded. Hard-coded execution metadata in the companion validator needs correction; see issue M2. |
| **8 Exploration, pp. 9–12** | Shape, column-level nulls and uniqueness, categories, duplicates, numeric summaries and actual exceptions are present. All raw numerical-measure summaries were checked by the validator. |
| **9 Cleaning, pp. 13–16** | Each substantive operation has a stated issue, code, counts, reason and effect; the full cleaned population is distinct from the positive-sales view. Deduplication, code taxonomy and country/time rules are transparent assumptions. Outliers are retained. |
| **10 EDA, pp. 17–20** | Frequency, geographic/product/credit comparisons, complete monthly table and multivariate RFM/country analysis support actual questions. In §10.3, replace language implying that credit-adjusted value proves retained or fulfilled demand. |
| **11 Statistics and worked examples, pp. 21–29** | Fourteen actual-data examples cover line/invoice values, missingness, variance, median, IQR, shares, growth, credits, repeat, Pearson, Welch, chi-square and sensitivity. Correct one ratio in §11.5 on p. 23. Group tests describe dependence, skew, multiplicity and sampling limitations; no causal conclusion is justified. |
| **12 Visualizations, pp. 30–43, plus dashboard on p. 3** | Bar, histogram, line, scatter, box, heatmap and count charts are present, with two plotting libraries and captions. All fifteen underlying chart images were visually examined; selected pages were checked in the rendered report. §12.3 should explicitly state monthly credits and sales need not relate to the same original orders. Some dense labels are small; verify legibility at normal zoom. The dashboard is static, not an interactive dashboard. |
| **13 Findings, pp. 44–47** | Twelve findings provide numbers, meaning and responses. In §13.11, use “observed repeat share” rather than “repeat propensity,” which could suggest a probability adjusted for exposure. |
| **14 Recommendations, pp. 48–51** | Eight proposals cite historical evidence, owners, expected mechanisms and measurement gates. No intervention or uplift is claimed. Some depend on unprovided current costs, permissions, stock or experiment data; that dependence is disclosed, not a missing analysis result. |
| **15 Limitations, p. 52; 16 Future scope, p. 53** | Covers historical/single-retailer scope, missing identities, incomplete credit linkage, duplicate assumptions, skew, dependence, current-data requirements and possible next steps. |
| **17 Conclusion, p. 54; 18 References, p. 55** | Conclusion summarizes defensible results; official UCI source, licence and technical documentation are identifiable. Repeated metrics can be lightly shortened if desired, but keep the decision boundary and main conclusions. |
| **19 Appendix, pp. 56–73** | Reproduction commands, outputs, explicit data read-back and the three full computational source files are present. The executed validator checks the appendix against those source files. Small source-code text is less comfortable to read; the accompanying runnable files remain the authoritative copy. |

## 4. Numerical and technical validation

The workbook-backed validator was rerun during this review: **76/76 checks passed**. It re-reads the original Excel file rather than the cached analysis pickle. Its checks include the source hash, partition and financial bridge, saved profiles, cleaned records, invoice/customer aggregates, manually worked Pearson, Welch and chi-square calculations, chart and appendix structure, and notebook outputs. The 76 checks are not a proof that every word or every displayed digit is correct: the §11.5 ratio below escaped the suite. Prior layout checks were **10/10**, with selected additional rendered pages examined here; they do not constitute direct Microsoft Word testing.

| Check | Calculation / evidence | Review outcome |
|---|---|---|
| Workbook shape and missing IDs | 541,909 rows × 8; 135,080 / 541,909 × 100 = 24.926694% | Matches report. |
| Exact duplicates | 5,268 / 541,909 × 100 = 0.972119%; 541,909 − 5,268 = 536,641 | Matches report; removal remains an assumption. |
| Invoice calculation | 15.30 + 20.34 + 22.00 + 20.34 + 20.34 + 15.30 + 25.50 = £139.12 | Matches the seven actual lines of invoice 536365. |
| Financial bridge | £10,642,110.80 − £893,979.73 = £9,748,131.07; less £22,124.12 = £9,726,006.95 | Matches on displayed rounding basis; source sub-penny precision is retained. |
| Mean and median | £10,642,110.804 / 19,960 = £533.171883968; median £303.30. Their mean/median − 1 = **0.757902684**, or **75.7902684%** | Report’s £533.17, £303.30 and 75.79% are right. The intermediate 0.7579039 on p. 23 is wrong. |
| UK sales share | £9,001,744.094 / £10,642,110.804 × 100 = 84.586078% | Matches report’s 84.59%. |
| November versus October | £1,503,866.78 / £1,151,263.73 − 1 = 30.627478%; invoice growth 2,769 / 2,040 − 1 = 35.735294%; AOV falls 3.763071% | Matches report; identity decomposes observed changes, not a causal price analysis. |
| Repeat share | 2,845 / 4,338 × 100 = 65.583218% | Matches report; identified purchasers within the observed window only. |
| Quantity IQR | Q1 = 1, Q3 = 11; IQR = 10; bounds −14 and 26; 27,111 / 524,878 = 5.1652% | Matches report; flags do not imply data errors. |
| Welch and chi-square | UK/non-UK customer-level Welch t ≈ −5.474116, df ≈ 1,008.183, p ≈ 5.55×10⁻⁸. Yates χ² ≈ 0.0015383, p ≈ 0.968714; standard V ≈ 0.00141765 based on uncorrected χ² | Reproduced. Conditional exploratory tests; they do not prove a geography effect or group equivalence. |
| Figures and outputs | Figure 1 dashboard and Figures 2–15 inspected; counts, key axis labels, chart types and numerical annotations compared with underlying outputs | No material chart/text discrepancy found in the checked values. This is not an independent audit of every plotted point. |
| Customer-ID consistency inside sales invoices | Checked directly in qualified-sales export: **zero** sales invoices contain both missing and present customer IDs | Supports invoice-level attribution for this dataset; avoids assuming missing line IDs in a mixed invoice. |

## 5. Issues and exact corrections

### Critical

**None identified** in the data or calculations checked. This is not a claim that every number in 73 pages was independently recalculated. The outstanding GitHub requirement is classified Major because it is a publication/compliance blocker, not corruption of the report's data.

### Major

**M1 — Required GitHub publication missing.** Submission package; no report page applies. A Google Doc and a full downloadable ZIP exist, but no new revised Task 4 repository was created or pushed. The earlier user decision to defer publication explains the status; it does not itself satisfy the original GitHub requirement. **Correction:** securely publish the included project to a new GitHub repository, confirm README, notebook, source, outputs, data/licence and report are accessible as permitted, and submit the actual tested URL. Follow `docs/PUBLISH_TO_GITHUB.md`; do not paste a token in chat or alter Task 5. If the evaluator has explicitly waived GitHub, record that waiver instead.

**M2 — Validator/date metadata can misstate a later run and reject a legitimate date.** Companion `tests/validate_outputs.py`, around lines 356 and 380; report reproduction instruction §19.1, p. 56; related metadata in scripts. The test forbids the literal text `2026-11-10` as a stale marker and assigns `validation_date = '2026-11-07'` every time it runs. Other scripts hard-code that date as analysis/verification metadata. This is not evidence that the existing report’s stated date is wrong; it is a defect when the project is refreshed or rerun later. **Correction:** remove the arbitrary date string from the stale-marker blacklist; store actual run time separately, e.g. `datetime.now(timezone.utc).isoformat()` under `validation_run_at_utc`. Keep a fixed historical report date as `report_date` when referring to that version. Apply the same distinction to other execution/verification metadata, rerun checks, and update distributed verification records. If source files embedded in §19 change, regenerate the appendix and revalidate source equality. Do not relabel genuinely historical source-consultation dates.

### Minor

**m1 — Incorrect extra-precision ratio.** §11.5, p. 23. Replace `Mean/median − 1 = 0.7579039` with `Mean/median − 1 = 0.757902684`, or show `≈ 0.7579`. Keep the already correct **75.79%**, £533.17 mean and £303.30 median unchanged. Add a validator assertion against the narrative’s numeric value so it cannot pass merely because the underlying mean and median are right.

**m2 — Credit-adjusted value can be mistaken for fulfilled or retained demand.** §10.3, p. 18; §12.6, p. 35; related wording in §13.7, p. 46. Replace “retained demand”/“retains £…” with “recorded credit-adjusted transaction value”/“has £… after recorded C-credit notes.” Where helpful state: “This is not verified fulfilment, cash received or profit; credits are not generally linked to their original orders.” Keep the £0.00, £4,221.28 and £164,459.49 numbers unchanged.

**m3 — Monthly credit ratios could be misread as same-order returns.** §12.3, p. 32, and Figure 4. Add: “The numerator is C-credit value recorded in the month; the denominator is qualified sales value recorded in the same month. Credits may relate to earlier sales, so this is a period activity ratio, not a cohort return rate.” No calculation change.

**m4 — Observed repeat is not an exposure-adjusted propensity.** §13.11, p. 47. Replace “repeat propensity” with “observed repeat share within the recorded window.” Preserve the 65.79% versus 65.56% values and the non-equivalence caveat.

**m5 — Readability and controlled repetition.** §10–14, pp. 17–51; code §19.4, pp. 58–73. The full report repeats some key caveats and monetary figures, and product labels and full source code can look small at normal page scale. In §13, retain evidence and business implications but cross-reference one already-explained method or caveat rather than repeating its full explanation; keep all required content. Check Figures 7 and 11 at 100% zoom and enlarge labels if needed. Preserve all code in the appendix and include runnable files rather than deleting source to shorten the report. Refresh contents and page fields after edits.

**m6 — Application compatibility not directly checked.** Whole document; no specific page. LibreOffice/PDF and OOXML checks passed, but the report has not been opened in Microsoft Word. Open the final DOCX in Word if available; update the table of contents and page fields; check pages 2, 11, 26–27, 35, 39, 41, 56 and 58–73 for clipping or broken formula/code lines. Re-export only after that check. Google Docs may reflow and its page numbers may differ.

## 6. Task-objective checklist

This checklist gives equal weight to each high-level item solely to explain the 13/14 ≈ 93% completion estimate.

- [x] Genuine real-world dataset and verifiable source/licence.
- [x] Business context, defined variables and at least five analytical questions.
- [x] Full column profiling, missingness, duplicates, categories and numerical summaries.
- [x] Traceable cleaning with code, before/after figures, assumptions and retained outliers.
- [x] Univariate, bivariate and multivariate EDA, including temporal and group analysis.
- [x] Statistical comparisons, stated assumptions, uncertainty/effect-size caveats and non-causal interpretation, subject to the minor correction above.
- [x] At least five worked numerical examples; fourteen are present.
- [x] Meaningful labelled visuals and a static KPI dashboard; all required chart types are present.
- [x] At least 8–10 numerically supported findings; twelve are present.
- [x] At least five evidence-linked practical recommendations; eight are present.
- [x] Limitations and future scope, including missing evidence and non-generalisation.
- [x] Complete conclusion, references, logical section order and professional documentation.
- [x] Original workbook, cleaned datasets, executed notebook, source, outputs, Google Docs/Word links and ≥200-word description are available in the companion package; technical metadata issue remains as noted.
- [ ] New revised Task 4 GitHub repository published, accessible and supplied as an actual URL — **pending**.

## 7. Supporting evidence and publication status

- **Available:** original workbook; complete cleaned and qualified sales datasets; executed notebook; full computational source; fifteen figures; output/evidence CSVs; QA and layout records; documentation, attribution and licences; 364-word submission description. The ZIP manifest was inspected for these key files.
- **Google Docs:** https://docs.google.com/document/d/16LW-yUiFtfg5I2DpL6op8MAkQDAdFShBj_PMgNdrLuo/edit — anonymous text export returned successfully during this review.
- **Original Word:** https://drive.google.com/file/d/1ZiL6KOnVqQMN9jtcoJkkdK_c9J7CEA-l/view — anonymous download returned successfully and matched the reviewed local Word hash.
- **Project ZIP:** https://drive.google.com/file/d/1Zdu6EHTf9oaNzzUOdVuX5i6HEh9TQOU4/view — shared viewer returned successfully during this review; earlier confirmed-download verification matched the complete ZIP hash. Drive may require a large-file confirmation.
- **Missing for the full originally requested submission:** actual public GitHub repository URL and successful publication evidence. The reviewer should not treat the proposed repository name as an existing link.
- **Not present in the source, and not to be fabricated:** linked original order/credit reasons, costs or profit margins, inventory/fulfilment data, campaign assignments, current customer permissions and current outcomes. They are needed for certain future decisions, not to verify the historical descriptive findings.

**After making corrections:** regenerate the Word/Google Doc/ZIP or otherwise ensure every submitted copy reflects the same final version; rerun workbook and layout checks; replace the links/hashes in the handoff if new versions are uploaded. Do not claim 76/76 on a modified report without re-running the checks. The old published versions remain the reviewed versions until replaced.
