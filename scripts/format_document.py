"""Populate a real TOC and page fields using LibreOffice's UNO bridge.

Optional publishing dependency (Linux): libreoffice-writer, python3-uno.
Start a headless Writer service with the named pipe 'task4lo', then run this
script with the system Python that supplies UNO (often /usr/bin/python3).
The finished .docx is the deliverable; the internal PDF is for layout QA only.
"""
from pathlib import Path
import json
import uno
from com.sun.star.beans import PropertyValue

ROOT=Path(__file__).resolve().parents[1]

def prop(name,value):
    p=PropertyValue();p.Name=name;p.Value=value;return p

local=uno.getComponentContext()
resolver=local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',local)
ctx=resolver.resolve('uno:pipe,name=task4lo;urp;StarOffice.ComponentContext')
desktop=ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop',ctx)
source=uno.systemPathToFileUrl(str(ROOT/'.cache'/'Task4_draft.docx'))
doc=desktop.loadComponentFromURL(source,'_blank',0,(prop('Hidden',True),prop('ReadOnly',False)))
if not doc:raise RuntimeError('Writer could not load the generated draft')
search=doc.createSearchDescriptor();search.SearchString='[TABLE_OF_CONTENTS]'
found=doc.findFirst(search)
if found is None:raise RuntimeError('TOC insertion marker not found')
cursor=found.getText().createTextCursorByRange(found.getStart())
found.setString('')
index=doc.createInstance('com.sun.star.text.ContentIndex')
index.CreateFromOutline=True
index.Level=1
index.Title=''
index.CreateFromMarks=False
cursor.getText().insertTextContent(cursor,index,False)
# Refresh text fields and indexes, then force pagination before saving.
doc.getTextFields().refresh()
for i in range(doc.getDocumentIndexes().getCount()):doc.getDocumentIndexes().getByIndex(i).update()
doc.refresh()
view=doc.getCurrentController().getViewCursor();view.jumpToLastPage()
pages=view.getPage()
for i in range(doc.getDocumentIndexes().getCount()):doc.getDocumentIndexes().getByIndex(i).update()
doc.getTextFields().refresh()
final=ROOT/'reports'/'YuvaIntern_Task4_Real_World_Dataset_Analysis_Revised.docx'
final.parent.mkdir(exist_ok=True)
doc.storeAsURL(uno.systemPathToFileUrl(str(final)),(prop('FilterName','Office Open XML Text'),prop('Overwrite',True)))
pdf=ROOT/'.cache'/'Task4_layout_check.pdf'
filter_data=(prop('UseLosslessCompression',True),prop('ReduceImageResolution',False),prop('ExportBookmarks',True))
doc.storeToURL(uno.systemPathToFileUrl(str(pdf)),(prop('FilterName','writer_pdf_Export'),prop('FilterData',filter_data),prop('Overwrite',True)))
# Normalize Writer's core-properties relationship and preserve attribution explicitly.
# This changes metadata only and does not alter pagination, text, tables or images.
import zipfile
import xml.etree.ElementTree as ET
cp='http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
dc='http://purl.org/dc/elements/1.1/'
ET.register_namespace('cp',cp)
ET.register_namespace('dc',dc)
ET.register_namespace('dcterms','http://purl.org/dc/terms/')
ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
tmp=final.with_suffix('.metadata.docx')
with zipfile.ZipFile(final) as src, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as dst:
    for item in src.infolist():
        data=src.read(item.filename)
        if item.filename=='_rels/.rels':
            data=data.replace(
                b'http://schemas.openxmlformats.org/officedocument/2006/relationships/metadata/core-properties',
                b'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties')
        if item.filename=='docProps/core.xml':
            root=ET.fromstring(data)
            for namespace,key,value in [
                (dc,'creator','T. Aparna Reddy'),
                (dc,'title','Real-World Dataset Analysis | UCI Online Retail | Revised Task 4'),
                (dc,'subject','Complete EDA, transparent cleaning and worked statistical analysis'),
                (cp,'lastModifiedBy','T. Aparna Reddy'),
                (cp,'keywords','Task 4, UCI Online Retail, EDA, evidence-based analysis'),
            ]:
                element=root.find('{'+namespace+'}'+key)
                if element is None:element=ET.SubElement(root,'{'+namespace+'}'+key)
                element.text=value
            data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
        dst.writestr(item,data)
tmp.replace(final)
info={'writer_pages':pages,'toc_indexes':doc.getDocumentIndexes().getCount(),'docx_bytes':final.stat().st_size,'pdf_bytes':pdf.stat().st_size}
(ROOT/'.cache'/'layout_info.json').write_text(json.dumps(info,indent=2))
doc.close(True)
print(json.dumps(info,indent=2))
