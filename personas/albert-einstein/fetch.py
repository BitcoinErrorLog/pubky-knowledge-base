#!/usr/bin/env python3
import hashlib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
R=Path(__file__).parent; T='Zur Elektrodynamik bewegter Körper'; D='2026-09-28'
def main():
 u='https://de.wikisource.org/w/api.php?'+urllib.parse.urlencode({'action':'parse','page':T,'prop':'text','format':'json'})
 req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
 raw=json.load(urllib.request.urlopen(req))['parse']['text']['*']; raw=re.sub(r'<(script|style)[^>]*>.*?</\1>','',raw,flags=re.S|re.I);raw=re.sub(r'<br\s*/?>','\n',raw,flags=re.I);raw=re.sub(r'</(p|div|h[1-6]|li|tr|table|section)>','\n',raw,flags=re.I)
 s=html.unescape(re.sub(r'<[^>]+>','',raw)).replace('\xa0',' ');s='\n'.join(x.rstrip() for x in s.splitlines());s=re.sub(r'\n{3,}','\n\n',s);s=s[s.index('Zur Elektrodynamik bewegter Körper;'):];h=hashlib.sha256((s.strip()+'\n').encode()).hexdigest()
 (R/'zur-elektrodynamik-bewegter-koerper.md').write_text(f'''---
title: "{T}"
author: "Albert Einstein"
date: "1905"
original_url: "https://de.wikisource.org/wiki/Zur_Elektrodynamik_bewegter_Körper"
archive_url: "{u}"
source_collection: "Annalen der Physik 17 (1905); German Wikisource transcription"
rights_status: "Author died 1955; public domain in life-plus-70 countries from 2026; published before 1931, public domain in the US. Transcription CC BY-SA 4.0."
retrieval_date: "{D}"
checksum: "sha256:{h}"
---

'''+s.strip()+'\n')
 (R/'SOURCES.md').write_text(f'''# Albert Einstein sources

| ID | Item | Rights basis | Copied text | Provenance | SHA-256 |
|---|---|---|---|---|---|
| einstein-electrodynamics-1905 | *{T}* | Author died 1955; public domain in life-plus-70 countries from 2026; published before 1931, public domain in the US. Transcription CC BY-SA 4.0. | Yes | [German Wikisource](https://de.wikisource.org/wiki/Zur_Elektrodynamik_bewegter_Körper), retrieved {D}. | `sha256:{h}` |

## Reference-only

No exact Wikisource leaf transcription resolved for *Die Grundlage der allgemeinen Relativitätstheorie* (1916), *Über die spezielle und die allgemeine Relativitätstheorie* (1917), *Äther und Relativitätstheorie* (1920), or *Geometrie und Erfahrung* (1921); no body is copied. Lawson’s 1920 English translation is reference-only because Lawson died in 1960. All other translations are reference-only until their translator’s independent public-domain basis is recorded.
''')
if __name__=='__main__':main()
