"""Create 15 non-redundant Task 4 figures using Matplotlib and Seaborn."""
from pathlib import Path
import json
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.patches import FancyBboxPatch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs'; V=ROOT/'visualizations'; V.mkdir(exist_ok=True)
m=json.loads((O/'metrics.json').read_text())
monthly=pd.read_csv(O/'monthly_performance.csv')
countries=pd.read_csv(O/'country_performance.csv')
customers=pd.read_csv(O/'customer_rfm.csv')
segments=pd.read_csv(O/'rfm_segments.csv')
products=pd.read_csv(O/'product_performance.csv')
invoices=pd.read_csv(O/'invoice_summary.csv')
pareto=pd.read_csv(O/'customer_pareto.csv')
pp=pd.read_csv(O/'product_pareto.csv')
NAVY='#17364B'; TEAL='#008C87'; GOLD='#DFAB3B'; RED='#C45660'; GREY='#7C8D99'; LIGHT='#E7EEF2'
plt.rcParams.update({
 'font.family':'DejaVu Sans','font.size':11.5,'axes.titlesize':15,'axes.titleweight':'bold',
 'axes.titlepad':16,'axes.labelsize':12,'axes.labelcolor':NAVY,'text.color':NAVY,
 'axes.edgecolor':'#BCCAD2','axes.spines.top':False,'axes.spines.right':False,
 'xtick.color':'#415968','ytick.color':'#415968','grid.color':LIGHT,'grid.linewidth':.7,
 'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
 'legend.frameon':False,'legend.fontsize':10.5,
})
DPI=330
manifest=[]

def save(fig,name,title):
    fig.savefig(V/name,dpi=DPI,bbox_inches='tight',pad_inches=.18,pil_kwargs={'compress_level':9})
    plt.close(fig)
    # Adaptive 256-colour PNG retains chart geometry and high-resolution text
    # while eliminating redundant RGB shades; no blurry JPEG compression.
    im=Image.open(V/name).convert('RGB')
    im.quantize(256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save(V/name,optimize=True,dpi=(DPI,DPI))
    manifest.append({'file':name,'title':title,'bytes':(V/name).stat().st_size,'dpi':DPI})

def grid(ax,axis='y'):
    ax.grid(axis=axis);ax.set_axisbelow(True)

def pct(x,pos):return f'{x:.0f}%'
def gbpk(x,pos):return f'£{x/1000:,.0f}k'
def comma(x,pos):return f'{x:,.0f}'

# 01: compact executive summary, not an inferential performance scorecard.
fig,ax=plt.subplots(figsize=(9.1,4.3));ax.axis('off')
cards=[('SALES BEFORE CREDITS','£10.642m','Task 4 inclusion basis',TEAL),
       ('CREDIT-ADJUSTED VALUE','£9.748m','Sales less recorded C-credit notes',TEAL),
       ('RECORDED CREDIT VALUE','£0.894m','8.40% of sales before credits',RED),
       ('QUALIFIED SALES INVOICES','19,960','524,878 positive sales lines',NAVY),
       ('IDENTIFIED CUSTOMERS','4,338','65.58% repeat within the window',NAVY),
       ('AVERAGE ORDER VALUE','£533.17','Median order value: £303.30',NAVY)]
for i,(label,value,sub,col) in enumerate(cards):
    x=(i%3)/3+.012;y=.53-(i//3)*.48
    box=FancyBboxPatch((x,y),.307,.41,boxstyle='round,pad=.008,rounding_size=.014',facecolor='#F3F7F9',edgecolor='#DCE7ED',transform=ax.transAxes)
    ax.add_patch(box)
    ax.text(x+.016,y+.315,label,transform=ax.transAxes,fontsize=9.1,fontweight='bold',color=GREY)
    ax.text(x+.016,y+.18,value,transform=ax.transAxes,fontsize=25,fontweight='bold',color=col)
    ax.text(x+.016,y+.065,sub,transform=ax.transAxes,fontsize=8.5,color=NAVY)
ax.text(.012,1.015,'Historical commercial snapshot | 1 Dec 2010–9 Dec 2011',fontsize=15,fontweight='bold',transform=ax.transAxes)
save(fig,'01_executive_dashboard.png','Historical commercial KPI dashboard')

# 02: distinguish three legitimate but different financial bases.
fig,ax=plt.subplots(figsize=(9.2,4.7))
vals=[m['gross_sales'],-m['credit_value_abs'],m['credit_adjusted_value'],m['other_excluded_value'],m['dedup_signed_all_lines']]
labels=['Sales before\ncredits','Recorded\nC-credit notes','Credit-adjusted\ntransaction value','Other financial\nadjustments','All-line signed\ntransaction value']
bottoms=[0,m['credit_adjusted_value'],0,m['dedup_signed_all_lines'],0]
heights=[vals[0],abs(vals[1]),vals[2],abs(vals[3]),vals[4]]
colors=[TEAL,RED,TEAL,GOLD,NAVY]
ax.bar(range(5),np.array(heights)/1e6,bottom=np.array(bottoms)/1e6,color=colors,width=.62)
for i in [0,2,4]:ax.text(i,heights[i]/1e6+.14,f'£{heights[i]/1e6:.3f}m',ha='center',fontsize=11.5,fontweight='bold')
ax.annotate('−£893,979.73',xy=(1,10.18),xytext=(1,11.2),ha='center',fontsize=11,color=RED,arrowprops={'arrowstyle':'-','color':RED})
ax.annotate('−£22,124.12',xy=(3,9.74),xytext=(3,10.65),ha='center',fontsize=11,color='#8E6B1F',arrowprops={'arrowstyle':'-','color':GOLD})
ax.set_xticks(range(5),labels);ax.tick_params(axis='x',labelsize=10)
ax.set_ylim(0,11.9);ax.set_ylabel('Recorded transaction value (£ millions)');grid(ax)
ax.set_title('Revenue terminology changes the business interpretation')
save(fig,'02_value_reconciliation.png','Sales-to-credit-adjusted value reconciliation')

# 03: complete months versus partial final month.
fig,ax=plt.subplots(figsize=(9.2,4.7));x=np.arange(len(monthly))
ax.plot(x[:12],monthly.GrossSales[:12]/1e6,color=TEAL,marker='o',lw=2.5,label='Sales before credits')
ax.plot(x[:12],monthly.CreditAdjustedValue[:12]/1e6,color=NAVY,marker='s',ms=4.8,lw=2,label='Credit-adjusted value')
for col,color in [('GrossSales',TEAL),('CreditAdjustedValue',NAVY)]:
    ax.plot(x[11:13],monthly[col][11:13]/1e6,color=color,lw=1.5,ls='--',marker='o',ms=5)
ax.axvspan(11.6,12.4,color=GOLD,alpha=.16)
ax.text(12,.82,'Partial\n1–9 Dec',ha='center',color='#8E6B1F',fontsize=10)
ax.annotate('November peak\n£1.504m gross',xy=(11,monthly.GrossSales.iloc[11]/1e6),xytext=(8,1.57),arrowprops={'arrowstyle':'-','color':TEAL},fontsize=11)
ax.set_xticks(x,[pd.Timestamp(s).strftime('%b\n%Y') for s in monthly.Month]);ax.tick_params(axis='x',labelsize=9)
ax.set_ylabel('Transaction value (£ millions)');ax.set_ylim(.3,1.75);ax.legend(loc='upper left');grid(ax)
ax.set_title('A strong autumn build-up precedes the November peak')
save(fig,'03_monthly_sales.png','Monthly sales before credits and credit-adjusted value')


# 05: normalization changes the reading of cancellation counts.
fig,axes=plt.subplots(2,1,figsize=(9.2,5.5),sharex=True)
axes[0].bar(x,monthly.CreditInvoices,color=RED,width=.65)
axes[0].set_ylabel('C-credit invoices');axes[0].set_title('Credit counts peak in November; value severity peaks elsewhere');grid(axes[0])
axes[1].plot(x,monthly.CreditDocumentSharePct,color=NAVY,lw=2,marker='o',label='Credit-document share of sales + credits')
axes[1].plot(x,monthly.CreditValuePctOfGross,color=RED,lw=2,marker='s',label='Credit value / sales before credits')
axes[1].set_ylabel('Share (%)');axes[1].yaxis.set_major_formatter(FuncFormatter(pct));axes[1].legend(loc='upper left',fontsize=9.1)
axes[1].set_ylim(0,42);grid(axes[1])
for ax in axes:ax.axvspan(11.6,12.4,color=GOLD,alpha=.16)
axes[1].set_xticks(x,[pd.Timestamp(s).strftime('%b\n%Y') for s in monthly.Month]);axes[1].tick_params(axis='x',labelsize=9)
fig.tight_layout()
save(fig,'04_monthly_credits.png','Monthly credit counts, document share and value ratio')


# 07: Pareto uses identifiable sales, with denominator explicit in chart.
fig,ax=plt.subplots(figsize=(9.2,4.9))
ax.plot(pareto.CustomerPct,pareto.CumKnownSalesPct,lw=2.5,color=TEAL)
ax.plot([0,100],[0,100],ls=':',lw=1,color=GREY,label='Equal distribution')
cut=m['customer_n80_pct'];ax.axhline(80,color=GREY,ls='--',lw=1);ax.axvline(cut,color=GREY,ls='--',lw=1)
ax.scatter([cut],[80],s=70,color=GOLD,zorder=4)
ax.annotate('1,130 customers (26.05%)\nreach 80% of identified sales',xy=(cut,80),xytext=(43,64),arrowprops={'arrowstyle':'-','color':GREY},fontsize=11)
ax.text(7,32,'Top 43 accounts (~1%):\n31.84% of identified sales',fontsize=10,color=NAVY)
ax.set(xlim=(0,100),ylim=(0,103),xlabel='Cumulative share of 4,338 identified customers (%)',ylabel='Cumulative share of £8.887m identified sales (%)')
ax.xaxis.set_major_formatter(FuncFormatter(pct));ax.yaxis.set_major_formatter(FuncFormatter(pct));grid(ax)
ax.set_title('A concentrated customer base, measured on the correct revenue pool')
save(fig,'05_customer_pareto.png','Customer sales concentration on the identified-customer basis')

# 08: size and value are not the same metric.
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9.3,5.5),sharey=True,gridspec_kw={'width_ratios':[1,1.25]})
y=np.arange(len(segments));colors=[TEAL if x=='Champions' else GOLD if x in ["Can't Lose Them",'At Risk'] else '#8EA6B4' for x in segments.Segment]
ax1.barh(y,segments.Customers,color=colors);ax2.barh(y,segments.KnownSalesSharePct,color=colors)
for i,row in segments.iterrows():
 ax1.text(row.Customers+18,i,f'{row.Customers:,}',va='center',fontsize=9.5)
 ax2.text(row.KnownSalesSharePct+.8,i,f'{row.KnownSalesSharePct:.2f}%',va='center',fontsize=9.5)
ax1.set_yticks(y,segments.Segment);ax1.invert_yaxis();ax1.set_xlim(0,1150);ax2.set_xlim(0,76)
ax1.set_xlabel('Identified customers');ax2.set_xlabel('Share of identified sales (%)');grid(ax1,'x');grid(ax2,'x')
fig.suptitle('Champions account for 21.72% of customers and 64.47% of identified sales',fontsize=13.5,fontweight='bold',y=1.015)
fig.tight_layout(w_pad=1.5)
save(fig,'06_rfm_segment_value.png','RFM customer counts and identified-sales contribution')


# 10: comparison prevents canceled outliers becoming inventory recommendations.
fig,ax=plt.subplots(figsize=(9.5,6.4))
fig.subplots_adjust(left=.38,right=.97,bottom=.12,top=.87)
top=products.nlargest(10,'GrossSales').iloc[::-1];y=np.arange(len(top));h=.35
ax.barh(y+h/2,top.GrossSales/1000,height=h,color='#9CB8C7',label='Sales before credits')
ax.barh(y-h/2,top.CreditAdjustedValue/1000,height=h,color=TEAL,label='After recorded C-credit notes')
names=[textwrap.fill(f'{r.StockCode} | {r.Description}',30) for r in top.itertuples()]
ax.set_yticks(y,names);ax.tick_params(axis='y',labelsize=12);ax.set_xlabel('Merchandise-coded value (£ thousands)');grid(ax,'x')
for yi,row in enumerate(top.itertuples()):
 if str(row.StockCode)=='23843':ax.text(2,yi-.18,'£0 after credits',va='center',fontsize=10,color=RED,fontweight='bold')
ax.legend(loc='lower right',fontsize=11);ax.set_xlim(0,200)
ax.set_title('Gross product leaders must be checked against recorded credits')
save(fig,'07_product_gross_vs_credits.png','Top merchandise products: gross sales versus credit-adjusted value')


# 12: separate domestic dominance from the export comparison.
fig,ax=plt.subplots(figsize=(9.2,5.1));z=countries[countries.Country!='United Kingdom'].head(10).iloc[::-1]
ax.barh(z.Country,z.GrossSales/1000,color=TEAL)
for yi,row in enumerate(z.itertuples()):ax.text(row.GrossSales/1000+3,yi,f'£{row.GrossSales/1000:,.1f}k',va='center',fontsize=10)
ax.set_xlabel('Sales before credits (£ thousands)');ax.set_xlim(0,340);grid(ax,'x')
ax.set_title('Netherlands leads non-UK sales; the UK still contributes 84.59%')
ax.text(.98,.05,'UK: £9.002m\n18,019 sales invoices',transform=ax.transAxes,ha='right',fontsize=11,color=NAVY,bbox={'facecolor':'#F0F5F7','edgecolor':'none','pad':9})
save(fig,'08_nonuk_markets.png','Top ten non-UK country sales')


# 14: no clipping; log x-axis exposes the extreme tail.
fig,ax=plt.subplots(figsize=(9.2,4.7));values=invoices.InvoiceValue
bins=np.geomspace(values.min(),values.max()*1.001,50)
ax.hist(values,bins=bins,color=TEAL,edgecolor='white',linewidth=.4)
ax.axvline(m['median_invoice_value'],color=NAVY,lw=2,label='Median £303.30')
ax.axvline(m['aov'],color=RED,lw=2,ls='--',label='Mean £533.17')
ax.set_xscale('log');ax.set_xlabel('Sales invoice value (£, logarithmic axis; no values removed)');ax.set_ylabel('Number of invoices')
ax.legend(loc='upper right');grid(ax)
ax.set_title('The average order is larger than the typical order')
save(fig,'09_invoice_value_histogram.png','Invoice-value histogram with mean and median')

# 15: all invoices; relationships are not intervention estimates.
fig,ax=plt.subplots(figsize=(9.2,4.9))
ax.scatter(invoices.LineCount,invoices.InvoiceValue,s=8,alpha=.25,color=TEAL,edgecolors='none',rasterized=True)
ax.set_xscale('log');ax.set_yscale('log')
ax.set_xlabel('Positive sales lines per invoice (log scale)');ax.set_ylabel('Sales invoice value (£, log scale)');grid(ax)
ax.text(.97,.05,'Spearman ρ(value, line count) = 0.552\nAssociation, not estimated cross-sell lift',transform=ax.transAxes,ha='right',fontsize=10,bbox={'facecolor':'white','edgecolor':LIGHT,'pad':8})
ax.set_title('Larger baskets tend to have higher recorded invoice value')
save(fig,'10_basket_value_scatter.png','Invoice value versus sales-line count scatter plot')

# 16: Seaborn heatmap; no cyclic calendar integers treated as linear drivers.
corr=pd.read_csv(O/'invoice_spearman.csv',index_col=0)
fig,ax=plt.subplots(figsize=(8.7,5.1))
names=['Invoice value','Sales-line count','Total quantity','Mean unit price']
sns.heatmap(corr,annot=True,fmt='.3f',cmap='BrBG',vmin=-1,vmax=1,
            xticklabels=names,yticklabels=names,square=True,linewidths=.6,
            annot_kws={'size':12},cbar_kws={'label':'Spearman rank correlation'},ax=ax)
ax.set_xticklabels(names,rotation=15,ha='right');ax.set_yticklabels(names,rotation=0)
ax.set_title('Quantity and basket breadth correlate more with value than mean price',fontsize=13)
save(fig,'11_invoice_correlation_heatmap.png','Spearman invoice-level correlation heatmap')

# 17: each invoice is assigned once to its first recorded timestamp.
weekday=pd.read_csv(O/'weekday_performance.csv');hourly=pd.read_csv(O/'hourly_performance.csv')
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9.4,4.6),gridspec_kw={'width_ratios':[1,1.2]})
ax1.barh(weekday.Weekday,weekday.GrossSales/1e6,color=[TEAL if d!='Saturday' else LIGHT for d in weekday.Weekday]);ax1.invert_yaxis()
ax1.set_xlabel('Sales before credits (£m)');ax1.set_title('Recorded weekday mix',fontsize=13);grid(ax1,'x')
ax1.text(.08,5,'No Saturday records',fontsize=9.5,color=GREY,va='center')
ax2.plot(hourly.Hour,hourly.Orders,color=NAVY,marker='o',lw=2,ms=4);ax2.set_xlabel('First recorded invoice hour');ax2.set_ylabel('Sales invoices')
ax2.set_xticks([6,8,10,12,14,16,18,20]);grid(ax2);ax2.set_title('Noon: 3,219 invoices',fontsize=13)
fig.suptitle('Trading timestamps support capacity planning—not assumptions about opening hours',fontsize=12.5,fontweight='bold',y=1.01)
fig.tight_layout()
save(fig,'12_trading_rhythm.png','Weekday revenue and mutually exclusive hourly invoice counts')

# 18: Required box plot, all invoice observations retained on a log y-axis.
invoices['CountryGroup']=np.where(invoices.Country.eq('United Kingdom'),'UK','Non-UK')
fig,ax=plt.subplots(figsize=(9.2,5.0))
sns.boxplot(data=invoices,x='CountryGroup',y='InvoiceValue',hue='CountryGroup',
            order=['UK','Non-UK'],palette=[TEAL,NAVY],legend=False,
            whis=1.5,fliersize=2.2,linewidth=1,ax=ax)
ax.set_yscale('log');ax.set_xlabel('Customer country group');ax.set_ylabel('Sales invoice value (£, log scale)')
ax.set_title('Non-UK invoices have a higher median, with heavy tails in both groups')
grid(ax)
save(fig,'13_country_invoice_boxplot.png','UK and non-UK invoice-value box plots')

# 19: Seaborn count plot; each identified customer appears once.
customers['FrequencyBand']=pd.cut(customers.Frequency,bins=[0,1,2,5,10,np.inf],
                                labels=['1','2','3–5','6–10','11+'])
fig,ax=plt.subplots(figsize=(9.2,4.7))
sns.countplot(data=customers,x='FrequencyBand',hue='FrequencyBand',
              order=['1','2','3–5','6–10','11+'],palette=[GREY,TEAL,TEAL,NAVY,NAVY],
              legend=False,ax=ax)
for patch in ax.patches:
 if patch.get_height()>0:
  ax.text(patch.get_x()+patch.get_width()/2,patch.get_height()+20,
          f'{int(patch.get_height()):,}',ha='center',fontsize=11)
ax.set_ylim(0,max(customers.FrequencyBand.value_counts())*1.17)
ax.set_xlabel('Qualified sales invoices per identified customer');ax.set_ylabel('Number of customers')
ax.set_title('1,493 customers bought once; 2,845 bought more than once')
grid(ax)
save(fig,'14_customer_frequency_count.png','Observed purchase-frequency count plot')

# 20: Actual quantity and unit-price distributions, no clipped observations.
lines=pd.read_csv(O/'sales_line_measures.csv.gz',dtype={'InvoiceNo':'string','StockCode':'string'})
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9.4,4.6))
for ax,col,colr,label in [(ax1,'Quantity',TEAL,'Positive units per line (log scale)'),
                          (ax2,'UnitPrice',NAVY,'Recorded unit amount (£, log scale)')]:
 z=lines[col];bins=np.geomspace(z.min(),z.max()*1.00001,45)
 ax.hist(z,bins=bins,color=colr,edgecolor='white',linewidth=.3)
 ax.set_xscale('log');ax.set_xlabel(label);ax.set_ylabel('Sales lines');grid(ax)
 ax.axvline(z.median(),color=RED,ls='--',lw=1.5,label=f'Median {z.median():g}')
 ax.legend(fontsize=9)
fig.suptitle('Qualified sales lines are right-skewed in quantity and unit amount',fontsize=13,fontweight='bold',y=1.01)
fig.tight_layout()
save(fig,'15_line_quantity_price_histograms.png','Qualified line quantity and unit-amount histograms')

(V/'chart_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Charts:',len(manifest),'| total bytes:',sum(a['bytes'] for a in manifest))
for a in manifest:print(a['file'],f"{a['bytes']/1024:.1f} KiB")
