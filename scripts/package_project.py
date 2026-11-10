"""Build the complete, credential-free project ZIP and a file-hash manifest.

Run: python scripts/package_project.py
Archive includes the unchanged workbook, both complete cleaned gzip files,
final Word, notebook and all project source/evidence. Caches, credentials,
Git internals, virtual environments and ZIPs are excluded.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.cache','.git','.venv','__pycache__','.ipynb_checkpoints','node_modules'}
manifest_path=ROOT/'PACKAGE_MANIFEST.json'
archive=ROOT/'.cache/Task4_Online_Retail_Complete_Project.zip'
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p==manifest_path:continue
    rel=p.relative_to(ROOT)
    if any(x in EXCLUDE or x.startswith('.env') for x in rel.parts):continue
    if p.suffix.lower()=='.zip' or p.name in {'.git-credentials','.netrc'}:continue
    files.append(p)
manifest={'project':'Revised Task 4: Evidence-Based UCI Online Retail Analysis',
          'author':'T. Aparna Reddy','report_date':'2026-11-07',
          'includes_original_workbook':True,'includes_complete_cleaned_datasets':True,
          'credential_files_included':False,
          'note':'The manifest lists all archived files except itself; public archive link is recorded in the external handoff.',
          'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,
                    'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
manifest_path.write_text(json.dumps(manifest,indent=2))
archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files+[manifest_path]:
        info=zipfile.ZipInfo('Task4_Online_Retail_Project/'+str(p.relative_to(ROOT)),
                             date_time=(2026,11,7,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644 << 16
        z.writestr(info,p.read_bytes())
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('ZIP CRC validation failed')
summary={'file':archive.name,'workspace_path':str(archive),'bytes':archive.stat().st_size,
         'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files)+1,
         'zip_crc_test':'PASS'}
(ROOT/'.cache/archive_verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
