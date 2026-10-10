# Andrew Kuznetsov — portfolio

Статический сайт-портфолио. Публикуется через GitHub Pages из папки `site/` (ветка `main`).

- `index.html` — главная (концепт «Spec», v6)
- `cases/<slug>/index.html` — страницы кейсов (первый: `cases/obzhora/`)
- `.nojekyll` — отключает Jekyll, чтобы файлы отдавались как есть
- `CNAME` — кастомный домен (добавляется после покупки)

Исходники шаблонов и ассетов — в корне репозитория (`template-v6.html`, `cases/obzhora/*`), сборка `python3 cases/obzhora/build.py`, обёртка в полноценный HTML — `python3 wrap.py`.
