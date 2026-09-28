#!/usr/bin/env python3
import argparse,hashlib,re,shutil,tempfile
from pathlib import Path
R=Path(__file__).parent; F=('title','author','date','original_url','archive_url','source_collection','rights_status','retrieval_date','checksum')
def validate(root):
 e=[];p=root/'zur-elektrodynamik-bewegter-koerper.md';s=(root/'SOURCES.md').read_text()
 d=p.read_text();fm,b=d.split('---\n',2)[1:];b=b.lstrip('\n')
 for f in F:
  if not re.search(rf'^{f}:',fm,re.M):e.append('missing '+f)
 h=re.search(r'sha256:([0-9a-f]{64})',fm)
 if not h or h.group(1)!=hashlib.sha256(b.encode()).hexdigest():e.append('checksum mismatch')
 if not b.strip():e.append('empty body')
 if 'Lawson' not in s or 'Reference-only' not in s:e.append('missing translation boundary')
 return e
def mutation():
 with tempfile.TemporaryDirectory() as t:
  q=Path(t)/'c';shutil.copytree(R,q,ignore=shutil.ignore_patterns('__pycache__'));p=q/'zur-elektrodynamik-bewegter-koerper.md';p.write_text(p.read_text()+'x');assert 'checksum mismatch' in validate(q)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--mutation-test',action='store_true');x=a.parse_args()
 if x.mutation_test:mutation();print('mutation test: PASS (checksum mutation rejected)')
 e=validate(R)
 if e:print('\n'.join(e));raise SystemExit(1)
 print('Einstein corpus: PASS')
