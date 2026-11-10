"""Verified computational core for the revised YuvaIntern Task 4 project.

Run from any directory: python scripts/analyze.py
Downloads the official workbook when absent, verifies its SHA-256, reproduces
Task 4's valid-sales basis, and exports corrected, explicitly scoped measures.
No synthetic transactions, forecasts or intervention results are generated.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import platform
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CACHE = ROOT / ".cache"
for directory in (DATA, OUT, CACHE):
    directory.mkdir(parents=True, exist_ok=True)
SOURCE = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
EXPECTED_SHA256 = "43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d"
NON_PRODUCT = {
    "POST", "DOT", "M", "BANK CHARGES", "AMAZONFEE", "PADS", "D", "C2", "CRUK",
    "TEST001", "TEST002", "SAMPLES", "NOTES", "B", "S", "AMAZON", "CHECK", "COLLECT",
}
REFERENCE_DATE = pd.Timestamp("2011-12-10")


def rounded(x, digits=2):
    return round(float(x), digits)


def save(frame, filename, index=False):
    frame.to_csv(OUT / filename, index=index, float_format="%.8f")


def test_groups(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    u, up = stats.mannwhitneyu(a, b, alternative="two-sided")
    pooled_sd = np.sqrt(((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1)) / (len(a)+len(b)-2))
    return {
        "n_a": len(a), "n_b": len(b), "mean_a": rounded(a.mean()), "mean_b": rounded(b.mean()),
        "median_a": rounded(np.median(a)), "median_b": rounded(np.median(b)),
        "welch_t": rounded(t, 6), "welch_p": float(p),
        "cohens_d_a_minus_b": rounded((a.mean()-b.mean())/pooled_sd, 6),
        "mann_whitney_u": float(u), "mann_whitney_p": float(up),
    }


workbook = DATA / "Online Retail.xlsx"
if not workbook.exists():
    response = requests.get(SOURCE, timeout=180)
    response.raise_for_status()
    archive = zipfile.ZipFile(io.BytesIO(response.content))
    name = next(n for n in archive.namelist() if n.lower().endswith(".xlsx"))
    workbook.write_bytes(archive.read(name))
sha = hashlib.sha256(workbook.read_bytes()).hexdigest()
if sha != EXPECTED_SHA256:
    raise ValueError("Workbook checksum mismatch: stop rather than analyse an unverified file")
raw_cache = CACHE / (sha[:12] + "_raw.pkl")
if raw_cache.exists():
    raw = pd.read_pickle(raw_cache)
else:
    raw = pd.read_excel(workbook, sheet_name="Online Retail")
    raw.to_pickle(raw_cache)
assert raw.shape == (541909, 8)
assert raw["InvoiceDate"].notna().all()

old = json.loads((ROOT / "references" / "task4_original_results.json").read_text())
df = raw.drop_duplicates().copy()
df["InvoiceNo"] = df["InvoiceNo"].astype(str)
df["StockCode"] = df["StockCode"].astype(str)
df["Description"] = df["Description"].fillna("UNKNOWN")
df["IsCredit"] = df["InvoiceNo"].str.upper().str.startswith("C")
df["IsNonProduct"] = df["StockCode"].str.upper().isin(NON_PRODUCT)
df["LineValue"] = df["Quantity"] * df["UnitPrice"]
df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
valid_mask = (~df["IsCredit"]) & (df["Quantity"] > 0) & (df["UnitPrice"] > 0)
noncredit_negative_mask = (~df["IsCredit"]) & (df["Quantity"] < 0)
other_mask = ~(valid_mask | df["IsCredit"] | noncredit_negative_mask)
v = df.loc[valid_mask].copy()
c = df.loc[df["IsCredit"]].copy()
a = df.loc[noncredit_negative_mask].copy()
e = df.loc[other_mask].copy()
assert len(v) + len(c) + len(a) + len(e) == len(df)

# Customer and country are consistent within each invoice. Some line timestamps
# differ by a minute; allocate each invoice to its first recorded timestamp so
# hourly order counts are mutually exclusive (legacy line-hour counts are not).
conflicts = v.groupby("InvoiceNo")[["CustomerID", "Country", "InvoiceDate"]].nunique(dropna=True)
assert conflicts[["CustomerID", "Country"]].max().max() == 1
timestamp_exceptions = v.groupby("InvoiceNo").agg(First=("InvoiceDate","min"),Last=("InvoiceDate","max"),TimestampCount=("InvoiceDate","nunique"))
assert (timestamp_exceptions["First"].dt.normalize() == timestamp_exceptions["Last"].dt.normalize()).all()
timestamp_exceptions = timestamp_exceptions[timestamp_exceptions["TimestampCount"]>1]
timestamp_exceptions["SpanSeconds"] = (timestamp_exceptions["Last"]-timestamp_exceptions["First"]).dt.total_seconds()
save(timestamp_exceptions,"invoice_timestamp_exceptions.csv",index=True)
invoice = v.groupby("InvoiceNo", sort=True).agg(
    InvoiceValue=("LineValue", "sum"), InvoiceDate=("InvoiceDate", "min"),
    CustomerID=("CustomerID", "first"), Country=("Country", "first"),
    LineCount=("LineValue", "size"), TotalQty=("Quantity", "sum"),
    AvgPrice=("UnitPrice", "mean"),
).reset_index()
invoice["Month"] = invoice["InvoiceDate"].dt.to_period("M").astype(str)
invoice["Hour"] = invoice["InvoiceDate"].dt.hour
invoice["Weekday"] = invoice["InvoiceDate"].dt.day_name()
known_invoice = invoice[invoice["CustomerID"].notna()]
customers = known_invoice.sort_values(["InvoiceDate", "InvoiceNo"]).groupby("CustomerID", sort=True).agg(
    Frequency=("InvoiceNo", "nunique"), Monetary=("InvoiceValue", "sum"),
    AOV=("InvoiceValue", "mean"), LastPurchase=("InvoiceDate", "max"),
    FirstPurchase=("InvoiceDate", "min"), Country=("Country", "first"),
).reset_index()
# Calendar-day recency fixes the legacy floor-of-elapsed-days presentation;
# rank order and the reproduced segmentation are unchanged for this workbook.
customers["Recency"] = (REFERENCE_DATE - customers["LastPurchase"].dt.normalize()).dt.days
customers["RecencyLegacy"] = (REFERENCE_DATE - customers["LastPurchase"]).dt.days
customers["TenureDays"] = (customers["LastPurchase"] - customers["FirstPurchase"]).dt.days


def quintile(series, reverse=False):
    return pd.qcut(series.rank(method="first", ascending=not reverse), 5, labels=[1,2,3,4,5]).astype(int)


customers["R"] = quintile(customers["Recency"], reverse=True)
customers["F"] = quintile(customers["Frequency"])
customers["M"] = quintile(customers["Monetary"])
R, F, M = customers["R"], customers["F"], customers["M"]
conditions = [
    (R>=4)&(F>=4)&(M>=4), (R<=2)&(F>=4)&(M>=4), (R<=2)&(F>=3),
    (R>=3)&(F>=3)&(M>=3), (R>=4)&(F>=2), (R>=4)&(F==1),
    (R<=2)&(F==2), (R<=2)&(F==1), R==3,
]
labels = ["Champions", "Can't Lose Them", "At Risk", "Loyal Customers", "Potential Loyalist",
          "New / Promising", "Hibernating", "Lost", "Needs Attention"]
customers["Segment"] = np.select(conditions, labels, default="Other")
assert "Other" not in set(customers["Segment"])
segments = customers.groupby("Segment").agg(
    Customers=("CustomerID", "size"), Sales=("Monetary", "sum"),
    AvgRecency=("Recency", "mean"), AvgFrequency=("Frequency", "mean"),
).sort_values("Sales", ascending=False).reset_index()
gross = float(v["LineValue"].sum())
credit_abs = -float(c["LineValue"].sum())
known_sales = float(customers["Monetary"].sum())
segments["CustomerSharePct"] = segments["Customers"] / len(customers)*100
segments["KnownSalesSharePct"] = segments["Sales"] / known_sales*100
segments["TotalSalesSharePct"] = segments["Sales"] / gross*100

customer_pareto = customers.sort_values("Monetary", ascending=False).copy().reset_index(drop=True)
customer_pareto["Rank"] = np.arange(1, len(customers)+1)
customer_pareto["CumKnownSalesPct"] = customer_pareto["Monetary"].cumsum()/known_sales*100
customer_pareto["CumAllSalesPct"] = customer_pareto["Monetary"].cumsum()/gross*100
customer_pareto["CustomerPct"] = customer_pareto["Rank"]/len(customers)*100
n80 = int(np.searchsorted(customer_pareto["CumKnownSalesPct"],80)+1)

merch = v.loc[~v["IsNonProduct"]]
products = merch.groupby("StockCode").agg(
    Description=("Description", "first"), GrossSales=("LineValue", "sum"),
    Units=("Quantity", "sum"), SaleLines=("LineValue", "size"),
    Customers=("CustomerID", "nunique"),
).reset_index()
merch_credits = c.loc[~c["IsNonProduct"]].groupby("StockCode").agg(
    SignedCredits=("LineValue", "sum"), SignedCreditUnits=("Quantity", "sum"),
    CreditLines=("LineValue", "size"),
)
# Include credit-only merchandise codes in reconciliation; rankings require positive sales.
net_products = products.merge(merch_credits, on="StockCode", how="outer")
name_lookup = df.groupby("StockCode")["Description"].first()
net_products["Description"] = net_products["Description"].fillna(net_products["StockCode"].map(name_lookup))
for col in ["GrossSales","Units","SaleLines","Customers","SignedCredits","SignedCreditUnits","CreditLines"]:
    net_products[col] = net_products[col].fillna(0)
net_products["CreditAdjustedValue"] = net_products["GrossSales"] + net_products["SignedCredits"]
net_products["CreditAdjustedUnits"] = net_products["Units"] + net_products["SignedCreditUnits"]
net_products["CreditValuePctOfGross"] = np.where(net_products["GrossSales"]>0,-net_products["SignedCredits"]/net_products["GrossSales"]*100,np.nan)
net_products = net_products.sort_values("GrossSales",ascending=False)
product_pareto = products.sort_values("GrossSales",ascending=False).reset_index(drop=True)
product_pareto["CumProductSalesPct"] = product_pareto["GrossSales"].cumsum()/product_pareto["GrossSales"].sum()*100
n80_product = int(np.searchsorted(product_pareto["CumProductSalesPct"],80)+1)

countries = invoice.groupby("Country").agg(
    GrossSales=("InvoiceValue","sum"), Orders=("InvoiceNo","nunique"),
    Customers=("CustomerID","nunique"), AOV=("InvoiceValue","mean"),
).reset_index()
country_credit = c.groupby("Country")["LineValue"].sum().rename("SignedCredits")
countries = countries.merge(country_credit,on="Country",how="left").fillna({"SignedCredits":0})
countries["SalesSharePct"] = countries["GrossSales"]/gross*100
countries["CreditAdjustedValue"] = countries["GrossSales"] + countries["SignedCredits"]
country_top_known = known_invoice.groupby(["Country","CustomerID"])["InvoiceValue"].sum().groupby(level=0).max()
country_known = known_invoice.groupby("Country")["InvoiceValue"].sum()
countries["TopAccountKnownSalesPct"] = countries["Country"].map(country_top_known/country_known*100)
countries = countries.sort_values("GrossSales",ascending=False)

monthly = v.groupby("Month").agg(GrossSales=("LineValue","sum"),Orders=("InvoiceNo","nunique"),Units=("Quantity","sum")).reset_index()
cm = c.groupby("Month").agg(CreditValue=("LineValue", lambda x:-x.sum()), CreditInvoices=("InvoiceNo","nunique"),CreditLines=("InvoiceNo","size"))
monthly = monthly.merge(cm,on="Month",how="left").fillna(0)
monthly["CreditAdjustedValue"] = monthly["GrossSales"] - monthly["CreditValue"]
monthly["AOV"] = monthly["GrossSales"]/monthly["Orders"]
monthly["CreditDocumentSharePct"] = monthly["CreditInvoices"]/(monthly["CreditInvoices"]+monthly["Orders"])*100
monthly["CreditValuePctOfGross"] = monthly["CreditValue"]/monthly["GrossSales"]*100
monthly["MoMGrossPct"] = monthly["GrossSales"].pct_change()*100
monthly["CompleteMonth"] = monthly["Month"] != "2011-12"
weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday = invoice.groupby("Weekday").agg(GrossSales=("InvoiceValue","sum"),Orders=("InvoiceNo","size")).reindex(weekday_order).fillna(0).reset_index()
hourly = invoice.groupby("Hour").agg(GrossSales=("InvoiceValue","sum"),Orders=("InvoiceNo","size")).reindex(range(6,21)).fillna(0).reset_index()

# Directly inspect equal-and-opposite records for the two largest merchandise sales.
largest_sales = merch.nlargest(2,"LineValue")
pair_rows = []
for _, sale in largest_sales.iterrows():
    matched = c[(c["StockCode"]==sale["StockCode"]) &
                (c["Quantity"]==-sale["Quantity"]) &
                np.isclose(c["UnitPrice"],sale["UnitPrice"]) &
                (c["CustomerID"]==sale["CustomerID"]) &
                (c["InvoiceDate"]>=sale["InvoiceDate"])]
    for _, credit in matched.iterrows():
        pair_rows.append({
            "StockCode":sale["StockCode"],"Description":sale["Description"],
            "CustomerID":int(sale["CustomerID"]),"SaleInvoice":sale["InvoiceNo"],
            "SaleDate":str(sale["InvoiceDate"]),"SaleUnits":int(sale["Quantity"]),
            "UnitPrice":sale["UnitPrice"],"GrossLineValue":sale["LineValue"],
            "CreditInvoice":credit["InvoiceNo"],"CreditDate":str(credit["InvoiceDate"]),
            "CreditUnits":int(credit["Quantity"]),"SignedCredit":credit["LineValue"],
            "PairSignedValue":sale["LineValue"]+credit["LineValue"],
        })
pairs = pd.DataFrame(pair_rows)

# Statistics reproduce Task 4, with the unit of analysis explicit.
correlations = invoice[["InvoiceValue","LineCount","TotalQty","AvgPrice"]].corr(method="spearman")
uk = invoice.loc[invoice["Country"]=="United Kingdom","InvoiceValue"]
nonuk = invoice.loc[invoice["Country"]!="United Kingdom","InvoiceValue"]
rep = customers.loc[customers["Frequency"]>1,"AOV"]
one = customers.loc[customers["Frequency"]==1,"AOV"]
invoice_test = test_groups(uk,nonuk)
repeat_test = test_groups(rep,one)
customer_country_test = test_groups(customers.loc[customers["Country"]=="United Kingdom","AOV"],customers.loc[customers["Country"]!="United Kingdom","AOV"])
ci = stats.t.interval(.95,df=len(invoice)-1,loc=invoice["InvoiceValue"].mean(),scale=stats.sem(invoice["InvoiceValue"]))
ct = pd.crosstab(np.where(customers["Country"]=="United Kingdom","UK","Non-UK"),np.where(customers["Frequency"]>1,"Repeat","One-time"))
chi,pchi,dof,exp = stats.chi2_contingency(ct, correction=True)
chi_unc,pchi_unc,_,_ = stats.chi2_contingency(ct, correction=False)
threshold99 = v["LineValue"].quantile(.99)
winsor = v["LineValue"].clip(upper=threshold99).sum()
quantiles = invoice["InvoiceValue"].quantile([.25,.5,.75,.9,.95,.99])
q1,q3 = v["Quantity"].quantile([.25,.75])
p1,p3 = v["UnitPrice"].quantile([.25,.75])

# De-duplication is an explicit assumption. A no-dedup sensitivity is exported.
raw_c = raw["InvoiceNo"].astype(str).str.upper().str.startswith("C")
raw_valid = (~raw_c)&(raw["Quantity"]>0)&(raw["UnitPrice"]>0)
raw_valid_value = float((raw.loc[raw_valid,"Quantity"]*raw.loc[raw_valid,"UnitPrice"]).sum())

# Supplement, do not silently overwrite, the reproduced gross-value RFM.
customer_credit = c.groupby("CustomerID")["LineValue"].sum()
customers["SignedCredits"] = customers["CustomerID"].map(customer_credit).fillna(0)
customers["CreditAdjustedMonetary"] = customers["Monetary"]+customers["SignedCredits"]
winback_mask = customers["Segment"].isin(["At Risk","Can't Lose Them"])
legacy_hourly = v.groupby(v["InvoiceDate"].dt.hour)["InvoiceNo"].nunique()

metrics = {
    "report_date":"2026-11-07", "analysis_run_at_utc":datetime.now(timezone.utc).isoformat(), "author":"T. Aparna Reddy",
    "source_url":SOURCE,"sha256":sha,"workbook_bytes":workbook.stat().st_size,
    "raw_rows":len(raw),"raw_columns":len(raw.columns),"raw_invoices":raw["InvoiceNo"].nunique(),
    "raw_countries":raw["Country"].nunique(),"raw_customers":raw["CustomerID"].nunique(),
    "raw_stockcodes":raw["StockCode"].nunique(),"date_min":str(raw["InvoiceDate"].min()),"date_max":str(raw["InvoiceDate"].max()),
    "duplicates_removed":len(raw)-len(df),"deduplicated_rows":len(df),
    "raw_missing_customer":int(raw["CustomerID"].isna().sum()),"raw_missing_description":int(raw["Description"].isna().sum()),
    "working_missing_customer":int(df["CustomerID"].isna().sum()),
    "valid_sales_lines":len(v),"valid_sales_invoices":len(invoice),"gross_sales":rounded(gross),
    "gross_units":int(v["Quantity"].sum()),"aov":rounded(gross/len(invoice)),"median_invoice_value":rounded(invoice["InvoiceValue"].median()),
    "identified_customers":len(customers),"known_customer_invoices":len(known_invoice),
    "known_customer_sales":rounded(known_sales),"known_sales_share_pct":rounded(known_sales/gross*100),
    "anonymous_sales":rounded(gross-known_sales),"anonymous_sales_share_pct":rounded((gross-known_sales)/gross*100),
    "anonymous_sales_lines":int(v["CustomerID"].isna().sum()),"anonymous_sales_line_pct":rounded(v["CustomerID"].isna().mean()*100),
    "repeat_customers":int((customers["Frequency"]>1).sum()),"one_time_customers":int((customers["Frequency"]==1).sum()),
    "repeat_rate_pct":rounded((customers["Frequency"]>1).mean()*100),"mean_orders_per_customer":rounded(customers["Frequency"].mean()),
    "median_orders_per_customer":float(customers["Frequency"].median()),
    "credit_lines":len(c),"credit_invoices":c["InvoiceNo"].nunique(),"credit_value_abs":rounded(credit_abs),
    "credit_document_denominator":len(invoice)+c["InvoiceNo"].nunique(),
    "credit_document_share_pct":rounded(c["InvoiceNo"].nunique()/(len(invoice)+c["InvoiceNo"].nunique())*100),
    "credit_all_raw_invoice_share_pct":rounded(c["InvoiceNo"].nunique()/raw["InvoiceNo"].nunique()*100),
    "credit_line_share_pct":rounded(len(c)/(len(c)+len(v))*100),
    "credit_value_pct_of_gross":rounded(credit_abs/gross*100),
    "credit_absolute_activity_share_pct":rounded(credit_abs/(gross+credit_abs)*100),
    "credit_adjusted_value":rounded(gross-credit_abs),
    "noncredit_negative_qty_lines":len(a),"noncredit_negative_qty_value":rounded(a["LineValue"].sum()),
    "other_excluded_lines":len(e),"other_excluded_value":rounded(e["LineValue"].sum()),
    "nonpositive_price_working_lines":int((df["UnitPrice"]<=0).sum()),"negative_price_lines":int((df["UnitPrice"]<0).sum()),
    "dedup_signed_all_lines":rounded(df["LineValue"].sum()),
    "excluded_other_invoices":int(raw["InvoiceNo"].nunique()-len(invoice)-c["InvoiceNo"].nunique()),
    "nonproduct_working_lines":int(df["IsNonProduct"].sum()),
    "merchandise_sales":rounded(merch["LineValue"].sum()),"nonproduct_sales":rounded(v.loc[v["IsNonProduct"],"LineValue"].sum()),
    "merchandise_codes_with_sales":len(products),"top10_product_gross_share_pct":rounded(product_pareto.head(10)["GrossSales"].sum()/products["GrossSales"].sum()*100),
    "products_for_80pct":n80_product,"products_for_80pct_share":rounded(n80_product/len(products)*100),
    "uk_sales":rounded(countries.iloc[0]["GrossSales"]),"uk_sales_share_pct":rounded(countries.iloc[0]["SalesSharePct"]),
    "uk_orders":int(countries.iloc[0]["Orders"]),"uk_customers":int(countries.iloc[0]["Customers"]),
    "largest_nonuk_country":str(countries.iloc[1]["Country"]),"largest_nonuk_sales":rounded(countries.iloc[1]["GrossSales"]),
    "champions_customers":int(segments.loc[segments["Segment"]=="Champions","Customers"].iloc[0]),
    "champions_sales":rounded(segments.loc[segments["Segment"]=="Champions","Sales"].iloc[0]),
    "champions_known_sales_share_pct":rounded(segments.loc[segments["Segment"]=="Champions","KnownSalesSharePct"].iloc[0]),
    "champions_total_sales_share_pct":rounded(segments.loc[segments["Segment"]=="Champions","TotalSalesSharePct"].iloc[0]),
    "winback_customers":int(segments.loc[segments["Segment"].isin(["At Risk","Can't Lose Them"]),"Customers"].sum()),
    "winback_historical_sales":rounded(segments.loc[segments["Segment"].isin(["At Risk","Can't Lose Them"]),"Sales"].sum()),
    "customer_n80":n80,"customer_n80_pct":rounded(n80/len(customers)*100),
    "top20_customer_count":int(len(customers)*.2),"top20_known_share_pct":rounded(customer_pareto.iloc[int(len(customers)*.2)-1]["CumKnownSalesPct"]),
    "top1_customer_count":int(len(customers)*.01),"top1_known_share_pct":rounded(customer_pareto.iloc[int(len(customers)*.01)-1]["CumKnownSalesPct"]),
    "top1_total_share_pct":rounded(customer_pareto.iloc[int(len(customers)*.01)-1]["CumAllSalesPct"]),
    "top10_customers_sales":rounded(customer_pareto.head(10)["Monetary"].sum()),"top10_customers_total_share_pct":rounded(customer_pareto.head(10)["Monetary"].sum()/gross*100),
    "peak_month":str(monthly.loc[monthly["GrossSales"].idxmax(),"Month"]),"peak_month_sales":rounded(monthly["GrossSales"].max()),
    "peak_month_orders":int(monthly.loc[monthly["GrossSales"].idxmax(),"Orders"]),
    "nov_vs_oct_growth_pct":rounded(monthly.loc[monthly["Month"]=="2011-11","MoMGrossPct"].iloc[0]),
    "partial_december_sales":rounded(monthly.loc[monthly["Month"]=="2011-12","GrossSales"].iloc[0]),
    "partial_december_orders":int(monthly.loc[monthly["Month"]=="2011-12","Orders"].iloc[0]),
    "sep_nov_sales":rounded(monthly.loc[monthly["Month"].isin(["2011-09","2011-10","2011-11"]),"GrossSales"].sum()),
    "complete_months_sales":rounded(monthly.loc[monthly["CompleteMonth"],"GrossSales"].sum()),
    "peak_weekday":str(weekday.loc[weekday["GrossSales"].idxmax(),"Weekday"]),"peak_weekday_sales":rounded(weekday["GrossSales"].max()),
    "peak_hour":int(hourly.loc[hourly["Orders"].idxmax(),"Hour"]),"peak_hour_orders":int(hourly["Orders"].max()),
    "rho_value_lines":rounded(correlations.loc["InvoiceValue","LineCount"],6),"rho_value_quantity":rounded(correlations.loc["InvoiceValue","TotalQty"],6),
    "rho_value_avgprice":rounded(correlations.loc["InvoiceValue","AvgPrice"],6),
    "rho_frequency_monetary":rounded(customers["Frequency"].corr(customers["Monetary"],method="spearman"),6),
    "aov_iid_t_ci":[rounded(x) for x in ci],"invoice_quantiles":{str(q):rounded(x) for q,x in quantiles.items()},
    "invoice_value_skew":rounded(invoice["InvoiceValue"].skew(),3),
    "welch_uk_nonuk_invoice":invoice_test,"welch_repeat_onetime_customer_aov":repeat_test,
    "welch_uk_nonuk_customer_aov":customer_country_test,
    "chi_country_repeat":{"chi2":float(chi),"p":float(pchi),"dof":int(dof),"cramers_v":float(np.sqrt(chi_unc/ct.values.sum())),"chi2_uncorrected":float(chi_unc),"p_uncorrected":float(pchi_unc),"yates_correction":True},
    "line_p99_value":rounded(threshold99),"winsorised_sales_sensitivity":rounded(winsor),"winsorisation_change_pct":rounded((winsor-gross)/gross*100),
    "qty_iqr_outlier_pct":rounded(((v["Quantity"]<q1-1.5*(q3-q1))|(v["Quantity"]>q3+1.5*(q3-q1))).mean()*100),
    "price_iqr_outlier_pct":rounded(((v["UnitPrice"]<p1-1.5*(p3-p1))|(v["UnitPrice"]>p3+1.5*(p3-p1))).mean()*100),
    "raw_valid_sales_sensitivity":rounded(raw_valid_value),"duplicate_sales_effect":rounded(raw_valid_value-gross),
    "paired_extreme_gross":rounded(pairs["GrossLineValue"].sum()),"paired_extreme_count":len(pairs),
    "paired_extreme_credit_value_share_pct":rounded(pairs["GrossLineValue"].sum()/credit_abs*100),
    "winback_credit_adjusted_historical_value":rounded(customers.loc[winback_mask,"CreditAdjustedMonetary"].sum()),
    "winback_nonpositive_credit_adjusted_customers":int((customers.loc[winback_mask,"CreditAdjustedMonetary"]<=0).sum()),
    "invoices_multiple_timestamps":len(timestamp_exceptions),
    "timestamp_max_span_seconds":int(timestamp_exceptions["SpanSeconds"].max()),
    "legacy_peak_hour_orders":int(legacy_hourly.max()),
    "merchandise_units":int(merch["Quantity"].sum()),
    "runtime":{"python":platform.python_version(),"pandas":pd.__version__,"numpy":np.__version__,"scipy":__import__('scipy').__version__},
}

# Baseline reconciliation: refuse to publish silently divergent reproduced metrics.
comparisons = [
    ("Raw rows","raw_rows","raw_rows"),("Raw columns","raw_cols","raw_columns"),
    ("Duplicates","dup_count","duplicates_removed"),("Valid sale lines","valid_sales_rows","valid_sales_lines"),
    ("Valid invoices","n_invoices_valid","valid_sales_invoices"),("Identified customers","n_customers_valid","identified_customers"),
    ("Sales before credits","total_revenue","gross_sales"),("Units before credits","total_units","gross_units"),
    ("AOV before credits","aov","aov"),("Repeat rate (%)","repeat_rate","repeat_rate_pct"),
    ("Credit invoices","canc_invoices","credit_invoices"),("Credit value","cancel_value_abs","credit_value_abs"),
    ("Credit document share (%)","cancel_rate_inv","credit_document_share_pct"),
    ("UK sales","top_country_rev","uk_sales"),("UK share (%)","top_country_share","uk_sales_share_pct"),
    ("Peak month sales","peak_month_rev","peak_month_sales"),
    ("Champions customers","rfm_champions_n","champions_customers"),("Champions sales","rfm_champions_rev","champions_sales"),
    ("Champions share of identified sales (%)","rfm_champions_share","champions_known_sales_share_pct"),
    ("Customers for 80% identified sales","pareto_cust_n80","customer_n80"),
    ("Top 20% share of identified sales (%)","pareto_cust_top20_share","top20_known_share_pct"),
    ("Top ~1% share of identified sales (%)","pareto_cust_top1_share","top1_known_share_pct"),
    ("Product codes for 80% merchandise sales","pareto_prod_n80","products_for_80pct"),
    ("Top 10 product sales share (%)","top10_prod_rev_share","top10_product_gross_share_pct"),
]
rows=[]
for label,oldkey,newkey in comparisons:
    expected=float(old[oldkey]);actual=float(metrics[newkey]);ok=abs(expected-actual)<.011
    rows.append({"Metric":label,"OriginalTask4":expected,"RevisedTask4":actual,"Difference":rounded(actual-expected,8),"Status":"MATCH" if ok else "REVIEW"})
    assert ok,(label,expected,actual)
assert np.isclose(gross+c["LineValue"].sum()+a["LineValue"].sum()+e["LineValue"].sum(),df["LineValue"].sum())
assert rounded(gross+float(c["LineValue"].sum()))==metrics["credit_adjusted_value"]
assert int(segments["Customers"].sum())==len(customers)
assert np.isclose(segments["Sales"].sum(),known_sales)
assert np.isclose(countries["GrossSales"].sum(),gross)
assert np.isclose(monthly["GrossSales"].sum(),gross)
assert len(pairs)==2 and pairs["PairSignedValue"].abs().max()<1e-8

save(pd.DataFrame(rows),"task4_metric_reconciliation.csv")
save(monthly,"monthly_performance.csv")
save(countries,"country_performance.csv")
save(net_products,"product_performance.csv")
save(segments,"rfm_segments.csv")
save(customers,"customer_rfm.csv")
save(customer_pareto[["Rank","CustomerPct","CumKnownSalesPct","CumAllSalesPct"]],"customer_pareto.csv")
save(product_pareto,"product_pareto.csv")
save(pairs,"extreme_transaction_pairs.csv")
save(weekday,"weekday_performance.csv")
save(hourly,"hourly_performance.csv")
save(invoice,"invoice_summary.csv")
save(correlations,"invoice_spearman.csv",index=True)
save(ct,"country_repeat_contingency.csv",index=True)
save(df.loc[df["UnitPrice"]<0,["InvoiceNo","StockCode","Description","InvoiceDate","Quantity","UnitPrice","LineValue"]],"negative_price_exceptions.csv")
partition=pd.DataFrame([
    ["Positive-price non-credit sales",len(v),v["InvoiceNo"].nunique(),v["LineValue"].sum()],
    ["C-prefixed credit notes",len(c),c["InvoiceNo"].nunique(),c["LineValue"].sum()],
    ["Other negative-quantity movements",len(a),a["InvoiceNo"].nunique(),a["LineValue"].sum()],
    ["Remaining excluded lines",len(e),e["InvoiceNo"].nunique(),e["LineValue"].sum()],
],columns=["Partition","Lines","DistinctInvoicesInPartition","SignedValue"])
save(partition,"exclusive_line_partitions.csv")
# Do not sum invoice counts across line partitions: an invoice may span partitions.
save(pd.DataFrame({"Variable":raw.columns,"RawMissing":raw.isna().sum().values,"RawMissingPct":raw.isna().mean().values*100}),"missing_values.csv")

# JSON serializer accepts numpy scalars, while preserving unrounded analytical p-values.
(OUT/"metrics.json").write_text(json.dumps(metrics,indent=2,default=lambda x:x.item() if hasattr(x,"item") else str(x)))
for key in ["gross_sales","credit_value_abs","credit_adjusted_value","other_excluded_value","dedup_signed_all_lines","known_customer_sales","anonymous_sales_share_pct","champions_total_sales_share_pct","largest_nonuk_country","paired_extreme_gross"]:
    print(f"{key}: {metrics[key]}")
print(f"PASS: {len(rows)} Task 4 metric reconciliations; all aggregation and partition checks.")
