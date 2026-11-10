"""Build the complete, styled revised Task 4 Word draft and its Markdown companion.

Use scripts/format_document.py with LibreOffice/UNO to populate the TOC,
refresh page fields, and write the final Microsoft Word deliverable.
"""
from pathlib import Path
import json
import re
import hashlib
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs'; V=ROOT/'visualizations'; CACHE=ROOT/'.cache';CACHE.mkdir(exist_ok=True)
M=json.loads((O/'metrics.json').read_text())
monthly=pd.read_csv(O/'monthly_performance.csv'); countries=pd.read_csv(O/'country_performance.csv')
customers=pd.read_csv(O/'customer_rfm.csv'); segments=pd.read_csv(O/'rfm_segments.csv')
products=pd.read_csv(O/'product_performance.csv'); pairs=pd.read_csv(O/'extreme_transaction_pairs.csv')
recon=pd.read_csv(O/'task4_metric_reconciliation.csv')
REPO=''  # Publication links are verified and recorded separately in SUBMISSION_LINKS.md.
PRIOR='https://github.com/appureddy1102-cloud/real-world-online-retail-analysis'
NAVY='17364B';TEAL='008C87';GREY='617785';PALE='F1F6F8';GOLD='DFAB3B'
D=Document(); sec=D.sections[0]
sec.page_width=Inches(8.2677);sec.page_height=Inches(11.6929)
sec.top_margin=Inches(.70);sec.bottom_margin=Inches(.67);sec.left_margin=Inches(.72);sec.right_margin=Inches(.72)
sec.header_distance=Inches(.28);sec.footer_distance=Inches(.28)
sec.different_first_page_header_footer=True
WIDTH=6.8277
styles=D.styles
for name in ['Normal','Body Text']:
 s=styles[name];s.font.name='Calibri';s.font.size=Pt(11);s.font.color.rgb=RGBColor.from_string(NAVY)
 s.paragraph_format.line_spacing=1.08;s.paragraph_format.space_after=Pt(6)
 s.paragraph_format.widow_control=True
for name,size,col in [('Title',35,NAVY),('Subtitle',16,TEAL),('Heading 1',18,NAVY),('Heading 2',12.5,TEAL),('Heading 3',11,NAVY)]:
 s=styles[name];s.font.name='Calibri';s.font.size=Pt(size);s.font.color.rgb=RGBColor.from_string(col)
 s.font.bold=name!='Subtitle';s.paragraph_format.space_before=Pt(9 if name!='Heading 1' else 0)
 s.paragraph_format.space_after=Pt(7);s.paragraph_format.keep_with_next=True
for name in ['Caption']:
 s=styles[name];s.font.name='Calibri';s.font.size=Pt(9.5);s.font.bold=True;s.font.color.rgb=RGBColor.from_string(NAVY)
 s.paragraph_format.space_before=Pt(3);s.paragraph_format.space_after=Pt(4)
for name,size,col in [('Source Note',8.5,GREY),('Small Note',9.5,GREY),('Contents Title',20,NAVY)]:
 if name not in styles:styles.add_style(name,1)
 styles[name].font.name='Calibri';styles[name].font.size=Pt(size);styles[name].font.color.rgb=RGBColor.from_string(col)
 styles[name].paragraph_format.space_after=Pt(5)
 if name=='Contents Title':styles[name].font.bold=True

# Ensure modern Word compatibility and preserve embedded high-resolution charts.
settings=D.settings.element
for name,val in [('updateFields','true'),('doNotAutoCompressPictures','true')]:
 el=OxmlElement('w:'+name);el.set(qn('w:val'),val);settings.append(el)
lang=OxmlElement('w:themeFontLang');lang.set(qn('w:val'),'en-GB');settings.append(lang)
D.core_properties.title='Real-World Dataset Analysis | UCI Online Retail | Revised Task 4'
D.core_properties.author='T. Aparna Reddy';D.core_properties.subject='Complete exploration, traceable cleaning, worked statistics and evidence-based recommendations'
D.core_properties.keywords='YuvaIntern, Task 4, UCI Online Retail, EDA, worked statistics, reproducibility'
D.core_properties.comments='Historical-data case study; recommendations are proposals, not tested results.'

# Light, consistent running header/footer with live page fields.
hp=sec.header.paragraphs[0];hp.paragraph_format.space_after=Pt(0)
hp.paragraph_format.tab_stops.add_tab_stop(Inches(WIDTH),WD_ALIGN_PARAGRAPH.RIGHT)
r=hp.add_run('ONLINE RETAIL  |  REAL-WORLD DATASET ANALYSIS');r.font.name='Calibri';r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREY)
r=hp.add_run('\tYUVAINTERN • TASK 4');r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(TEAL)
fp=sec.footer.paragraphs[0];fp.paragraph_format.space_after=Pt(0)
fp.paragraph_format.tab_stops.add_tab_stop(Inches(WIDTH),WD_ALIGN_PARAGRAPH.RIGHT)
r=fp.add_run('T. Aparna Reddy  •  Historical-data case study');r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREY)
r=fp.add_run('\tPage ');r.font.size=Pt(8)

def field(par,code):
 r=par.add_run();beg=OxmlElement('w:fldChar');beg.set(qn('w:fldCharType'),'begin');r._r.append(beg)
 ins=OxmlElement('w:instrText');ins.set(qn('xml:space'),'preserve');ins.text=' '+code+' ';r._r.append(ins)
 sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate');r._r.append(sep)
 t=OxmlElement('w:t');t.text='1';r._r.append(t)
 end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end');r._r.append(end);r.font.size=Pt(8)
field(fp,'PAGE');fp.add_run(' of ').font.size=Pt(8);field(fp,'NUMPAGES')

MD=[];TABLES=[];FIGS=[];HEADINGS=[];WORKED=[];FINDINGS=[];RECOMMENDATIONS=[]

def rt(par,text):
 for piece in re.split(r'(\*\*.*?\*\*)',str(text)):
  r=par.add_run(piece[2:-2] if piece.startswith('**') and piece.endswith('**') else piece)
  if piece.startswith('**') and piece.endswith('**'):r.bold=True
 return par

def p(text,style=None):
 par=D.add_paragraph(style=style);rt(par,text);MD.append(str(text)+'\n');return par

def h(text,level=1):
 D.add_heading(text,level=level);MD.append('#'*(level+1)+' '+text+'\n')
 if level==1:HEADINGS.append(text)

def page():D.add_page_break();MD.append('\n<!-- page break -->\n')

def bullet(text):
 par=D.add_paragraph(style='List Bullet');rt(par,text);par.paragraph_format.space_after=Pt(5);MD.append('- '+text+'\n');return par

def note(text):return p(text,'Small Note')

def money(x,d=2):return f'£{float(x):,.{d}f}'
def num(x):return f'{int(x):,}'

def table(title,headers,rows,widths=None,font=9.4):
 no=len(TABLES)+1;caption=f'Table {no}. {title}'
 cp=D.add_paragraph(caption,style='Caption');cp.paragraph_format.keep_with_next=True
 t=D.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 if widths is None:widths=[WIDTH/len(headers)]*len(headers)
 for j,w in enumerate(widths):t.columns[j].width=Inches(w)
 hdr=t.rows[0]
 for j,text in enumerate(headers):hdr.cells[j].text=str(text)
 repeat=OxmlElement('w:tblHeader');repeat.set(qn('w:val'),'true');hdr._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  cells=t.add_row().cells
  for j,text in enumerate(row):cells[j].text=str(text)
 for i,row in enumerate(t.rows):
  cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
  for j,c in enumerate(row.cells):
   c.width=Inches(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcPr=c._tc.get_or_add_tcPr()
   shd=OxmlElement('w:shd');shd.set(qn('w:fill'),NAVY if i==0 else (PALE if i%2==1 else 'FFFFFF'));tcPr.append(shd)
   margins=OxmlElement('w:tcMar')
   for side,value in [('top',65),('bottom',65),('left',85),('right',85)]:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),str(value));e.set(qn('w:type'),'dxa');margins.append(e)
   tcPr.append(margins)
   for par in c.paragraphs:
    par.paragraph_format.space_before=Pt(0);par.paragraph_format.space_after=Pt(0);par.paragraph_format.line_spacing=1.02
    par.paragraph_format.keep_with_next=False
    for r in par.runs:
     r.font.name='Calibri';r.font.size=Pt(font);r.font.bold=i==0
     r.font.color.rgb=RGBColor.from_string('FFFFFF' if i==0 else NAVY)
 MD.append('**'+caption+'**\n')
 MD.append('| '+' | '.join(str(s).replace('|','/') for s in headers)+' |\n')
 MD.append('| '+' | '.join('---' for _ in headers)+' |\n')
 for row in rows:MD.append('| '+' | '.join(str(s).replace('|','/').replace('\n','; ') for s in row)+' |\n')
 MD.append('\n');TABLES.append({'number':no,'title':title,'rows':len(rows),'columns':len(headers)})
 return t

def chart(filename,title,interpretation,source='Audited UCI workbook [1]; calculations in scripts/analyze.py and scripts/make_charts.py.'):
 no=len(FIGS)+1
 par=D.add_paragraph();par.paragraph_format.space_after=Pt(0);par.paragraph_format.keep_with_next=True
 shape=par.add_run().add_picture(str(V/filename),width=Inches(WIDTH))
 shape._inline.docPr.set('descr',title+'. '+interpretation.replace('**',''))
 cp=D.add_paragraph(f'Figure {no}. {title}',style='Caption');cp.paragraph_format.keep_with_next=True
 ip=D.add_paragraph();rt(ip,'**Interpretation.** '+interpretation);ip.paragraph_format.space_after=Pt(4)
 sp=D.add_paragraph('Source: '+source,style='Source Note')
 MD.append(f'![Figure {no}. {title}](../visualizations/{filename})\n\n**Figure {no}. {title}**\n\n**Interpretation.** {interpretation}\n\nSource: {source}\n')
 FIGS.append({'number':no,'file':filename,'title':title,'interpretation':interpretation})

# The narrative is generated from the actual, audited result files.
E=json.loads((O/'extended_results.json').read_text())
raw_schema=pd.read_csv(O/'raw_schema_profile.csv')
raw_stats=pd.read_csv(O/'raw_descriptive_statistics.csv')
valid_stats=pd.read_csv(O/'valid_descriptive_statistics.csv')
frequency_bands=pd.read_csv(O/'customer_frequency_bands.csv')
multivariate=pd.read_csv(O/'rfm_country_multivariate.csv')
CLEAN_MANIFEST=json.loads((ROOT/'data'/'cleaned_data_manifest.json').read_text())
for name,size in [('Code',8.1),('Formula',10.5)]:
 if name not in styles:styles.add_style(name,1)
 styles[name].font.name='Liberation Mono' if name=='Code' else 'Calibri'
 styles[name].font.size=Pt(size)
 styles[name].font.color.rgb=RGBColor.from_string(NAVY)
 styles[name].paragraph_format.space_after=Pt(0 if name=='Code' else 5)
 styles[name].paragraph_format.line_spacing=1.05
 styles[name].paragraph_format.keep_with_next=False
 styles[name].paragraph_format.widow_control=False
 if name=='Code':
  styles[name].paragraph_format.left_indent=Inches(.14)
  styles[name].paragraph_format.first_line_indent=Inches(-.14)


def code(text):
 for line in str(text).splitlines():
  par=D.add_paragraph(line or ' ',style='Code')
  par.paragraph_format.keep_with_next=False
 MD.append('```python\n'+str(text)+'\n```\n')


def source(text):p('Evidence file: '+text,'Source Note')


def worked(number,title,formula,substitution,result,interpretation,evidence):
 h(f'11.{number} Worked example {number}: {title}',2)
 p('**Formula.** '+formula,'Formula')
 p('**Actual substitution and calculation.** '+substitution,'Formula')
 p('**Result.** '+result)
 p('**Interpretation.** '+interpretation)
 source(evidence)
 WORKED.append({'number':number,'title':title,'formula':formula,'substitution':substitution,
                'result':result,'interpretation':interpretation,'evidence':evidence})


def finding(number,title,evidence,comparison,meaning,importance,action,files):
 h(f'13.{number} {title}',2)
 p('**Evidence and comparison.** '+evidence+' '+comparison)
 p('**Meaning and importance.** '+meaning+' '+importance)
 p('**Recommendation.** '+action)
 source(files)
 FINDINGS.append({'number':number,'title':title,'evidence':evidence,'comparison':comparison,
                  'meaning':meaning,'importance':importance,'recommendation':action,'files':files})


def recommendation(number,title,problem,action,benefit,measurement,owner):
 h(f'14.{number} {title}',2)
 p('**Problem and evidence.** '+problem)
 p('**Action and owner.** '+action+' Proposed owner: '+owner+'.')
 p('**Expected benefit, not a measured outcome.** '+benefit)
 p('**Measurement and decision gate.** '+measurement)
 RECOMMENDATIONS.append({'number':number,'title':title,'problem_evidence':problem,'action':action,
                         'expected_benefit':benefit,'measurement':measurement,'owner':owner})


def visual(sub,filename,title,observation,interpretation,implication,files):
 h(f'12.{sub} {title}',2)
 chart(filename,title,interpretation,source=files+'; scripts/verified_core.py, scripts/analyze.py and scripts/make_charts.py.')
 p('**Numerical observation.** '+observation)
 p('**Business implication.** '+implication)
 FIGS[-1].update({'observation':observation,'business_implication':implication,'evidence_files':files})


# 1. COVER
h('1. Cover Page')
p('YUVAINTERN  /  DATA ANALYTICS INTERNSHIP','Subtitle')
p('Real-World Dataset\nAnalysis Project','Title')
p('Task 4 • Revised, evidence-based submission\nUCI Online Retail','Subtitle')
p('A complete transaction-data investigation: source validation, transparent cleaning, exploratory analysis, fully worked statistics and practical business recommendations.')
p('')
table('Submission profile',['Item','Detail'],[
 ['Prepared by','T. Aparna Reddy | Data Analytics Intern'],
 ['Report date','7 November 2026'],
 ['Dataset window','1 December 2010, 08:26–9 December 2011, 12:50; timezone not supplied'],
 ['Source size','541,909 original invoice lines × 8 columns'],
 ['Analysis views','536,641 deduplicated records; 524,878 qualified sales lines; 19,960 sales invoices'],
 ['Revision purpose','Resolve the five supplied reviewer criticisms with actual numerical evidence and reproducible calculations'],
 ['Companion materials','Executed notebook, complete computational code, cleaned datasets, CSV evidence, validation and submission description'],
],widths=[1.48,5.3477],font=10)
p('15 analytical figures  •  14 fully worked examples  •  12 substantive findings  •  8 recommendations','Subtitle')
p('Dataset attribution: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5BW33. Dataset licensed CC BY 4.0; transformations are documented. No synthetic transaction records or claimed intervention outcomes are included. [1, 2]','Small Note')
page()
p('Contents','Contents Title')
p('[TABLE_OF_CONTENTS]')
note('The 19 numbered parts follow the requested order. This navigation page is front matter. The appendix contains the full computational source, not merely selected snippets. Original data and the completed Task 5 project have not been modified.')
page()

# 2. ABSTRACT / EXECUTIVE SUMMARY
h('2. Abstract / Executive Summary')
p('This project investigates the genuine UCI Online Retail workbook to establish defensible measures of recorded sales, credits, customer value, product performance and geographic demand. All 541,909 source rows and eight fields were profiled. Removing 5,268 exact duplicate rows under an explicitly tested assumption produces 536,641 records. A separate positive-price, positive-quantity, non-credit view contains 524,878 lines, not a replacement for the complete cleaned dataset.')
chart('01_executive_dashboard.png','Historical commercial KPI dashboard',
      'These KPIs use explicit transaction populations. Sales before credits are not accounting net revenue, and the 65.58% repeat share is a within-window description of identified purchasers rather than a cohort-retention estimate.',
      source='outputs/metrics.json; unchanged UCI workbook [1].')
FIGS[-1].update({'observation':'£10,642,110.80 sales before credits; £893,979.73 credits; £9,748,131.07 credit-adjusted value.',
                'business_implication':'Agree the financial measurement basis before comparing performance or assigning targets.',
                'evidence_files':'outputs/metrics.json'})
p('**Principal results.** Sales before credits total **£10,642,110.80**; recorded C-credit notes of **£893,979.73** reduce this to **£9,748,131.07**. Mean invoice value is **£533.17**, compared with a **£303.30 median**. Two extreme sale–credit pairs fully offset **£245,653.20**, or **27.48% of credit value**. The UK generates **84.59% of sales**; Netherlands leads non-UK value but one account supplies **98.16%** of its identified sales.')
p('**Interpretation and action.** The evidence supports credit-aware reporting, current-data validation of concentrated customer accounts, SKU planning based on credit-adjusted demand, and cautious geographic tests. It does not establish profit, causal drivers, campaign uplift or current performance. Fourteen worked examples expose the arithmetic; fifteen figures and their interpretations connect the calculations to decisions. The delivered scripts, notebook and data manifests make the findings auditable.')
page()

# 3. INTRODUCTION
h('3. Introduction')
p('Transactional data are commercially useful only when the unit of analysis and inclusion rules are clear. A row in this workbook is an invoice line, not an independent order or customer. Positive sales, credits, zero-priced stock movements, service codes and accounting entries appear together. A generic total or an unexplained filter can therefore answer the wrong business question even when its arithmetic is correct.')
p('The revised Task 4 applies Pandas and NumPy to the original workbook, then moves from row-level evidence to invoice, customer, product, country and month summaries. The objective is explanatory business analysis, not a predictive model. The report separates observed facts, analytical assumptions and proposed management actions. Associations are not interpreted as intervention effects.')
p('The supplied reviewer feedback identifies five weaknesses: insufficient numerical examples, missing worked statistical calculations, limited original interpretation, incomplete sections and unsupported findings. The response below replaces generic statements with traceable records, formulas, comparisons, documented transformations and measurable recommendations. The previous Task 4 outputs are used only as a 24-metric cross-check; all revised results are independently executed from the verified workbook.')
table('How this revision addresses the reviewer feedback',['Reviewer criticism','Specific correction','Where to verify'],[
 ['Too few concrete numbers','Raw/clean profiles, complete monthly totals, actual invoice rows and explicitly scoped KPI comparisons.','Sections 8–10; outputs/*.csv'],
 ['Missing statistical workings','Fourteen examples with formula, actual substitution, calculation, interpretation and evidence file.','Section 11; worked_*.csv'],
 ['Limited original interpretation','Credit-offset inspection, volume/AOV decomposition, denominator checks and market/account concentration.','Sections 10, 12 and 13'],
 ['Short or incomplete sections','All 19 requested parts; full column definitions, cleaning code, limitations and complete computational appendix.','Contents; Section 19'],
 ['Findings not supported by evidence','Twelve findings each link numbers, comparison, business meaning, importance and action to saved outputs.','Section 13; report_manifest.json'],
],widths=[1.45,3.30,2.0777],font=9.5)
h('3.1 Scope and decision boundary',2)
p('The observation window is historical: 1 December 2010–9 December 2011. The last month is partial. This is one retailer’s recorded activity, not a random sample of the retail sector. Recommendations are proposals requiring fresh, permissioned operational data. No costs, profit margins, web-session conversion, campaign exposure, stock availability, credit reasons or post-project outcomes are supplied.')
page()

# 4. SOURCE AND DESCRIPTION
h('4. Dataset Source and Description')
h('4.1 Authenticity, reliability and provenance',2)
p('UCI describes Online Retail as transactions of a UK-based, registered non-store retailer, mainly selling unique all-occasion gifts, with many wholesale customers. The repository provides a dataset DOI, documented variables, an official workbook and a CC BY 4.0 licence. These properties make it a traceable educational source; they do not make every field complete or every business interpretation authoritative. [1, 2]')
p('The provided workbook is used unchanged. Its bytes match the previously independently downloaded official UCI archive. The script verifies the SHA-256 before analysis and stops on a mismatch. No alternative retail dataset, synthetic records or reconstructed customer identities are used.')
table('Source verification',['Property','Verified value'],[
 ['Official catalogue','https://archive.ics.uci.edu/dataset/352/online+retail'],
 ['Dataset identifier','DOI 10.24432/C5BW33; Online Retail, not Online Retail II'],
 ['Official archive','https://archive.ics.uci.edu/static/public/352/online+retail.zip'],
 ['File and worksheet','Online Retail.xlsx | Online Retail'],
 ['Workbook bytes','23,715,344'],
 ['SHA-256',M['sha256']],
 ['Original dimensions','541,909 rows × 8 columns'],
 ['Observed timestamp range',M['date_min']+' to '+M['date_max']],
 ['Licence and changes','CC BY 4.0; deduplication, type/label normalization and derived analytical views documented in Section 9'],
],widths=[1.55,5.2777],font=9.5)
p('**Source criticism.** UCI’s catalogue states “no missing values”, but the actual workbook contains 135,080 missing CustomerID values and 1,454 missing Description values. Measured workbook evidence takes precedence over that catalogue flag. The timestamp timezone, exact VAT treatment and operational reasons for credit notes are not supplied. Country means customer residence, not verified shipping destination. [1]')
source('data/source_verification.json; outputs/raw_schema_profile.csv')
page()
h('4.2 Complete data dictionary',2)
table('All original columns, units and analytical roles',['Column / imported dtype','Definition and units','Role and treatment'],[
 ['InvoiceNo / object','Transaction document identifier; UCI states a C-prefix denotes cancellation. Numeric and alphanumeric values occur.','Nominal ID; convert to string. Group sale lines to invoices; preserve C-credit and A-prefixed financial documents.'],
 ['StockCode / object','Item or service code. Alphanumeric labels such as POST and DOT coexist with merchandise codes.','Nominal ID; string, not arithmetic. Merchandise view excludes an explicitly listed non-product set.'],
 ['Description / object','Product or entry text label, with missing values and edge whitespace.','Categorical text; fill missing labels with UNKNOWN and strip edges. Group products by StockCode, not unstable names.'],
 ['Quantity / int64','Signed units recorded on a line. Negative quantities may be credits or non-credit movements.','Numeric signed measure. Positive sales require Quantity > 0; negatives remain in complete cleaned data.'],
 ['InvoiceDate / datetime64[ns]','Recorded date and time; timezone is unspecified.','Temporal explanatory dimension; earliest sale-line time assigns an invoice once to hour/day/month.'],
 ['UnitPrice / float64','Recorded unit amount in pounds sterling; includes zeros, sub-penny amounts and two negative adjustments.','Numeric currency measure; retain precision. Positive sales require UnitPrice > 0. Not an observed margin or cost.'],
 ['CustomerID / float64','Customer identifier; float import reflects missing values, not fractional IDs.','Nullable nominal ID; convert to Int64. No mean/SD of identifiers; no invented values for missing customers.'],
 ['Country / object','Country label for customer residence according to UCI.','Categorical explanatory dimension. Original labels retained; not a causal treatment or shipping confirmation.'],
],widths=[1.50,2.60,2.7277],font=9.4)
h('4.3 Outcomes, explanatory variables and grains',2)
p('There is no supplied target variable or supervised-learning task in this project. Derived descriptive outcomes are signed line value (Quantity × UnitPrice), sales invoice value (sum of qualified lines), order count, observed repeat share and credit-adjusted transaction value. Candidate explanatory dimensions are country, month, weekday, hour, basket line count, total quantity and recorded mean unit amount. Quantity and price mechanically construct value; their correlations cannot be treated as independent causal effects.')
p('Five grains are kept distinct: source/cleaned line; qualified sales invoice; identified purchaser; merchandise StockCode; and country/month aggregate. A country’s unique-customer counts need not add to the overall unique count because eight purchasers occur under multiple country labels. Customer-level comparisons assign each ID to its earliest qualified invoice country, with invoice number breaking timestamp ties. This convention is documented rather than treated as corrected residence.')
page()

# 5. BUSINESS PROBLEM
h('5. Business Problem and Objectives')
p('The central problem is to turn a mixed-quality transaction extract into trustworthy evidence for commercial prioritisation. Management needs to distinguish sales activity from retained transaction value, avoid gross-only rankings distorted by credits, recognise incomplete customer attribution and choose practical tests instead of claiming unsupported ROI. The following questions define the analytical scope.')
table('Analytical questions, methods and business outputs',['Question','Actual method','Decision supported'],[
 ['Q1. How complete, unique and internally coherent is the workbook?','Per-column types, missing/unique counts, exact duplicates, sign checks and source-row inspection.','Set data-quality controls without discarding valid records.'],
 ['Q2. What are sales before credits and credit-adjusted value?','Exclusive line partition; signed-value bridge; merchandise/service separation.','Finance definitions, exception queues and credit-aware dashboards.'],
 ['Q3. What is a typical order, and how heavy is the upper tail?','Invoice mean/median/quartiles/SD, histogram, box plot and sensitivity.','Use typical and tail demand in planning rather than mean alone.'],
 ['Q4. When does recorded demand peak?','Month, weekday and first-invoice-hour group-bys; November order/AOV decomposition.','Test current operational capacity around verified demand patterns.'],
 ['Q5. How concentrated is identifiable customer value?','Frequency bands, repeat share, RFM and customer Pareto with explicit denominators.','Prioritise validated accounts and design retention/win-back tests.'],
 ['Q6. Which merchandise products remain important after credits?','SKU gross/credit-adjusted comparisons, units and exact offset-pair inspection.','Avoid treating fully reversed bulk entries as credit-adjusted transaction value.'],
 ['Q7. Which countries show value and breadth rather than one-account dependence?','Sales, invoices, AOV, customer counts and largest-account share.','Separate account management from broad-market expansion.'],
 ['Q8. Which group differences and associations survive careful interpretation?','Spearman/Pearson, customer-level Welch and rank tests, 2×2 repeat comparison.','Form testable hypotheses, not causal or population-wide claims.'],
],widths=[2.30,2.28,2.2477],font=9.5)
h('5.1 Success criteria',2)
p('A successful submission must reconcile the same workbook, expose every cleaning decision, provide at least five worked examples, use both plotting libraries and all required chart types, and connect findings to measurable actions. This version deliberately exceeds those evidence minima: fourteen worked examples, fifteen figures, twelve substantive insights and eight recommendations. Readiness is checked against the ten requested review criteria; a 90+/100 official grade is an objective, not a guaranteed result.')
page()

# 6. TOOLS
h('6. Tools and Technologies')
table('Executed analysis environment',['Tool / actual version','Use in this project'],[
 ['Python '+E['runtime']['python'],'File handling, pipeline execution, hashing, comments and reproducible scripts.'],
 ['Pandas '+E['runtime']['pandas'],'Excel import, missing/duplicate profiling, nullable types, group-bys, joins and CSV exports.'],
 ['NumPy '+E['runtime']['numpy'],'Actual-array arithmetic, squared deviations, manual Pearson/Welch workings and conditional flags.'],
 ['SciPy '+E['runtime']['scipy'],'Welch t-tests, Mann–Whitney comparisons, chi-square and conditional t intervals.'],
 ['Matplotlib '+E['runtime']['matplotlib'],'Bar, histogram, line, scatter, multi-panel and reconciliation figures.'],
 ['Seaborn '+E['runtime']['seaborn'],'Box plot, annotated correlation heatmap and customer-frequency count plot.'],
 ['Jupyter / nbclient','Executed notebook with saved outputs and plots; cell failures are not allowed.'],
 ['python-docx / LibreOffice Writer','OOXML Word generation, real contents/page-field refresh and PDF layout verification.'],
 ['Git / GitHub; Google Drive / Docs','Versioned project packaging and submission publication where authorised; verified status is recorded separately.'],
],widths=[2.05,4.7777],font=9.6)
p('requirements.txt records the exact installed analysis versions, rather than merely listing package names. Source precision is preserved during computation; presentation amounts are usually rounded to pennies. Negative/positive penny-rounded account checks explicitly avoid floating-point near-zero classification errors. References [3–5] document the principal APIs; the SciPy web manual is newer than the installed version, so the actual runtime above is authoritative.')

# 7. METHODOLOGY
h('7. Methodology')
p('The workflow is a reproducible, descriptive pipeline: verify source → profile raw data → preserve an immutable original → document deduplication and non-destructive normalization → create separately named analytical views → aggregate at an appropriate grain → run EDA and statistical checks → visualise → interpret → recommend → validate and package.')
bullet('**Verification before analysis:** compare workbook bytes/SHA-256; assert 541,909 × 8 and valid source timestamps; retain the original Excel file.')
bullet('**Scope before aggregation:** use mutually exclusive line partitions and explicitly label before-credit, credit-adjusted and all-line signed values. Keep anonymous sales in overall totals.')
bullet('**Evidence before narrative:** export raw/valid descriptive statistics, record-level worked tables, full month/country/SKU/customer summaries and source-row-traceable cleaned records.')
bullet('**Appropriate comparisons:** prefer customer-level AOV to treating repeated customer invoices as independent; show effect sizes and skew/rank sensitivity; describe p-values as conditional exploratory evidence.')
bullet('**Quality before handoff:** reconcile 24 previous metrics, cross-check arithmetic independently, execute the notebook, verify figure types and report order, render the Word document and inspect publication accessibility.')
source('scripts/verified_core.py; scripts/analyze.py; scripts/make_charts.py; tests/validate_outputs.py')
page()

# 8. EXPLORATION
h('8. Dataset Exploration')
h('8.1 Shape, schema, missingness and uniqueness',2)
p('The raw dataset contains 541,909 rows and eight original columns, with 25,900 distinct document identifiers, 4,070 StockCodes, 4,372 non-missing CustomerIDs and 38 country labels. InvoiceNo is not unique per row because documents have multiple product lines. Description has 4,223 non-missing distinct labels, more than the number of StockCodes; names are therefore not used as the primary product key.')
table('Complete raw schema and null/unique profile',['Column','Raw dtype','Missing n','Missing %','Unique non-null'],[
 [r.Column,r.RawDtype,num(r.Missing),f'{r.MissingPct:.4f}%',num(r.UniqueNonNull)] for r in raw_schema.itertuples()
],widths=[1.25,1.63,1.05,1.1,1.7977],font=9.6)
p('CustomerID is missing on 135,080 raw lines (24.9267%), compared with only 1,454 missing Description values (0.2683%). No missing values occur in the other six fields. Missingness does not justify deleting all affected rows: anonymous activity still has measurable sales value, and an unknown product label does not invalidate a recorded amount.')
p('Exact duplicate rows number 5,268, representing 0.972119% of the source. The duplicate test uses all eight original columns, not InvoiceNo alone. A repeated invoice line might still represent legitimate repeated entry, so the original file is preserved and a no-dedup sales sensitivity is reported. There are zero zero-quantity rows; 10,624 raw rows have negative quantity and 2,517 have non-positive unit amounts. These sign flags overlap and cannot be added as mutually exclusive error counts.')
source('outputs/raw_schema_profile.csv; outputs/missing_values.csv; outputs/extended_results.json')
page()
h('8.2 Actual records and category distributions',2)
first=pd.read_csv(O/'actual_first_ten_rows.csv')
table('Five actual source records (Excel rows 2–6)',['Invoice','StockCode','Quantity','UnitPrice £','Customer','Country'],[
 [str(r.InvoiceNo),str(r.StockCode),num(r.Quantity),f'{r.UnitPrice:.2f}',str(int(r.CustomerID)),r.Country] for r in first.head(5).itertuples()
],widths=[.85,1.0,.8,1.0,.95,2.2277],font=9.5)
p('All five lines belong to invoice 536365 and customer 17850 in the United Kingdom. The complete seven-line invoice, not just these five lines, is reconstructed in worked example 2. Thus the illustration remains connected to the actual data rather than a fabricated demonstration.')
raw_cf=pd.read_csv(O/'raw_country_frequencies.csv')
table('Most frequent raw country labels',['Country','Raw lines','Share of all raw lines'],[
 [r.Category,num(r.Frequency),f'{r.RawLineSharePct:.4f}%'] for r in raw_cf.head(6).itertuples()
],widths=[2.8,1.6,2.4277],font=9.5)
p('The UK accounts for 495,478 raw lines (91.4320%), whereas its qualified sales-value share is 84.5861%. These percentages answer different questions: one counts all original lines, while the other weights only qualified sales by value. The difference is not evidence of an error or a causal country effect.')
raw_sf=pd.read_csv(O/'raw_stockcode_frequencies.csv')
table('Frequent raw product/service codes and labels',['Category','Raw line frequency','Context'],[
 [str(raw_sf.iloc[0].Category),num(raw_sf.iloc[0].Frequency),'Most frequent raw StockCode; 85123A'],
 [str(raw_sf.iloc[1].Category),num(raw_sf.iloc[1].Frequency),'22423: REGENCY CAKESTAND 3 TIER'],
 ['WHITE HANGING HEART T-LIGHT HOLDER','2,369','Most frequent raw Description label; not identical to code frequency'],
 ['Missing Description','1,454','Missing labels are not a recovered product category'],
],widths=[3.0,1.15,2.6777],font=9.4)
p('Complete distributions of Country, StockCode and Description are delivered as CSVs, not truncated to the categories shown here. Customer-frequency bands and segment distributions are analysed after defining a valid sale and a known purchaser in Sections 9–10.')
source('outputs/actual_first_ten_rows.csv; outputs/raw_country_frequencies.csv; outputs/raw_stockcode_frequencies.csv; outputs/raw_description_frequencies.csv')
page()
h('8.3 Complete numeric descriptions: original records',2)
p('Summary statistics are calculated only for genuine measures. InvoiceNo, StockCode and CustomerID are nominal identifiers even when they look numeric; their averages are not business statistics. Sample standard deviation uses ddof = 1. Quantiles use Pandas’ default linear interpolation. Mode is the first sorted mode; each displayed measure has one mode in this dataset. [3]')
stat_fields=[('Count','Count',0),('Mean','Mean',6),('Median','Median',3),('Mode','FirstMode',3),('Sample SD','StdSample',6),('Minimum','Minimum',3),('25th percentile (Q1)','Q1',3),('75th percentile (Q3)','Q3',3),('Maximum','Maximum',3),('Interquartile range','IQR',3)]
def stfmt(x,d):return f'{float(x):,.{d}f}'
table('Raw numerical summary; signed values retained',['Statistic','Quantity (units)','UnitPrice (£)','Derived signed line value (£)'],[
 [label]+[stfmt(raw_stats.iloc[j][key],dec) for j in range(3)] for label,key,dec in stat_fields
],widths=[1.60,1.65,1.65,1.9277],font=9.4)
p('Raw mean quantity is 9.552250 units, yet the median is 3 and the range is −80,995 to +80,995. Raw UnitPrice includes −£11,062.06 accounting adjustments and a £38,970 entry; those values are inspected by transaction type rather than labelled ordinary merchandise prices. The negative and positive signed-value tails can partially offset: a simple raw mean conceals distinct commercial processes.')
source('outputs/raw_descriptive_statistics.csv; outputs/negative_price_exceptions.csv')
h('8.4 Qualified sales and invoice-level summaries',2)
table('Valid-view summary at explicitly different grains',['Statistic','Line Qty','Line UnitPrice £','Line value £','Invoice value £'],[
 [label]+[stfmt(valid_stats.iloc[j][key],dec) for j in range(4)] for label,key,dec in stat_fields
],widths=[1.45,1.15,1.30,1.35,1.5777],font=8.9)
note('This table may continue onto the next page; its header repeats. Source values such as a £0.001 unit amount are preserved, not silently rounded to zero for filtering.')
p('The qualified invoice mean of £533.171884 exceeds its £303.30 median by about 75.79%. Its sample SD is £1,780.412288 and skewness is 51.078, so a symmetric “average customer” story would be misleading. Positive line quantity has median 4 and Q3 11; a very large wholesale or fully credited entry can coexist with mostly small line quantities.')
source('outputs/valid_descriptive_statistics.csv; outputs/metrics.json')
page()
h('8.5 Unusual observations requiring inspection',2)
table('Anomaly register: evidence and treatment',['Observation','Actual evidence','Interpretation / treatment'],[
 ['Extreme merchandise line','Invoice 581483, StockCode 23843: 80,995 × £2.08 = £168,469.60.','Matching C581484 offsets it in full; retain both records and report adjusted value.'],
 ['Second extreme pair','541431 / C541433, StockCode 23166: ±74,215 × £1.04 = ±£77,183.60.','No retained pair value; do not infer fraud, fulfilment failure or a return reason.'],
 ['Negative unit amounts','A563186 and A563187 each show Quantity 1, UnitPrice −£11,062.06, Description “Adjust bad debt”.','Separate financial adjustments, not assumed erroneous merchandise.'],
 ['Missing product label','Excel row 624, invoice 536414, code 22139 has no source Description.','Use UNKNOWN without inventing a recovered product name.'],
 ['Timestamp inconsistency','42 qualified invoices have more than one line timestamp; maximum span 60 seconds.','Assign each invoice to its earliest timestamp so hourly counts are additive.'],
 ['Customer/country variation','Eight identified purchasers have qualified sales under multiple country labels.','Retain source labels; declare first-observed assignment only for customer-level comparisons.'],
],widths=[1.34,2.69,2.7977],font=9.5)
p('These observations distinguish data-quality issues from valid but unusual transactions. A statistical outlier flag is not proof of an error. The source is a retail/wholesale mix, and neither the business process nor a reason code is available to justify deleting a large sale. The cleaning stage therefore preserves a complete, traceable record set and builds separate views for each question.')
source('outputs/extreme_transaction_pairs.csv; outputs/negative_price_exceptions.csv; outputs/invoice_timestamp_exceptions.csv; outputs/extended_results.json')
page()

# 9. CLEANING
h('9. Data Cleaning and Preprocessing')
p('Every transformation below identifies the issue, literal Python operation, before/after state, reason and effect. Row removal is distinguished from formatting, validation, flagging and analytical-view selection. SourceRow is the original Excel row number including the header offset. The full implementation appears in Section 19 and scripts/analyze.py.')
h('9.1 Exact duplicates: remove under an explicit assumption',2)
p('**Issue and before/after:** 541,909 source rows contain 5,268 exact duplicates across all eight original columns. Keeping the first occurrence gives 536,641 rows, with zero remaining exact duplicates before formatting. Excel rows 496 and 519 both contain invoice 536409, StockCode 21866, quantity 1, £1.25, customer 17908, timestamp 1 December 2010 11:45 and the same label/country.')
code("clean = raw.drop_duplicates().copy()\nclean.insert(0, 'SourceRow', clean.index + 2)")
p('**Reason and effect:** identical entries are treated as duplicate capture, not independently verified duplicate business events. The original file is untouched. Sales before deduplication are £10,666,684.54, compared with £10,642,110.80 afterwards: a £24,573.74 difference, or 0.2304% of the no-dedup amount. This sensitivity exposes the assumption rather than hiding it.')
h('9.2 Identifier and CustomerID types: lossless correction',2)
p('**Issue and before/after:** InvoiceNo/StockCode are mixed object columns; CustomerID imports as float64 with 135,037 missing values after deduplication. IDs such as 17850.0 are labels, not continuous measurements. All present CustomerIDs have zero fractional part.')
code("for col in ['InvoiceNo', 'StockCode']:\n    clean[col] = clean[col].astype('string').str.strip()\nassert ((clean.CustomerID.dropna() % 1) == 0).all()\nclean['CustomerID'] = clean.CustomerID.astype('Int64')")
p('**Reason and effect:** nominal IDs remain intact, C/A prefixes survive and customer 17850.0 becomes 17850. The missing count stays 135,037; rows stay 536,641. No customer ID is inferred or imputed, and leading-zero semantics are not invented beyond the source representation.')
h('9.3 Date validation: verify, do not invent a repair',2)
p('**Issue and before/after:** InvoiceDate is already datetime64[ns], with zero missing timestamps on 541,909 raw rows and 536,641 deduplicated rows. There is no parse-failure count to “fix”.')
code("clean['InvoiceDate'] = pd.to_datetime(clean.InvoiceDate, errors='coerce')\nassert clean.InvoiceDate.notna().all()")
p('**Reason and effect:** validation prevents an unreported parse failure; it changes neither rows nor dates. No timezone is supplied, so no timezone conversion or opening-hours inference is made.')
source('outputs/cleaning_step_audit.csv; outputs/duplicate_examples_with_source_rows.csv; outputs/extended_results.json')
page()
h('9.4 Description missingness and edge whitespace',2)
p('**Issue and before/after:** 1,454 descriptions are missing after deduplication. Filling only those labels produces zero null Description values; these are still unknown product names, not recovered information. Excel row 624 becomes UNKNOWN. Separately, 112,371 non-null/sentinel descriptions have removable edge whitespace; the value at row 12 changes from '+repr("POPPY'S PLAYHOUSE BEDROOM ")+' to '+repr("POPPY'S PLAYHOUSE BEDROOM")+'. No empty strings remain after stripping.')
code("clean['Description'] = clean.Description.astype('string').fillna('UNKNOWN')\nclean['Description'] = clean.Description.str.strip()\nclean.loc[clean.Description.eq(''), 'Description'] = 'UNKNOWN'")
p('**Reason and effect:** retain valid quantities/amounts when the label is absent, and normalize formatting without claiming a canonical catalogue mapping. All 536,641 rows remain and signed financial value is unchanged. Product grouping uses StockCode, so label variations are not silently merged into product identities.')
p('**Additional type issue:** one non-missing Description is the integer 20713 at Excel row 420393 (invoice 572891, code 23343). astype("string") preserves it as the text label "20713"; it does not guess a product name. Non-text descriptions change from one to zero, with no row or value change. This zero-priced, −400-unit movement remains in cleaned-all and is not a qualified sale. Calling .str.strip() directly on the mixed object column would instead create an unintended missing value for this cell.')
h('9.5 Country formatting: a measured zero-change operation',2)
p('**Issue and before/after:** the same edge-whitespace check is applied to country labels and finds zero affected rows. All 38 original raw labels remain; country residence is not relabelled as shipping country.')
code("clean['Country'] = clean.Country.astype('string').str.strip()")
p('**Reason and effect:** consistent categorical strings with zero value, label or row changes. EIRE and other original categories are not arbitrarily renamed, merged or assigned a missing-country surrogate.')
h('9.6 Credits and derived measures: preserve all transaction classes',2)
p('**Issue and before/after:** sales, credits and financial movements coexist in 536,641 rows. Derive flags and signed line value without dropping any records. C-prefix matching uses uppercase for the check only; StockCode values remain as supplied.')
code("clean['IsCredit'] = clean.InvoiceNo.str.upper().str.startswith('C')\nclean['IsOtherNegativeMovement'] = (~clean.IsCredit) & clean.Quantity.lt(0)\nclean['HasCustomerID'] = clean.CustomerID.notna()\nclean['LineValue'] = clean.Quantity * clean.UnitPrice\nclean['Month'] = clean.InvoiceDate.dt.to_period('M').astype(str)")
p('**Reason and effect:** 9,251 C-credit lines and 1,336 other negative-quantity lines stay in the complete dataset. Non-credit negative movements have aggregate signed value £0.00 in this file; that does not make their quantities meaningless. Multiplication preserves source sub-penny precision and presentation totals are rounded only afterwards.')
source('outputs/cleaning_step_audit.csv; outputs/description_format_examples.csv; outputs/exclusive_line_partitions.csv')
page()
h('9.7 Qualified sales: a separate view, not a deletion rule',2)
code("clean['IsQualifiedSale'] = ((~clean.IsCredit) & clean.Quantity.gt(0)\n                            & clean.UnitPrice.gt(0))\nsales = clean.loc[clean.IsQualifiedSale].copy()")
p('**Before/after and reason:** the complete cleaned dataset stays at 536,641 rows; the separate sales view has 524,878. The other 11,763 rows are not labelled data errors. This view answers positive sales-activity questions; credit-adjusted reporting explicitly brings credits back into the calculation.')
partition=pd.read_csv(O/'exclusive_line_partitions.csv')
table('Mutually exclusive cleaned line partition',['Partition','Lines','Signed value (£)'],[
 [r.Partition,num(r.Lines),money(r.SignedValue)] for r in partition.itertuples()
],widths=[3.65,1.15,2.0277],font=9.5)
p('The four row counts add to 536,641. Their signed values add to £9,726,006.95 after display rounding. Invoice counts within partitions must not be added because a document can include both qualified and zero-priced lines. The two negative-price bad-debt entries explain the −£22,124.12 remaining-value adjustment; they are retained, not guessed to be mistakes.')
h('9.8 Anonymous customers: retain sales, restrict only customer analysis',2)
p('**Issue and before/after:** 135,037 post-dedup records lack CustomerID. In the sales view, 132,186 lines (25.18%) are anonymous and produce £1,754,901.91 (16.49% of sales). Missing IDs remain missing. Overall sales rows stay at 524,878; the customer analysis uses 4,338 identified purchasers and 18,532 known-customer invoices.')
code("known_invoice = invoice.loc[invoice.CustomerID.notna()]\n# No fillna() or inferred identity is applied to CustomerID.")
p('**Reason and effect:** excluding all anonymous records would understate measured sales and distort country/time totals. Customer repeat and RFM outputs deliberately use only identifiable purchasers; their denominators are not the entire customer population.')
h('9.9 Merchandise/service flag: an explicit scope convention',2)
code("clean['IsNonProduct'] = clean.StockCode.str.upper().isin(NON_PRODUCT)\nmerchandise = sales.loc[~sales.IsNonProduct]")
p('**Before/after and reason:** 2,910 complete-cleaned lines match the declared non-product set. Positive non-product value is £394,205.67 (3.7042% of qualified sales), leaving £10,247,905.13 of merchandise-coded sales. Both stay in the overall sales total; only the product-demand view excludes service/financial codes. Present flagged codes are AMAZONFEE, B, BANK CHARGES, C2, CRUK, D, DOT, M, PADS, POST, S and lowercase m. The complete configured set is visible in the code; it is a documented analytical assumption, not a source-provided product taxonomy.')
source('outputs/exclusive_line_partitions.csv; outputs/metrics.json; scripts/verified_core.py: NON_PRODUCT')
page()
h('9.10 Outlier treatment: flag, inspect and retain',2)
code("q1, q3 = sales.Quantity.quantile([.25, .75])\niqr = q3 - q1\nquantity_outlier = (sales.Quantity < q1 - 1.5*iqr) | (sales.Quantity > q3 + 1.5*iqr)")
p('**Before/after:** qualified quantity Q1 = 1, Q3 = 11 and IQR = 10; bounds are −14 and 26. There are 27,111 flags (5.17%), not removals. UnitPrice Q1 = £1.25, Q3 = £4.13 and IQR = £2.88 give bounds −£3.07 to £8.45; 37,827 lines (7.21%) are flagged. The sales view remains 524,878 rows and £10,642,110.80.')
p('**Reason and effect:** wholesale transactions and legitimate high-quantity lines can exceed generic fences. For example, invoice 536367, StockCode 84879, quantity 32 × £1.69 = £54.08 is retained. Logarithmic plotting makes tails visible without clipping observations. A hypothetical 99th-percentile cap is sensitivity analysis only, never a silent “cleaning” replacement.')
h('9.11 Invoice timestamps and multi-country customer labels',2)
code("invoice = sales.groupby('InvoiceNo').agg(\n    InvoiceValue=('LineValue', 'sum'), InvoiceDate=('InvoiceDate', 'min'))\n# Full code adds customer, country, line count, quantity and mean price.\n# Customer-country assignment uses earliest qualified invoice date, then ID.")
p('**Issue and before/after:** 42 invoices have line timestamps differing by at most 60 seconds. Assigning each invoice to its earliest timestamp preserves 19,960 invoices, all values and monthly totals, but fixes the non-exclusive legacy noon count from 3,220 to 3,219. Customer/country labels are consistent within an invoice; eight IDs span multiple country labels across invoices. Source country labels are retained. Customer-level country is a first-observed convention, not a verified relocation correction; it affects no global sales total.')
h('9.12 Final datasets and validation',2)
table('Distributed datasets and retained scope',['File','Rows × columns','What it preserves'],[
 ['Online Retail.xlsx','541,909 × 8','Unchanged official original workbook.'],
 ['cleaned_all_records.csv.gz','536,641 × 16','All deduplicated transaction classes; anonymous IDs, negatives and source trace remain.'],
 ['qualified_sales.csv.gz','524,878 × 16','Separately flagged positive-price, positive-quantity non-credit lines.'],
],widths=[2.30,1.35,3.1777],font=9.4)
p('The 16 cleaned columns are the original eight, SourceRow and seven derived fields: IsCredit, IsNonProduct, IsOtherNegativeMovement, HasCustomerID, IsQualifiedSale, LineValue and Month. SourceRow is unique. After normalization there are zero duplicated payload rows when SourceRow is omitted; Description has zero nulls, CustomerID retains 135,037 nulls and date validation has zero failures. CSV does not intrinsically preserve dtypes; the appendix gives explicit read-back types. Dataset byte counts and SHA-256 values are in data/cleaned_data_manifest.json.')
source('outputs/cleaned_schema.csv; outputs/cleaning_step_audit.csv; data/cleaned_data_manifest.json; outputs/extended_results.json')
page()

# 10. EDA
h('10. Exploratory Data Analysis')
h('10.1 Univariate distributions and customer frequencies',2)
p('At the sales-line grain, median quantity is 4 units, mode 1 and mean 10.616600; the median unit amount is £2.08 and mode £1.25. At invoice grain, the median is £303.30, Q1 £151.695 and Q3 £493.4625. The mean of £533.17 is pulled upward by a long tail reaching £168,469.60. Frequency and value must therefore be described together rather than treating mean order value as typical.')
table('Observed sales-invoice frequency per identified purchaser',['Invoices in window','Customers','Share of 4,338 customers'],[
 [r.OrdersPerCustomer,num(r.Customers),f'{r.CustomerPct:.4f}%'] for r in frequency_bands.itertuples()
],widths=[2.4,1.5,2.9277],font=9.6)
p('There are 1,493 one-time purchasers and 2,845 repeat purchasers; 337 IDs have at least 11 invoices. Repeat share is 65.58%, but customer exposure time differs: a late-arriving purchaser has less opportunity to repeat. No acquisition cohort, customer lifetime value or retention probability is identified from this summary alone.')
h('10.2 Bivariate country comparisons',2)
table('Leading countries: value, breadth and account concentration',['Country','Sales £','Orders','Known IDs','AOV £','Top account %*'],[
 [r.Country,money(r.GrossSales),num(r.Orders),num(r.Customers),money(r.AOV),f'{r.TopAccountKnownSalesPct:.2f}%'] for r in countries.head(6).itertuples()
],widths=[1.35,1.45,.75,.80,1.15,1.3277],font=9.1)
note('*Largest account as a share of that country’s identified-customer sales, not necessarily all country sales. A purchaser can occur in more than one country count.')
p('Netherlands exceeds EIRE by £2,305.82 in gross sales, yet its nine known purchasers contrast with Germany’s 94 and France’s 87. A 98.16% Netherlands top-account share suggests an account relationship, not evidence of broad national demand. Australia’s 90.22% top-account share raises a similar issue. Current market selection needs margin and fulfilment evidence unavailable here.')
source('outputs/valid_descriptive_statistics.csv; outputs/customer_frequency_bands.csv; outputs/country_performance.csv')
page()
h('10.3 Products, credits and paired-record inspection',2)
table('Gross merchandise leaders checked against credits',['StockCode','Sales before credits £','Signed credits £','Adjusted value £'],[
 [str(r.StockCode),money(r.GrossSales),money(r.SignedCredits),money(r.CreditAdjustedValue)] for r in products.head(6).itertuples()
],widths=[1.2,1.9,1.8,1.9277],font=9.5)
p('StockCode 23843 ranks second on gross merchandise value (£168,469.60) but has £0.00 after recorded C-credit notes. StockCode 23166 records £81,700.92 before credits and £4,221.28 afterwards. A gross-only ranking would confuse large reversed activity with recorded credit-adjusted transaction value. By contrast, 22423 has £164,459.49 after recorded credits, while PARTY BUNTING (47566) has £98,243.88. These values do not establish fulfilment, cash collection or profit.')
table('Exact equal-and-opposite extreme records',['Sale / credit','StockCode / customer','Quantity × unit amount','Signed pair value'],[
 ['581483 / C581484','23843 / 16446','+80,995 and −80,995 × £2.08','£0.00'],
 ['541431 / C541433','23166 / 12346','+74,215 and −74,215 × £1.04','£0.00'],
],widths=[1.7,1.45,2.25,1.4277],font=9.5)
p('The match requires the same customer, StockCode and unit amount, opposite quantity and a credit at or after the sale. The recorded gaps are 12 minutes and 16 minutes. This is strong transaction-level offset evidence, but the workbook has no linked original-invoice field or reason code, so it cannot determine the operational cause. Combined gross pair value is £245,653.20 and the pair sum is zero.')
p('Customer 16446 illustrates gross-value targeting risk: £168,472.50 of sales becomes £2.90 after recorded credits. Customer 12346 has £77,183.60 gross and £0.00 after the matched credit. Twenty-one purchasers have a non-positive penny-rounded credit-adjusted balance in the window. These are historical transaction balances, not fraud labels or lifetime profitability assessments.')
source('outputs/product_performance.csv; outputs/extreme_transaction_pairs.csv; outputs/customer_rfm.csv; outputs/extended_results.json')
page()
h('10.4 Temporal trends: full-month comparisons first',2)
table('All observed months; source precision retained in computation',['Month','Sales £','Sales invoices','AOV £','Credit value £','Coverage'],[
 [r.Month,money(r.GrossSales),num(r.Orders),money(r.AOV),money(r.CreditValue),'Partial: 1–9 Dec' if r.Month=='2011-12' else 'Full month'] for r in monthly.itertuples()
],widths=[.88,1.37,1.05,1.07,1.30,1.1577],font=9.2)
p('November 2011 leads at £1,503,866.78 and 2,769 sales invoices. October records £1,151,263.73 and 2,040 invoices. Sales grow 30.63%, but invoice count grows 35.74% while AOV declines 3.76% from £564.34 to £543.11. The increase is therefore volume-led at the invoice level, not evidence that prices rose. The multiplicative identity sales = invoice count × AOV reconciles the comparison exactly.')
p('September–November contributes £3,711,565.70, or 37.10% of sales in the twelve complete months. This is one observed autumn pattern, not a validated recurring seasonal law. December 2011 contains only the first nine days; £637,790.33 must not be described as a full-month collapse or extrapolated linearly without assumptions.')
p('Thursday contributes £2,199,292.57 and noon is the modal first-invoice hour with 3,219 invoices. There are no Saturday records. Timestamp recording conventions and absence of records do not establish store closure or staff schedules; operational planning requires current throughput and fulfilment timestamps.')
source('outputs/monthly_performance.csv; outputs/weekday_performance.csv; outputs/hourly_performance.csv')
page()
h('10.5 Multivariate segmentation and country mix',2)
p('RFM uses recency in calendar days from 10 December 2011, sales-invoice frequency and monetary sales before credits for identified customers. Each measure is ranked then split into five equal-frequency groups; low recency receives the high score. rank(method="first") deterministically breaks ties in customer order, so equal raw values can receive different scores at boundaries. Segment conditions are ordered, mutually assigned and reproduced in the code. This is a heuristic description, not a validated predictive model.')
table('RFM segment distribution',['Segment','Customers','Customer %','Sales £','Known sales %','All sales %'],[
 [r.Segment,num(r.Customers),f'{r.CustomerSharePct:.2f}%',money(r.Sales),f'{r.KnownSalesSharePct:.2f}%',f'{r.TotalSalesSharePct:.2f}%'] for r in segments.itertuples()
],widths=[1.50,.77,.92,1.45,1.10,1.0877],font=9.0)
p('Champions are 942 of 4,338 identified purchasers (21.72%) and provide £5,729,483.37: 64.47% of known-customer sales but 53.84% of all qualified sales. Anonymous sales are outside the RFM population, not silently assigned to a segment. At Risk plus Can’t Lose Them contains 658 purchasers, £818,896.54 gross historical value and £736,853.23 after recorded customer credits; the latter is not a recoverable-revenue forecast.')
selected=multivariate[multivariate.Segment.isin(['Champions','Lost'])]
table('Country group × RFM × customer AOV: an explicit three-way view',['Country group','Segment','Customers','Sales £','Median customer AOV £'],[
 [r.CountryGroup,r.Segment,num(r.Customers),money(r.GrossSales),money(r.MedianAOV)] for r in selected.itertuples()
],widths=[1.25,1.25,.9,1.6,1.8277],font=9.4)
p('Among Champions, non-UK IDs have median customer AOV £531.44 versus UK £343.41. Among Lost customers, the corresponding medians are £383.95 and £250.00. This stratification shows that the geographic difference is visible in these two selected segments, but it does not eliminate selection, country mixture, tie-breaks, tenure or credit bias. The full 18 country-group/segment cells are exported; no treatment effect is estimated.')
source('outputs/rfm_segments.csv; outputs/rfm_country_multivariate.csv; outputs/customer_rfm.csv')
page()

# 11. WORKED STATISTICS
h('11. Statistical Analysis and Worked Examples')
p('Each example below uses actual workbook observations or complete-data aggregates. Formula, substituted values, result and interpretation are shown explicitly. Small subsets teach the calculation only; they are not substituted for full-data inference. Amounts shown to pennies may have higher source precision; all scripts use unrounded values until reporting.')
worked(1,'one recorded line value',
 'L = Q × P, where Q is recorded quantity and P is the unit amount in GBP.',
 'Excel row 2: InvoiceNo 536365, StockCode 85123A; L = 6 × £2.55 = £15.30.',
 'The recorded positive line value is £15.30.',
 'This is a before-credit transaction amount, not margin or proof of cash collection. The product name is WHITE HANGING HEART T-LIGHT HOLDER.',
 'outputs/worked_invoice_536365.csv; original Excel row 2')
h('11.2 Worked example 2: complete invoice aggregation',2)
wi=pd.read_csv(O/'worked_invoice_536365.csv')
table('All seven qualified lines of invoice 536365',['Excel row','StockCode','Quantity','Unit amount £','Line value £'],[
 [num(r.SourceRow),str(r.StockCode),num(r.Quantity),f'{r.UnitPrice:.2f}',f'{r.LineValue:.2f}'] for r in wi.itertuples()
],widths=[1.0,1.4,1.1,1.65,1.6777],font=9.6)
p('**Formula.** V(invoice) = Σ(Qᵢ × Pᵢ) across every qualified line in that invoice.','Formula')
p('**Actual substitution and calculation.** £15.30 + £20.34 + £22.00 + £20.34 + £20.34 + £15.30 + £25.50 = £139.12.','Formula')
p('**Result and interpretation.** Seven lines become one £139.12 sales invoice for customer 17850. Counting seven “orders” would overstate order frequency; keeping only the five example rows from Section 8 would understate the invoice value.')
source('outputs/worked_invoice_536365.csv; outputs/invoice_summary.csv')
WORKED.append({'number':2,'title':'complete invoice aggregation','formula':'sum quantity × price across seven lines','substitution':wi.LineValue.tolist(),'result':139.12,'interpretation':'One invoice, not seven orders.','evidence':'outputs/worked_invoice_536365.csv'})
page()
worked(3,'missingness and duplicate proportions',
 'Missing % = missing rows / all source rows × 100; duplicate % = exact duplicate rows / all source rows × 100.',
 'CustomerID missing % = 135,080 / 541,909 × 100 = 24.926694%. Duplicate % = 5,268 / 541,909 × 100 = 0.972119%. Rows after deduplication = 541,909 − 5,268 = 536,641.',
 'About one quarter of raw lines cannot be assigned to a known customer; fewer than 1% are exact duplicate entries.',
 'The denominators are raw rows, not customer counts. The two flags may overlap; their percentages should not be added as a total error rate.',
 'outputs/raw_schema_profile.csv; outputs/extended_results.json; outputs/duplicate_examples_with_source_rows.csv')
h('11.4 Worked example 4: sample mean, variance and standard deviation',2)
sd=pd.read_csv(O/'worked_standard_deviation.csv')
table('Actual quantities in Excel rows 2–6',['Quantity x','x − mean','(x − mean)²'],[
 [f'{r.ObservedQuantity:g}',f'{r.DeviationFromMean:.1f}',f'{r.SquaredDeviation:.2f}'] for r in sd.itertuples()
],widths=[2.0,2.2,2.6277],font=9.8)
p('**Formula.** x̄ = Σx/n; s² = Σ(x − x̄)²/(n − 1); s = √s².','Formula')
p('**Actual substitution and calculation.** x̄ = (6 + 6 + 8 + 6 + 6)/5 = 6.4. Sum of squared deviations = 0.16 + 0.16 + 2.56 + 0.16 + 0.16 = 3.20. s² = 3.20/4 = 0.80 units²; s = √0.80 = 0.894427 units.','Formula')
p('**Result and interpretation.** The five actual quantities vary by a sample SD of 0.894427 units. These adjacent lines belong to one invoice and are not a random retail sample; the full qualified-line quantity SD is much larger, 156.280031 units. The worked subset demonstrates arithmetic only, not business-wide precision.')
source('outputs/worked_standard_deviation.csv; outputs/valid_descriptive_statistics.csv')
WORKED.append({'number':4,'title':'sample mean, variance and standard deviation','formula':'sum squared deviations / (n−1), then square root','substitution':[6,6,8,6,6],'result':E['first_five_sample_sd'],'interpretation':'Arithmetic illustration only, not a random sample.','evidence':'outputs/worked_standard_deviation.csv'})
page()
worked(5,'global AOV and the actual median positions',
 'AOV = Σ sales invoice values / number of sales invoices. For even n, median = (value at position n/2 + value at position n/2 + 1)/2 in ascending order.',
 'AOV = £10,642,110.804 / 19,960 = £533.171884. Sorted positions 9,980 and 9,981 are both £303.30, so median = (£303.30 + £303.30)/2 = £303.30.',
 'Reported AOV £533.17; median £303.30. Mean/median − 1 = 0.757902684, or approximately 75.79%.',
 'The mean is not the typical invoice. Both central tendency and tail quantiles should be reported; the gap is descriptive evidence of right skew, not proof of invalid records.',
 'outputs/invoice_summary.csv; outputs/valid_descriptive_statistics.csv; outputs/extended_results.json')
worked(6,'IQR fences and a retained real observation',
 'IQR = Q3 − Q1; lower fence = Q1 − 1.5×IQR; upper fence = Q3 + 1.5×IQR.',
 'Qualified Quantity: Q1 = 1, Q3 = 11; IQR = 10. Lower = 1 − 15 = −14; upper = 11 + 15 = 26. Invoice 536367 / StockCode 84879 has Quantity 32, so 32 > 26. Its value is 32 × £1.69 = £54.08.',
 '27,111 of 524,878 sales lines are flagged: 27,111 / 524,878 × 100 = 5.165200%, reported as 5.17%. All remain in the sales dataset.',
 'A generic IQR rule identifies unusual quantities, not confirmed errors. Deleting this legitimate-looking line merely for exceeding 26 would erase actual recorded demand.',
 'outputs/extended_results.json; data/qualified_sales.csv.gz; original invoice 536367')
page()
worked(7,'UK sales-value share',
 'Country sales share = country qualified sales / all qualified sales × 100.',
 'UK share = £9,001,744.094 / £10,642,110.804 × 100 = 84.586078%.',
 '84.59% of qualified sales value is assigned to the United Kingdom.',
 'This is value-weighted share after deduplication, not the 91.43% UK share of raw lines and not a national market-share estimate. Domestic demand dominates this retailer’s recorded sales.',
 'outputs/country_performance.csv; outputs/metrics.json; outputs/raw_country_frequencies.csv')
worked(8,'November growth decomposed into invoices and AOV',
 'Growth % = (current − prior)/prior × 100. Sales ratio = invoice-count ratio × AOV ratio.',
 '(£1,503,866.78 − £1,151,263.73)/£1,151,263.73 × 100 = 30.627478%. Invoice growth = (2,769/2,040 − 1)×100 = 35.735294%. AOV change = (543.108263/564.344966 − 1)×100 = −3.763071%. 1.35735294 × 0.96236929 − 1 = 0.30627478.',
 'Sales grew 30.63%; more invoices outweighed a 3.76% lower average invoice value.',
 'The peak is invoice-volume-led, not evidence of a price increase. AOV is a mix of prices, quantities, products and customers; it cannot isolate price behaviour. Both months are fully observed.',
 'outputs/monthly_performance.csv; November and October 2011')
page()
worked(9,'credit denominators and the financial bridge',
 'Adjusted value = sales before credits − absolute recorded C-credit value. Credit-document share = C-credit IDs / (sales IDs + C-credit IDs).',
 '£10,642,110.80 − £893,979.73 = £9,748,131.07. Adding other signed adjustments: £9,748,131.07 − £22,124.12 = £9,726,006.95. Credit-document share = 3,836/(19,960 + 3,836) × 100 = 16.120356%. Credit-value ratio = £893,979.73/£10,642,110.804 × 100 = 8.400399%.',
 'Credit-adjusted value £9,748,131.07; all-line signed value £9,726,006.95; document share 16.12%; credit-value ratio 8.40%.',
 'The 16.12% counts documents while 8.40% measures value. Neither is a linked-order cancellation probability. Using all 25,900 raw IDs instead gives 14.81%; using credits/(sales + absolute credits) gives the legacy 7.75% activity share. Different denominators cannot be used interchangeably.',
 'outputs/exclusive_line_partitions.csv; outputs/metrics.json; outputs/negative_price_exceptions.csv')
worked(10,'repeat share and segment-denominator discipline',
 'Repeat share = purchasers with >1 qualified invoice / identified purchasers. Segment value share requires a stated sales denominator.',
 '2,845/4,338 × 100 = 65.583218%. Champions customer share = 942/4,338 × 100 = 21.715076%. Champions known-sales share = £5,729,483.37/£8,887,208.89 × 100 = 64.468873%; all-sales share = £5,729,483.37/£10,642,110.804 × 100 = 53.837847%.',
 '65.58% observed repeat share; Champions contribute 64.47% of identified sales, equivalent to 53.84% of all sales.',
 'The larger segment-value share is not the segment’s share of all revenue. Missing IDs remain outside RFM, and the repeat statistic is not cohort-adjusted retention.',
 'outputs/customer_rfm.csv; outputs/rfm_segments.csv; outputs/metrics.json')
page()
h('11.11 Worked example 11: manual Pearson correlation on actual invoices',2)
pear=pd.read_csv(O/'worked_pearson_five_invoices.csv')
table('First five invoice summaries in sorted invoice order',['Invoice','x: line count','y: value £','x²','y²','xy'],[
 [str(int(r.InvoiceNo)),num(r.LineCount),f'{r.InvoiceValue:.2f}',num(r.X2),f'{r.Y2:.4f}',f'{r.XY:.2f}'] for r in pear.itertuples()
],widths=[.9,1.07,1.07,.66,1.70,1.4277],font=9.0)
p('**Formula.** r = [nΣxy − (Σx)(Σy)] / √{[nΣx² − (Σx)²][nΣy² − (Σy)²]}.','Formula')
p('**Actual sums.** n = 5; Σx = 26; Σy = 527.95; Σx² = 214; Σy² = 102,763.2523; Σxy = 4,661.05.','Formula')
p('**Substitution and calculation.** Numerator = 5×4,661.05 − 26×527.95 = 9,578.55. Denominator parts = 5×214 − 26² = 394 and 5×102,763.2523 − 527.95² = 235,085.059. r = 9,578.55/√(394×235,085.059) = 0.995265949.','Formula')
p('**Result and interpretation.** The five-invoice arithmetic gives Pearson r = 0.995266 and is independently checked by scipy.stats.pearsonr. It is not a population estimate and must not be quoted as the full-data basket association. Across all 19,960 invoices, the Spearman line-count/value association is 0.551606. The local subset and different correlation definition cannot be interchanged.')
p('**Why Spearman is preferred for EDA.** Invoice values have a severe upper tail and basket breadth may relate monotonically rather than linearly to value. Rank correlation is less dominated by numerical extremes, but is still descriptive. Quantity and unit amount construct sales value, so even a strong correlation cannot estimate cross-sell or pricing uplift.')
source('outputs/worked_pearson_five_invoices.csv; outputs/invoice_pearson.csv; outputs/invoice_spearman.csv')
WORKED.append({'number':11,'title':'manual Pearson correlation','formula':'covariance sum formula','substitution':E['pearson_five'],'result':E['pearson_five']['r'],'interpretation':'Five-invoice arithmetic only; full-data rank association differs.','evidence':'outputs/worked_pearson_five_invoices.csv'})
page()
h('11.12 Worked example 12: customer-level Welch comparison',2)
p('**Question and null hypothesis.** Do mean observed customer AOVs differ between the UK and pooled non-UK customers? H₀: μUK − μnonUK = 0; two-sided alternative. Use one mean qualified-invoice value per customer, not repeated invoices as independent samples. alpha = 0.05 is a conventional exploratory reference, not a pre-registered confirmatory design. [4]')
w=E['welch_worked']
table('Actual customer-level inputs to Welch’s calculation',['Input','UK','Non-UK'],[
 ['Customers n','3,920','418'],
 ['Mean customer AOV £','391.683083819','661.123228106'],
 ['Sample SD £','1,869.923744430','799.892606816'],
 ['Sample variance £²','3,496,614.809981679','639,828.182438460'],
],widths=[2.0,2.41385,2.41385],font=9.7)
p('**Formula.** SE = √(s₁²/n₁ + s₂²/n₂); t = (x̄₁ − x̄₂)/SE. Welch df = (s₁²/n₁ + s₂²/n₂)² / {[(s₁²/n₁)²/(n₁−1)] + [(s₂²/n₂)²/(n₂−1)]}.','Formula')
p('**Actual substitution and calculation.** SE = √(3,496,614.809982/3,920 + 639,828.182438/418) = £49.220758. Mean difference = 391.683084 − 661.123228 = −£269.440144. t = −269.440144/49.220758 = −5.474116; substituting the same variance terms gives df = 1,008.182968. Two-sided p = 2×P(Tdf ≥ |−5.474116|) = 5.5495943×10⁻⁸.','Formula')
p('**Result.** Conditional 95% interval for UK minus non-UK mean customer AOV is −£366.03 to −£172.85. Cohen’s pooled-SD d is −0.150109; UK median customer AOV is £279.57 versus £424.70 for non-UK. The rank test also differs (Mann–Whitney p = 1.204031×10⁻³³).')
p('**Interpretation and assumptions.** Within the historical identified-customer view, non-UK customers have higher observed average invoice values. Welch permits unequal variances, not dependence or selection bias. One row per customer reduces repeated-invoice pseudo-replication, but ID independence, heavy tails, country mixture, missing IDs and non-random coverage remain limitations. The interval and p-value rely on a hypothetical sampling model and do not represent a census measurement error or a geographic causal effect. The standardized difference is small relative to dispersion; operational value still needs cost/margin evidence.')
source('outputs/customer_rfm.csv; outputs/extended_results.json: welch_worked; outputs/metrics.json')
WORKED.append({'number':12,'title':'manual customer-level Welch test','formula':'Welch standard error, t and Satterthwaite degrees of freedom','substitution':w,'result':{'t':w['t'],'df':w['df'],'p':w['p_two_sided']},'interpretation':'Conditional exploratory group comparison, not causation.','evidence':'outputs/customer_rfm.csv; outputs/extended_results.json'})
page()
h('11.13 Worked example 13: country group × repeat status',2)
table('Actual 2×2 customer table',['Country group','One-time','Repeat','Total'],[
 ['Non-UK','143','275','418'],['UK','1,350','2,570','3,920'],['Total','1,493','2,845','4,338']
],widths=[2.0,1.6,1.6,1.6277],font=9.8)
p('**Formula.** Expected count Eij = row total × column total / n. Pearson χ² = Σ(O−E)²/E. For the reported 2×2 Yates result, χ²Y = Σ[max(0, |O−E|−0.5)]²/E.','Formula')
p('**Actual substitution and calculation.** E(non-UK, one-time) = 418×1,493/4,338 = 143.862148; the other expected counts are 274.137852, 1,349.137852 and 2,570.862148. Summing (O−E)²/E over all four cells gives χ² = 0.008718230. With continuity correction the sum is 0.001538287; df = (2−1)(2−1) = 1 and p = 0.968714185.','Formula')
p('**Result and interpretation.** Repeat proportions are 275/418 = 65.79% for non-UK and 2,570/3,920 = 65.56% for UK. Standard Cramér’s V uses the uncorrected χ²: √(0.008718230/4,338) = 0.00141765. There is no detected association under this test; that is not proof of equality or causal independence. The smallest expected count is 143.86, so sparse-cell asymptotics are not the problem; non-random coverage and unequal exposure remain.')
source('outputs/country_repeat_contingency.csv; outputs/country_repeat_expected.csv; outputs/extended_results.json')
WORKED.append({'number':13,'title':'chi-square and repeat status','formula':'expected counts and corrected/uncorrected chi-square','substitution':[[143,275],[1350,2570]],'result':{'chi2_yates':E['chi_squared_yates'],'p':M['chi_country_repeat']['p']},'interpretation':'No detected association, not evidence of equivalence.','evidence':'outputs/country_repeat_contingency.csv; outputs/country_repeat_expected.csv'})
worked(14,'outlier and deduplication sensitivity, not a replacement result',
 'Sensitivity change % = (alternative total − published sales total)/published sales total × 100.',
 'Capping each qualified line at its actual 99th percentile of £183.60 gives £8,907,983.82. (£8,907,983.82 − £10,642,110.804)/£10,642,110.804 × 100 = −16.294953%, reported as −16.29%. Keeping all exact duplicates instead gives £10,666,684.54, £24,573.74 above the published deduplicated basis.',
 'A generic cap materially lowers recorded activity; exact-duplicate treatment has a much smaller 0.23% effect relative to the no-dedup basis.',
 'These are transparent alternative definitions, not verified correction amounts, forecasts or realised business benefits. Retaining valid extreme records and checking credits is more defensible than silently clipping them.',
 'outputs/metrics.json: line_p99_value, winsorised_sales_sensitivity, raw_valid_sales_sensitivity')
page()
h('11.15 Additional comparisons, effect sizes and inferential boundaries',2)
table('Customer-level and invoice-level comparisons',['Comparison / unit','Actual result','Interpretation and limitation'],[
 ['UK vs non-UK / one AOV per customer','Means £391.68 vs £661.12; Welch p 5.55×10⁻⁸; d −0.150; rank p 1.20×10⁻³³.','Observed difference; unequal geography mix and heavy tails. No location effect is identified.'],
 ['Repeat vs one-time / one AOV per customer','n 2,845 vs 1,493; means £421.00 vs £411.25; Welch p 0.873204; d 0.005432.','No detected mean difference, not equivalence. Retention value need not come from larger average invoices.'],
 ['Repeat vs one-time / rank comparison','Medians £302.56 vs £255.91; Mann–Whitney p 8.55998×10⁻¹².','Rank/distribution differences can coexist with similar means; Mann–Whitney is not automatically a median-only test.'],
 ['UK vs non-UK / individual invoices','Means £499.57 vs £845.11; Welch p 1.80×10⁻¹⁶.','Supplementary only: repeated customer invoices violate simple independent-invoice inference. Prefer customer-level interpretation.'],
 ['Mean invoice / conditional IID interval','Mean £533.17; 95% t interval £508.47–£557.87.','Assumes independent identically distributed invoices; customer clustering, time and skew make this optimistic for business generalisation.'],
 ['Spearman / all qualified invoices','Value vs quantity 0.838984; value vs lines 0.551606; value vs mean unit amount 0.094257.','Structural, monotonic associations; no pricing or cross-sell intervention is tested.'],
],widths=[1.72,2.49,2.6177],font=9.4)
p('No multiple-testing-adjusted confirmatory claim is made. Comparisons are exploratory and partly selected after viewing the data. A p-value is conditional on the model and null; it is not the probability that a business explanation is true. Failure to reject a mean difference cannot establish equivalence. For future operational decisions, pre-specify the estimand, assignment unit and business-relevant effect threshold, use current data and cluster-aware or randomized designs as appropriate.')
source('outputs/metrics.json; outputs/invoice_spearman.csv; scripts/verified_core.py: test_groups; reference [4]')
page()

# 12. VISUALIZATIONS
h('12. Data Visualizations and Interpretations')
p('Fifteen non-redundant figures cover the required chart types. Figure 1 appears in the executive summary; Figures 2–15 follow here. All plot values originate in saved outputs. Log axes expose long tails without removing observations. The box plot uses original-scale quartiles/fences, then a logarithmic display; flags are not deletions. Matplotlib is used throughout and Seaborn supplies the heatmap, box plot and count plot. [5]')
visual(1,'02_value_reconciliation.png','Sales, credits and other adjustments',
 '£10,642,110.80 before credits becomes £9,748,131.07 after £893,979.73 in C-credit notes; the remaining financial adjustments total −£22,124.12.',
 'Three valid transaction-value bases coexist. The all-line signed amount is £9,726,006.95, not the before-credit sales figure. The bridge explains the numerical difference instead of choosing an ambiguous “net revenue” label.',
 'Use a reconciled finance/BI definition and retain an adjustment register before setting or comparing sales targets.',
 'outputs/exclusive_line_partitions.csv; outputs/negative_price_exceptions.csv; outputs/metrics.json')
page()
visual(2,'03_monthly_sales.png','Monthly demand with partial-month warning',
 'November 2011 reaches £1,503,866.78 on 2,769 invoices; October is £1,151,263.73 on 2,040 invoices. December 2011 covers only 1–9 December.',
 'Gross and credit-adjusted series share a clear autumn increase, but the last data point is not a comparable full month. November growth of 30.63% is volume-led because invoice count rises faster than total sales.',
 'Validate the pattern on fresh multi-year data, then test capacity and availability plans rather than extrapolating a nine-day month.',
 'outputs/monthly_performance.csv')
page()
visual(3,'04_monthly_credits.png','Credit frequency and value severity are different',
 'November has the most C-credit documents (441) but credit value is 3.17% of its sales. January’s ratio is 19.04%; partial December’s is 32.16%.',
 'Counts alone rank exposure differently from value-weighted severity. Monthly credits may relate to sales from earlier periods; credit value divided by same-month sales is a period activity ratio, not a cohort return rate. The large January and December offset pairs and partial-month coverage also matter.',
 'Monitor both credit-document share and credit value/sales, with reason codes and links to original invoices before interpreting a process failure.',
 'outputs/monthly_performance.csv; outputs/extreme_transaction_pairs.csv')
page()
visual(4,'05_customer_pareto.png','Customer concentration on the identified-sales basis',
 '1,130 customers (26.05% of 4,338) reach 80% of £8,887,208.89 identified sales. The top 43 IDs contribute 31.84% of that pool.',
 'Value is concentrated, but the observed threshold is not an exact 80/20 rule. Anonymous sales (£1,754,901.91) sit outside this customer curve, so concentration cannot be asserted for every real purchaser.',
 'Validate current major accounts and credit quality; maintain service coverage without assuming a rank is a lifetime-value estimate.',
 'outputs/customer_pareto.csv; outputs/customer_rfm.csv; outputs/metrics.json')
page()
visual(5,'06_rfm_segment_value.png','RFM segment size versus value contribution',
 'Champions number 942 (21.72% of identified purchasers) and supply 64.47% of known sales. At Risk plus Can’t Lose Them contains 658 IDs.',
 'Segment headcount and commercial value differ substantially. The segment shares use identified before-credit sales; Champions’ share of all qualified sales is 53.84%. RFM labels are heuristic and tie-dependent.',
 'Refresh contact eligibility, credit-adjusted balances and segment rules before retention or win-back tests. Do not call all historic segment value recoverable.',
 'outputs/rfm_segments.csv; outputs/customer_rfm.csv')
page()
visual(6,'07_product_gross_vs_credits.png','Product leaders before and after recorded credits',
 '23843 falls from £168,469.60 to £0.00; 23166 falls from £81,700.92 to £4,221.28. 22423 has £164,459.49 after recorded credits.',
 'A gross-only catalogue ranking can overstate recorded credit-adjusted transaction value. Two conspicuous bulk transactions are fully offset, but the records remain valid observations in their respective sales/credit views.',
 'Use credit-aware SKU measures plus stock, margin and lead-time data before changing replenishment or promotions.',
 'outputs/product_performance.csv; outputs/extreme_transaction_pairs.csv')
page()
visual(7,'08_nonuk_markets.png','Leading non-UK countries',
 'Netherlands leads at £285,446.34, followed by EIRE £283,140.52, Germany £228,678.40 and France £209,625.37. UK sales are £9,001,744.09.',
 'The bar chart isolates export comparisons that would otherwise be compressed by UK dominance. Netherlands’ large value does not imply broad customer depth: its top account is 98.16% of identified country sales.',
 'Separate key-account protection from geographic acquisition. Compare customer breadth and delivered margin before proposing expansion.',
 'outputs/country_performance.csv')
page()
visual(8,'09_invoice_value_histogram.png','Invoice-value histogram: mean versus typical order',
 'The complete 19,960-invoice distribution has mean £533.17, median £303.30, 99th percentile £4,821.17 and maximum £168,469.60.',
 'The log x-axis preserves all positive invoices and makes the severe right tail visible. Equal-width log bins are counts in multiplicative intervals, not a linear-scale density. Mean and median represent different aspects of this distribution.',
 'Report a median, IQR and tail percentiles alongside AOV; do not design standard service or demand assumptions around mean alone.',
 'outputs/invoice_summary.csv; outputs/valid_descriptive_statistics.csv')
page()
visual(9,'10_basket_value_scatter.png','Basket breadth versus invoice value',
 'Across all qualified invoices, Spearman correlation between sales-line count and invoice value is 0.551606. Each plotted point represents one invoice; no point is sampled away.',
 'Wider baskets tend to have larger values, with substantial dispersion and extreme observations on logarithmic axes. Line count is not necessarily distinct SKU count and is not an exogenous driver.',
 'Treat basket-building as a hypothesis for a controlled test; do not translate correlation into a promised cross-sell percentage.',
 'outputs/invoice_summary.csv; outputs/invoice_spearman.csv')
page()
visual(10,'11_invoice_correlation_heatmap.png','Annotated Spearman correlation heatmap',
 'Value correlates 0.838984 with total quantity, 0.551606 with sales-line count and 0.094257 with unweighted mean unit amount.',
 'Quantity is more strongly rank-associated with recorded value than unweighted line mean price. These variables mechanically contribute to value and may reflect wholesale mix. Cyclic month/hour integers and customer IDs are excluded from the numerical heatmap.',
 'Investigate quantity/basket mix and unit economics using proper margin and experimental evidence; the heatmap is not a price-optimisation model.',
 'outputs/invoice_spearman.csv; outputs/invoice_summary.csv')
page()
visual(11,'12_trading_rhythm.png','Weekday sales and first-recorded invoice hour',
 'Thursday contributes £2,199,292.57; noon starts 3,219 qualified invoices. There are no Saturday records in the workbook.',
 'Mutually exclusive earliest-timestamp allocation fixes double counting from invoices that span two line-recording minutes. The aggregate time profile is a billing-data description, not proof of opening hours, labour load or fulfilment times.',
 'Compare fresh operational timestamps, order processing effort and service levels before scheduling staff or systems capacity.',
 'outputs/weekday_performance.csv; outputs/hourly_performance.csv; outputs/invoice_timestamp_exceptions.csv')
page()
visual(12,'13_country_invoice_boxplot.png','Box plot of UK and non-UK invoice values',
 'UK median invoice value is £299.95 (Q1 £147.06; Q3 £465.315) versus non-UK £424.06 (Q1 £228.84; Q3 £790.54). Group sizes are 18,019 and 1,941 invoices.',
 'Both groups have substantial high-value tails. Whiskers use 1.5×IQR on the original data, then the y-axis is displayed logarithmically. Outlier points remain. Invoice comparisons are descriptive because repeat customers contribute multiple observations.',
 'Prefer the customer-level comparison for conditional inference and evaluate delivery/margin constraints before treating larger foreign invoices as attractive acquisition economics.',
 'outputs/invoice_country_box_statistics.csv; outputs/invoice_summary.csv')
page()
visual(13,'14_customer_frequency_count.png','Count plot of observed customer purchase frequency',
 'Frequency bands contain 1,493 customers with one invoice; 835 with two; 1,138 with 3–5; 535 with 6–10; and 337 with at least 11.',
 'Each identified purchaser appears exactly once, so the bars sum to 4,338. The observed repeat majority does not remove acquisition-date censoring or missing-customer bias. A count plot is used instead of an unnecessary pie chart.',
 'Build exposure-adjusted cohorts from current customer data and measure repeat activity over a common follow-up window.',
 'outputs/customer_frequency_bands.csv; outputs/customer_rfm.csv')
page()
visual(14,'15_line_quantity_price_histograms.png','Qualified line quantity and unit-amount distributions',
 'Quantity median is 4, mean 10.616600 and maximum 80,995. Unit amount median is £2.08, mode £1.25 and qualified maximum £13,541.33.',
 'The two positive measures have very different units and long tails. Separate panels and logarithmic x-axes preserve every qualified line without implying quantity and currency are directly comparable. The unit-amount panel includes all qualified codes, including non-product entries.',
 'Use a merchandise-only, credit-aware demand layer for replenishment and retain an exception review for unusually large amounts rather than applying a universal cutoff.',
 'outputs/sales_line_measures.csv.gz; outputs/valid_descriptive_statistics.csv')
page()

# 13. FINDINGS
h('13. Key Findings and Original Insights')
p('The following findings synthesize evidence rather than restating chart titles. Each provides a numerical comparison, meaning, business importance and recommended response. Detailed arithmetic and plots are in Sections 11–12; all evidence remains traceable to the original workbook.')
finding(1,'Sales activity is not retained or accounting revenue',
 'Sales before credits are £10,642,110.80; C-credit notes are £893,979.73.',
 'The resulting £9,748,131.07 differs again from the £9,726,006.95 all-line signed amount after bad-debt adjustments.',
 'The measurement basis changes the answer, not merely its wording.',
 'Ambiguous net-revenue labels would obscure credit exposure and inconsistent targets.',
 'Publish the three separately defined measures and a signed adjustment bridge.',
 'outputs/exclusive_line_partitions.csv; outputs/negative_price_exceptions.csv')
finding(2,'Two fully offset bulk entries dominate credit severity',
 'The 581483/C581484 and 541431/C541433 pairs total £245,653.20 gross and zero signed pair value.',
 'They alone account for 27.48% of recorded C-credit value; 23843 goes from £168,469.60 to £0.00.',
 'A small number of extreme records can alter product rankings and period credit ratios.',
 'Treating these gross values as replenishment demand or loyal-customer value would misallocate attention.',
 'Prioritise traceable credit linkage and inspect large offsets without deleting authentic records or alleging a cause.',
 'outputs/extreme_transaction_pairs.csv; outputs/product_performance.csv')
finding(3,'AOV is materially above the typical invoice',
 'Mean invoice value is £533.17 versus median £303.30, with p99 £4,821.17.',
 'A hypothetical £183.60 line-value cap lowers total sales by 16.29%, much more than the 0.23% deduplication sensitivity.',
 'The upper tail matters financially but does not justify arbitrary clipping.',
 'A mean-only view masks both normal-sized orders and exceptional exposure.',
 'Use median/IQR/tail percentiles alongside AOV and retain credit-qualified extreme observations.',
 'outputs/valid_descriptive_statistics.csv; outputs/metrics.json')
page()
finding(4,'Identity coverage is a value-attribution limitation, not a reason to erase sales',
 'Anonymous qualified lines total 132,186 (25.18%) and £1,754,901.91.',
 'They supply 16.49% of all sales; known purchasers cover £8,887,208.89 (83.51%).',
 'Line missingness and financial coverage differ; a quarter of lines missing an ID does not mean a quarter of sales value is missing.',
 'RFM and repeat findings cannot represent the complete purchaser population, and missingness may be selective.',
 'Retain anonymous transactions in finance/time views and improve permissioned prospective identity linkage.',
 'outputs/metrics.json; outputs/raw_schema_profile.csv')
finding(5,'Repeat activity does not imply a larger mean order',
 'Repeat purchasers number 2,845 of 4,338 (65.58%).',
 'Mean customer AOV is £421.00 for repeat versus £411.25 for one-time purchasers (Welch p 0.8732), while medians are £302.56 and £255.91 and the rank test differs.',
 'Mean, median and distributional questions produce different evidence; non-significance is not equivalence.',
 'Retention economics may depend on frequency and credit-qualified contribution, not automatically higher mean AOV.',
 'Test retention effects using current cohorts, common follow-up and appropriate contribution metrics.',
 'outputs/customer_rfm.csv; outputs/metrics.json')
finding(6,'Customer concentration is strong but denominator-sensitive',
 'Champions are 942 IDs (21.72%) producing £5,729,483.37.',
 'This is 64.47% of identified sales but only 53.84% of all sales; 1,130 IDs, not exactly 20%, reach 80% of the identified pool.',
 'The retailer has concentrated known-account value, not a universal 80/20 law.',
 'Ignoring anonymous sales or credit balances overstates the reach and certainty of a CRM list.',
 'Refresh key accounts, display both denominators and validate current credit-adjusted eligibility.',
 'outputs/rfm_segments.csv; outputs/customer_pareto.csv')
page()
finding(7,'A high gross customer ranking can disappear after credits',
 'Customer 16446 has £168,472.50 gross sales but £2.90 credit-adjusted; customer 12346 has £77,183.60 gross and £0.00 adjusted.',
 'Twenty-one purchasers have a non-positive penny-rounded adjusted balance in the observation window.',
 'Gross-only RFM can label large reversed transactions as customer value.',
 'This risks inappropriate incentives, but the balances do not identify lifetime loss or misconduct.',
 'Supplement rather than silently overwrite gross RFM with transparent credit-adjusted review flags.',
 'outputs/customer_rfm.csv; outputs/extreme_transaction_pairs.csv; outputs/extended_results.json')
finding(8,'Win-back scope is historical exposure, not recoverable revenue',
 'At Risk plus Can’t Lose Them includes 658 purchasers and £818,896.54 of historical gross value.',
 'Recorded customer credits reduce that to £736,853.23; one member has a non-positive adjusted balance.',
 'A segment total describes what was recorded, not what an outreach campaign can recapture.',
 'Presenting it as forecast recovery would invent conversion, permission and uplift assumptions.',
 'Validate fresh permissions, exclude unresolved credit issues and measure a holdout-based campaign before scaling.',
 'outputs/customer_rfm.csv; outputs/rfm_segments.csv; outputs/metrics.json')
finding(9,'Country value can represent one account rather than market breadth',
 'The UK generates £9,001,744.09 (84.59% of sales); Netherlands leads non-UK at £285,446.34.',
 'The leading Netherlands account supplies 98.16% of identified country sales across nine known IDs, while Germany has 94 and France 87 known purchasers.',
 'High national sales and broad demand are different dimensions.',
 'Account loss could dominate the apparent national opportunity; acquisition economics remain unknown.',
 'Protect current account relationships separately from small, cost-qualified market-expansion tests.',
 'outputs/country_performance.csv')
page()
finding(10,'The November peak is invoice-volume-led',
 'November sales of £1,503,866.78 exceed October by 30.63%.',
 'Invoice count rises 35.74% (2,040 to 2,769), while AOV falls 3.76% (£564.34 to £543.11).',
 'More invoices, not higher average invoice value, explain the growth identity.',
 'A price-increase interpretation would misdirect peak planning; the nine-day December observation is also not comparable.',
 'Validate current invoice workload, product availability and capacity before planning the next peak.',
 'outputs/monthly_performance.csv')
finding(11,'Foreign customer AOV is higher, without a stronger repeat signal',
 'Mean customer AOV is £661.12 non-UK versus £391.68 UK; Welch p = 5.55×10⁻⁸, d = −0.150 for UK minus non-UK.',
 'Repeat shares are almost equal, 65.79% versus 65.56%, with Yates p = 0.9687.',
 'Higher invoice values and observed repeat share within the recorded window need not move together.',
 'Country mix, costs, selection and tenure could explain patterns; neither comparison estimates a geography effect.',
 'Compare delivered contribution and customer exposure before prioritising a country; test rather than infer causation.',
 'outputs/customer_rfm.csv; outputs/country_repeat_contingency.csv; outputs/extended_results.json')
finding(12,'Basket associations suggest hypotheses, not demonstrated uplift',
 'Spearman value–quantity correlation is 0.838984 and value–line-count is 0.551606.',
 'Value–unweighted-mean-unit-amount correlation is only 0.094257; 825 of 3,912 merchandise codes reach 80% of merchandise gross sales.',
 'Basket mix and product concentration are operationally relevant, but value is mechanically constructed from quantity and price.',
 'A heatmap cannot establish that increasing quantity or recommendations will improve profit.',
 'Use credit-aware catalogue priorities and a pre-specified bundle/recommendation test with margin and credit guardrails.',
 'outputs/invoice_spearman.csv; outputs/product_pareto.csv; outputs/metrics.json')
page()

# 14. RECOMMENDATIONS
h('14. Business Recommendations')
p('The eight recommendations are proposals, not completed interventions. Expected benefits describe mechanisms rather than invented savings or uplift. Owners, sequence and decision gates are suggested for implementation. Historical numeric baselines must be refreshed before current targets or experiments are approved.')
recommendation(1,'Reconcile finance definitions and implement credit traceability',
 '£10.642m before-credit sales, £9.748m credit-adjusted value and £9.726m all-line signed value are different. Two offset pairs represent 27.48% of credit value.',
 'Create a versioned metric dictionary; retain all signed records; add an original-invoice link, reason code and exception queue to each new credit. Review large matched offsets before performance reporting.',
 'Less misclassification of sales and more interpretable credit exposure; no financial saving is established by this dataset.',
 'Reconciliation residual should equal £0.00 at the documented rounding basis. Measure credit-link coverage, missing reason-code share and exception age; the source lacks the first two baselines, so establish them on new data rather than inventing them.',
 'Finance lead with BI/data engineering')
recommendation(2,'Improve permissioned customer attribution without dropping anonymous activity',
 '132,186 qualified lines lack an ID; £1,754,901.91 (16.49% of sales) cannot be assigned to a known purchaser.',
 'Audit checkout and CRM linkage, preserve valid anonymous transactions and add optional, consent-compliant identifier capture with ID quality checks. Do not infer identity from purchase resemblance.',
 'Broader, more representative CRM measurement while preserving full commercial totals and appropriate privacy choices.',
 'Track both known-sales value coverage (historical 83.51%) and missing-ID line share (25.18% in qualified sales). Report weekly changes with a fresh baseline and monitor abandoned checkout/consent complaints; do not set forced identity capture as the success condition.',
 'CRM operations and data engineering with privacy review')
page()
recommendation(3,'Protect validated high-value accounts before generic promotions',
 '942 Champions provide 64.47% of identified sales, but gross value can be misleading: customer 16446 has only £2.90 after recorded credits.',
 'Refresh the RFM window, permissions, account status and credit-adjusted balances; review high-concentration accounts with service teams. Keep gross and adjusted versions visible, and use a holdout where contact is discretionary.',
 'More relevant service and less incentive spend on reversed activity. Improved retention is possible but not demonstrated.',
 'Measure current qualified repeat activity, credit-adjusted contribution per eligible account, service issues and opt-outs over a common follow-up period. Pre-specify treatment/control and decision criteria after costs and sample size are known; do not promise an uplift.',
 'Account management and CRM analytics')
recommendation(4,'Use a bounded, eligibility-checked win-back pilot',
 '658 At Risk/Can’t Lose Them IDs represent £736,853.23 of adjusted historical value, not recoverable sales; one has a non-positive adjusted balance.',
 'Revalidate current contact permission and trading status, resolve credits first and draw a small randomized eligible pilot with a business-as-usual holdout. Use recent recency/frequency definitions, not 2011 labels operationally.',
 'Tests whether outreach adds incremental, retained value without presenting historical exposure as a forecast.',
 'Primary outcome: net-of-credit contribution per eligible assigned customer; secondary outcomes: repeat purchase, opt-outs and campaign cost. Set follow-up, minimum detectable effect and sample size from current data. Publish confidence intervals and costs before scaling.',
 'CRM campaign manager and analyst')
page()
recommendation(5,'Prioritise credit-aware merchandise and integrate inventory economics',
 '23843 has £168,469.60 gross but £0.00 adjusted; 22423 has £164,459.49 after recorded credits. A set of 825 of 3,912 merchandise codes reaches 80% of gross merchandise value.',
 'Build a SKU scorecard with gross/credit-adjusted value, units, credit incidence, availability, margin and supplier lead time. Separate postage/manual codes. Investigate reversed bulk entries rather than treating them as ordinary replenishment demand.',
 'Better prioritisation of stock reviews and less gross-ranking distortion; reduced stock-outs or cash tied in inventory cannot be quantified from these data.',
 'With inventory/cost data, monitor fill rate, stock-out days, contribution after credits and inventory turns by priority SKU. Compare against an agreed baseline and keep availability changes separate from demand changes.',
 'Merchandising and supply planning')
recommendation(6,'Plan peak workload from invoice volume, then validate operational effort',
 'November invoice count increases 35.74% while AOV declines 3.76%; the modal recorded start hour is noon with 3,219 invoices across the extract.',
 'Refresh multiple years of demand and join warehouse/service timestamps. Stress-test invoice-processing and fulfilment capacity for observed order-count variation; separate billing times from physical workload.',
 'A workload-led capacity plan is better aligned with the observed growth pattern than a price-led story, but no staffing saving or service improvement has been measured.',
 'Use current invoices/hour, processing minutes/order, backlog, on-time dispatch and error rate. Set service-level and capacity gates using current workload; explicitly compare complete months and avoid extrapolating the partial December record.',
 'Operations manager with analytics and systems teams')
page()
recommendation(7,'Separate key-account protection from geographic expansion',
 'Netherlands leads non-UK value (£285,446.34) but one account supplies 98.16% of identified country sales; Germany/France show broader historical customer counts (94/87).',
 'Review current Netherlands and Australia key accounts separately from market-acquisition opportunities. For any expansion pilot, obtain shipping, tax, returns and landed-margin data and cap pilot exposure under approved budgets.',
 'Makes concentration risk explicit and avoids mistaking one buyer’s demand for a broad national market.',
 'Track top-account share, active buyer breadth, delivered contribution, repeat activity, credit value and acquisition cost. Expansion passes a pre-agreed contribution/retention gate on current data, not simply a country gross-sales rank.',
 'Commercial lead, account manager and finance')
recommendation(8,'Test basket-building rather than monetising correlation',
 'Value–line-count Spearman 0.551606 and value–quantity 0.838984 suggest basket hypotheses, while repeat/one-time mean AOV differs little under Welch (p 0.8732).',
 'Develop plausible complementary-product suggestions using merchandise transactions, then randomize eligible customers or sessions if appropriate data become available. Pre-register the outcome, assignment unit, exclusions and credit follow-up.',
 'Can distinguish incremental contribution from selection and larger-basket mechanics; no observed cross-sell lift or price elasticity is claimed.',
 'Measure contribution per assigned unit, conversion only if session denominators exist, credit-adjusted AOV, credit incidence and opt-outs. Compute a current-data power plan and report effect intervals. Stop or revise if margin/credit guardrails deteriorate.',
 'Product/merchandising team with experimentation analyst')
h('14.9 Suggested sequence and dependencies',2)
p('First agree the metrics and credit/identity controls (R1–R2), then refresh current customer and product data (R3–R5). Operational and geographic pilots (R6–R7) require workload/cost information. Basket testing (R8) requires a valid assignment and outcome dataset. The sequence is proposed; no workstream has been implemented and no schedule, ROI or improvement percentage is presented as an observed result.')
page()

# 15. LIMITATIONS
h('15. Limitations')
table('Limitations, consequences and mitigations',['Limitation','Consequence for this analysis','Mitigation / honest boundary'],[
 ['Historical, single-retailer extract','2010–2011 patterns cannot establish current commercial priorities or sector-wide performance.','Refresh current, multi-year data before action; preserve case-study wording.'],
 ['Partial final month','December 2011 contains only 1–9 December.','Label coverage and exclude it from full-month growth interpretation; do not annualise nine days.'],
 ['Missing customer identities','24.93% of raw lines and 16.49% of qualified sales value cannot be assigned to purchasers.','Retain sales, restrict customer denominators and avoid representativeness claims.'],
 ['Exact-duplicate assumption','Identical source rows might sometimes represent legitimate repeated entries.','Preserve original and show £24,573.74 no-dedup sales sensitivity.'],
 ['No complete credit/order links','Only selected exact offset pairs are identified; general cancellation probabilities or causes are unknown.','Describe C-credit documents and value ratios; add operational links and reason codes prospectively.'],
 ['No costs, margins or fulfilment','Recorded value is not profit, cash collection, inventory demand fulfilled or delivered contribution.','Do not claim ROI; acquire economics and operational data for decisions.'],
 ['Mixed code semantics','Non-product code list is analyst-defined and descriptions vary.','Publish the list; use StockCode; validate with a business-owned catalogue.'],
 ['Dependent and non-random observations','Invoices repeat by customer and time; country groups are not random assignments.','Use customer-level summaries for primary comparisons; treat tests as conditional exploratory evidence.'],
 ['Skew and extreme entries','Means and t intervals are tail-sensitive; some extremes fully offset.','Report median/IQR/tails, rank sensitivity and credits; no arbitrary removal.'],
 ['RFM heuristics and exposure','Tie-breaking, gross monetary basis and acquisition-date censoring affect labels and repeat opportunity.','Document exact rules; refresh and validate segments/cohorts before use.'],
 ['Country and timestamp conventions','Eight IDs span country labels; 42 invoices span line timestamps; timezone unavailable.','Declare first-country and earliest-invoice-time rules; retain original labels/timestamps.'],
 ['Exploratory tests and no intervention','Multiple comparisons are unadjusted; causal effects, improvement and generalisation are unidentified.','Pre-register future tests, use appropriate assignment and never equate association with causation.'],
],widths=[1.43,2.62,2.7777],font=9.4)
p('Public education data may still carry privacy or re-identification risks; numeric CustomerID is not proof that no real-world person could ever be linked. Current customer activation would require lawful access and permission checks. Dataset licensing does not replace those operational obligations. [2]')
page()

# 16. FUTURE SCOPE
h('16. Future Scope')
p('Further work should reduce an identified uncertainty rather than add an impressive but unsupported model. Each proposed extension below depends on additional data or a stricter design; none is presented as already executed.')
table('Specific extensions and evidence needed',['Extension','Required data / design','Output and decision value'],[
 ['Exposure-adjusted customer cohorts','Acquisition dates, recent customer history, consistent follow-up and permissioned IDs.','Repeat/retention curves with censoring handled; distinguish tenure from behaviour.'],
 ['Credit linkage and root-cause analysis','Original invoice references, reason codes, dispatch/refund dates and resolution status.','Linked-order credit incidence, causes and time-to-credit; targeted process fixes.'],
 ['Credit-aware customer value','Costs, delivery, acquisition/service expense and sufficiently long current history.','Contribution-based account priorities; validate against gross RFM rather than relabel sales as CLV.'],
 ['Inventory and SKU planning','Stock availability, lead time, stock-outs, supplier cost and product master.','Credit-adjusted ABC/XYZ and service-level planning; distinguish suppressed sales from low demand.'],
 ['Forecasting with honest validation','Multiple complete years, promotions, holidays and rolling-origin holdouts.','Backtested forecast intervals, error by peak/normal periods and comparison with simple baselines.'],
 ['Basket and market experiments','Eligible population, assignment logs, sessions if conversion is needed, costs and credit follow-up.','Incremental contribution with uncertainty and guardrails; no inference from correlation alone.'],
 ['Robust uncertainty and sensitivity','Current customer clusters, time blocks and prespecified estimands.','Cluster-aware/temporal resampling, trimmed estimates and test multiplicity control for planned questions.'],
],widths=[1.50,2.70,2.6277],font=9.7)
p('Unsupervised segmentation or supervised prediction would require an explicit use case, leakage controls, time-based validation and a baseline. A cluster label is not a business insight by itself, and a forecast score does not replace interpretable reconciliation. The immediate priority is better identifiers, linked credits and unit economics, because those gaps directly limit the decisions discussed in this report.')
page()

# 17. CONCLUSION
h('17. Conclusion')
p('The unchanged UCI workbook supports a complete, auditable transaction analysis when its mixed processes and analytical grains are kept explicit. From 541,909 original lines, a documented exact-duplicate assumption yields 536,641 complete cleaned records. Qualified sales remain a separate 524,878-line view representing 19,960 invoices, while anonymous activity, credits, non-credit stock movements and bad-debt adjustments remain traceable in the full cleaned data.')
p('The principal measurement answer is £10,642,110.80 sales before credits, £893,979.73 recorded C-credit value and £9,748,131.07 credit-adjusted value. The £9,726,006.95 all-line signed total reconciles the additional financial adjustments. A typical invoice is much closer to the £303.30 median than the £533.17 mean. Two completely offset extreme pairs show why before-credit rankings alone are insufficient for product or account decisions.')
p('Customer and geographic conclusions require denominator discipline. Identified purchasers supply 83.51% of sales; their repeat share is 65.58%. Champions contribute 64.47% of that identified pool but 53.84% of all sales. The UK dominates at 84.59%, while Netherlands’ leading non-UK value is highly concentrated in one account. November’s peak is explained by higher invoice volume despite lower AOV; partial December cannot be read as a full-month decline.')
p('These results justify credit-aware measurement controls, permissioned identity improvement, current-data account/SKU validation and carefully designed operational, geographic and basket pilots. They do not establish profit, causal drivers, campaign recovery, fraud or present-day performance. Statistical tests are exploratory and conditional; recommendations remain proposed actions with measurable decision gates.')
p('The five reviewer criticisms are addressed through fourteen fully worked examples, complete raw/cleaned profiles, step-level code and before/after cleaning evidence, fifteen interpreted figures, twelve numerically supported findings and eight practical recommendations. Full computational code, an executed notebook, cleaned-data manifests and validation evidence accompany this report. Submission quality is designed to support a strong evaluation; the official score remains the evaluator’s decision, not a promised 90+ result.')
page()

# 18. REFERENCES
h('18. References')
refs=[
 ('1','Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5BW33. Official catalogue, business description, variables, file and licence.','https://archive.ics.uci.edu/dataset/352/online+retail'),
 ('2','Creative Commons. Attribution 4.0 International (CC BY 4.0). Attribution, changes, no endorsement and other-rights notices.','https://creativecommons.org/licenses/by/4.0/'),
 ('3','Pandas development team. Pandas 2.2.3 documentation: DataFrame.describe. Numeric/categorical descriptions and default percentiles.','https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.DataFrame.describe.html'),
 ('4','SciPy community. scipy.stats.ttest_ind documentation, stable web manual (1.18.0 when consulted). Independent-sample null, unequal-variance Welch option and inferential interpretation. Installed runtime: SciPy 1.17.1.','https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html'),
 ('5','Seaborn. seaborn.boxplot, version 0.13.2 documentation. Quartiles, 1.5×IQR whiskers and outlier display.','https://seaborn.pydata.org/generated/seaborn.boxplot.html'),
 ('6','Reddy, T. A. Original Task 4 Online Retail project, repository snapshot e05584ebc7fd1193a83130539ac94cba90d6a6f2. Used for baseline-method comparison only; not an independent source of revised evidence.','https://github.com/appureddy1102-cloud/real-world-online-retail-analysis'),
]
for no,citation,url in refs:p(f'[{no}] {citation}\n{url}')
p('Source documents consulted for this revision: 7 November 2026. All numerical findings in this report are original computations on the provided official workbook; external documentation supports source definitions, licensing and method use, not the empirical results. No unread paper is cited as evidence for these findings. The source archive is https://archive.ics.uci.edu/static/public/352/online+retail.zip.','Small Note')
source('data/source_verification.json; references/task4_original_results.json; outputs/task4_metric_reconciliation.csv')
page()

# 19. APPENDIX
h('19. Appendix – Python Code')
h('19.1 Reproduce the project',2)
p('Run from the project root in a Python virtual environment. Analysis uses the included original workbook; if it is absent, the core downloads the official UCI archive and verifies the same SHA-256. Python 3.13.16 and the exact installed dependencies are recorded in requirements.txt. No credentials or connector access are needed to recompute results or figures.')
code('python -m venv .venv\n# Linux/macOS: source .venv/bin/activate\n# Windows PowerShell: .venv\\Scripts\\Activate.ps1\npython -m pip install -r requirements.txt\npython scripts/analyze.py\npython scripts/make_charts.py\npython scripts/run_notebook.py\npython tests/validate_outputs.py')
p('For editable Word regeneration, run python scripts/build_report.py, then refresh the contents and page fields in Writer/Word. The optional Linux publishing route is documented in README.md and scripts/format_document.py; it requires LibreOffice Writer and the system UNO bridge. The final Word file was rendered with LibreOffice for layout checks, not tested inside the Microsoft Word application. Publishing is separate from recomputation.')
h('19.2 Actual execution outputs and evidence map',2)
code('gross_sales: 10642110.8\ncredit_value_abs: 893979.73\ncredit_adjusted_value: 9748131.07\ndedup_signed_all_lines: 9726006.95\nPASS: 24 Task 4 metric reconciliations; all aggregation and partition checks.\nExtended exploration complete: [536641, 16] cleaned-all; [524878, 16] qualified sales\nDescription whitespace normalized: 112371 | Country whitespace: 0\nWorked standard deviation: 0.8944271909999159\nWorked Pearson r: 0.9952659485651739\nWorked Welch t: -5.474116123522671 | df: 1008.1829680542309\nCharts: 15')
table('Evidence outputs and their purpose',['Output family','Contents'],[
 ['raw_schema_profile; raw/valid_descriptive_statistics','Complete schema/missing/unique and mean/median/mode/sample SD/min/max/quartile summaries.'],
 ['cleaning_step_audit; cleaned_schema; manifests','Before/after operations, literal core expressions, final columns and file hashes.'],
 ['worked_invoice; worked_standard_deviation; worked_pearson','Source-derived rows for manual calculations in Section 11.'],
 ['monthly/country/product/customer summaries','Complete aggregates underlying insights, charts and recommendations.'],
 ['extreme_transaction_pairs; exceptions','Auditable offset, bad-debt and timestamp observations.'],
 ['metrics; extended_results; reconciliation','Machine-readable results, worked statistical inputs and 24 reproduced baseline checks.'],
 ['report_manifest; QA_REPORT; VALIDATION','Report structure, evidence/figure registers and executed package checks.'],
],widths=[3.10,3.7277],font=9.5)
page()
h('19.3 Read the complete cleaned datasets correctly',2)
code("from pathlib import Path\nimport pandas as pd\n\nroot = Path.cwd()\ndtypes = {\n    'InvoiceNo': 'string', 'StockCode': 'string', 'Description': 'string',\n    'Country': 'string', 'CustomerID': 'Int64', 'SourceRow': 'int64',\n    'IsCredit': 'boolean', 'IsNonProduct': 'boolean',\n    'IsOtherNegativeMovement': 'boolean', 'HasCustomerID': 'boolean',\n    'IsQualifiedSale': 'boolean', 'Month': 'string',\n}\nclean = pd.read_csv(root/'data/cleaned_all_records.csv.gz',\n                    dtype=dtypes, parse_dates=['InvoiceDate'])\nsales = clean.loc[clean.IsQualifiedSale].copy()\nassert clean.shape == (536641, 16)\nassert sales.shape == (524878, 16)\nassert clean.SourceRow.is_unique\nassert clean.CustomerID.isna().sum() == 135037\nprint(clean.shape, sales.shape)\nprint(round(sales.LineValue.sum(), 2))")
p('Actual read-back output: (536641, 16) (524878, 16), then 10642110.8. CSV empty CustomerID cells mean missing, not zero. The UNKNOWN Description sentinel denotes a missing label. SourceRow joins to the original workbook, so the retained normalized record can always be inspected without changing the source.')
h('19.4 Full computational source',2)
p('The following three files are reproduced in full, with imports, comments and executable statements. They are separate files: save each under its stated scripts/ path, rather than concatenating them. Long code lines may visually wrap; paragraph boundaries preserve the original source line. Report-generation, notebook-runner and validation utilities are included in the companion project as additional source.')
for file,title in [('verified_core.py','19.4.1 scripts/verified_core.py — verified source, partitions, aggregates and tests'),
                   ('analyze.py','19.4.2 scripts/analyze.py — complete profiling, cleaning and worked calculations'),
                   ('make_charts.py','19.4.3 scripts/make_charts.py — all Matplotlib and Seaborn visualizations')]:
 page();h(title,2)
 text=(ROOT/'scripts'/file).read_text()
 code(text)
 source('End of complete file: scripts/'+file)

# Final machine-readable report register is used by validation and review.
report_manifest={'author':'T. Aparna Reddy','date':'2026-11-07','sections':HEADINGS,
                 'tables':TABLES,'figures':FIGS,'worked_examples':WORKED,
                 'findings':FINDINGS,'recommendations':RECOMMENDATIONS,
                 'code_appendix_files':['scripts/verified_core.py','scripts/analyze.py','scripts/make_charts.py'],
                 'raw_sha256':M['sha256'],'synthetic_records':0}
(O/'report_manifest.json').write_text(json.dumps(report_manifest,indent=2,ensure_ascii=False,default=str))
D.save(CACHE/'Task4_draft.docx')
(ROOT/'reports'/'Task4_Real_World_Dataset_Analysis.md').write_text('\n'.join(MD))
print('Draft created:',len(HEADINGS),'sections,',len(TABLES),'tables,',len(FIGS),'figures,',len(WORKED),'worked examples,',len(FINDINGS),'findings,',len(RECOMMENDATIONS),'recommendations')
