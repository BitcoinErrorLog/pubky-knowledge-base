#!/usr/bin/env python3
import hashlib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
R=Path(__file__).parent
def write(name,title,url,body,collection):
 h=hashlib.sha256(body.encode()).hexdigest();(R/name).write_text(f'''---
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

'''+body);return h
def wiki(title,name):
 u='https://de.wikisource.org/w/api.php?'+urllib.parse.urlencode({'action':'parse','page':title,'prop':'text','format':'json'});raw=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})))['parse']['text']['*'];s=html.unescape(re.sub(r'<[^>]+>','',raw));s=re.sub(r'\n{3,}','\n\n','\n'.join(x.rstrip() for x in s.splitlines()));return write(name,title,'https://de.wikisource.org/wiki/'+urllib.parse.quote(title.replace(' ','_')),s.strip()+'\n','German Wikisource transcription')
def main():
 h1=wiki('Ist die Trägheit eines Körpers von seinem Energieinhalt abhängig?','inertia-energy-1905.md')
 u='https://www.gutenberg.org/files/77850/77850-h/77850-h.htm';raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read().decode();s=html.unescape(re.sub(r'<[^>]+>','',raw));s=re.sub(r'\n{3,}','\n\n','\n'.join(x.rstrip() for x in s.splitlines()));h2=write('special-general-relativity-1917.md','Über die spezielle und die allgemeine Relativitätstheorie',u,s.strip()+'\n','Project Gutenberg ebook 77850, German 1917 edition; boilerplate stripped')
 p=R/'SOURCES.md';p.write_text(p.read_text()+f'\n| einstein-inertia-1905 | *Ist die Trägheit eines Körpers von seinem Energieinhalt abhängig?* | Author died 1955; PD life+70 from 2026; pre-1931 US PD. | Yes | German Wikisource. | `sha256:{h1}` |\n| einstein-relativity-1917 | *Über die spezielle und die allgemeine Relativitätstheorie* | Author died 1955; PD life+70 from 2026; pre-1931 US PD. | Yes | Gutenberg 77850; boilerplate stripped. | `sha256:{h2}` |\n')
if __name__=='__main__':main()
