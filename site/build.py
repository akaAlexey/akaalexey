#!/usr/bin/env python3
"""Build the dependency-free static website from site_config.json."""
from pathlib import Path
import json, html, shutil, re
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
CFG=json.loads((ROOT/'site_config.json').read_text())
KIND=CFG['kind']
ORIGIN=CFG['origins'][KIND].rstrip('/')
BASE_PATH=urlsplit(ORIGIN).path.rstrip('/')
AGL=CFG['origins']['agl'].rstrip('/')
PERSONAL=CFG['origins']['personal'].rstrip('/')
TG='https://t.me/akaAlexey'
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
IS_PERSONAL=KIND=='personal'
ARROW='<span class="arrow" aria-hidden="true">↗</span>'

def button(text,href,secondary=False):
    return f'<a class="button {"secondary" if secondary else "primary"}" href="{href}">{text}{ARROW}</a>'

def tag(text,live=False):
    return f'<span class="tag{" live" if live else ""}">{("<span class=status-dot aria-hidden=true></span>") if live else ""}{text}</span>'

def header():
    if IS_PERSONAL:
        brand='<span class="personal-wordmark">akaalexey<b>.</b></span>'
        items=[('about','Обо мне'),('projects','Проект'),('experience','Опыт'),('contact','Контакты')]
        theme='<button class="icon-button" data-theme-toggle hidden type="button" aria-label="Включить тёмную тему" aria-pressed="false"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4m11.2 11.2L19 19M5 19l1.4-1.4M17.6 6.4 19 5"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M20.8 13.2A8.8 8.8 0 0 1 10.8 3a8.9 8.9 0 1 0 10 10.2Z"/></svg></button>'
    else:
        brand='<img src="/assets/logo.svg" width="42" height="42" alt=""><span class="brand-name">ALEX GAME LAB<small>НЕЗАВИСИМАЯ ИГРОВАЯ КОМАНДА</small></span>'
        items=[('games','Игры'),('studio','Студия'),('team','Команда'),('contact','Контакты')]
        theme=''
    portal_nav=f'<a href="{AGL}/news/">Новости</a><a href="{AGL}/account/">AGL ID ↗</a>'
    nav=''.join(f'<a href="/#{id}">{label}</a>' for id,label in items)
    return f'<a class="skip" href="#main">Перейти к содержимому</a><header class="site-header"><div class="header-inner shell"><a class="brand" href="/" aria-label="{"Алексей akaalexey" if IS_PERSONAL else "Alex Game Lab"} — главная">{brand}</a><nav class="navigation" id="navigation" data-navigation aria-label="Основная навигация">{nav}{portal_nav}</nav><div class="header-actions"><a class="header-cta" href="{TG}">Написать ↗</a>{theme}<button class="icon-button menu-toggle" type="button" data-menu-toggle aria-controls="navigation" aria-expanded="false" aria-label="Открыть меню" hidden><span aria-hidden="true"><span></span><span></span></span></button></div></div></header>'

def footer():
    if IS_PERSONAL:
        title='<a class="personal-wordmark" href="/">akaalexey<b>.</b></a>'
        links=f'<a href="{AGL}">Alex Game Lab ↗</a><a href="{TG}">Telegram ↗</a><a href="/privacy/">Конфиденциальность</a>'
        copy='Алексей · akaalexey'
        note='Разработка ПО и игр'
    else:
        title='<a class="brand-name" href="/">ALEX GAME LAB</a>'
        links=f'<a href="/games/rublemet/">Рублемёт</a><a href="{PERSONAL}">Профиль основателя ↗</a><a href="https://github.com/Alex-Game-Lab">GitHub ↗</a><a href="/privacy/">Конфиденциальность</a>'
        copy='Alex Game Lab'
        note='Независимая игровая команда'
    return f'<footer class="site-footer"><div class="shell"><div class="footer-main">{title}<nav class="footer-links" aria-label="Ссылки в подвале">{links}</nav></div><div class="footer-bottom"><span>© <span data-year>2026</span> {copy}</span><span>{note}</span><a href="#top">Наверх ↑</a></div></div></footer>'

def contact(personal=False):
    if personal:
        content=f'<div><p class="section-label">ДАВАЙТЕ ПОЗНАКОМИМСЯ</p><h2>Есть задача?<br>Давайте обсудим.</h2><p>Открыт к предложениям работы, сотрудничеству и идеям. Можно просто написать и рассказать о своей задаче.</p></div><div class="contact-actions">{button("Написать в Telegram",TG)}<button class="button secondary" type="button" data-copy-contact>Скопировать @akaAlexey</button><span class="copy-status" role="status" aria-live="polite" data-copy-status></span></div>'
    else:
        content=f'<div><p class="section-label">ОБРАТНАЯ СВЯЗЬ</p><h2>У хорошей идеи<br>есть продолжение.</h2><p>Предложения о сотрудничестве, впечатления от «Рублемёта» и идеи для игры можно прислать Алексею.</p></div>{button("Обсудить идею",TG)}'
    return f'<section class="contact-section shell reveal" id="contact"><div class="contact-panel">{content}</div></section>'

def head(title,description,path,cover='rublemet-cover.jpg',noindex=False):
    robots='index,follow' if CFG.get('production') and not noindex else 'noindex,nofollow'
    theme_script='<script src="/assets/theme.js"></script>' if IS_PERSONAL else ''
    data={'@context':'https://schema.org','@type':'Person' if IS_PERSONAL else 'Organization','name':'Алексей · akaalexey' if IS_PERSONAL else 'Alex Game Lab','url':ORIGIN,'sameAs':[TG] if IS_PERSONAL else ['https://github.com/Alex-Game-Lab']}
    if IS_PERSONAL:
        data.update({'givenName':'Алексей','jobTitle':'Разработчик ПО и игр, основатель AGL','image':ORIGIN+'/assets/alexey-portrait.webp','affiliation':{'@type':'Organization','name':'Alex Game Lab','url':AGL},'knowsAbout':['Python','SQL','JavaScript','Разработка игр','Игровые механики','Сюжет и тексты']})
    else:
        data.update({'logo':ORIGIN+'/assets/logo.svg','founder':{'@type':'Person','name':'Алексей','url':PERSONAL}})
    return f'''<!doctype html><html lang="ru" id="top" class="{"personal" if IS_PERSONAL else "agl"}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="{"#f7f5ef" if IS_PERSONAL else "#0b0c16"}">
<meta name="description" content="{html.escape(description,quote=True)}"><meta name="robots" content="{robots}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'none'; object-src 'none'">
<link rel="canonical" href="{ORIGIN}{path}"><link rel="icon" href="/assets/{"personal-mark.svg" if IS_PERSONAL else "logo.svg"}" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:title" content="{html.escape(title,quote=True)}"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{ORIGIN}{path}"><meta property="og:image" content="{ORIGIN}/assets/{cover}"><meta property="og:image:alt" content="{"Аниме-образ Алексея akaalexey" if cover.startswith("alexey") else "Иллюстрация игрового мира"}">
<meta name="twitter:card" content="summary_large_image"><title>{html.escape(title)}</title>
{theme_script}<link rel="preload" href="/assets/fonts/noto-sans-regular.woff" as="font" type="font/woff" crossorigin><link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{json.dumps(data,ensure_ascii=False).replace('<','\\u003c')}</script><script src="/assets/site.js" defer></script></head><body>'''

def page(path,title,description,body,cover='rublemet-cover.jpg',noindex=False):
    target=OUT/(path.strip('/')+'/index.html' if path!='/' else 'index.html')
    if path=='/404.html':target=OUT/'404.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    document=head(title,description,path,cover,noindex)+header()+'<main id="main">'+body+'</main>'+footer()+'</body></html>'
    if BASE_PATH:
        document=re.sub(r'\b(href|src|srcset)="(/(?!/)[^"]*)"',lambda m:f'{m[1]}="{BASE_PATH}{m[2]}"',document)
    target.write_text(document)

def agl_home():
    return f'''
<section class="agl-hero"><div class="shell"><div class="hero-copy entrance"><p class="eyebrow"><span class="status-dot" aria-hidden="true"></span> ALEX GAME LAB · НЕЗАВИСИМАЯ КОМАНДА</p><h1>Создаём игры,<br>в которых есть<br><em>характер.</em></h1><p class="hero-lead">Механики, истории и немного смелости. Мы — Alex Game Lab. Сейчас работаем над «Рублемётом» и его игровым миром.</p><div class="button-row">{button("Наш проект","#games")}{button("О команде","#team",True)}</div></div><picture class="hero-art entrance-delay"><source media="(max-width:760px)" srcset="/assets/agl-mobile.webp"><img src="/assets/agl-hero.webp" alt="" width="1672" height="941" fetchpriority="high"></picture><div class="hero-bottom"><span>ОДИН ПРОЕКТ. МНОГО ИДЕЙ.</span><a href="/games/rublemet/">Сейчас в работе — Рублемёт ↗</a></div></div></section>
<section class="section shell" id="games"><div class="section-top reveal"><div><p class="section-label">01 / НАШ ПРОЕКТ</p><h2>Начинаем<br>с «Рублемёта»<span class="accent">.</span></h2></div><p>Простое действие становится началом большой истории. Знакомьтесь с нашей игрой для Android.</p></div><article class="feature-card reveal"><div class="feature-visual"><img src="/assets/rublemet-cover.webp" alt="Промо-иллюстрация «Рублемёта»: герой на тёплой городской улице" width="1536" height="864" loading="lazy"><span class="visual-caption">ИЛЛЮСТРАЦИЯ МИРА ИГРЫ</span></div><div class="feature-body">{tag("В разработке",True)}<h3>Рублемёт</h3><p>Работа, деньги и неожиданные повороты карьеры. История роста, в которой нашлось место профессиям, мини-играм и собственным решениям.</p><div class="tags">{tag("Android")}{tag("Кликер / история")}</div><a class="text-link" href="/games/rublemet/">Познакомиться с игрой <span aria-hidden="true">↗</span></a><p class="small-note" style="margin-top:21px">Дата выхода будет объявлена после завершения тестирования.</p></div></article></section>
<section class="section shell" id="studio"><div class="studio-grid"><div class="studio-copy reveal"><p class="section-label">02 / СТУДИЯ</p><h2>Идея важна.<br>Детали решают.</h2><div class="principle"><span>01</span><div><h3>Интересная механика</h3><p>Игроку должно быть интересно действовать, пробовать и замечать, как меняется его игровой мир.</p></div></div><div class="principle"><span>02</span><div><h3>Живые истории</h3><p>Персонажи, диалоги и маленькие события делают прогресс личной историей игрока.</p></div></div><div class="principle"><span>03</span><div><h3>Внимание к качеству</h3><p>Развитие проекта складывается из последовательной работы над игровым опытом, текстами и визуальными деталями.</p></div></div></div><figure class="studio-art reveal"><img src="/assets/agl-studio.webp" alt="Объёмная иллюстрация мастерской: раскадровки, игровые фигуры и детали мира" width="1536" height="1024" loading="lazy"></figure></div></section>
<section class="section shell" id="team"><div class="section-top reveal"><div><p class="section-label">03 / КОМАНДА</p><h2>За проектом — люди.</h2></div></div><article class="team-card reveal"><div class="team-avatar"><img src="/assets/alexey-portrait.webp" alt="Аниме-образ Алексея akaalexey" width="1312" height="1200" loading="lazy"></div><div class="team-body"><h3>Алексей <span class="violet">· akaalexey</span></h3><p class="role">Основатель AGL · Руководитель проекта</p><p>Работаю над игровыми механиками, сюжетом и текстами «Рублемёта». На личном сайте — подробнее обо мне, опыте и моём вкладе в проект.</p><div class="button-row">{button("Личный сайт",PERSONAL,True)}</div></div></article><p class="team-note">Не все участники команды представлены публично.</p></section>
{contact()}'''

def personal_home():
    return f'''
<section class="personal-hero shell"><div class="hero-copy entrance"><p class="eyebrow"><span class="status-dot" aria-hidden="true"></span> ОТКРЫТ К ПРЕДЛОЖЕНИЯМ И ИДЕЯМ</p><h1>Алексей.<br>В сети —<br><span>akaalexey.</span></h1><p class="hero-lead">Разработчик ПО и игр. Основатель AGL и руководитель проекта. В продуктовом программировании — капитан команды.</p><div class="button-row">{button("Обсудить работу",TG)}{button("Мой проект","#projects",True)}</div></div><figure class="portrait-stage entrance-delay"><svg class="portrait-star" width="66" height="66" viewBox="0 0 66 66" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" aria-hidden="true"><path d="M33 5v56M5 33h56M13 13l40 40M13 53l40-40"/></svg><img src="/assets/alexey-portrait.webp" alt="Аниме-образ Алексея: короткие каштановые волосы, очки и голубая рубашка" width="1312" height="1200" fetchpriority="high"><figcaption class="portrait-label"><strong>Идея → продукт</strong>Код, механики и истории</figcaption></figure></section>
<div class="stats shell"><div class="stat"><strong>5</strong><span>лет занимаюсь<br>разработкой сайтов</span></div><div class="stat"><strong>3</strong><span>года создаю<br>приложения</span></div><div class="stat"><strong>II</strong><span>спортивный разряд<br>по программированию</span></div></div>
<section class="section shell" id="about"><div class="about-grid"><div class="reveal"><p class="section-label">01 / ОБО МНЕ</p><h2>Разбираюсь.<br>Придумываю.<br>Довожу до продукта.</h2></div><div class="about-copy reveal"><p>Меня зовут Алексей, в сети — akaalexey. Я разрабатываю программное обеспечение и игры, основал Alex Game Lab и руковожу проектом «Рублемёт».</p><p>Работаю с Python, SQL и JavaScript, владею C++ на базовом уровне. Использую нейросети в работе над продуктами. Интересуюсь задачами, в которых нужны и техническое понимание, и работа с идеей.</p><p>В «Рублемёте» моя зона ответственности — игровые механики, сюжет и тексты, а также руководство проектом.</p><div class="skills"><span class="skill">Python</span><span class="skill">SQL</span><span class="skill">JavaScript</span><span class="skill">C++ <small>базовый</small></span></div></div></div></section>
<section class="section shell" id="projects"><div class="section-top reveal"><div><p class="section-label">02 / ПРОЕКТ</p><h2>Игра, над которой<br>работаю сейчас.</h2></div><a class="text-link" href="{AGL}">Alex Game Lab <span aria-hidden="true">↗</span></a></div><article class="feature-card reveal"><div class="feature-visual"><img src="/assets/rublemet-cover.webp" alt="Промо-иллюстрация игрового мира «Рублемёта»" width="1536" height="864" loading="lazy"><span class="visual-caption">ПРОЕКТ ALEX GAME LAB</span></div><div class="feature-body">{tag("В разработке",True)}<h3>Рублемёт</h3><p>Игра о работе, деньгах и переменах. Механики развития, маленькие истории и персонажи складываются в один игровой путь.</p><div class="tags">{tag("Игровые механики")}{tag("Сюжет и тексты")}{tag("Руководство")}</div><a class="text-link" href="/projects/rublemet/">Мой вклад в проект <span aria-hidden="true">↗</span></a></div></article></section>
<section class="section shell" id="experience"><div class="section-top reveal"><div><p class="section-label">03 / ОПЫТ И ДОСТИЖЕНИЯ</p><h2>Практика, команда<br>и сложные задачи.</h2></div></div><div class="credentials"><article class="credential reveal"><span class="credential-icon" aria-hidden="true">↗</span><h3>Капитан команды</h3><p>Участвую в продуктовом программировании как капитан команды — team lead.</p></article><article class="credential reveal"><span class="credential-icon" aria-hidden="true">II</span><h3>Спортивный разряд</h3><p>Имею второй спортивный разряд по спортивному программированию.</p></article><article class="credential reveal"><span class="credential-icon" aria-hidden="true">⌘</span><h3>Алгоритмы и CTF</h3><p>Участвовал и занимал призовые места в соревнованиях по алгоритмическому программированию и CTF.</p></article></div></section>
<section class="section shell"><div class="workspace-grid"><figure class="workspace-image reveal"><img src="/assets/alexey-workspace.webp" alt="Иллюстрация: аниме-образ Алексея за столом с ноутбуком и блокнотом" width="1536" height="1024" loading="lazy"></figure><div class="workspace-copy reveal"><p class="section-label">04 / НАПРАВЛЕНИЯ</p><h2>На стыке<br>технологий и идей.</h2><p>Интересны руководство игровыми проектами, управление IT-продуктами и разработка игровых концепций. Готов рассматривать и другие направления.</p><p>Ценю обратную связь: впечатления, предложения и вопросы помогают увидеть продукт с другой стороны.</p><div class="button-row">{button("Познакомиться",TG,True)}</div></div></div></section>
{contact(True)}'''

def game_page(personal=False):
    crumb='Мой проект' if personal else 'Игры'
    first=f'<section class="page-hero shell"><nav class="breadcrumbs" aria-label="Хлебные крошки"><a href="/">{"Алексей · akaalexey" if personal else "Alex Game Lab"}</a><span aria-hidden="true">/</span><span>{crumb}</span></nav><p class="eyebrow">{"ЛИЧНЫЙ ВКЛАД В ПРОЕКТ AGL" if personal else "ПРОЕКТ ALEX GAME LAB"}</p><h1>Рублемёт<span class="violet">.</span><br>{"Механики и история." if personal else "У каждого пути — своя история."}</h1><p class="lead">{"Работаю над игровыми механиками, сюжетом и текстами, а также руковожу проектом. Здесь — моя зона ответственности в игре AGL." if personal else "Игра о работе, деньгах и переменах. Начать с простого дела, открыть новые возможности и пройти собственную историю."}</p><div class="tags">{tag("В разработке",True)}{tag("Android")}{tag("Кликер / история")}</div><figure class="cover-image"><img src="/assets/rublemet-cover.webp" width="1536" height="864" alt="Промо-иллюстрация: герой «Рублемёта» на городской улице" fetchpriority="high"><figcaption>Промо-иллюстрация мира «Рублемёта». Не снимок игрового интерфейса.</figcaption></figure></section>'
    if personal:
        return first+f'''
<section class="section shell"><div class="section-top reveal"><div><p class="section-label">МОЯ РОЛЬ</p><h2>От игрового действия<br>до истории.</h2></div></div><div class="detail-rows"><article class="detail-row reveal"><span>01</span><h3>Игровые механики</h3><p>Работаю над тем, какие действия выполняет игрок и как они связаны с развитием. В «Рублемёте» важны понятный прогресс, новые возможности и связь механик между собой.</p></article><article class="detail-row reveal"><span>02</span><h3>Сюжет и тексты</h3><p>Занимаюсь сюжетной частью и текстами: историями, персонажами и их репликами. Они должны поддерживать игровой путь и оставаться понятными и естественными.</p></article><article class="detail-row reveal"><span>03</span><h3>Руководство проектом</h3><p>Определяю направление развития проекта и координирую работу над ним. «Рублемёт» создаётся в AGL; мой личный вклад здесь выделен отдельно от работы команды.</p></article></div><div class="button-row">{button("Страница игры в AGL",AGL+"/games/rublemet/")}{button("Обсудить работу",TG,True)}</div></section>{contact(True)}'''
    return first+f'''
<section class="section shell"><div class="two-col"><div class="reveal"><p class="section-label">ОБ ИГРЕ</p><h2>Простое начало.<br>Новые возможности.</h2></div><div class="body-copy reveal"><p>«Рублемёт» соединяет кликер, развитие карьеры, мини-игры и сюжетные эпизоды. Привычное действие становится частью большего пути: новые профессии, события и знакомство с персонажами.</p><p>Игра разрабатывается для Android. Сейчас проект проходит разработку и тестирование; дата публичного релиза пока не объявлена.</p><div class="button-row">{button("Отзыв или идея",TG,True)}</div></div></div></section>
<section class="section shell"><div class="section-top reveal"><div><p class="section-label">АТМОСФЕРА</p><h2>Знакомый город.<br>Необычный путь.</h2></div><p>Иллюстрации из игрового мира. Откройте изображение, чтобы рассмотреть детали.</p></div><div class="art-grid"><figure class="reveal"><a href="/assets/rublemet-street.webp" data-preview-image data-image-alt="Городская улица из игрового мира «Рублемёта»"><img src="/assets/rublemet-street.webp" alt="Городская улица из игрового мира «Рублемёта»" width="900" height="1600" loading="lazy"></a><figcaption>Город и его маленькие истории ↗</figcaption></figure><figure class="reveal"><a href="/assets/rublemet-character.webp" data-preview-image data-image-alt="Один из образов героя «Рублемёта»"><img class="character-art" src="/assets/rublemet-character.webp" alt="Образ героя в светлом костюме" width="450" height="600" loading="lazy"></a><figcaption>Один из образов игрового героя ↗</figcaption></figure></div></section>
<section class="section shell"><div class="section-top reveal"><div><p class="section-label">ВОПРОСЫ</p><h2>Что важно знать.</h2></div></div><div class="faq"><details><summary>На какой платформе будет игра?</summary><p>Проект разрабатывается для Android.</p></details><details><summary>Где скачать «Рублемёт»?</summary><p>Публичный релиз пока не объявлен. Проверенную ссылку на магазин опубликуем на этой странице, когда игра будет готова к выпуску.</p></details><details><summary>Как предложить идею или сообщить об ошибке?</summary><p>Напишите Алексею в <a class="text-link" href="{TG}">Telegram ↗</a>. Для ошибки полезно описать, что происходило и какой результат вы ожидали.</p></details><details><summary>Кто работает над проектом?</summary><p>Игра создаётся в AGL. Основатель и руководитель проекта — <a class="text-link" href="{PERSONAL}">Алексей · akaalexey ↗</a>. Остальные участники не представлены публично.</p></details></div></section>
{contact()}<dialog class="image-dialog" data-image-dialog aria-labelledby="gallery-caption"><header><span id="gallery-caption" data-image-caption></span><button type="button" aria-label="Закрыть изображение">Закрыть ×</button></header><img src="/assets/rublemet-street.webp" alt=""></dialog>'''

def privacy():
    theme='<h2>Настройка темы</h2><p>Выбранная светлая или тёмная тема сохраняется в локальном хранилище браузера. Это функциональная настройка; она не отправляется владельцу сайта и не используется для отслеживания. Её можно удалить вместе с данными сайта в браузере.</p>' if IS_PERSONAL else ''
    return f'''<section class="page-hero shell"><nav class="breadcrumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span aria-hidden="true">/</span><span>Конфиденциальность</span></nav><p class="eyebrow">ДАННЫЕ И СВЯЗЬ</p><h1>Конфиденциальность.</h1><p class="lead">Как устроена эта версия сайта и что происходит при переходе к внешним сервисам.</p></section><article class="legal shell"><p class="small-note">Обновлено 6 ноября 2026 года.</p><h2>Что делает сайт</h2><p>Это информационный сайт {"Алексея (akaalexey)" if IS_PERSONAL else "игровой команды Alex Game Lab"}. На страницах нет регистрации, контактных форм, оплаты, рассылки и подключённых счётчиков аналитики. Сайт не запрашивает имя, почту или номер телефона посетителя.</p><p>Шрифты, иллюстрации и сценарии загружаются с самого сайта. Код сайта не устанавливает рекламные или аналитические cookies.</p>{theme}<h2>Техническая работа хостинга</h2><p>Эта версия размещена на GitHub Pages. Для доставки страниц и обеспечения работы сервиса провайдер может обрабатывать технические сведения запроса, включая IP-адрес и данные браузера. Отсутствие форм и аналитики в коде сайта не означает отсутствия технической обработки у хостинга. Условия провайдера описаны в <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">его политике конфиденциальности</a>.</p><h2>Обращения и внешние ссылки</h2><p>Связаться с Алексеем можно через <a href="{TG}">Telegram @akaAlexey</a>. При переходе к Telegram, GitHub и другим внешним сервисам действуют их условия и практики обработки данных.</p><p>Если вы отправляете сообщение, указанные в нём сведения используются для ответа и обсуждения вашего обращения. Для первого сообщения достаточно описать вопрос; документы и другие дополнительные сведения сайт не запрашивает.</p><h2>Вопросы о данных</h2><p>По вопросам об этой странице или об информации, которую вы ранее прислали Алексею, можно написать в <a href="{TG}">Telegram</a>.</p><h2>Границы этой страницы</h2><p>Информация относится к этому сайту. Она не заменяет отдельное описание обработки данных в приложении «Рублемёт» и других сервисах. При изменении хостинга или добавлении новых функций сведения на этой странице обновляются.</p><div class="button-row">{button("Вернуться на главную","/",True)}</div></article>'''

if IS_PERSONAL:
    page('/','Алексей · akaalexey — разработчик ПО и игр','Разработчик ПО и игр, основатель AGL. Опыт, проект «Рублемёт» и связь для предложений работы и идей.',personal_home(),'alexey-workspace.jpg')
    page('/projects/rublemet/','Рублемёт — мой вклад · akaalexey','Личный вклад Алексея в «Рублемёт»: игровые механики, сюжет, тексты и руководство проектом.',game_page(True))
else:
    page('/','Alex Game Lab — независимая игровая команда','Alex Game Lab: создаём «Рублемёт», работаем над игровыми механиками, историями и визуальным миром.',agl_home(),'agl-hero.jpg')
    page('/games/rublemet/','Рублемёт — игра Alex Game Lab','История, карьера и игровые механики. «Рублемёт» — проект AGL для Android, находящийся в разработке.',game_page())
page('/privacy/','Конфиденциальность · '+('akaalexey' if IS_PERSONAL else 'Alex Game Lab'),'Информация о работе сайта, настройках и внешних сервисах.',privacy(),'alexey-workspace.jpg' if IS_PERSONAL else 'agl-hero.jpg')
error=f'<section class="error-page shell"><div><p class="error-number">404 / СТРАНИЦА НЕ НАЙДЕНА</p><h1>Похоже, мы<br>свернули не туда.</h1><p>Страница могла переехать. Вернёмся к началу?</p><div class="button-row">{button("На главную","/")}</div></div></section>'
page('/404.html','Страница не найдена · '+('akaalexey' if IS_PERSONAL else 'AGL'),'Страница не найдена. Вернитесь на главную.',error,'alexey-workspace.jpg' if IS_PERSONAL else 'agl-hero.jpg',True)
paths=['/','/privacy/','/projects/rublemet/' if IS_PERSONAL else '/games/rublemet/']
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}{p}</loc></url>' for p in paths)+'</urlset>')
(OUT/'robots.txt').write_text('User-agent: *\n'+('Allow: /\n' if CFG.get('production') else 'Disallow: /\n')+'Sitemap: '+ORIGIN+'/sitemap.xml\n')
(OUT/'.nojekyll').touch()
print(json.dumps({'kind':KIND,'pages':len(paths)+1,'output':str(OUT),'origin':ORIGIN},ensure_ascii=False))

