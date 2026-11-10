"""Independent, workbook-backed numerical and deliverable validation.

Run from any directory: python tests/validate_outputs.py
Re-reads Excel directly: it does not use the analysis pickle or import its results
as the source of truth. Saved metrics are compared with independently calculated
quantities. Writes reports/QA_REPORT.json and reports/VALIDATION.md; fails nonzero
if any mandatory check fails. Network/publishing checks are recorded separately.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile
import ast
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats
from PIL import Image
from docx import Document
import nbformat

ROOT = Path(__file__).resolve().parents[1]
O = ROOT/'outputs'
R = ROOT/'reports'
R.mkdir(exist_ok=True)
M = json.loads((O/'metrics.json').read_text())
E = json.loads((O/'extended_results.json').read_text())
F = json.loads((O/'report_manifest.json').read_text())
RESULTS = []


def check(name, condition, detail=''):
    ok = bool(condition)
    RESULTS.append({'check': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    print(('PASS' if ok else 'FAIL')+': '+name)


def near(a, b, tolerance=0.011):
    return bool(np.allclose(a, b, rtol=0, atol=tolerance, equal_nan=True))


workbook = ROOT/'data/Online Retail.xlsx'
check('Official workbook fingerprint and bytes',
      hashlib.sha256(workbook.read_bytes()).hexdigest() ==
      '43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d'
      and workbook.stat().st_size == 23715344)
raw = pd.read_excel(workbook, sheet_name='Online Retail')
check('Raw dimensions and exact eight-column order', raw.shape == (541909, 8)
      and list(raw.columns) == ['InvoiceNo','StockCode','Description','Quantity',
                               'InvoiceDate','UnitPrice','CustomerID','Country'])
check('Raw missing counts in all eight columns',
      raw.isna().sum().tolist() == [0,0,1454,0,0,0,135080,0])
check('Raw missing and duplicate percentages',
      near(raw.CustomerID.isna().mean()*100, E['raw_missing_pct'], 1e-10)
      and near(raw.duplicated().mean()*100, E['duplicate_pct'], 1e-10))
check('Raw uniqueness and timestamp range',
      raw.InvoiceNo.nunique()==25900 and raw.StockCode.nunique()==4070
      and raw.CustomerID.nunique()==4372 and raw.Country.nunique()==38
      and str(raw.InvoiceDate.min())=='2010-12-01 08:26:00'
      and str(raw.InvoiceDate.max())=='2011-12-09 12:50:00')
check('Exact duplicates independently counted', raw.duplicated().sum()==5268)
profile = pd.read_csv(O/'raw_schema_profile.csv').set_index('Column')
check('Saved schema non-null/missing/unique/dtype profile', all(
      int(profile.loc[c,'NonNull'])==raw[c].notna().sum()
      and int(profile.loc[c,'Missing'])==raw[c].isna().sum()
      and int(profile.loc[c,'UniqueNonNull'])==raw[c].nunique()
      and profile.loc[c,'RawDtype']==str(raw[c].dtype) for c in raw))

base = raw.drop_duplicates().copy()
base.insert(0,'SourceRow',base.index+2)
base['InvoiceNo']=base.InvoiceNo.astype(str)
base['StockCode']=base.StockCode.astype(str)
base['Credit']=base.InvoiceNo.str.upper().str.startswith('C')
base['Value']=base.Quantity*base.UnitPrice
valid=(~base.Credit)&base.Quantity.gt(0)&base.UnitPrice.gt(0)
sales = base.loc[valid].copy()
credit = base.loc[base.Credit]
othernegative = base.loc[(~base.Credit)&base.Quantity.lt(0)]
remaining = base.loc[~(valid|base.Credit|((~base.Credit)&base.Quantity.lt(0)))]
check('Independently partitioned line counts',
      [len(base),len(sales),len(credit),len(othernegative),len(remaining)] ==
      [536641,524878,9251,1336,1176])
check('Financial bridge from independently computed line values',
      near(sales.Value.sum(), M['gross_sales'])
      and near(-credit.Value.sum(), M['credit_value_abs'])
      and near(sales.Value.sum()+credit.Value.sum(),M['credit_adjusted_value'])
      and near(remaining.Value.sum(),-22124.12)
      and near(base.Value.sum(),M['dedup_signed_all_lines']))
check('Exclusive partition export',
      near(pd.read_csv(O/'exclusive_line_partitions.csv').Lines,
           [len(sales),len(credit),len(othernegative),len(remaining)],0)
      and near(pd.read_csv(O/'exclusive_line_partitions.csv').SignedValue,
               [sales.Value.sum(),credit.Value.sum(),othernegative.Value.sum(),remaining.Value.sum()],1e-6))
check('Bad-debt records are retained and disclosed, not guessed errors',
      set(remaining.loc[remaining.UnitPrice.lt(0),'InvoiceNo'])=={'A563186','A563187'}
      and near(remaining.loc[remaining.UnitPrice.lt(0),'Value'],[-11062.06,-11062.06]))

clean = pd.read_csv(ROOT/'data/cleaned_all_records.csv.gz',
    dtype={'InvoiceNo':'string','StockCode':'string','CustomerID':'Int64',
           'IsQualifiedSale':'boolean','IsCredit':'boolean'},parse_dates=['InvoiceDate'])
qualified = pd.read_csv(ROOT/'data/qualified_sales.csv.gz',
    dtype={'InvoiceNo':'string','StockCode':'string','CustomerID':'Int64'},
    parse_dates=['InvoiceDate'])
check('Complete cleaned and separate sales export shapes',
      clean.shape==(536641,16) and qualified.shape==(524878,16))
check('SourceRow preserves exact deduplicated workbook provenance',
      clean.SourceRow.is_unique and clean.SourceRow.tolist()==base.SourceRow.tolist())
check('Original quantity and unit amount preserved',
      near(clean.Quantity,base.Quantity,0) and near(clean.UnitPrice,base.UnitPrice,1e-8)
      and near(clean.LineValue,base.Value,1e-7))
check('Identifier normalization is lossless and missing IDs retained',
      clean.InvoiceNo.tolist()==base.InvoiceNo.str.strip().tolist()
      and clean.StockCode.tolist()==base.StockCode.str.strip().tolist()
      and clean.CustomerID.isna().sum()==135037
      and clean.CustomerID.reset_index(drop=True).equals(base.CustomerID.astype('Int64').reset_index(drop=True)))
expected_description=base.Description.astype('string').fillna('UNKNOWN').str.strip().replace('','UNKNOWN')
check('Description sentinel/whitespace normalization is exact',
      clean.Description.tolist()==expected_description.tolist()
      and clean.Description.isna().sum()==0)
check('Whitespace affected count comes from actual source',
      sum(str(value)!=str(value).strip() for value in base.Description.dropna())==112371
      and E['description_trimmed_rows']==112371 and E['country_trimmed_rows']==0
      and E['raw_description_nontext_count']==1)
check('Dates and original country labels preserved',
      clean.InvoiceDate.tolist()==base.InvoiceDate.tolist()
      and clean.Country.tolist()==base.Country.str.strip().tolist())
check('Derived sales/credit flags match literal sign and prefix rules',
      clean.IsQualifiedSale.tolist()==valid.tolist()
      and clean.IsCredit.tolist()==base.Credit.tolist()
      and clean.HasCustomerID.tolist()==base.CustomerID.notna().tolist()
      and clean.IsOtherNegativeMovement.tolist()==((~base.Credit)&base.Quantity.lt(0)).tolist())
check('Sales export is an exact view of complete cleaned data',
      qualified.SourceRow.tolist()==sales.SourceRow.tolist()
      and near(qualified.LineValue,sales.Value,1e-7))
check('No duplicate cleaned payload after normalization',
      clean.drop(columns='SourceRow').duplicated().sum()==0)
manifest=json.loads((ROOT/'data/cleaned_data_manifest.json').read_text())
check('Cleaned dataset file hashes and byte counts', all(
      (ROOT/'data'/item['file']).stat().st_size==item['bytes']
      and hashlib.sha256((ROOT/'data'/item['file']).read_bytes()).hexdigest()==item['sha256']
      for item in manifest))

iv=sales.groupby('InvoiceNo').agg(Value=('Value','sum'),Date=('InvoiceDate','min'),
     CustomerID=('CustomerID','first'),Country=('Country','first'),Lines=('Value','size'),
     Quantity=('Quantity','sum'),MeanPrice=('UnitPrice','mean')).reset_index()
check('Invoice counts and independent summary arithmetic',len(iv)==19960
      and near(iv.Value.sum(),sales.Value.sum(),1e-7)
      and near(pd.read_csv(O/'invoice_summary.csv').InvoiceValue,iv.Value,1e-7))
check('Invoice date allocation uses earliest timestamp exactly',
      pd.read_csv(O/'invoice_summary.csv',parse_dates=['InvoiceDate']).InvoiceDate.tolist()==iv.Date.tolist())
check('Hourly counts are mutually exclusive and noon is 3219',
      len(iv)==iv.Date.dt.hour.value_counts().sum()
      and int(iv.Date.dt.hour.value_counts().loc[12])==3219
      and pd.read_csv(O/'hourly_performance.csv').Orders.sum()==19960)
known=iv.loc[iv.CustomerID.notna()].sort_values(['Date','InvoiceNo'])
cu=known.groupby('CustomerID').agg(Frequency=('InvoiceNo','nunique'),Monetary=('Value','sum'),
                                AOV=('Value','mean'),Country=('Country','first'))
check('Known-customer counts and financial coverage',
      len(cu)==4338 and len(known)==18532
      and near(cu.Monetary.sum(),M['known_customer_sales'])
      and near(sales.loc[sales.CustomerID.isna(),'Value'].sum(),M['anonymous_sales'])
      and sales.CustomerID.isna().sum()==132186)
check('Customer exported AOV/frequency/country reconcile independently',
      near(pd.read_csv(O/'customer_rfm.csv').AOV,cu.AOV,1e-7)
      and near(pd.read_csv(O/'customer_rfm.csv').Frequency,cu.Frequency,0)
      and pd.read_csv(O/'customer_rfm.csv').Country.tolist()==cu.Country.tolist())
check('Customer country ambiguity disclosed',
      (sales.groupby('CustomerID').Country.nunique()>1).sum()==8
      and E['country_multi_label_customers']==8)

for filename,serieslist in [
    ('raw_descriptive_statistics.csv',[raw.Quantity,raw.UnitPrice,raw.Quantity*raw.UnitPrice]),
    ('valid_descriptive_statistics.csv',[sales.Quantity,sales.UnitPrice,sales.Value,iv.Value])]:
    table=pd.read_csv(O/filename)
    ok=True
    for row,s in zip(table.to_dict('records'),serieslist):
        expected={'Count':len(s),'Mean':s.mean(),'Median':s.median(),
                  'FirstMode':s.mode().iloc[0],'StdSample':s.std(ddof=1),
                  'Minimum':s.min(),'Q1':s.quantile(.25),'Q3':s.quantile(.75),
                  'Maximum':s.max(),'IQR':s.quantile(.75)-s.quantile(.25)}
        ok &= all(near(row[k],value,1e-6) for k,value in expected.items())
    check('All required descriptive statistics: '+filename,ok)

first=sales.loc[sales.InvoiceNo.eq('536365')]
check('Worked first line and all seven invoice lines',
      len(first)==7 and near(first.Value.iloc[0],15.30,1e-10)
      and near(first.Value.sum(),139.12,1e-8)
      and pd.read_csv(O/'worked_invoice_536365.csv').SourceRow.tolist()==first.SourceRow.tolist())
q=raw.Quantity.iloc[:5].to_numpy(float)
check('Worked mean, sample variance and SD independently verified',
      q.tolist()==[6,6,8,6,6] and near(q.mean(),6.4,1e-12)
      and near(q.var(ddof=1),0.8,1e-12)
      and near(q.std(ddof=1),E['first_five_sample_sd'],1e-12))
check('Global AOV and exact central median observations',
      near(iv.Value.mean(),M['aov']) and near(iv.Value.median(),303.30)
      and np.sort(iv.Value.to_numpy())[9979:9981].tolist()==[303.3,303.3])
q1,q3=sales.Quantity.quantile([.25,.75]);iqr=q3-q1
qtyflag=(sales.Quantity<q1-1.5*iqr)|(sales.Quantity>q3+1.5*iqr)
p1,p3=sales.UnitPrice.quantile([.25,.75]);piqr=p3-p1
priceflag=(sales.UnitPrice<p1-1.5*piqr)|(sales.UnitPrice>p3+1.5*piqr)
check('Worked IQR bounds, counts and retained example',
      [q1,q3,iqr,q1-1.5*iqr,q3+1.5*iqr]==[1,11,10,-14,26]
      and qtyflag.sum()==27111 and priceflag.sum()==37827
      and E['first_retained_quantity_outlier']['Quantity']==32)
country=sales.groupby('Country').Value.sum()
month=sales.groupby(sales.InvoiceDate.dt.to_period('M')).agg(Sales=('Value','sum'),Orders=('InvoiceNo','nunique'))
check('Country/month aggregates reconcile to complete sales',
      near(pd.read_csv(O/'country_performance.csv').GrossSales.sum(),sales.Value.sum(),1e-7)
      and near(pd.read_csv(O/'monthly_performance.csv').GrossSales.sum(),sales.Value.sum(),1e-7))
check('Worked UK share and correct non-UK leading country',
      near(country.loc['United Kingdom'],9001744.094,1e-6)
      and country.sort_values(ascending=False).index[1]=='Netherlands'
      and near(country.loc['United Kingdom']/sales.Value.sum()*100,M['uk_sales_share_pct']))
october,november=month.loc['2011-10'],month.loc['2011-11']
sg=november.Sales/october.Sales-1
og=november.Orders/october.Orders-1
ag=(november.Sales/november.Orders)/(october.Sales/october.Orders)-1
check('Worked November growth and multiplicative decomposition',
      near(sg*100,M['nov_vs_oct_growth_pct']) and near(og*100,35.7352941176,1e-8)
      and near(ag*100,-3.7630711836,1e-8)
      and near((1+og)*(1+ag)-1,sg,1e-12))
check('Partial final month is flagged, not used as a full-month decline',
      raw.InvoiceDate.max().day==9
      and not bool(pd.read_csv(O/'monthly_performance.csv').iloc[-1].CompleteMonth)
      and 'partial' in (ROOT/'reports/Task4_Real_World_Dataset_Analysis.md').read_text().lower())
check('Worked credit ratios use explicit correct denominators',
      credit.InvoiceNo.nunique()==3836
      and near(3836/(19960+3836)*100,M['credit_document_share_pct'])
      and near(-credit.Value.sum()/sales.Value.sum()*100,M['credit_value_pct_of_gross']))
check('Worked repeat share is observed customer frequency, not row count',
      (cu.Frequency>1).sum()==2845 and (cu.Frequency==1).sum()==1493
      and near((cu.Frequency>1).mean()*100,M['repeat_rate_pct']))
segments=pd.read_csv(O/'rfm_segments.csv')
champ=segments.loc[segments.Segment.eq('Champions')].iloc[0]
check('RFM customers and sales partition the known population',
      segments.Customers.sum()==4338 and near(segments.Sales.sum(),cu.Monetary.sum(),1e-6))
check('Worked Champions proportions use both denominators',
      champ.Customers==942 and near(champ.Sales,5729483.37)
      and near(champ.Sales/cu.Monetary.sum()*100,M['champions_known_sales_share_pct'])
      and near(champ.Sales/sales.Value.sum()*100,M['champions_total_sales_share_pct']))
check('Multivariate country × RFM aggregate reconciles',
      pd.read_csv(O/'rfm_country_multivariate.csv').Customers.sum()==4338
      and near(pd.read_csv(O/'rfm_country_multivariate.csv').GrossSales.sum(),cu.Monetary.sum(),1e-6))
p5=iv.head(5);x=p5.Lines.to_numpy(float);y=p5.Value.to_numpy(float);n=len(x)
r=(n*np.sum(x*y)-x.sum()*y.sum())/np.sqrt((n*np.sum(x*x)-x.sum()**2)*(n*np.sum(y*y)-y.sum()**2))
check('Worked manual Pearson r independently matches SciPy',
      near(r,E['pearson_five']['r'],1e-12) and near(r,stats.pearsonr(x,y).statistic,1e-12))
check('Full-data rank correlations independently reproduced',
      near(stats.spearmanr(iv.Value,iv.Lines).statistic,M['rho_value_lines'],1e-6)
      and near(stats.spearmanr(iv.Value,iv.Quantity).statistic,M['rho_value_quantity'],1e-6)
      and near(stats.spearmanr(iv.Value,iv.MeanPrice).statistic,M['rho_value_avgprice'],1e-6))
a=cu.loc[cu.Country.eq('United Kingdom'),'AOV'].to_numpy(float)
b=cu.loc[~cu.Country.eq('United Kingdom'),'AOV'].to_numpy(float)
v1,v2=a.var(ddof=1),b.var(ddof=1);se=np.sqrt(v1/len(a)+v2/len(b))
t=(a.mean()-b.mean())/se
nu=(v1/len(a)+v2/len(b))**2/((v1/len(a))**2/(len(a)-1)+(v2/len(b))**2/(len(b)-1))
test=stats.ttest_ind(a,b,equal_var=False)
check('Worked Welch n, means, standard error, t, df and p',
      [len(a),len(b)]==[3920,418] and near(t,E['welch_worked']['t'],1e-10)
      and near(nu,E['welch_worked']['df'],1e-8)
      and near(se,E['welch_worked']['standard_error'],1e-10)
      and near(test.pvalue,E['welch_worked']['p_two_sided'],1e-18))
ci=test.confidence_interval()
check('Worked mean-difference interval matches SciPy directly',
      near([ci.low,ci.high],E['welch_mean_difference_ci95'],1e-9))
ct=pd.crosstab(np.where(cu.Country.eq('United Kingdom'),'UK','Non-UK'),np.where(cu.Frequency>1,'Repeat','One-time'))
chi=stats.chi2_contingency(ct,correction=True)
unc=stats.chi2_contingency(ct,correction=False)
check('Worked contingency table, expected counts, Yates and standard V',
      ct.values.tolist()==[[143,275],[1350,2570]]
      and near(chi.statistic,E['chi_squared_yates'],1e-12)
      and near(chi.pvalue,M['chi_country_repeat']['p'],1e-12)
      and near(np.sqrt(unc.statistic/4338),M['chi_country_repeat']['cramers_v'],1e-12)
      and near(chi.expected_freq.min(),143.8621484555,1e-9))
cap=sales.Value.quantile(.99);alternative=sales.Value.clip(upper=cap).sum()
check('Worked cap sensitivity and duplicate sensitivity independently reproduced',
      near(cap,183.6,1e-8) and near(alternative,M['winsorised_sales_sensitivity'])
      and near((alternative/sales.Value.sum()-1)*100,M['winsorisation_change_pct'])
      and near((raw.loc[(~raw.InvoiceNo.astype(str).str.upper().str.startswith('C'))&raw.Quantity.gt(0)&raw.UnitPrice.gt(0),'Quantity']*
               raw.loc[(~raw.InvoiceNo.astype(str).str.upper().str.startswith('C'))&raw.Quantity.gt(0)&raw.UnitPrice.gt(0),'UnitPrice']).sum(),M['raw_valid_sales_sensitivity']))
pairs=pd.read_csv(O/'extreme_transaction_pairs.csv')
check('Two extreme matches are genuine equal-and-opposite source records',all(
      len(sales.loc[sales.InvoiceNo.eq(str(row.SaleInvoice)) & sales.StockCode.eq(str(row.StockCode)) & sales.CustomerID.eq(row.CustomerID)])==1
      and len(credit.loc[credit.InvoiceNo.eq(row.CreditInvoice)&credit.StockCode.eq(str(row.StockCode))&credit.CustomerID.eq(row.CustomerID)])==1
      and near(row.GrossLineValue+row.SignedCredit,0,1e-8)
      for row in pairs.itertuples()) and len(pairs)==2
      and near(pairs.GrossLineValue.sum(),245653.20))
adj=cu.Monetary.add(credit.groupby('CustomerID').Value.sum(),fill_value=0).reindex(cu.index)
check('Penny-rounded non-positive account count avoids float near-zero errors',
      adj.round(2).le(0).sum()==21 and E['customers_nonpositive_credit_adjusted']==21)
check('Customer offset examples are supported by actual balances',
      near(adj.loc[16446],2.90) and near(adj.loc[12346],0))
check('Netherlands top-account share is independently verified',
      near(known.loc[known.Country.eq('Netherlands')].groupby('CustomerID').Value.sum().max()/
           known.loc[known.Country.eq('Netherlands'),'Value'].sum()*100,
           pd.read_csv(O/'country_performance.csv').set_index('Country').loc['Netherlands','TopAccountKnownSalesPct'],1e-8))
check('All 24 previous Task 4 metrics reconcile with MATCH status',
      len(pd.read_csv(O/'task4_metric_reconciliation.csv'))==24
      and pd.read_csv(O/'task4_metric_reconciliation.csv').Status.eq('MATCH').all())

# Structural and deliverable checks do not substitute for the calculations above.
charts=json.loads((ROOT/'visualizations/chart_manifest.json').read_text())
check('Exactly 15 real, non-empty high-resolution chart files',
      len(charts)==15 and len(list((ROOT/'visualizations').glob('*.png')))==15
      and all((ROOT/'visualizations'/item['file']).stat().st_size>10000
              and Image.open(ROOT/'visualizations'/item['file']).width>=2000 for item in charts))
chart_source=(ROOT/'scripts/make_charts.py').read_text()
ast.parse(chart_source)
check('Both plotting libraries and all seven required chart types are implemented',
      all(s in chart_source for s in ['import matplotlib.pyplot as plt','import seaborn as sns',
             '.bar(','.hist(','.plot(','.scatter(','sns.boxplot(','sns.heatmap(','sns.countplot(']))
check('Every figure has numerical observation, interpretation, implication and evidence',
      len(F['figures'])==15 and all(all(str(f.get(k,'')) for k in
          ['observation','interpretation','business_implication','evidence_files']) for f in F['figures']))
check('Fourteen worked examples cover every requested component',
      len(F['worked_examples'])==14 and [x['number'] for x in F['worked_examples']]==list(range(1,15))
      and all(all(str(w.get(k,'')) for k in ['formula','substitution','result','interpretation','evidence'])
              for w in F['worked_examples']))
check('Twelve findings each contain evidence/comparison/meaning/importance/action',
      len(F['findings'])==12 and all(all(str(x.get(k,'')) for k in
          ['evidence','comparison','meaning','importance','recommendation','files']) for x in F['findings']))
check('Eight measurable recommendations contain all required fields',
      len(F['recommendations'])==8 and all(all(str(x.get(k,'')) for k in
          ['problem_evidence','action','expected_benefit','measurement','owner']) for x in F['recommendations']))

report=ROOT/'reports/YuvaIntern_Task4_Real_World_Dataset_Analysis_Revised.docx'
doc=Document(report)
headings=[p.text for p in doc.paragraphs if p.style.name=='Heading 1']
check('Exact 19-part report order and required section names',headings==F['sections']
      and len(headings)==19 and [int(re.match(r'^(\d+)\.',h).group(1)) for h in headings]==list(range(1,20)))
check('Author metadata and sensible Word size',doc.core_properties.author=='T. Aparna Reddy'
      and 1000000<report.stat().st_size<3000000)
check('Embedded figure/table counts and sequential captions',len(doc.inline_shapes)==15 and len(doc.tables)==31
      and len([p for p in doc.paragraphs if re.match(r'^Figure \d+\.',p.text)])==15
      and len([p for p in doc.paragraphs if re.match(r'^Table \d+\.',p.text)])==31)
with zipfile.ZipFile(report) as z:
    xml=z.read('word/document.xml').decode()
    footer=''.join(z.read(n).decode() for n in z.namelist() if re.match(r'word/footer\d+.xml',n))
    check('Real generated contents and live page fields, no insertion marker',
          '[TABLE_OF_CONTENTS]' not in xml and 'TOC ' in xml and 'PAGE' in footer and 'NUMPAGES' in footer)
all_text='\n'.join(p.text for p in doc.paragraphs)+'\n'+'\n'.join(c.text for t in doc.tables for row in t.rows for c in row.cells)
check('At least eight specific analytical questions are present',all('Q'+str(i)+'.' in all_text for i in range(1,9)))
check('All original column definitions and all required raw statistics are present',
      all(c in all_text for c in raw.columns)
      and all(term in all_text for term in ['Sample SD','Minimum','Maximum','FirstMode','25th percentile','75th percentile']))
for filename in ['verified_core.py','analyze.py','make_charts.py']:
    ps=doc.paragraphs
    i=next(i for i,p in enumerate(ps) if p.text.startswith('19.4.') and 'scripts/'+filename+' —' in p.text)
    j=next(j for j,p in enumerate(ps[i+1:],i+1) if p.text=='Evidence file: End of complete file: scripts/'+filename)
    got='\n'.join(p.text if p.text!=' ' else '' for p in ps[i+1:j] if p.style.name=='Code')
    expected=(ROOT/'scripts'/filename).read_text().rstrip('\n')
    check('Complete code appendix equals runnable source: '+filename,got==expected)
check('Worked mean/median ratio narrative matches workbook arithmetic',
      'Mean/median − 1 = 0.757902684' in all_text
      and abs((iv.Value.mean()/iv.Value.median()-1)-0.757902684)<1e-9)
check('No stale draft marker, invented grade or unreplaced placeholder',
      all(term not in all_text for term in ['[TABLE_OF_CONTENTS]','TODO','INSERT CHART','guaranteed 90']))
nb=nbformat.read(ROOT/'notebooks/Task4_Online_Retail_Evidence_Based_Analysis.ipynb',as_version=4)
nc=[c for c in nb.cells if c.cell_type=='code']
check('Executed notebook has all code cells run and no error output',len(nc)>=13
      and all(c.execution_count is not None and len(c.outputs)>0 for c in nc)
      and not any(o.output_type=='error' for c in nc for o in c.outputs))
check('Notebook embeds all 15 generated chart outputs',
      sum('image/png' in o.get('data',{}) for c in nc for o in c.outputs)>=15)
required=['README.md','LICENSE','DATA_LICENSE.md','CITATION.cff','requirements.txt',
          'REVIEW_AND_CORRECTIONS.md','SUBMISSION_DESCRIPTION.md','data/source_verification.json',
          'scripts/run_notebook.py','scripts/build_report.py','scripts/format_document.py']
check('Documentation, licences, provenance and reproducibility files present',all((ROOT/p).exists() for p in required))
if (ROOT/'SUBMISSION_DESCRIPTION.md').exists():
    words=len(re.findall(r"\b[\w'-]+\b",(ROOT/'SUBMISSION_DESCRIPTION.md').read_text()))
    check('Separate submission description exceeds 200 words',words>=200,f'{words} words')
check('All distributed Python source parses successfully',all(
      isinstance(ast.parse(p.read_text()),ast.Module) for folder in ['scripts','tests'] for p in (ROOT/folder).glob('*.py')))
secret_pattern=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,})')
scan=[p for folder in ['scripts','tests','reports','outputs','references','docs']
      for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.md','.json','.csv','.txt']]
scan += [p for p in ROOT.iterdir() if p.is_file() and p.suffix in ['.md','.txt','.cff']]
check('No credential patterns in distributed text artifacts',not any(secret_pattern.search(p.read_text(errors='ignore')) for p in scan))

failures=[r for r in RESULTS if r['status']=='FAIL']
summary={'validation_run_at_utc':datetime.now(timezone.utc).isoformat(),'report_date':'2026-11-07','author':'T. Aparna Reddy',
         'source':'direct original Excel re-read; independent calculations',
         'checks':len(RESULTS),'passed':len(RESULTS)-len(failures),'failed':len(failures),
         'official_evaluator_score':None,'report_bytes':report.stat().st_size,
         'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'results':RESULTS}
(R/'QA_REPORT.json').write_text(json.dumps(summary,indent=2))
lines=['# Task 4 — Executed validation','',f"**{summary['passed']}/{summary['checks']} checks passed; {summary['failed']} failed.**",'',
       'This is an executed technical validation, not an official grade or an independent external review.',
       'The raw Excel workbook was re-read directly; the analysis cache was not trusted for numerical verification.','',
       '| Check | Result | Detail |','|---|---|---|']
lines += [f"| {r['check']} | {r['status']} | {r['detail']} |" for r in RESULTS]
(R/'VALIDATION.md').write_text('\n'.join(lines)+'\n')
(R/'SHA256SUMS.txt').write_text(summary['report_sha256']+'  '+report.name+'\n')
print(f"\n{summary['passed']}/{summary['checks']} PASS; {len(failures)} FAIL")
if failures:sys.exit(1)
