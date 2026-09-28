#!/usr/bin/env python3
import hashlib, html, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).parent
URL='https://www.gutenberg.org/cache/epub/75107/pg75107-images.html'
ARCHIVE='https://www.gutenberg.org/ebooks/75107'
DATE='2026-09-28'
NOTES=re.compile(r'^NOTE ([A-G])\.—',re.M)
def clean(markup):
 markup=re.sub(r'<(script|style)[^>]*>.*?</\1>','',markup,flags=re.S|re.I)
 markup=re.sub(r'<br\s*/?>','\n',markup,flags=re.I)
 markup=re.sub(r'</(p|div|h[1-6]|li|tr|table|section|blockquote)>','\n',markup,flags=re.I)
 text=html.unescape(re.sub(r'<[^>]+>','',markup)).replace('\xa0',' ').replace('\r','')
 text="\n".join(line.rstrip() for line in text.splitlines())
 text=re.sub(r'\n{3,}','\n\n',text)
 text=text[text.index('NOTE A.—'):]
 return text[:text.index('*** END OF THE PROJECT GUTENBERG EBOOK')].strip()+'\n'
def front(title,checksum):
 return f'''---
title: "{title}"
author: "Ada Lovelace"
date: "1843"
original_url: "{URL}"
archive_url: "{ARCHIVE}"
source_collection: "Project Gutenberg ebook 75107, transcribed from Scientific Memoirs volume 3 (1843)"
rights_status: "Lovelace died in 1852; the 1843 Notes are public domain worldwide under ordinary life-plus-70 terms"
retrieval_date: "{DATE}"
checksum: "sha256:{checksum}"
---

'''
def main():
 req=urllib.request.Request(URL,headers={'User-Agent':'pubky-knowledge-base-corpus-fetch/1.0'})
 with urllib.request.urlopen(req,timeout=30) as r: text=clean(r.read().decode())
 points=[(m.start(),m.group(1)) for m in NOTES.finditer(text)]
 if len(points)!=7: raise ValueError(f'expected Notes A-G, found {len(points)}')
 for p in ROOT.glob('note-*.md'): p.unlink()
 rows=[]
 for i,(start,letter) in enumerate(points):
  body=text[start:(points[i+1][0] if i+1<len(points) else len(text))].strip()+'\n'
  digest=hashlib.sha256(body.encode()).hexdigest(); name=f'note-{letter.lower()}.md'
  (ROOT/name).write_text(front(f'Note {letter}',digest)+body)
  rows.append(f'| ada-note-{letter.lower()} | Lovelace, Note {letter} | Public domain worldwide: Lovelace died in 1852. | Yes | [Gutenberg ebook 75107]({ARCHIVE}), Scientific Memoirs vol. 3 (1843), retrieved {DATE}. | `sha256:{digest}` |')
 (ROOT/'SOURCES.md').write_text('# Ada Lovelace sources\n\n| ID | Item | Rights basis | Copied text | Provenance | SHA-256 |\n| --- | --- | --- | --- | --- | --- |\n'+'\n'.join(rows)+'\n\n## Reference-only correspondence\n\nNo letter body is copied. Known holdings include the British Library, Add MS 37192 (Lovelace–Babbage correspondence), and Bodleian Library Babbage Papers. Betty Alexandra Toole, *Ada, the Enchantress of Numbers* (1992), is in copyright and is reference-only.\n\nMenabrea’s translation is historical context only and is not included in Ada-voice source files.\n')
if __name__=='__main__': main()
