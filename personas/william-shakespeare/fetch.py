#!/usr/bin/env python3
import hashlib,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).parent
URL='https://www.gutenberg.org/files/100/100-0.txt'
ARCHIVE='https://www.gutenberg.org/ebooks/100'
DATE='2026-09-28'
def body(text):
 start=re.search(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*',text,re.S).end(); end=re.search(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*',text,re.S).start()
 text=text[start:end]
 first=text.find('THE PASSIONATE PILGRIM'); second=text.find('THE PASSIONATE PILGRIM',first+1)
 next_work=text.find('THE PHOENIX AND THE TURTLE',second)
 if min(first,second,next_work)<0: raise ValueError('cannot locate apocrypha boundary')
 return "\n".join(line.rstrip() for line in (text[:second]+text[next_work:]).splitlines() if line.strip() != 'THE PASSIONATE PILGRIM').strip()+'\n'
def main():
 req=urllib.request.Request(URL,headers={'User-Agent':'pubky-knowledge-base-corpus-fetch/1.0'})
 with urllib.request.urlopen(req,timeout=30) as r: text=body(r.read().decode())
 digest=hashlib.sha256(text.encode()).hexdigest()
 (ROOT/'complete-works-gutenberg-100.md').write_text(f'''---
title: "The Complete Works of William Shakespeare"
author: "William Shakespeare"
date: "Project Gutenberg ebook 100"
original_url: "{URL}"
archive_url: "{ARCHIVE}"
source_collection: "Project Gutenberg ebook 100, modernized Complete Works text"
rights_status: "Shakespeare died in 1616; the underlying works are public domain worldwide under ordinary life-plus-70 terms"
retrieval_date: "{DATE}"
checksum: "sha256:{digest}"
---

'''+text)
 (ROOT/'SOURCES.md').write_text(f'''# William Shakespeare sources

| ID | Item | Rights basis | Copied text | Provenance | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| shakespeare-complete-works-gutenberg-100 | *The Complete Works of William Shakespeare* | Shakespeare died in 1616; the works are public domain worldwide. | Yes | [Project Gutenberg ebook 100]({ARCHIVE}), retrieved {DATE}; Gutenberg boilerplate removed. | `sha256:{digest}` |

## Attribution and exclusions

This corpus identifies Gutenberg ebook 100’s modernized *Complete Works* text; spelling and editorial conventions are therefore not First Folio readings. It retains the complete plays and sonnets but excludes *The Passionate Pilgrim*, an apocryphal/misattributed collection. No modern Folger text, notes, performance material, or apocrypha is presented as Shakespeare.
''')
if __name__=='__main__': main()
