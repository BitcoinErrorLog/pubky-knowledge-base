#!/usr/bin/env python3
import hashlib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
R=Path(__file__).parent
F=('title','author','date','original_url','archive_url','source_collection','rights_status','retrieval_date','checksum')
def render(raw):
 raw=re.sub(r'<(script|style)[^>]*>.*?</\1>','',raw,flags=re.S|re.I);raw=re.sub(r'<br\s*/?>','\n',raw,flags=re.I);raw=re.sub(r'</(p|div|h[1-6]|li|tr|table|section)>','\n',raw,flags=re.I);return re.sub(r'\n{3,}','\n\n','\n'.join(x.rstrip() for x in html.unescape(re.sub(r'<[^>]+>','',raw)).splitlines()))
def write(name,title,url,b,collection):
 b=b.strip()+'\n';h=hashlib.sha256(b.encode()).hexdigest();(R/name).write_text(f'''---
title: "{title}"
author: "Albert Einstein"
date: "Pre-1931 original German publication"
original_url: "{url}"
archive_url: "{url}"
source_collection: "{collection}"
rights_status: "Author died 1955; public domain in life-plus-70 countries from 2026; published before 1931, public domain in the US."
retrieval_date: "2026-09-28"
checksum: "sha256:{h}"
---

'''+b);return h
def main():
 t='Ist die Trägheit eines Körpers von seinem Energieinhalt abhängig?';u='https://de.wikisource.org/w/api.php?'+urllib.parse.urlencode({'action':'parse','page':t,'prop':'text','format':'json'});raw=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})))['parse']['text']['*'];b=render(raw);b=b[b.find(t,b.find(t)+1):];h1=write('inertia-energy-1905.md',t,'https://de.wikisource.org/wiki/'+urllib.parse.quote(t.replace(' ','_')) ,b,'German Wikisource transcription')
 u='https://www.gutenberg.org/files/77850/77850-h/77850-h.htm';raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read().decode();b=render(raw);start=b.find('Über die spezielle und die allgemeine Relativitätstheorie',b.find('Über die spezielle und die allgemeine Relativitätstheorie')+1);end=b.find('*** END OF THE PROJECT GUTENBERG EBOOK');b=b[start:end if end>0 else None];h2=write('special-general-relativity-1917.md','Über die spezielle und die allgemeine Relativitätstheorie',u,b,'Project Gutenberg ebook 77850, German 1917 edition')
 s=(R/'SOURCES.md').read_text();s=re.sub(r'\| einstein-inertia.*',f'| einstein-inertia-1905 | *{t}* | Author died 1955; PD life+70 from 2026; pre-1931 US PD. | Yes | German Wikisource. | `sha256:{h1}` |',s);s=re.sub(r'\| einstein-relativity.*',f'| einstein-relativity-1917 | *Über die spezielle und die allgemeine Relativitätstheorie* | Author died 1955; PD life+70 from 2026; pre-1931 US PD. | Yes | Gutenberg 77850; boilerplate and transcriber notes stripped. | `sha256:{h2}` |',s);(R/'SOURCES.md').write_text(s)
if __name__=='__main__':main()
