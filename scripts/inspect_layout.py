"""Optional PDF/OOXML layout verification after the Word formatter.

Requires PyMuPDF (requirements-publishing.txt). Does not change the report.
Run: python scripts/inspect_layout.py
"""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone
import pymupdf
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
pdf=ROOT/'.cache/Task4_layout_check.pdf'
word=ROOT/'reports/YuvaIntern_Task4_Real_World_Dataset_Analysis_Revised.docx'
layout=json.loads((ROOT/'.cache/layout_info.json').read_text())
manifest=json.loads((ROOT/'outputs/report_manifest.json').read_text())
d=pymupdf.open(pdf)
page_data=[];caption_pages={};outside=[];replacement=0
for i,page in enumerate(d):
    text=page.get_text()
    replacement+=text.count('\ufffd')
    captions=re.findall(r'^Figure (\d+)\.',text,flags=re.M)
    for c in captions:caption_pages[int(c)]=i+1
    for block in page.get_text('dict')['blocks']:
        if 'lines' not in block:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<20 or x1>page.rect.width-20 or y0<10 or y1>page.rect.height-10:
                    outside.append({'page':i+1,'text':span['text'],'bounds':[x0,y0,x1,y1]})
    page_data.append({'page':i+1,'text_characters':len(text),
                      'image_count':len(page.get_images()),'figure_captions':captions})
doc=Document(word)
checks={
 'pdf_pages_equal_writer_pagination':len(d)==layout['writer_pages'],
 'all_pages_nonempty':all(p['text_characters']>250 for p in page_data),
 'all_fifteen_captions_present_once':set(caption_pages)==set(range(1,16)),
 'caption_and_chart_share_page':all(page_data[p-1]['image_count']>0 for p in caption_pages.values()),
 'no_text_spans_beyond_generous_page_boundaries':not outside,
 'no_replacement_characters':replacement==0,
 'word_has_fifteen_inline_figures':len(doc.inline_shapes)==15,
 'word_has_thirty_one_tables':len(doc.tables)==31,
 'author_attribution_preserved':doc.core_properties.author=='T. Aparna Reddy',
 'title_attribution_preserved':'Revised Task 4' in doc.core_properties.title,
}
result={
 'report_date':'2026-11-07','layout_checked_at_utc':datetime.now(timezone.utc).isoformat(),'application':'LibreOffice Writer 25.2.3.2',
 'direct_microsoft_word_application_tested':False,'pages':len(d),
 'figures':len(doc.inline_shapes),'tables':len(doc.tables),
 'word_bytes':word.stat().st_size,
 'word_sha256':hashlib.sha256(word.read_bytes()).hexdigest(),
 'checks':checks,'passed':sum(checks.values()),'total':len(checks),
 'figure_caption_pages':caption_pages,'outside_spans':outside,
 'page_summary':page_data,
 'manual_visual_samples':'Cover, contents, descriptive-statistics tables, worked arithmetic, product chart, heatmap, box plot, recommendations and code pages reviewed.',
}
(ROOT/'reports/layout_verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['page_summary','outside_spans']},indent=2))
if not all(checks.values()):raise SystemExit('Layout verification requires review')
