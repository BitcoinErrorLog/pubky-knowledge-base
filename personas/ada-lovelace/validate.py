#!/usr/bin/env python3
import argparse,hashlib,re,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).parent
FIELDS=('title','author','date','original_url','archive_url','source_collection','rights_status','retrieval_date','checksum')
def validate(root):
 errors=[]; sources=(root/'SOURCES.md').read_text(); notes=sorted(root.glob('note-?.md'))
 if [p.stem for p in notes]!=[f'note-{x}' for x in 'abcdefg']: errors.append('expected exactly Notes A-G')
 if 'Reference-only correspondence' not in sources or 'Toole' not in sources: errors.append('missing correspondence rights register')
 context=root/'menabrea-context.md'
 if not context.exists() or 'role: "context-only; never mount as Ada voice"' not in context.read_text(): errors.append('missing labelled Menabrea context')
 elif not re.search(r'checksum: "sha256:[0-9a-f]{64}"', context.read_text()): errors.append('Menabrea context missing checksum')
 for p in notes:
  d=p.read_text();
  if not d.startswith('---\n') or d.count('---\n')<2: errors.append(f'{p.name}: missing frontmatter'); continue
  fm,b=d.split('---\n',2)[1:]; b=b.lstrip('\n')
  for field in FIELDS:
   if not re.search(rf'^{field}:',fm,re.M): errors.append(f'{p.name}: missing {field}')
  h=re.search(r'sha256:([0-9a-f]{64})',fm)
  if not h or h.group(1)!=hashlib.sha256(b.encode()).hexdigest(): errors.append(f'{p.name}: checksum mismatch')
  if not b.strip(): errors.append(f'{p.name}: empty body')
  if 'ARTICLE XXIX.' in b or 'BEFORE submitting to our readers' in b: errors.append(f'{p.name}: Menabrea/editor context leaked into voice source')
 return errors
def mutation_test():
 with tempfile.TemporaryDirectory() as tmp:
  target=Path(tmp)/'corpus'; shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__'))
  p=target/'note-g.md'; p.write_text(p.read_text()+'\nARTICLE XXIX.\n')
  assert any('Menabrea/editor context' in e for e in validate(target))
if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('--mutation-test',action='store_true'); args=parser.parse_args()
 if args.mutation_test: mutation_test(); print('mutation test: PASS (context leak rejected)')
 errors=validate(ROOT)
 if errors: print('\n'.join(errors)); raise SystemExit(1)
 print('Ada Lovelace corpus: PASS (Notes A-G, checksums, provenance, and reference-only letters verified)')
