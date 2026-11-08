# Алексей · akaalexey

Личный сайт публикуется независимо от AGL из `akaAlexey/akaalexey` на https://akaalexey.ru/.

Страницы: главная, обо мне, проекты, опыт, контакты, «Рублемёт», конфиденциальность.
Главное меню открывает отдельные HTML-страницы, без прокрутки общего лендинга.

Источник: `build.py`, `site_config.json` и ресурсы `dist/assets/`.
Сборка: `python3 site/build.py`; проверка: `python3 site/tools/check_site.py`
и `node --check site/dist/assets/site.js` из корня репозитория.
Готовый `site/dist/` публикует `.github/workflows/pages.yml`.
`CNAME`, canonical, Open Graph и sitemap используют akaalexey.ru.

Публичный контакт: https://t.me/akaAlexey. AGL ID остаётся на домене AGL.
