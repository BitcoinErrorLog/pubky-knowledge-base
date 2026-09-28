#!/usr/bin/env python3
import hashlib, html, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).parent
URL='https://www.gutenberg.org/cache/epub/75107/pg75107-images.html'
ARCHIVE='https://www.gutenberg.org/ebooks/75107'
DATE='2026-09-28'
NOTES=re.compile(r'^NOTE ([A-G])\.—',re.M)
def clean(markup, notes_only=True):
 markup=re.sub(r'<(script|style)[^>]*>.*?</\1>','',markup,flags=re.S|re.I)
 def image_alt(match):
  alt=re.search(r'\balt="([^"]*)"',match.group(0),re.I)
  return '\n'+html.unescape(alt.group(1))+'\n' if alt else ''
 markup=re.sub(r'<img\b[^>]*>',image_alt,markup,flags=re.I)
 markup=re.sub(r'<br\s*/?>','\n',markup,flags=re.I)
 markup=re.sub(r'</(p|div|h[1-6]|li|tr|table|section|blockquote)>','\n',markup,flags=re.I)
 text=html.unescape(re.sub(r'<[^>]+>','',markup)).replace('\xa0',' ').replace('\r','')
 text="\n".join(line.rstrip() for line in text.splitlines())
 text=re.sub(r'\n{3,}','\n\n',text)
 if notes_only:
  text=text[text.index('NOTE A.—'):text.index('Transcriber’s Notes')]
 end=text.find('*** END OF THE PROJECT GUTENBERG EBOOK')
 return text[:end if end >= 0 else len(text)].strip()+'\n'
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
 with urllib.request.urlopen(req,timeout=30) as r: markup=r.read().decode()
 text=clean(markup)
 full=clean(markup, notes_only=False)
 points=[(m.start(),m.group(1)) for m in NOTES.finditer(text)]
 if len(points)!=7: raise ValueError(f'expected Notes A-G, found {len(points)}')
 for p in ROOT.glob('note-*.md'): p.unlink()
 rows=[]
 for i,(start,letter) in enumerate(points):
  body=text[start:(points[i+1][0] if i+1<len(points) else len(text))].strip()+'\n'
  digest=hashlib.sha256(body.encode()).hexdigest(); name=f'note-{letter.lower()}.md'
  (ROOT/name).write_text(front(f'Note {letter}',digest)+body)
  rows.append(f'| ada-note-{letter.lower()} | Lovelace, Note {letter} | Public domain worldwide: Lovelace died in 1852. | Yes | [Gutenberg ebook 75107]({ARCHIVE}), Scientific Memoirs vol. 3 (1843), retrieved {DATE}. | `sha256:{digest}` |')
 start=full.index('THOSE labours which')
 end=full.rfind('NOTES BY THE TRANSLATOR.', 0, full.index('NOTE A.—'))
 context=full[start:end].strip()+'\n'; digest=hashlib.sha256(context.encode()).hexdigest()
 (ROOT/'menabrea-context.md').write_text(f'''---\ntitle: \"Sketch of the Analytical Engine — Menabrea translation\"\nauthor: \"Luigi Menabrea; translated by Ada Lovelace\"\ndate: \"1843\"\noriginal_url: \"{URL}\"\narchive_url: \"{ARCHIVE}\"\nsource_collection: \"Project Gutenberg ebook 75107, Scientific Memoirs volume 3 (1843)\"\nrights_status: \"Menabrea died in 1896 and Lovelace in 1852; this 1843 translation is public domain worldwide under ordinary life-plus-70 terms\"\nretrieval_date: \"{DATE}\"\nchecksum: \"sha256:{digest}\"\nrole: \"context-only; never mount as Ada voice\"\n---\n\n'''+context)
 rows.append(f'| menabrea-context-1843 | Menabrea translation by Lovelace | Public domain worldwide: Menabrea died 1896 and Lovelace 1852. | Yes, context only | [Gutenberg ebook 75107]({ARCHIVE}), retrieved {DATE}; never mount as Ada voice. | `sha256:{digest}` |')
 (ROOT/'SOURCES.md').write_text('# Ada Lovelace sources\n\n| ID | Item | Rights basis | Copied text | Provenance | SHA-256 |\n| --- | --- | --- | --- | --- | --- |\n'+'\n'.join(rows)+'\n\n## Extraction integrity\n\nThe fetcher preserves Gutenberg image `alt` text and formula text, including the Note G Bernoulli table, and cuts Note G before Gutenberg’s Transcriber’s Notes. The validator rejects either a transcriber-note boundary failure or missing Bernoulli table/formula cells.\n\n## Reference-only correspondence\n\nNo letter body is copied. Known holdings include the British Library, Add MS 37192 (Lovelace–Babbage correspondence), and Bodleian Library Babbage Papers. Betty Alexandra Toole, *Ada, the Enchantress of Numbers* (1992), is in copyright and is reference-only.\n\nMenabrea’s translation is labelled context-only and is excluded from Ada voice material.\n')
if __name__=='__main__': main()
