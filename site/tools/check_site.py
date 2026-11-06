#!/usr/bin/env python3
"""Check static navigation, metadata, assets and structured data."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,sys
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
cfg=json.loads((root/'site_config.json').read_text())
base_path=urlsplit(cfg['origins'][cfg['kind']]).path.rstrip('/')
class Page(HTMLParser):
 def __init__(self): super().__init__();self.ids=set();self.refs=[];self.h1=0;self.title=0;self.description=0;self.scripts=[];self.jsonmode=False;self.jsonbuf=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:
   assert a['id'] not in self.ids,('duplicate id',a['id'])
   self.ids.add(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='title':self.title+=1
  if tag=='meta'and a.get('name')=='description':self.description+=1
  if tag=='img':assert 'alt'in a,('missing alt',a)
  for attr in ('href','src'):
   if attr in a:self.refs.append(a[attr])
  if 'srcset'in a:self.refs.extend(x.strip().split()[0] for x in a['srcset'].split(','))
  if tag=='script'and a.get('type')=='application/ld+json':self.jsonmode=True;self.jsonbuf=''
 def handle_endtag(self,tag):
  if tag=='script'and self.jsonmode:json.loads(self.jsonbuf);self.jsonmode=False
 def handle_data(self,s):
  if self.jsonmode:self.jsonbuf+=s
pages={}
for p in dist.rglob('*.html'):
 if '_qa'in p.parts:continue
 q=Page();q.feed(p.read_text());assert q.h1==1,(p,'h1',q.h1);assert q.title==1 and q.description==1,p
 pages[p.resolve()]=q
for path,page in pages.items():
 for ref in page.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc or ref.startswith('data:'):continue
  assert ref!='#',('empty target',path)
  local_path=u.path
  if local_path.startswith('/') and base_path:
   assert local_path==base_path or local_path.startswith(base_path+'/'),(path,ref,'outside site base path')
   local_path=local_path[len(base_path):] or '/'
  target=(dist/unquote(local_path.lstrip('/')))if local_path.startswith('/')else path.parent/unquote(local_path)
  if not u.path:target=path
  elif u.path.endswith('/'):target=target/'index.html'
  elif target.is_dir():target=target/'index.html'
  assert target.exists(),(path,ref,'missing target')
  if u.fragment and target.resolve()in pages:assert unquote(u.fragment)in pages[target.resolve()].ids,(path,ref,'missing anchor')
text='\n'.join(p.read_text()for p in pages)
for name in ('BrainPumping','Вектор','Самозанят','самозанят','api_key','PRIVATE KEY'):
 assert name not in text,('unexpected public content',name)
assert not list(dist.rglob('*bot-token*'))
assert not any(p.name.startswith('._')for p in dist.rglob('*'))
print(json.dumps({'pages':len(pages),'references':sum(len(p.refs)for p in pages.values()),'html_bytes':sum(p.stat().st_size for p in pages),'result':'passed'},ensure_ascii=False))

