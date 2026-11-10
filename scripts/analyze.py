"""Task 4 revised: execute the verified core, then original profiling/worked examples.

Run: python scripts/analyze.py
Every result is computed from the SHA-256-verified original UCI workbook.
No synthetic records, recovered-revenue forecasts or intervention outcomes.
"""
from pathlib import Path
import json
import hashlib
import platform
import runpy
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs';DATA=ROOT/'data'
ns=runpy.run_path(str(ROOT/'scripts'/'verified_core.py'))
raw,df,v,invoice,customers,c=map(ns.get,['raw','df','v','invoice','customers','c'])
m=ns['metrics']

def export(frame,name,index=False):
    frame.to_csv(O/name,index=index,float_format='%.10f')

def describe(series,label,grain):
    q=series.quantile([.25,.5,.75])
    modes=series.mode()
    return {'Variable':label,'Grain':grain,'Count':len(series),'Mean':series.mean(),
            'Median':series.median(),'FirstMode':modes.iloc[0],'NumberOfModes':len(modes),
            'StdSample':series.std(ddof=1),'VarianceSample':series.var(ddof=1),
            'Minimum':series.min(),'Q1':q.loc[.25],'Q3':q.loc[.75],
            'IQR':q.loc[.75]-q.loc[.25],'Maximum':series.max(),
            'P95':series.quantile(.95),'P99':series.quantile(.99),
            'Skewness':series.skew()}

# 1. Exact raw-profile outputs, with identifier roles distinguished from measures.
roles={
 'InvoiceNo':'nominal invoice/credit identifier','StockCode':'nominal item/service identifier',
 'Description':'categorical text label','Quantity':'numeric signed measure',
 'InvoiceDate':'datetime, source timezone unspecified','UnitPrice':'numeric GBP measure',
 'CustomerID':'nullable nominal identifier, not a monetary/quantity measure',
 'Country':'categorical customer-country label'}
schema=pd.DataFrame([{'Column':k,'RawDtype':str(raw[k].dtype),'Role':roles[k],
                     'NonNull':int(raw[k].notna().sum()),'Missing':int(raw[k].isna().sum()),
                     'MissingPct':raw[k].isna().mean()*100,'UniqueNonNull':raw[k].nunique()}
                    for k in raw.columns])
export(schema,'raw_schema_profile.csv')
raw_signed=raw.Quantity*raw.UnitPrice
raw_stats=pd.DataFrame([describe(raw.Quantity,'Quantity','raw invoice line'),
                        describe(raw.UnitPrice,'UnitPrice','raw invoice line'),
                        describe(raw_signed,'Derived signed line value','raw invoice line')])
valid_stats=pd.DataFrame([describe(v.Quantity,'Quantity','qualified sales line'),
                          describe(v.UnitPrice,'UnitPrice','qualified sales line'),
                          describe(v.LineValue,'LineValue','qualified sales line'),
                          describe(invoice.InvoiceValue,'InvoiceValue','qualified sales invoice')])
export(raw_stats,'raw_descriptive_statistics.csv');export(valid_stats,'valid_descriptive_statistics.csv')
export(raw.head(10),'actual_first_ten_rows.csv')
export(raw.loc[raw.duplicated(keep=False)].head(12),'duplicate_record_examples.csv')
for col in ['Country','StockCode','Description']:
    vc=raw[col].value_counts(dropna=False)
    freq=pd.DataFrame({'Category':vc.index.astype(str),'Frequency':vc.values,'RawLineSharePct':vc.values/len(raw)*100})
    export(freq,'raw_'+col.lower()+'_frequencies.csv')

# 2. Explicit, non-destructive type/format corrections for the distributed dataset.
# SourceRow is the original Excel row, including the header row offset.
clean=raw.drop_duplicates().copy()
clean.insert(0,'SourceRow',clean.index+2)
for col in ['InvoiceNo','StockCode']:
    clean[col]=clean[col].astype('string').str.strip()
assert ((clean.CustomerID.dropna()%1)==0).all()
clean['CustomerID']=clean.CustomerID.astype('Int64')
clean['InvoiceDate']=pd.to_datetime(clean.InvoiceDate,errors='coerce')
assert clean.InvoiceDate.notna().all()
working_missing=int(clean.Description.isna().sum())
clean['Description']=clean.Description.astype('string').fillna('UNKNOWN')
trim_desc=clean.Description.ne(clean.Description.str.strip())
format_examples=pd.DataFrame({'SourceRow':clean.loc[trim_desc,'SourceRow'],
                             'Before':clean.loc[trim_desc,'Description'],
                             'After':clean.loc[trim_desc,'Description'].str.strip()}).head(10)
export(format_examples,'description_format_examples.csv')
clean['Description']=clean.Description.str.strip()
blank_desc=int(clean.Description.eq('').sum())
clean.loc[clean.Description.eq(''),'Description']='UNKNOWN'
country_trim=int(clean.Country.astype('string').ne(clean.Country.astype('string').str.strip()).sum())
clean['Country']=clean.Country.astype('string').str.strip()
clean['IsCredit']=clean.InvoiceNo.str.upper().str.startswith('C')
clean['IsNonProduct']=clean.StockCode.str.upper().isin(ns['NON_PRODUCT'])
clean['IsOtherNegativeMovement']=(~clean.IsCredit)&clean.Quantity.lt(0)
clean['HasCustomerID']=clean.CustomerID.notna()
clean['IsQualifiedSale']=(~clean.IsCredit)&clean.Quantity.gt(0)&clean.UnitPrice.gt(0)
clean['LineValue']=clean.Quantity*clean.UnitPrice
clean['Month']=clean.InvoiceDate.dt.to_period('M').astype(str)
sales=clean.loc[clean.IsQualifiedSale].copy()
assert len(sales)==524878 and np.isclose(sales.LineValue.sum(),m['gross_sales'])
assert clean.SourceRow.is_unique
assert clean[['InvoiceNo','StockCode','Country','InvoiceDate']].notna().all().all()
assert clean.CustomerID.isna().sum()==135037

# Gzip exports preserve anonymous rows and credits. CSV read-back types are documented.
for frame,filename in [(clean,'cleaned_all_records.csv.gz'),(sales,'qualified_sales.csv.gz')]:
    frame.to_csv(DATA/filename,index=False,float_format='%.8f',date_format='%Y-%m-%d %H:%M:%S',
                 compression={'method':'gzip','compresslevel':6,'mtime':0})
export(pd.DataFrame({'Column':clean.columns,'Dtype':clean.dtypes.astype(str).values}),
       'cleaned_schema.csv')
export(clean.head(10),'cleaned_first_ten_rows.csv')

# 3. Before/after audit: issue flags overlap, line partitions do not.
qty_q1,qty_q3=v.Quantity.quantile([.25,.75]);qty_iqr=qty_q3-qty_q1
qty_lower,qty_upper=qty_q1-1.5*qty_iqr,qty_q3+1.5*qty_iqr
price_q1,price_q3=v.UnitPrice.quantile([.25,.75]);price_iqr=price_q3-price_q1
qout=v.Quantity.lt(qty_lower)|v.Quantity.gt(qty_upper)
pout=v.UnitPrice.lt(price_q1-1.5*price_iqr)|v.UnitPrice.gt(price_q3+1.5*price_iqr)
audit=[
 ['Exact duplicate source rows',541909,536641,5268,'raw.drop_duplicates()','Assumption: identical source rows are duplicate entries; keep raw and report sensitivity.'],
 ['InvoiceNo / StockCode types',536641,536641,0,"astype('string').str.strip()",'Nominal identifiers, no financial values or rows removed.'],
 ['CustomerID nullable integer',536641,536641,135037,"CustomerID.astype('Int64')",'Lossless integer IDs; missing IDs remain missing, not imputed.'],
 ['Missing Description',536641,536641,working_missing,"Description.fillna('UNKNOWN')",'Sentinel only; does not claim to recover the product name.'],
 ['Description edge whitespace',536641,536641,int(trim_desc.sum()),'Description.str.strip()','Formatting only; product aggregation uses StockCode and monetary values unchanged.'],
 ['Country edge whitespace',536641,536641,country_trim,'Country.str.strip()','Measured count may be zero; no invented country reclassification.'],
 ['InvoiceDate validation',536641,536641,0,"pd.to_datetime(..., errors='coerce')",'Original datetime is already valid; assert no missing dates.'],
 ['C-credit flag / partition',536641,536641,len(c),"InvoiceNo.str.upper().str.startswith('C')",'Retain credits in cleaned-all; separate from qualified positive sales.'],
 ['Qualified positive sales filter',536641,524878,11763,'(~IsCredit) & (Quantity > 0) & (UnitPrice > 0)','Create a separate view, not deletion from cleaned-all; exclusive partitions reconcile.'],
 ['IQR quantity / price flags',524878,524878,int(qout.sum()),'Q1 - 1.5*IQR; Q3 + 1.5*IQR','Flag, inspect and retain all qualified outliers; no winsorization of published data.'],
 ['Missing-ID sales retained',524878,524878,int(sales.CustomerID.isna().sum()),'HasCustomerID = CustomerID.notna()','Only customer-level analysis excludes missing IDs.'],
]
export(pd.DataFrame(audit,columns=['Operation','RowsBefore','RowsAfter','AffectedOrFlagged','Code','ReasonAndEffect']),'cleaning_step_audit.csv')

# 4. Actual small-record worked calculations, not made-up numerical demonstrations.
first_invoice=clean.loc[clean.InvoiceNo.eq('536365')&clean.IsQualifiedSale,
 ['SourceRow','InvoiceNo','StockCode','Description','Quantity','UnitPrice','LineValue']]
export(first_invoice,'worked_invoice_536365.csv')
small_qty=raw.Quantity.iloc[:5].to_numpy(float)
mean5=float(small_qty.mean());dev=small_qty-mean5
sd_steps=pd.DataFrame({'ExcelRow':raw.index[:5]+2,'ObservedQuantity':small_qty,
                       'DeviationFromMean':dev,'SquaredDeviation':dev**2})
export(sd_steps,'worked_standard_deviation.csv')
five=invoice.head(5)[['InvoiceNo','LineCount','InvoiceValue']].copy()
five['X2']=five.LineCount**2;five['Y2']=five.InvoiceValue**2
five['XY']=five.LineCount*five.InvoiceValue
export(five,'worked_pearson_five_invoices.csv')
x=five.LineCount.to_numpy(float);y=five.InvoiceValue.to_numpy(float);n=len(x)
pear_num=n*np.sum(x*y)-x.sum()*y.sum()
pear_dx=n*np.sum(x*x)-x.sum()**2;pear_dy=n*np.sum(y*y)-y.sum()**2
pear_manual=pear_num/np.sqrt(pear_dx*pear_dy)
assert np.isclose(pear_manual,stats.pearsonr(x,y).statistic)
all_iv=np.sort(invoice.InvoiceValue.to_numpy())
lo=all_iv[len(all_iv)//2-1];hi=all_iv[len(all_iv)//2]

uk=customers.loc[customers.Country.eq('United Kingdom'),'AOV'].to_numpy(float)
nonuk=customers.loc[~customers.Country.eq('United Kingdom'),'AOV'].to_numpy(float)
var1,var2=uk.var(ddof=1),nonuk.var(ddof=1)
se=np.sqrt(var1/len(uk)+var2/len(nonuk))
t_manual=(uk.mean()-nonuk.mean())/se
df_w=(var1/len(uk)+var2/len(nonuk))**2/((var1/len(uk))**2/(len(uk)-1)+(var2/len(nonuk))**2/(len(nonuk)-1))
p_manual=2*stats.t.sf(abs(t_manual),df_w)
assert np.isclose(t_manual,stats.ttest_ind(uk,nonuk,equal_var=False).statistic)
assert np.isclose(p_manual,stats.ttest_ind(uk,nonuk,equal_var=False).pvalue)

invoice['CountryGroup']=np.where(invoice.Country.eq('United Kingdom'),'UK','Non-UK')
invoice['RepeatCustomer']=invoice.CustomerID.map(customers.set_index('CustomerID').Frequency.gt(1))
frequency=customers.Frequency
bins=[0,1,2,5,10,np.inf];freq_labels=['1','2','3–5','6–10','11+']
freq_bands=pd.cut(frequency,bins=bins,labels=freq_labels)
counts=freq_bands.value_counts(sort=False)
export(pd.DataFrame({'OrdersPerCustomer':counts.index.astype(str),'Customers':counts.values,
                     'CustomerPct':counts.values/len(customers)*100}),'customer_frequency_bands.csv')
export(invoice,'invoice_summary.csv')
export(v[['InvoiceNo','StockCode','Quantity','UnitPrice','LineValue']],'sales_line_measures.csv.gz')
pearson=invoice[['InvoiceValue','LineCount','TotalQty','AvgPrice']].corr(method='pearson')
export(pearson,'invoice_pearson.csv',index=True)

# Customer-country breadth is not additive: a customer can appear in multiple labels.
country_multi=int((sales.groupby('CustomerID').Country.nunique()>1).sum())
# A stratified descriptive group-by is a multivariate comparison, not a treatment effect.
seg_country=customers.assign(CountryGroup=np.where(customers.Country.eq('United Kingdom'),'UK','Non-UK')).groupby(['CountryGroup','Segment']).agg(Customers=('CustomerID','size'),GrossSales=('Monetary','sum'),MedianAOV=('AOV','median')).reset_index()
export(seg_country,'rfm_country_multivariate.csv')

extra={
 'author':'T. Aparna Reddy','report_date':'2026-11-07','raw_shape':list(raw.shape),
 'raw_missing_pct':raw.CustomerID.isna().mean()*100,'duplicate_pct':raw.duplicated().mean()*100,
 'raw_signed_total':float(raw_signed.sum()),'description_trimmed_rows':int(trim_desc.sum()),
 'blank_after_trim':blank_desc,'country_trimmed_rows':country_trim,
 'cleaned_all_shape':list(clean.shape),'qualified_sales_shape':list(sales.shape),
 'cleaned_payload_duplicate_rows_after_normalization':int(clean.drop(columns='SourceRow').duplicated().sum()),
 'country_multi_label_customers':country_multi,
 'first_line':{'invoice':str(raw.InvoiceNo.iloc[0]),'stock':str(raw.StockCode.iloc[0]),
               'quantity':int(raw.Quantity.iloc[0]),'unit_price':float(raw.UnitPrice.iloc[0]),
               'value':float(raw.Quantity.iloc[0]*raw.UnitPrice.iloc[0])},
 'first_invoice_total':float(first_invoice.LineValue.sum()),'first_invoice_lines':len(first_invoice),
 'first_five_quantity':small_qty.tolist(),'first_five_mean':mean5,'first_five_sq_dev_sum':float((dev**2).sum()),
 'first_five_sample_variance':float((dev**2).sum()/(len(small_qty)-1)),
 'first_five_sample_sd':float(np.sqrt((dev**2).sum()/(len(small_qty)-1))),
 'quantity_q1':float(qty_q1),'quantity_q3':float(qty_q3),'quantity_iqr':float(qty_iqr),
 'quantity_iqr_lower':float(qty_lower),'quantity_iqr_upper':float(qty_upper),
 'quantity_outlier_count':int(qout.sum()),'price_outlier_count':int(pout.sum()),
 'price_q1':float(price_q1),'price_q3':float(price_q3),'price_iqr':float(price_iqr),
 'first_retained_quantity_outlier':v.loc[qout,['InvoiceNo','StockCode','Quantity','UnitPrice','LineValue']].iloc[0].to_dict(),
 'median_invoice_lower_centre':float(lo),'median_invoice_upper_centre':float(hi),
 'pearson_five':{'n':n,'sum_x':float(x.sum()),'sum_y':float(y.sum()),'sum_x2':float(np.sum(x*x)),
                 'sum_y2':float(np.sum(y*y)),'sum_xy':float(np.sum(x*y)),
                 'numerator':float(pear_num),'dx':float(pear_dx),'dy':float(pear_dy),'r':float(pear_manual)},
 'welch_worked':{'n_uk':len(uk),'n_nonuk':len(nonuk),'mean_uk':float(uk.mean()),'mean_nonuk':float(nonuk.mean()),
                 'sd_uk':float(uk.std(ddof=1)),'sd_nonuk':float(nonuk.std(ddof=1)),
                 'var_uk':float(var1),'var_nonuk':float(var2),'standard_error':float(se),
                 't':float(t_manual),'df':float(df_w),'p_two_sided':float(p_manual)},
 'runtime':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,
             'scipy':__import__('scipy').__version__,'matplotlib':__import__('matplotlib').__version__,
             'seaborn':__import__('seaborn').__version__},
}

# Extra provenance and direct, traceable quality examples for the revised report.
raw_sources=raw.copy()
raw_sources.insert(0,'SourceRow',raw_sources.index+2)
description_nontext = raw_sources.loc[raw.Description.notna() & ~raw.Description.map(lambda x: isinstance(x, str))]
export(description_nontext, 'description_nontext_examples.csv')
duplicate_groups=raw_sources.loc[raw.duplicated(keep=False)].copy()
export(duplicate_groups.head(16),'duplicate_examples_with_source_rows.csv')
first_dup_index=raw.index[raw.duplicated()][0]
first_dup=raw.loc[first_dup_index]
match=(raw.eq(first_dup)| (raw.isna() & first_dup.isna())).all(axis=1)
first_dup_sources=raw.index[match].to_numpy()+2
missing_example=clean.loc[clean.SourceRow.isin(raw.index[raw.Description.isna()]+2)].iloc[0]
normal_invoice_counts=sales.groupby('InvoiceNo').size()
raw_nonpositive=int(raw.UnitPrice.le(0).sum())
nonproduct_present=sorted(clean.loc[clean.IsNonProduct,'StockCode'].unique().tolist())
invoice['KnownCustomer']=invoice.CustomerID.notna()
country_box=invoice.groupby('CountryGroup').InvoiceValue.agg(['count','mean','median','std','min','max'])
country_box['Q1']=invoice.groupby('CountryGroup').InvoiceValue.quantile(.25)
country_box['Q3']=invoice.groupby('CountryGroup').InvoiceValue.quantile(.75)
export(country_box,'invoice_country_box_statistics.csv',index=True)
from scipy.stats import t as student_t
welch_critical=student_t.ppf(.975,df_w)
diff=float(uk.mean()-nonuk.mean())
welch_ci=[float(diff-welch_critical*se),float(diff+welch_critical*se)]
ct=ns['ct'];chi_unc=stats.chi2_contingency(ct,correction=False)
chi_yates=stats.chi2_contingency(ct,correction=True)
export(pd.DataFrame(chi_yates.expected_freq,index=ct.index,columns=ct.columns),'country_repeat_expected.csv',index=True)
extra.update({
 'raw_description_nontext_count':len(description_nontext),
 'raw_description_nontext_source_rows':description_nontext.SourceRow.tolist(),
 'first_duplicate_source_rows':first_dup_sources.tolist(),
 'first_duplicate_record':{k:(None if pd.isna(val) else str(val) if k=='InvoiceDate' else val)
                           for k,val in first_dup.items()},
 'missing_description_example':{'SourceRow':int(missing_example.SourceRow),
                                'InvoiceNo':str(missing_example.InvoiceNo),
                                'StockCode':str(missing_example.StockCode),
                                'DescriptionAfter':str(missing_example.Description)},
 'raw_nonpositive_price_lines':raw_nonpositive,
 'present_nonproduct_codes':nonproduct_present,
 'customers_nonpositive_credit_adjusted':int(customers.CreditAdjustedMonetary.round(2).le(0).sum()),
 'welch_mean_difference_uk_minus_nonuk':diff,
 'welch_mean_difference_ci95':welch_ci,
 'chi_squared_uncorrected':float(chi_unc.statistic),
 'chi_squared_yates':float(chi_yates.statistic),
 'chi_squared_expected_min':float(chi_yates.expected_freq.min()),
 'cramers_v_uncorrected':float(np.sqrt(chi_unc.statistic/ct.to_numpy().sum())),
 'cramers_v_yates_convention':float(np.sqrt(chi_yates.statistic/ct.to_numpy().sum())),
 'gross_unrounded':float(sales.LineValue.sum()),
 'gross_nonproduct_share_pct':float(m['nonproduct_sales']/sales.LineValue.sum()*100),
 'duplicated_sales_share_pct':float((m['duplicate_sales_effect']/m['raw_valid_sales_sensitivity'])*100),
 'raw_quantity_negative_lines':int(raw.Quantity.lt(0).sum()),
 'raw_zero_quantity_lines':int(raw.Quantity.eq(0).sum()),
 'invoice_timestamp_allocation':'earliest timestamp per invoice',
 'customer_country_assignment':'earliest qualified invoice timestamp; invoice number breaks ties',
})

(O/'extended_results.json').write_text(json.dumps(extra,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
manifest=[]
for name in ['cleaned_all_records.csv.gz','qualified_sales.csv.gz']:
 p=DATA/name;manifest.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                            'rows':len(clean) if name.startswith('cleaned_all') else len(sales),'columns':len(clean.columns)})
(DATA/'cleaned_data_manifest.json').write_text(json.dumps(manifest,indent=2))
(DATA/'source_verification.json').write_text(json.dumps({'dataset':'UCI Online Retail','doi':'10.24432/C5BW33',
 'official_url':ns['SOURCE'],'workbook_bytes':ns['workbook'].stat().st_size,'sha256':ns['sha'],
 'dimensions':list(raw.shape),'verification_run_at_utc':datetime.now(timezone.utc).isoformat(),'synthetic_records':0},indent=2))
print('Extended exploration complete:',list(clean.shape),'cleaned-all;',list(sales.shape),'qualified sales')
print('Description whitespace normalized:',int(trim_desc.sum()),'| Country whitespace:',country_trim)
print('Raw mean / min Quantity:',raw.Quantity.mean(),raw.Quantity.min())
print('Worked standard deviation:',extra['first_five_sample_sd'])
print('Worked Pearson r:',pear_manual,'| Worked Welch t:',t_manual,'df:',df_w,'p:',p_manual)
print('Quantity IQR outliers:',int(qout.sum()),'| first invoice:',float(first_invoice.LineValue.sum()))
