#!/usr/bin/env python3
import argparse,hashlib,re,shutil,tempfile
from pathlib import Path
R=Path(__file__).parent;N=('zur-elektrodynamik-bewegter-koerper.md','inertia-energy-1905.md','special-general-relativity-1917.md');B=('Textdaten','*** START','Transcriber','body {','.x-ebookmaker')
def validate(root):
 e=[]
 for n in N:
  p=root/n;d=p.read_text();fm,b=d.split('---\n',2)[1:];b=b.lstrip('\n');h=re.search(r'sha256:([0-9a-f]{64})',fm)
  if not h or h.group(1)!=hashlib.sha256(b.encode()).hexdigest():e.append(n+': checksum mismatch')
  for x in B:
   if x in b:e.append(n+': prohibited marker '+x)
  if not b.strip():e.append(n+': empty body')
 return e
def mutation():
 for marker in B:
  with tempfile.TemporaryDirectory() as t:
   q=Path(t)/'c';shutil.copytree(R,q,ignore=shutil.ignore_patterns('__pycache__'));p=q/N[0];p.write_text(p.read_text()+'\n'+marker);assert any(marker in x for x in validate(q))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--mutation-test',action='store_true');x=a.parse_args()
 if x.mutation_test:mutation();print('mutation test: PASS (every prohibited-marker rule rejected)')
 e=validate(R)
 if e:print('\n'.join(e));raise SystemExit(1)
 print('Einstein corpus: PASS (three checksummed marker-free sources)')
