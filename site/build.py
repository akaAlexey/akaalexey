#!/usr/bin/env python3
"""Build the portfolio and its published fallback snapshots; no credentials or private data."""
from pathlib import Path
import html,json,re,shutil
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist';OUT.mkdir(exist_ok=True)
ORIGIN='https://akaalexey.ru'
DATA=json.loads((ROOT/'content/published.json').read_text())
PAGES={'home':'/','about':'/about/','projects':'/projects/','project-rublemet':'/projects/rublemet/','experience':'/experience/','contact':'/contact/'}
ASSETS=ROOT/'assets'
shutil.copytree(ASSETS,OUT/'assets',dirs_exist_ok=True)
(OUT/'content').mkdir(exist_ok=True);shutil.copy2(ROOT/'content/published.json',OUT/'content/published.json')
E=lambda s:html.escape(str(s or ''),quote=True)
ARROW='<span aria-hidden="true">↗</span>'
def link(l,cls='text-link'):
 return '<a class="'+cls+'" href="'+E(l.get('url'))+'">'+E(l.get('label'))+ARROW+'</a>' if l.get('url') else ''
def img(src):return 'https://api.alexgamelab.ru/v1/media/'+src[6:] if src.startswith('media:') else src
def buttons(d):return '<div class="actions">'+link(d['primary'],'button')+link(d['secondary'],'button secondary')+'</div>'
def hero(d):
 image='https://api.alexgamelab.ru/v1/media/'+str(d['hero_media_id']) if d.get('hero_media_id') else img(d['hero_image'])
 return '<header class="page-hero '+('with-art' if image else '')+'"><div><p class="eyebrow">'+E(d['eyebrow'])+'</p><h1>'+E(d['title'])+'</h1><p class="lead">'+E(d['intro'])+'</p>'+buttons(d)+'</div>'+('<figure><picture>' + ('<source media="(max-width:600px)" srcset="' + E(img(d['hero_mobile_image'])) + '">' if d.get('hero_mobile_image') else '') + '<img src="'+E(image)+'" alt="'+E(d['hero_alt'])+'" width="1600" height="900" fetchpriority="high"></picture><figcaption>Иллюстрация</figcaption></figure>' if image else '')+'</header>'
def blocks(d):
 result=[]
 for i,b in enumerate(d['sections']):
  image='<figure><img src="'+E(img(b['image']))+'" alt="'+E(b.get('alt'))+'" width="1200" height="720" loading="lazy"><figcaption>'+E(b.get('caption'))+'</figcaption></figure>' if b.get('image') else ''
  gallery='<div class="gallery">'+''.join('<figure><picture>' + ('<source media="(max-width:600px)" srcset="' + E(img(d['hero_mobile_image'])) + '">' if d.get('hero_mobile_image') else '') + '<img src="'+E(img(x['src']))+'" alt="'+E(x['alt'])+'" width="900" height="1100" loading="lazy"><figcaption>'+E(x['caption'])+'</figcaption></figure>' for x in b.get('images',[]))+'</div>' if b.get('type')=='gallery' else ''
  result.append('<section class="content-section '+('with-image' if image else '')+'"><span class="index" aria-hidden="true">'+str(i+1).zfill(2)+'</span><div><p class="eyebrow">'+E(b.get('eyebrow'))+'</p><h2>'+E(b['title'])+'</h2><p class="body-copy">'+E(b['body']).replace('\n','<br>')+'</p><div class="actions">'+''.join(link(l) for l in b.get('links',[]))+'</div></div>'+image+gallery+'</section>')
 return ''.join(result)
def nav(path):
 d=DATA['personal/navigation']
 return ''.join('<a href="'+E(l['url'])+'"'+(' aria-current="page"' if path==l['url'] else '')+'>'+E(l['label'])+'</a>' for l in d['links'])
def footer():
 d=DATA['personal/navigation'];return '<div class="footer-top"><a class="wordmark" href="/">'+E(d['title'])+'<span>↗</span></a><p>'+E(d['footer_note'])+'</p><nav aria-label="Другие ссылки">'+''.join(link(l) for b in d['sections'] for l in b.get('links',[]))+'</nav></div><div class="footer-bottom"><span>© 2026 akaalexey</span><a href="/privacy/">Данные и конфиденциальность</a><a href="#top">Наверх ↑</a></div>'
def document(page,path,d,body):
 title=d.get('seo_title') or d['title'];description=d.get('seo_description') or d['intro'];image=img(d.get('seo_image') or d.get('hero_image') or '/assets/redesign/personal-studio-social.jpg');image=ORIGIN+image if image.startswith('/') else image
 if image.endswith('.webp') and 'redesign/personal-studio' in image:image=ORIGIN+'/assets/redesign/personal-studio-social.jpg'
 if image.endswith('.webp') and 'redesign/rublemet-cover' in image:image=ORIGIN+'/assets/redesign/rublemet-cover-social.jpg'
 robots='noindex,follow' if page=='404' else 'index,follow'
 jsdata={'@context':'https://schema.org','@type':'Person','name':'akaalexey','url':ORIGIN,'sameAs':['https://github.com/akaAlexey']}
 return '<!doctype html><html lang="ru" id="top" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,interactive-widget=resizes-content"><meta name="color-scheme" content="light dark"><meta name="theme-color" content="#f0eee5"><meta name="robots" content="'+robots+'"><meta name="description" content="'+E(description)+'"><meta name="referrer" content="strict-origin-when-cross-origin"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; img-src \'self\' data: https://api.alexgamelab.ru; style-src \'self\'; script-src \'self\'; font-src \'self\'; connect-src \'self\' https://api.alexgamelab.ru; base-uri \'self\'; form-action \'none\'; object-src \'none\'"><link rel="canonical" href="'+ORIGIN+path+'"><link rel="icon" href="/assets/personal-mark.svg" type="image/svg+xml"><meta property="og:type" content="website"><meta property="og:title" content="'+E(title)+'"><meta property="og:description" content="'+E(description)+'"><meta property="og:url" content="'+ORIGIN+path+'"><meta property="og:image" content="'+E(image)+'"><meta name="twitter:card" content="summary_large_image"><title>'+E(title)+'</title><script src="/assets/theme.js"></script><link rel="stylesheet" href="/assets/site.css"><link rel="preload" href="/assets/fonts/noto-sans-regular.woff" as="font" type="font/woff" crossorigin><script type="application/ld+json">'+json.dumps(jsdata,ensure_ascii=False).replace('<','\\u003c')+'</script><script src="/assets/site.js" defer></script></head><body class="page-'+page+'" data-page="'+page+'"><a class="skip" href="#main">К содержимому</a><header class="site-header shell"><a class="wordmark" href="/">'+E(DATA['personal/navigation']['title'])+'<span>↗</span></a><nav id="site-nav" aria-label="Навигация">'+nav(path)+'</nav><div class="header-actions"><button class="icon-button" data-theme-toggle aria-label="Переключить тему"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4m11.2 11.2L19 19M5 19l1.4-1.4M17.6 6.4 19 5"/></svg></button><button class="icon-button menu-button" aria-label="Открыть меню" aria-controls="site-nav" aria-expanded="false" data-menu-toggle><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button></div></header><main id="main" tabindex="-1" class="shell">'+body+'</main><footer class="site-footer shell">'+footer()+'</footer></body></html>'
for key,path in PAGES.items():
 d=DATA['personal/'+key];target=OUT/path.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(document(key,path,d,hero(d)+blocks(d)))
privacy='''<header class="page-hero"><div><p class="eyebrow">ДАННЫЕ</p><h1>Данные и конфиденциальность.</h1><p class="lead">Как работают портфолио, публичный API и переход к AGL ID.</p></div></header><article class="legal"><h2>Публичные страницы</h2><p>Портфолио размещено на GitHub Pages. Изображения и шрифты загружаются с сайта; опубликованные тексты и изображения из медиатеки могут загружаться с API AGL на api.alexgamelab.ru. На этом сайте нет регистрации и контактной формы. Хостинг и API обрабатывают технические данные запросов для доставки страниц.</p><h2>Настройки в браузере</h2><p>Выбранная тема и последняя загруженная публичная редакция страниц сохраняются локально. Это можно удалить вместе с данными сайта в браузере. Аналитические и рекламные счётчики в код сайта не добавлены.</p><h2>AGL ID</h2><p>При переходе к AGL ID используется отдельная система аккаунтов. Она хранит ник, идентификатор аккаунта и, если указана, почту. Данные профиля, роли, игровые сохранения и обращения привязаны к аккаунту. Пароль обрабатывается Keycloak и не хранится в открытом виде. Подробнее — на странице <a href="https://alexgamelab.ru/privacy/">данных AGL</a>.</p><h2>Внешние ссылки</h2><p>Канал AGL, GitHub и другие внешние сервисы работают по своим правилам. Telegram-бот для обращений пока не подключён; ссылка будет добавлена после запуска.</p></article>'''
d=dict(title='Данные и конфиденциальность',intro='Работа портфолио, публичного API и внешних ссылок.',seo_title='Данные и конфиденциальность · akaalexey',seo_description='',hero_image='')
(OUT/'privacy').mkdir(exist_ok=True);(OUT/'privacy/index.html').write_text(document('privacy','/privacy/',d,privacy))
d=dict(title='Страница не найдена',intro='Вернитесь на главную или откройте выбранный проект.',seo_title='Страница не найдена · akaalexey',seo_description='',hero_image='')
(OUT/'404.html').write_text(document('404','/404.html',d,'<section class="page-hero"><div><p class="eyebrow">404</p><h1>Страница не найдена.</h1><a class="button" href="/">На главную ↗</a></div></section>'))
(OUT/'CNAME').write_text('akaalexey.ru\n');(OUT/'.nojekyll').touch();(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+p+'</loc></url>' for p in list(PAGES.values())+['/privacy/'])+'</urlset>')
# Preserve the existing branch-root export as well as the normal Pages artifact.
shutil.copytree(OUT,ROOT.parent,dirs_exist_ok=True)
print(json.dumps({'pages':8,'output':str(OUT),'result':'built'},ensure_ascii=False))
