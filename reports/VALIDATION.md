# Task 4 — Executed validation

**77/77 checks passed; 0 failed.**

This is an executed technical validation, not an official grade or an independent external review.
The raw Excel workbook was re-read directly; the analysis cache was not trusted for numerical verification.

| Check | Result | Detail |
|---|---|---|
| Official workbook fingerprint and bytes | PASS |  |
| Raw dimensions and exact eight-column order | PASS |  |
| Raw missing counts in all eight columns | PASS |  |
| Raw missing and duplicate percentages | PASS |  |
| Raw uniqueness and timestamp range | PASS |  |
| Exact duplicates independently counted | PASS |  |
| Saved schema non-null/missing/unique/dtype profile | PASS |  |
| Independently partitioned line counts | PASS |  |
| Financial bridge from independently computed line values | PASS |  |
| Exclusive partition export | PASS |  |
| Bad-debt records are retained and disclosed, not guessed errors | PASS |  |
| Complete cleaned and separate sales export shapes | PASS |  |
| SourceRow preserves exact deduplicated workbook provenance | PASS |  |
| Original quantity and unit amount preserved | PASS |  |
| Identifier normalization is lossless and missing IDs retained | PASS |  |
| Description sentinel/whitespace normalization is exact | PASS |  |
| Whitespace affected count comes from actual source | PASS |  |
| Dates and original country labels preserved | PASS |  |
| Derived sales/credit flags match literal sign and prefix rules | PASS |  |
| Sales export is an exact view of complete cleaned data | PASS |  |
| No duplicate cleaned payload after normalization | PASS |  |
| Cleaned dataset file hashes and byte counts | PASS |  |
| Invoice counts and independent summary arithmetic | PASS |  |
| Invoice date allocation uses earliest timestamp exactly | PASS |  |
| Hourly counts are mutually exclusive and noon is 3219 | PASS |  |
| Known-customer counts and financial coverage | PASS |  |
| Customer exported AOV/frequency/country reconcile independently | PASS |  |
| Customer country ambiguity disclosed | PASS |  |
| All required descriptive statistics: raw_descriptive_statistics.csv | PASS |  |
| All required descriptive statistics: valid_descriptive_statistics.csv | PASS |  |
| Worked first line and all seven invoice lines | PASS |  |
| Worked mean, sample variance and SD independently verified | PASS |  |
| Global AOV and exact central median observations | PASS |  |
| Worked IQR bounds, counts and retained example | PASS |  |
| Country/month aggregates reconcile to complete sales | PASS |  |
| Worked UK share and correct non-UK leading country | PASS |  |
| Worked November growth and multiplicative decomposition | PASS |  |
| Partial final month is flagged, not used as a full-month decline | PASS |  |
| Worked credit ratios use explicit correct denominators | PASS |  |
| Worked repeat share is observed customer frequency, not row count | PASS |  |
| RFM customers and sales partition the known population | PASS |  |
| Worked Champions proportions use both denominators | PASS |  |
| Multivariate country × RFM aggregate reconciles | PASS |  |
| Worked manual Pearson r independently matches SciPy | PASS |  |
| Full-data rank correlations independently reproduced | PASS |  |
| Worked Welch n, means, standard error, t, df and p | PASS |  |
| Worked mean-difference interval matches SciPy directly | PASS |  |
| Worked contingency table, expected counts, Yates and standard V | PASS |  |
| Worked cap sensitivity and duplicate sensitivity independently reproduced | PASS |  |
| Two extreme matches are genuine equal-and-opposite source records | PASS |  |
| Penny-rounded non-positive account count avoids float near-zero errors | PASS |  |
| Customer offset examples are supported by actual balances | PASS |  |
| Netherlands top-account share is independently verified | PASS |  |
| All 24 previous Task 4 metrics reconcile with MATCH status | PASS |  |
| Exactly 15 real, non-empty high-resolution chart files | PASS |  |
| Both plotting libraries and all seven required chart types are implemented | PASS |  |
| Every figure has numerical observation, interpretation, implication and evidence | PASS |  |
| Fourteen worked examples cover every requested component | PASS |  |
| Twelve findings each contain evidence/comparison/meaning/importance/action | PASS |  |
| Eight measurable recommendations contain all required fields | PASS |  |
| Exact 19-part report order and required section names | PASS |  |
| Author metadata and sensible Word size | PASS |  |
| Embedded figure/table counts and sequential captions | PASS |  |
| Real generated contents and live page fields, no insertion marker | PASS |  |
| At least eight specific analytical questions are present | PASS |  |
| All original column definitions and all required raw statistics are present | PASS |  |
| Complete code appendix equals runnable source: verified_core.py | PASS |  |
| Complete code appendix equals runnable source: analyze.py | PASS |  |
| Complete code appendix equals runnable source: make_charts.py | PASS |  |
| Worked mean/median ratio narrative matches workbook arithmetic | PASS |  |
| No stale draft marker, invented grade or unreplaced placeholder | PASS |  |
| Executed notebook has all code cells run and no error output | PASS |  |
| Notebook embeds all 15 generated chart outputs | PASS |  |
| Documentation, licences, provenance and reproducibility files present | PASS |  |
| Separate submission description exceeds 200 words | PASS | 364 words |
| All distributed Python source parses successfully | PASS |  |
| No credential patterns in distributed text artifacts | PASS |  |
