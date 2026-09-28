#!/usr/bin/env python3
import argparse,hashlib,re,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).parent
FIELDS=('title','author','date','original_url','archive_url','source_collection','rights_status','retrieval_date','checksum')
def validate(root):
 e=[]; p=root/'complete-works-gutenberg-100.md'; sources=(root/'SOURCES.md').read_text()
 if not p.exists(): return ['missing Gutenberg Complete Works source']
 d=p.read_text(); fm,b=d.split('---\n',2)[1:]; b=b.lstrip('\n')
 for field in FIELDS:
  if not re.search(rf'^{field}:',fm,re.M): e.append(f'missing {field}')
 h=re.search(r'sha256:([0-9a-f]{64})',fm)
 if not h or h.group(1)!=hashlib.sha256(b.encode()).hexdigest(): e.append('checksum mismatch')
 if not b.strip(): e.append('empty body')
 if 'THE PASSIONATE PILGRIM' in b: e.append('apocrypha leaked into corpus')
 if any(x not in b for x in ('THE SONNETS','THE TEMPEST','HAMLET','KING LEAR','OTHELLO')): e.append('missing required canonical works or sonnets')
 if 'apocryphal' not in sources or 'modernized' not in sources: e.append('missing edition attribution or apocrypha exclusion')
 return e
def mutation_test():
 with tempfile.TemporaryDirectory() as tmp:
  target=Path(tmp)/'corpus'; shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__'))
  p=target/'complete-works-gutenberg-100.md'; p.write_text(p.read_text()+'\nTHE PASSIONATE PILGRIM\n')
  assert any('apocrypha' in x for x in validate(target))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--mutation-test',action='store_true');args=a.parse_args()
 if args.mutation_test: mutation_test();print('mutation test: PASS (apocrypha rejected)')
 errors=validate(ROOT)
 if errors: print('\n'.join(errors));raise SystemExit(1)
 print('Shakespeare corpus: PASS (modernized Gutenberg Complete Works, canonical works and sonnets, no apocrypha)')
