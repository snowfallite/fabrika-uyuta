# tech.md: Фабрика Уюта, сайт-визитка

- Версия: v10
- Дата: 2026-11-16
- Каркас: готов
- Статус: контракты заморожены. Любое изменение ядра: бамп версии и строка в Changelog (раздел 3).

## Changelog

Новая строка сверху. Формат: `vN (YYYY-MM-DD): что изменилось`.

- v10 (2026-11-16): подготовка к деплою, решение владельца. Production разворачивается единым `compose.prod.yml` (caddy, db, release, backend, worker, frontend): образы собираются на VPS из репозитория, GHCR, внешняя сеть `edge` и отдельный compose для edge Caddy не нужны. Staging убран, окружений три: dev, e2e, production. Деплой запускает владелец на сервере через `deploy/deploy.sh`, CI на GitHub только проверяет PR; `deploy/edge/`, `deploy/compose.yml`, `deploy-staging.yml` и `release.yml` удалены, проверка `LEGAL_TEXT_PENDING` переехала в `deploy.sh`. Новые переменные `.env`: `DOMAIN` (домен сайта) и `ACME_EMAIL` (почта для Let's Encrypt). Каталог `template/` вынесен из репозитория в архив владельца: вёрстка уже перенесена в компоненты, значения токенов и типографика записаны в разделе 11. Добавлен `README.md`.
- v9 (2026-11-15): VK и MAX выделены в контактах, решение владельца. Новое поле `SiteSettings.vk_url` (ссылка на страницу ВКонтакте, пустое скрывает карточку) и ключ `vk_url` в DTO `SiteSettings`: `social_links` остаётся для прочих сетей, `seed_demo` пишет `vk_url` и ссылок не создаёт. Новые брендовые токены в hex, hsl не годится (округление сдвигает фирменный цвет): `--brand-vk` `#0077FF` (официальный SVG логотипа VK), `--brand-max` `#471AFF` и `--brand-max-accent` `#9500FF` (брендбук MAX, «Синий гигант» и «Пурпурная туманность»), `--brand-foreground` `#FFFFFF`. Знаки из официальных брендбуков лежат в `src/lib/icons/VkLogo.svelte` и `src/lib/icons/MaxLogo.svelte`, `MessageCircle` у MAX больше не нужен. Приложение А: карточки «ВКонтакте» и «MAX» идут брендовым блоком над сеткой контактов, текст на брендовом фоне не меньше 24 px (белый на `--brand-vk` даёт 4,1:1).
- v8 (2026-11-14): контакты и юр. черновики, решение владельца. Новое поле `SiteSettings.max_phone` (E.164, пустое скрывает карточку) и ключи `max_phone`, `max_phone_display` в DTO `SiteSettings`: ссылки на профиль по номеру у MAX нет, номер показывается текстом без ссылки. Приложение А: подпись карточки «MAX», иконка `MessageCircle`. Черновик политики ПДн и согласия пишет сессия, плашка «Проект документа. Текст проверяет юрист.» и маркер `LEGAL_TEXT_PENDING` стоят до текста юриста.
- v7 (2026-09-26): аудит внешнего вида (`.design-audit/REPORT.md`), решение владельца. Плашки hero («Материалы / ЛДСП и МДФ») и about («Индивидуально / под ваше пространство») убраны из приложения А. Токен `--input` отделён от `--border`: `hsl(30 7% 52%)`, граница поля 3,4:1 к фону (было 1,4:1). Новый токен `--success` `hsl(100 25% 32%)` для Alert `success`. Hero: `sizes="(min-width: 1024px) 50vw, 100vw"` вместо `100vw` (фото в половину ширины на десктопе). Плейсхолдер размеров короче: «Стена 3,2 м, высота 2,6 м» (обрезался на 360 px). Новые тексты UI: `aria-label` «Позвонить» у кнопки звонка в шапке на мобильных, счётчик лайтбокса `<n> / <всего>`.
- v6 (2026-09-26): S2-02, расширение контракта примитивов: `autofocus?: boolean` у Input, Textarea, Select, Checkbox, PhoneInput. Без JS фокус на первое ошибочное поле (AC7) ставит только атрибут `autofocus`.
- v5 (2026-09-26): S1-11, каркас готов: contract-guard переходит в режим ошибки, в `.claude/settings.json` добавлены строки `ask` из 16.6. Проверено локально: гейт фронта и бэка, миграции и `makemigrations --check` на Postgres 18, drift `openapi.yaml` и `api.d.ts`, Schemathesis по всем операциям, воркер против фейка и тесты идемпотентности, сид и тестовый эндпоинт, полный стек `compose.e2e.yml` с Caddy, `smoke.sh`, все E2E на 1440 и 360 px, axe. Ждут инфраструктуры владельца: прогоны CI на GitHub и branch protection (`scripts/protect-main.sh`), деплой на staging (VPS, домен), long-lead раздела 20.
- v4 (2026-09-26): S1-10. Деплой-конфиг вне `.env.example`: `deploy.sh` берёт `GHCR_OWNER` (владелец GHCR в нижнем регистре) из окружения; GitHub Secret `STAGING_BASIC_AUTH` (`user:password` для smoke staging) и Variable `DOMAIN`; `/opt/fabrika/edge/.env` для edge Caddy: `DOMAIN`, `ACME_EMAIL`, `PRODUCTION_ADMIN_PATH`, `STAGING_ADMIN_PATH`, `STAGING_BASIC_AUTH_USER`, `STAGING_BASIC_AUTH_HASH`. Том media стека называется `<stack>_media`. `/robots.txt` появляется в S1-10 (AC1 staging), S2-11 его проверяет.
- v3 (2026-09-26): S1-02. Компонентные тесты: браузерный режим Vitest (`vitest-browser-svelte`, `@vitest/browser-playwright`, Chromium), как ставит `sv add vitest`; jsdom и `@testing-library/svelte` не используются. `.env.example`: комментарии к пустым значениям вынесены на отдельные строки, Docker Compose и python-dotenv читают `KEY=   # comment` как значение `# comment`. Фактические версии `sv create`: Kit 2.63, Svelte 5.56, Vite 8, Vitest 4, TypeScript 6, ESLint 10. Конфиг Kit остаётся в `svelte.config.js` (плагин `sveltekit()` без опций читает его). shadcn-svelte 1.7 ставит `cn` (замена clsx и tailwind-merge), `tailwind-variants`, `tw-animate-css`. Правило eslint `svelte/no-navigation-without-resolve` выключено: сайт в корне домена без `paths.base`, ссылки `NAV` с якорями. django-stubs 5.2.x и djangorestframework-stubs 3.16.x под Django 5.2.
- v2 (2026-09-26): S1-01, инвентаризация `template/`. Приложение А заполнено: 11 секций в порядке шаблона, статичные тексты, ассеты. Добавлены секция и якорь `materials` (карточки ЛДСП и МДФ из шаблона). Секция `about` стала «О компании» по шаблону, секции «О производстве» в шаблоне нет. `SiteImageSlot`: `production` заменён на `material_ldsp` и `material_mdf` (фото карточек материалов), `HomeSlots` и счётчики слотов (6, 15.2, 15.3, S1-04, S1-08, S1-09, S2-10) следом: слотов 4. `NAV`: 6 пунктов шаблона. Токены раздела 11 со значениями из `template/src/index.css`. Текстовый шрифт: Manrope вместо Plus Jakarta Sans, у Plus Jakarta Sans нет базовой кириллицы (только `cyrillic-ext`). Контейнер: `max-w-7xl`, поля `px-5 md:px-8` по шаблону. Не переносятся: фильтр галереи по категориям (на главной не больше 12 работ, полная галерея на `/catalog/<slug>`), ссылка «Админ-панель» в подвале (путь админки секретный, 13.1), отдельный текст «Нажимая кнопку…» (его заменяет чекбокс согласия, 12.1). Вторичный текст подвала не прозрачнее `/80`: иначе контраст ниже AA.
- v1 (2026-09-25): первичное ядро. Стек, схема БД, API v1 с заглушками каркаса, контракт Google Sheets и воркера, пайплайн изображений, UI-примитивы, CI/CD, стадии 1 и 2.

---

## 0. Как читать

- Этот файл: единственный источник истины. `CLAUDE.md` импортирует его в каждую сессию Claude Code.
- Приоритет: tech.md > CLAUDE.md > существующий код. Код расходится с tech.md: прав tech.md, сессия сообщает о расхождении.
- Номера разделов стабильны, на них ссылается CLAUDE.md. Новое добавляется подпунктом или разделом в конце.
- Контракт: всё, от чего зависят несколько частей системы (раздел 3).
- Задача: одна задача = одна ветка = один PR (разделы 21, 22).
- Владелец: человек, который ведёт проект. Совмещает тимлида и разработчика.
- Плейсхолдеры: `<domain>` (домен сайта), `<owner>` (владелец репозитория на GitHub), `ABC` (ключ команды в Linear).
- Карта: 1 проект, 2 режим работы, 3 контракты, 4 стек, 5 архитектура, 6 БД, 7 API, 8 Google Sheets, 9 изображения, 10 фронтенд, 11 UI-примитивы, 12 форма, 13 безопасность и 152-ФЗ, 14 конфиг, 15 миграции и сид, 16 CI/CD, 17 тесты, 18 конвенции, 19 DoD и ревью, 20 long-lead, 21 стадия 1, 22 стадия 2, 23 вне скоупа, приложение А.

## 1. Проект

Что: сайт-визитка компании «Фабрика Уюта». Компания производит и продаёт мебель из дерева: кухни под заказ, кухонные столы, шкафы, шкафы-купе, офисную мебель.

Для кого:
- посетитель: частный клиент или компания, выбирает мебель под заказ, оставляет заявку;
- менеджер компании: получает заявки в Google-таблице, перезванивает;
- контент-менеджер компании: загружает фото через админку.

Цель: заявки. Отправленная заявка не теряется, даже если Google недоступен.

Функции v1:
1. Публичный сайт: главная (секции по шаблону), страницы категорий, страница заявки, политика обработки ПДн, согласие на обработку ПДн.
2. Форма заявки: ФИО, телефон, что заказать, примерные размеры, комментарий, согласие на обработку ПДн.
3. Заявка сохраняется в Postgres. Воркер доставляет её в Google-таблицу через API с ретраями.
4. Админка (Django admin): фото главного экрана и секций, обложки категорий, галерея работ, контакты, заявки и статус их отправки.

Нефункциональные требования:
- Lighthouse mobile ≥ 90 во всех четырёх категориях для `/` и `/catalog/<slug>`.
- LCP ≤ 2,5 с на эмуляции 4G, CLS ≤ 0,05.
- Форма отправляется без JavaScript (progressive enhancement).
- Доступность: axe без нарушений уровня serious и critical.
- Русский язык, одна светлая тема, адаптив от 360 px.

## 2. Режим работы

- Один человек совмещает тимлида и разработчика. Файлы ролей не разделены: здесь и обязанности тимлида (каркас, контракты, CI/CD, ревью), и задачи разработчика (слайсы).
- Сессия Claude Code берёт одну задачу из раздела 21 или 22 и выдаёт сфокусированный дифф. Всё приложение за раз не пишется.
- Сессия предлагает, владелец решает: принять ли `CONTRACT GAP`, мёрджить ли PR, выпускать ли релиз.
- День один: задачи S1-01..S2-12 заведены в Linear (заголовок = название задачи, описание = ссылка на раздел), long-lead пункты раздела 20 запущены.
- Две стадии:
  1. Каркас: S1-01..S1-11 строго по порядку. Каркас замораживает всю поверхность контрактов: схему БД, API, типы, примитивы, окружение.
  2. Фичи: вертикальные слайсы S2-01..S2-12. Порядок рекомендованный, зависимости указаны в задаче. Слайс наполняет поведением заглушки каркаса и контракты не меняет.
- Задачи Стадии 2 не начинаются, пока в шапке стоит `Каркас: не готов`. S1-11 переключает строку на `Каркас: готов` с бампом версии.

## 3. Контракты и CONTRACT GAP

| Контракт | Раздел | Машинный артефакт |
|---|---|---|
| Схема БД | 6 | `backend/apps/*/models.py`, `backend/apps/*/migrations/` |
| Перечисления | 6 | `backend/apps/core/enums.py` |
| HTTP API v1 | 7 | `contracts/openapi.yaml` (генерируется) |
| Строка Google Sheets и джоба | 8 | `backend/apps/leads/sheets/row.py` |
| Изображения: DTO и пайплайн | 9 | `ImageAsset` в `openapi.yaml`, `backend/apps/content/services/images.py` |
| Общие TS-типы и API-клиент | 10 | `frontend/src/lib/types/`, `frontend/src/lib/server/api.ts` |
| UI-примитивы и их пропсы | 11 | `frontend/src/lib/components/ui/` |
| Тексты и форматы формы | 12 | `contracts/fixtures/phone-cases.json` |
| Переменные окружения | 14 | `.env.example` |
| Зависимости | 4 | `frontend/package.json`, `backend/pyproject.toml` |

Правило: сессия не выдумывает контракт. Нет нужного типа, поля, эндпоинта, кода ответа, пропса, переменной, текста или зависимости: стоп, блок `CONTRACT GAP` (формат в CLAUDE.md). Код с выдуманным контрактом не пишется.

Контракты меняются только расширением: новое поле, эндпоинт, вариант. Удаление и переименование: отдельная задача, миграции в два релиза (15.1).

Процедура изменения:
1. Сессия выдаёт `CONTRACT GAP` и ждёт решения владельца. Пока ждёт, продолжает только часть задачи, не зависящую от пробела, на локальной заглушке в файлах задачи.
2. Владелец принимает, правит или отклоняет. Решение отложено: задача в Linear с меткой `contract-change`, текст блока в описании.
3. Принято: коммит `docs(tech): vN <summary>` с бампом строки `Версия`, строкой в Changelog и правкой раздела. Он идёт раньше коммитов, которые используют новый контракт.
4. Затем генерируемые артефакты: `make migrations` (схема), `make gen` (OpenAPI и TS-типы).
5. Затем код. Всё в одной ветке и одном PR.

Три уровня защиты:
1. Поведенческий: `CONTRACT GAP` в CLAUDE.md.
2. Процессный: изменение контракта = бамп версии и строка Changelog в том же PR.
3. Тулинговый:
   - CI-джоба `contract-guard` (`scripts/contract_guard.py`): PR меняет замороженный путь без изменения строки `Версия` → красный. Режим берётся из шапки: `Каркас: не готов` → предупреждение, `Каркас: готов` → ошибка. Обход: метка PR `no-contract-change` для правок без изменения интерфейса (стиль примитива, опечатка, `verbose_name`), причина в описании PR.
   - `.claude/settings.json` (16.6): инструменты Claude Code не правят миграции, сгенерированные файлы и шаблон; правка tech.md и замороженных путей требует подтверждения владельца.
   - Branch protection на `main` (16.2).

Замороженные пути:
```
contracts/**
backend/apps/*/migrations/**
backend/apps/core/enums.py
backend/apps/leads/sheets/row.py
frontend/src/lib/types/**
frontend/src/lib/server/api.ts
frontend/src/lib/components/ui/**
.env.example
```
Модели защищены через миграции: `makemigrations --check` в CI требует миграцию на каждую правку схемы. Зависимости guard не проверяет: новая зависимость проходит через `CONTRACT GAP` и пункт 12 чек-листа ревью.

## 4. Стек и версии

| Слой | Выбор | Версия |
|---|---|---|
| Фронтенд | SvelteKit, Svelte (только руны), TypeScript strict, Vite, `@sveltejs/adapter-node` | Kit 2.x, Svelte 5.x |
| Рантайм фронта | Node.js, pnpm | Node 24 LTS |
| Стили | Tailwind CSS: CSS-first, токены в `@theme`, без `tailwind.config.js` | 4.x |
| Примитивы | shadcn-svelte (Bits UI), иконки `@lucide/svelte` | CLI latest |
| Шрифты | self-hosted: `@fontsource-variable/cormorant-garamond` (заголовки), `@fontsource-variable/manrope` (текст), подмножества `latin` и `cyrillic` | |
| Клиент API | `openapi-typescript` (генерация типов), `openapi-fetch` (клиент) | |
| Бэкенд | Python, Django, Django REST Framework, drf-spectacular, gunicorn (`gthread`) | Python 3.13, Django 5.2 LTS, DRF 3.16+ |
| Бэкенд, библиотеки | psycopg 3, Pillow, phonenumberslite, google-auth, requests, django-axes, whitenoise, python-dotenv | |
| БД | PostgreSQL | 18 |
| Очередь | outbox в таблице `leads_lead` + процесс `run_sheets_worker` | без брокера |
| Кэш | Django DatabaseCache: троттлинг заявок, heartbeat воркера | без Redis |
| Интеграция | Google Sheets API v4, сервисный аккаунт | |
| Edge | Caddy: TLS, маршрутизация, раздача media | 2.x |
| Контейнеры | Docker, Docker Compose | |
| Python-окружение | uv | |
| CI/CD | GitHub Actions, GHCR | |
| Трекер | Linear | |
| Гейт фронта | prettier (`prettier-plugin-svelte`, `prettier-plugin-tailwindcss`), eslint (flat config, `eslint-plugin-svelte`, typescript-eslint), svelte-check, knip | |
| Гейт бэка | ruff (lint и format), mypy (django-stubs, djangorestframework-stubs), `makemigrations --check`, drift OpenAPI и TS-типов | |
| Тесты фронта | vitest, Playwright + `@axe-core/playwright`, fast-check | |
| Тесты бэка | pytest + pytest-django, Hypothesis, Schemathesis, responses, pytest-socket | |

Решения:
- Гейт и тесты из ТЗ (prettier, eslint, svelte-check, knip, vitest, Playwright, fast-check) покрывают TypeScript. Бэкенд на Python: добавлены ruff, mypy, pytest, Hypothesis (property-based, аналог fast-check), Schemathesis (ответы API против схемы).
- Django 5.2 LTS, не 6.1: поддержка 5.2 до апреля 2028, 6.1 до декабря 2027; фичи 6.x проекту не нужны. Переход на 6.2 LTS: отдельная задача в 2027.
- SvelteKit 2: версия 3 на дату v1 в release candidate. Переход только через `CONTRACT GAP`.
- Очередь без брокера: десятки заявок в день, Redis и Celery не окупаются.
- Google Sheets через REST v4 и `google-auth` без обёрток: полный контроль таймаутов и HTTP-статусов.
- gunicorn с воркерами `gthread`: долгая загрузка фото в админке не упирается в таймаут воркера.
- Транспорт реального времени (SSE, WebSocket) не нужен: живых данных нет.

Фиксация версий: `pnpm-lock.yaml`, `uv.lock`. Базовые образы по мажору: `python:3.13-slim`, `node:24-slim`, `postgres:18`, `caddy:2`. У `postgres:18` том монтируется в `/var/lib/postgresql`, не в `/var/lib/postgresql/data`: с 18-й версии PGDATA в образе `/var/lib/postgresql/18/docker`.

## 5. Архитектура и структура репозитория

```
Браузер
  │ HTTPS
  ▼
Caddy (сервис того же compose, TLS от Let's Encrypt)
  ├─ /api/*                                    → 404
  ├─ /media/*                                  → файлы из тома media (read-only)
  ├─ /<DJANGO_ADMIN_PATH>*, /django-static/*   → backend:8000
  └─ остальное                                 → frontend:3000

frontend: SvelteKit, adapter-node (SSR, load, form actions)
  │ HTTP + X-Internal-Token + X-Client-IP
  ▼
backend: Django + DRF, gunicorn (/api/v1/*, админка, /healthz)
  │
  ▼
Postgres 18 ◄── worker (образ backend, run_sheets_worker) ──► Google Sheets API v4
```

Принципы:
1. Postgres: источник истины. Google-таблица: проекция для менеджеров, пишет в неё только воркер.
2. SvelteKit: BFF. Браузер не обращается к Django API: Caddy отвечает 404 на `/api/*`, Django требует внутренний токен.
3. Django: домен, валидация, админка, API для SvelteKit, воркер.
4. Один образ backend на три роли: `web` (gunicorn), `worker`, `release` (одноразовый шаг деплоя).
5. Внешние клиенты за интерфейсом с фейком. Разработка и тесты идут без реальных ключей.
6. Каркас объявляет всю поверхность API с заглушками (раздел 7). Слайсы меняют поведение, не схему.

Структура:
```
/
├─ README.md                   # установка, разработка, деплой
├─ tech.md                     # ядро
├─ CLAUDE.md                   # импорт ядра в Claude Code
├─ Makefile                    # единые команды (15.4)
├─ .env.example                # единый файл окружения для бэка и фронта
├─ compose.yml                 # dev: db, backend, worker
├─ compose.e2e.yml             # полный стек из Dockerfile для E2E
├─ compose.prod.yml            # production: caddy, db, release, backend, worker, frontend
├─ .claude/settings.json       # правила доступа Claude Code (16.6)
├─ .github/workflows/ci.yml    # гейт на PR, деплоя в CI нет
├─ contracts/
│  ├─ openapi.yaml             # генерируется, руками не править
│  └─ fixtures/phone-cases.json
├─ scripts/contract_guard.py, scripts/test_contract_guard.py
├─ docs/adr/                   # ADR по решениям о контрактах (19.2)
├─ deploy/
│  ├─ deploy.sh, smoke.sh, backup.sh, RESTORE.md
│  ├─ caddy/Caddyfile          # production: домен, TLS, маршрутизация
│  ├─ caddy/Caddyfile.e2e      # e2e: localhost:8080
│  └─ caddy/site.caddy         # сниппет маршрутизации, общий для e2e и production
├─ backend/
│  ├─ pyproject.toml, uv.lock, Dockerfile, manage.py
│  ├─ config/settings.py, urls.py, wsgi.py
│  ├─ fixtures/demo/           # картинки для seed_demo
│  ├─ var/                     # dev: media и фейковая таблица; в .gitignore
│  └─ apps/
│     ├─ core/                 # enums, env, checks, phone, text, внутренний токен, healthz; команды release, sync_reference_data, seed_demo
│     ├─ content/              # категории, галерея, картинки сайта, контакты, пайплайн изображений
│     └─ leads/                # заявки, API создания, Sheets-клиенты, воркер, алерты, sheets_check
└─ frontend/
   ├─ package.json, Dockerfile, svelte.config.js, vite.config.ts, knip.json, components.json
   ├─ src/app.css, src/app.html, src/hooks.server.ts
   ├─ src/lib/components/ui/      # примитивы (11)
   ├─ src/lib/components/layout/  # Header, MobileNav, Footer, SkipLink, Seo
   ├─ src/lib/features/<feature>/
   ├─ src/lib/domain/             # чистая логика + тесты
   ├─ src/lib/content/            # статичные тексты секций и юр. тексты
   ├─ src/lib/config/nav.ts
   ├─ src/lib/icons/
   ├─ src/lib/server/api.ts
   ├─ src/lib/types/api.d.ts, src/lib/types/index.ts
   ├─ src/routes/
   └─ tests/e2e/
```

Раскладка Django-приложения:
```
apps/<app>/
  models.py
  admin.py
  selectors.py            # чтение: querysets и данные для API
  services/               # запись и бизнес-логика; чистые функции отдельно от ORM
  api/serializers.py, api/views.py, api/urls.py
  management/commands/
  tests/
```
Правила бэкенда: view тонкие, логика в `services`, чтение в `selectors`, сериализатор только валидирует и форматирует. Сигналы только для удаления файлов. Бизнес-логики в admin нет.

Раскладка фичи фронтенда:
```
src/lib/features/<feature>/
  <Feature>.svelte             # секция или виджет
  <Part>.svelte                # локальные компоненты фичи
  <Feature>.svelte.test.ts     # компонентный тест
  <feature>.ts                 # чистая логика фичи, если есть
  <feature>.test.ts            # vitest (+ fast-check)
```
Роут собирает фичи. Компоненты фич не делают запросов: данные приходят пропсами из `load`.

Эталонный слайс: Hero (S1-09). Слайс заменяет заглушку каркаса поведением: селектор, view, админка, UI, тесты. Схема API и модели не меняются. Каждый слайс Стадии 2 повторяет раскладку эталона:
- бэкенд: модель в `apps/content/models.py` (уже есть), селектор в `apps/content/selectors.py`, view в `apps/content/api/views.py`, admin в `apps/content/admin.py`, тесты в `apps/content/tests/`;
- фронтенд: `src/routes/+page.server.ts` (load), `src/routes/+page.svelte` (сборка секций), `src/lib/features/hero/Hero.svelte`, `src/lib/features/hero/Hero.svelte.test.ts`, E2E `tests/e2e/home.spec.ts`.

## 6. Схема БД

Таблицы по умолчанию Django: `<app>_<model>`. Время в БД в UTC (`USE_TZ = True`), отображение `Europe/Moscow`.

```python
# backend/apps/core/enums.py
from django.db import models


class ProductKind(models.TextChoices):
    KITCHENS = "kitchens", "Кухни под заказ"
    KITCHEN_TABLES = "kitchen-tables", "Кухонные столы"
    WARDROBES = "wardrobes", "Шкафы"
    SLIDING_WARDROBES = "sliding-wardrobes", "Шкафы-купе"
    OFFICE = "office", "Офисная мебель"
    OTHER = "other", "Другое"


# Every kind except OTHER has a category page; the value doubles as the URL slug.
CATEGORY_SLUG_CHOICES = [(v, label) for v, label in ProductKind.choices if v != ProductKind.OTHER]


class SiteImageSlot(models.TextChoices):
    HERO = "hero", "Главный экран"
    ABOUT = "about", "О компании"
    MATERIAL_LDSP = "material_ldsp", "Материал ЛДСП"
    MATERIAL_MDF = "material_mdf", "Материал МДФ"


class SheetStatus(models.TextChoices):
    PENDING = "pending", "Ожидает отправки"
    SENT = "sent", "Отправлена"
    FAILED = "failed", "Ошибка отправки"
```

```python
# backend/apps/content/models.py
from django.db import models

from apps.core.enums import CATEGORY_SLUG_CHOICES, SiteImageSlot


class ImageFieldsMixin(models.Model):
    # Written only by services.images.ingest_image.
    image = models.ImageField("Фото", upload_to="content/", max_length=255)
    image_width = models.PositiveIntegerField(null=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, editable=False)
    image_variants = models.JSONField(default=dict, editable=False)  # {"640": "content/<uuid>/w640.webp"}
    image_color = models.CharField(max_length=7, blank=True, editable=False)  # "#a07850"
    alt = models.CharField("Описание фото (alt)", max_length=200, blank=True)

    class Meta:
        abstract = True


class Category(ImageFieldsMixin):
    image = models.ImageField("Обложка", upload_to="content/", max_length=255, blank=True)
    slug = models.CharField(max_length=32, unique=True, choices=CATEGORY_SLUG_CHOICES)
    title = models.CharField("Название", max_length=120)
    short_description = models.CharField("Кратко", max_length=300, blank=True)
    description = models.TextField("Описание", blank=True)  # plain text, paragraphs split by a blank line
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    position = models.PositiveSmallIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]


class GalleryItem(ImageFieldsMixin):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="gallery_items")
    title = models.CharField("Название", max_length=120, blank=True)
    caption = models.CharField("Подпись", max_length=300, blank=True)
    position = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    is_featured = models.BooleanField("На главной", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "-created_at"]
        indexes = [
            models.Index(fields=["category", "is_published", "position"], name="gallery_cat_pub_pos_idx"),
            models.Index(fields=["is_featured", "is_published", "position"], name="gallery_featured_idx"),
        ]


class SiteImage(ImageFieldsMixin):
    image = models.ImageField("Фото", upload_to="content/", max_length=255, blank=True)  # empty slot allowed
    slot = models.CharField(max_length=32, unique=True, choices=SiteImageSlot.choices)
    updated_at = models.DateTimeField(auto_now=True)


class SiteSettings(models.Model):
    phone = models.CharField("Телефон", max_length=16, blank=True)  # E.164, normalized on save
    max_phone = models.CharField("Номер в MAX", max_length=16, blank=True)  # E.164, no profile URL
    vk_url = models.URLField("Ссылка ВКонтакте", blank=True)  # brand card, empty hides it
    email = models.EmailField(blank=True)
    address = models.CharField("Адрес", max_length=300, blank=True)
    work_hours = models.CharField("Часы работы", max_length=120, blank=True)
    map_url = models.URLField("Ссылка на карту", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name="site_settings_singleton")]


class SocialLink(models.Model):
    settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name="social_links")
    label = models.CharField(max_length=40)
    url = models.URLField()
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
```

```python
# backend/apps/leads/models.py
import uuid

from django.db import models
from django.utils import timezone

from apps.core.enums import ProductKind, SheetStatus


class Lead(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("ФИО", max_length=120)
    phone = models.CharField("Телефон", max_length=16)  # E.164
    product = models.CharField("Что заказать", max_length=32, choices=ProductKind.choices)
    dimensions = models.CharField("Размеры", max_length=300, blank=True)
    comment = models.TextField("Комментарий", blank=True)  # the API caps it at 2000
    source_url = models.CharField("Источник", max_length=500, blank=True)  # path + query, no host
    consent_version = models.CharField(max_length=32)
    consent_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    sheet_status = models.CharField(max_length=16, choices=SheetStatus.choices, default=SheetStatus.PENDING)
    sheet_attempts = models.PositiveSmallIntegerField(default=0)
    sheet_next_attempt_at = models.DateTimeField(default=timezone.now)
    sheet_last_error = models.CharField(max_length=500, blank=True)  # status + error class, never PII
    sheet_synced_at = models.DateTimeField(null=True, blank=True)
    sheet_alerted_at = models.DateTimeField(null=True, blank=True)  # alerts, section 8.4

    class Meta:
        ordering = ["-created_at"]
        permissions = [("retry_sheet_sync", "Может повторить отправку в таблицу")]
        indexes = [
            models.Index(
                fields=["sheet_next_attempt_at"],
                name="lead_sheet_due_idx",
                condition=models.Q(sheet_status="pending"),
            ),
            models.Index(fields=["created_at"], name="lead_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone__regex=r"^\+[1-9][0-9]{7,14}$"),
                name="lead_phone_e164",
            ),
            models.CheckConstraint(
                condition=~models.Q(sheet_status="sent") | models.Q(sheet_synced_at__isnull=False),
                name="lead_sent_has_synced_at",
            ),
        ]
```

Справочные строки создаёт `sync_reference_data` (15.2): 5 категорий (по одной на `CATEGORY_SLUG_CHOICES`), 4 слота `SiteImage` (по одному на `SiteImageSlot`), одна строка `SiteSettings` с `id=1`. В админке у этих моделей нет добавления и удаления.

## 7. HTTP API v1 (внутренний)

Ниже нормативная форма. drf-spectacular генерирует из кода `contracts/openapi.yaml`. Расхождение схемы с этим разделом: баг.

Каркас (S1-04) объявляет все операции с заглушками. Слайс заменяет заглушку поведением, схема не меняется.

| Метод | Путь | Назначение | Ответы | Заглушка S1-04 → поведение |
|---|---|---|---|---|
| GET | `/api/v1/site-settings/` | контакты для layout | 200 `SiteSettings` | пустые строки и `[]` → S2-10 |
| GET | `/api/v1/home/` | контент главной | 200 `HomeContent` | `null` и `[]` → `slots` S1-09, `categories` S2-06, `featured` S2-07 |
| GET | `/api/v1/categories/{slug}/` | страница категории | 200 `CategoryDetail`, 404 | всегда 404 → S2-08 |
| POST | `/api/v1/leads/` | создать заявку | 201 `LeadCreated`, 400, 429 | валидация типов и длин, 201 со случайным UUID без сохранения → S2-01, S2-02 |
| GET | `/api/v1/test/fake-sheet/` | строки фейковой таблицы для E2E | 200 `{"rows": [[8 строк], ...]}` | S1-07; только при `ENABLE_TEST_ENDPOINTS=true`, вне схемы |
| GET | `/healthz` | здоровье бэкенда | 200 `{"status": "ok"}`, 503 `{"status": "degraded", "checks": {...}}` | S1-04: БД; S1-07: плюс heartbeat воркера; без токена, вне схемы |

Общие правила:
- Базовый адрес: `API_INTERNAL_URL` (в Docker `http://backend:8000`).
- Каждый запрос к `/api/v1/` несёт `X-Internal-Token: <INTERNAL_API_TOKEN>`. Нет или неверный: 403. Сравнение через `hmac.compare_digest`. 403 объявлен у каждой операции.
- `authentication_classes = []`: без сессий и CSRF.
- `X-Client-IP`: IP посетителя, SvelteKit берёт его из `event.getClientAddress()`. Ключ троттлинга. Нет заголовка или значение не IP: ключ `REMOTE_ADDR`.
- JSON, поля в snake_case. TS-типы генерируются без переименования.
- Ошибки в формате DRF по умолчанию: 400 `{"<field>": ["msg"], "non_field_errors": ["msg"]}`, 403/404/429 `{"detail": "msg"}`. Тексты 400: раздел 12.1.
- GET-ответы: `Cache-Control: no-store`.
- `{slug}` в пути: строка; неизвестный или скрытый slug даёт 404.
- drf-spectacular: `COMPONENT_SPLIT_REQUEST = True`; `ENUM_NAME_OVERRIDES` фиксирует `ProductKindEnum` (из `ProductKind.choices`) и `CategorySlugEnum` (из `CATEGORY_SLUG_CHOICES`); поля вида и категории в схеме ссылаются на эти enum, не на `string`; схема безопасности apiKey в заголовке `X-Internal-Token`.

DTO (имена = имена компонентов в `openapi.yaml`):
```ts
type ProductKind = 'kitchens' | 'kitchen-tables' | 'wardrobes' | 'sliding-wardrobes' | 'office' | 'other';
type CategorySlug = Exclude<ProductKind, 'other'>;

type ImageAsset = {
  url: string;          // widest variant, "/media/content/<uuid>/w1920.webp"
  srcset: string;       // all variants ascending: "/media/.../w640.webp 640w, ..."
  width: number;        // px of the variant in `url`
  height: number;
  alt: string;          // never empty, fallback rules in section 9
  color: string;        // "#rrggbb", placeholder background
};

type SocialLink = { label: string; url: string };

type SiteSettings = {
  phone: string;              // E.164 or ""
  phone_display: string;      // "+7 (999) 123-45-67" or ""
  max_phone: string;          // MAX messenger number, E.164 or ""
  max_phone_display: string;  // "+7 (999) 123-45-67" or ""
  vk_url: string;             // VK page URL or ""
  email: string;
  address: string;
  work_hours: string;
  map_url: string;
  social_links: SocialLink[];
};

type CategorySummary = {
  slug: CategorySlug;
  title: string;
  short_description: string;
  cover: ImageAsset | null;
};

type GalleryItem = {
  id: number;
  category: CategorySlug;
  title: string;
  caption: string;
  image: ImageAsset;
};

type HomeSlots = {
  hero: ImageAsset | null;
  about: ImageAsset | null;
  material_ldsp: ImageAsset | null;
  material_mdf: ImageAsset | null;
};

type HomeContent = {
  slots: HomeSlots;
  categories: CategorySummary[];  // published only, by position
  featured: GalleryItem[];        // is_featured && is_published, by position, max 12
};

type CategoryDetail = CategorySummary & {
  description: string;            // plain text, paragraphs split by "\n\n"
  seo_title: string;              // fallback: title
  seo_description: string;        // fallback: short_description
  gallery: GalleryItem[];         // published only, by position
};

type LeadCreateRequest = {
  name: string;          // 2..120 after cleanup
  phone: string;         // raw input, max 32, normalized to E.164
  product: ProductKind;
  dimensions?: string;   // max 300
  comment?: string;      // max 2000
  consent: boolean;      // must be true
  website?: string;      // honeypot, must be empty
  source_url?: string;   // max 2000 on input; stored as path + query, cut to 500
};

type LeadCreated = { id: string };  // Lead.public_id
```

Поведение `POST /api/v1/leads/` (S2-01, S2-02):
- Порядок: токен → троттлинг → honeypot → валидация → сохранение.
- Honeypot `website` непустой: 201 со случайным UUID, запись не создаётся, лог без ПДн.
- Успех: `Lead` сохранён, телефон в E.164, `sheet_status=pending`, `consent_at=now`, `consent_version=CONSENT_VERSION`, ответ 201 `{ "id": "<public_id>" }`.
- `source_url`: сохраняется только path + query, обрезка до 500.
- Троттлинг: `LEAD_THROTTLE_RATE` (по умолчанию `5/hour`) на ключ из `X-Client-IP`, ответ 429.
- Тексты ошибок полей: раздел 12.1. Фронтенд показывает их как есть.

## 8. Google Sheets: контракт строки и джоба

### 8.1 Строка таблицы

Лист `GOOGLE_WORKSHEET_TITLE` (по умолчанию `Заявки`). Строка 1: заголовки, ровно как ниже. Приложение пишет только колонки A..H. Колонки I и дальше принадлежат менеджерам (статус, заметки): приложение их не читает и не пишет.

| Кол. | Заголовок | Источник | Формат |
|---|---|---|---|
| A | ID | `lead.public_id` | UUID4, нижний регистр |
| B | Дата | `lead.created_at` в `SHEETS_TIMEZONE` | `YYYY-MM-DD HH:MM` (текст, сортируется как дата) |
| C | ФИО | `lead.name` | как сохранено |
| D | Телефон | `lead.phone` | E.164 |
| E | Что заказать | метка `ProductKind` | `Кухни под заказ` и т.д. |
| F | Размеры | `lead.dimensions` | как сохранено или пусто |
| G | Комментарий | `lead.comment` | как сохранено или пусто |
| H | Источник | `lead.source_url` | path + query или пусто |

`backend/apps/leads/sheets/row.py`:
- `HEADERS: Final[tuple[str, ...]]`: восемь заголовков выше;
- `SheetRow = tuple[str, str, str, str, str, str, str, str]`;
- `build_row(lead, tz) -> SheetRow`: чистая функция;
- `validate_row(row) -> None`: 8 строк; A это UUID4; B по шаблону `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$`; D по шаблону E.164; E из меток `ProductKind`; ячейка ≤ 5000 символов. Нарушение: `ContractViolation`. Сообщение называет колонку и правило, значение ячейки не включает.

### 8.2 Транспорт

REST Sheets API v4 через `google.auth.transport.requests.AuthorizedSession`, scope `https://www.googleapis.com/auth/spreadsheets`, ключ сервисного аккаунта из `GOOGLE_SERVICE_ACCOUNT_FILE`, таймаут 10 с на запрос.
- `exists(lead_id)`: `GET values/'<title>'!A:A`, поиск ID в колонке.
- `append(row)`: `POST values/'<title>'!A:H:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS`, тело `{"values": [row]}`. `RAW` обязателен: текст вида `=IMPORTXML(...)` из формы остаётся текстом (защита от formula injection).
- `read_header()`: `GET values/'<title>'!A1:H1`.

Классификация ошибок:
- `SheetsRetryableError`: таймаут, ошибка соединения, HTTP 408, 429, 500, 502, 503, 504.
- `SheetsPermanentError`: HTTP 400, 401, 403, 404 и прочие 4xx.

### 8.3 Интерфейс и реализации

```python
# backend/apps/leads/sheets/client.py
class SheetsClient(Protocol):
    def exists(self, lead_id: str) -> bool: ...
    def append(self, row: SheetRow) -> None: ...
    def read_header(self) -> list[str]: ...

class SheetsRetryableError(Exception): ...
class SheetsPermanentError(Exception): ...

def get_sheets_client() -> SheetsClient: ...  # by SHEETS_BACKEND: "fake" | "google"
```
- `GoogleSheetsClient` (`sheets/google.py`): транспорт 8.2.
- `FakeSheetsClient` (`sheets/fake.py`): хранит строки в памяти (юнит-тесты) или в JSONL-файле `SHEETS_FAKE_PATH` (dev, E2E). Каждую строку проверяет `validate_row`. Инъекция сбоев: `fail_next(kind, times)`, где `kind` из `429`, `500`, `403`, `timeout`; `lose_response_once()`: строка записана, затем `SheetsRetryableError` (ответ потерян).

### 8.4 Джоба `sheets.append_lead` (outbox)

- Очередь: строки `leads_lead` с `sheet_status=pending` и `sheet_next_attempt_at <= now()`.
- Воркер: `python manage.py run_sheets_worker`. Цикл раз в `SHEETS_POLL_SECONDS`, до 10 заявок за цикл по `sheet_next_attempt_at`, каждая в своей транзакции через `select_for_update(skip_locked=True)`.
- Обработчик `sync_lead(lead_id, client, now, rng) -> Outcome` в `apps/leads/worker.py`:
  1. Заблокировать заявку. Статус не `pending`: ничего не делать.
  2. `if not client.exists(public_id): client.append(build_row(lead, tz))`.
  3. Успех: `sent`, `sheet_synced_at=now`, `sheet_last_error=""`.
  4. `SheetsRetryableError`: `attempts += 1`. `attempts >= SHEETS_MAX_ATTEMPTS`: переход в `failed`. Иначе `next_attempt_at = now + backoff_seconds(attempts, rng)`.
  5. `SheetsPermanentError`: `attempts += 1`, переход в `failed`.
  6. Прочее исключение: как retryable, лог с traceback.
- Переход в `failed` обнуляет `sheet_alerted_at`.
- `backoff_seconds(n, rng) = min(30 * 2 ** (n - 1), 3600) * rng.uniform(0.8, 1.2)`, `n ≥ 1`. С `SHEETS_MAX_ATTEMPTS=12` заявка ретраится около 5 часов.
- Идемпотентность: одна заявка даёт не больше одной строки с её ID, даже если append прошёл, а ответ или коммит потерялись.
- Переходы статусов: `pending → sent`, `pending → pending` (ретрай), `pending → failed`, `failed → pending` (админ-действие «Повторить отправку»: `attempts=0`, `next_attempt_at=now`, `sheet_last_error=""`, `sheet_alerted_at=NULL`). Других переходов нет.
- Heartbeat: после каждой заявки и в конце цикла воркер пишет время в кэш, ключ `sheets_worker:heartbeat`. Backend `/healthz` отвечает 503, если heartbeat старше 120 с.
- SIGTERM: воркер заканчивает текущую заявку и выходит; `stop_grace_period: 30s`.
- Логи: `lead=<public_id> attempt=<n> outcome=<sent|retry|failed>`. Без ФИО, телефона, комментария.
- Алерты (S2-05), проверка в конце каждого цикла:
  - кандидаты: `failed` с `sheet_alerted_at IS NULL`; `pending` с `sheet_attempts >= 7` (около 30 минут ретраев) и `sheet_alerted_at IS NULL`;
  - кандидаты есть, и последнее письмо (максимум `sheet_alerted_at`) старше 30 минут или писем не было: одно письмо на `ALERT_EMAIL` со списком `public_id` и ссылкой на список заявок в админке; кандидатам `sheet_alerted_at = now`;
  - в письме нет ПДн;
  - ошибка SMTP: лог без ПДн, `sheet_alerted_at` не ставится, следующая попытка не раньше чем через 5 минут;
  - `ALERT_EMAIL` пуст: алерты выключены.
- `python manage.py sheets_check`: читает A1:H1, сравнивает с `HEADERS`. Расхождение или нет доступа: exit 1 с понятным сообщением. Запускается в release-шаге, если `SHEETS_BACKEND=google`.

### 8.5 Настройка таблицы (один раз)

1. Создать лист `Заявки`, в строку 1 записать заголовки A..H из 8.1.
2. Дать сервисному аккаунту доступ «Редактор» по его email.
3. Менеджерам: колонки A..H не переставлять и не переименовывать. Свои колонки добавлять правее H.

## 9. Изображения: пайплайн и хранение

- Загрузка только через админку и `seed_demo`.
- Файл: JPEG, PNG, WebP; до 20 МБ; длинная сторона ≥ 800 px; не больше 40 Мпикс (защита от decompression bomb). Иначе ошибка валидации на русском, в media ничего не пишется.
- `ingest_image(instance, file)` в `apps/content/services/images.py`:
  1. Открыть Pillow, `verify`, `ImageOps.exif_transpose`, перевести в RGB (альфа на белый фон).
  2. Мастер: длинная сторона ≤ 2560, JPEG q=88, progressive, без EXIF (GPS не утекает).
  3. Варианты WebP q=80 по ширинам `plan_variants(master_width)`.
  4. Цвет-заглушка: среднее по картинке 1×1 → `#rrggbb`.
  5. Файлы: `content/<uuid4>/master.jpg`, `content/<uuid4>/w<width>.webp`.
  6. Поля: `image` (мастер), `image_width`, `image_height` (мастер), `image_variants`, `image_color`.
  7. Замена фото: старая папка удаляется в `transaction.on_commit`. Откат транзакции оставляет старые файлы.
- Очистка фото (флажок «Очистить» в админке): папка удаляется в `on_commit`, поля картинки обнуляются.
- Удаление записи: `post_delete` удаляет папку в `on_commit`.
- `plan_variants(w)`: цели `(640, 1280, 1920)`. Результат `sorted({t for t in TARGETS if t < w} | {min(w, 1920)})`. Примеры: 2560 → [640, 1280, 1920]; 1500 → [640, 1280, 1500]; 600 → [600]. Апскейла нет.
- Высота варианта: `max(1, round(h * vw / w))`.
- `ImageAsset`: `url` = самый широкий вариант, `srcset` = все варианты по возрастанию, `width` и `height` от варианта в `url`.
- Alt, если пустой: `SiteImage` → «Фабрика Уюта: <метка слота>»; `Category` → `title`; `GalleryItem` → `title`, иначе `category.title`. Подсказка у поля в админке: «Что на фото: для незрячих и поисковиков».
- Кэш: путь содержит uuid и не меняется, Caddy отдаёт `/media/*` с `Cache-Control: public, max-age=31536000, immutable`.
- Пакетная загрузка (S2-09): до 20 файлов за запрос, пакет атомарный.
- Тело запроса к админке: до 200 МБ (Caddy).
- Чистые функции для property-тестов: `plan_variants`, `fit_within(w, h, max_side)`, `average_color_hex`.

## 10. Фронтенд

### 10.1 Роуты

| Роут | Файлы | Данные | Примечание |
|---|---|---|---|
| layout | `+layout.server.ts`, `+layout.svelte` | `GET /site-settings/` | Header, Footer, LeadDialog |
| `/` | `+page.server.ts`, `+page.svelte` | `GET /home/` | секции по карте шаблона (приложение А) |
| `/catalog/[slug]` | `+page.server.ts`, `+page.svelte` | `GET /categories/{slug}/` | 404 для неизвестной или скрытой категории |
| `/lead` | `+page.server.ts` (`load`, `actions.default`), `+page.svelte` | `POST /leads/` | форма отдельной страницей; `?product=<slug>` предвыбирает вид; приёмник формы со всех страниц; `noindex` |
| `/privacy` | `+page.svelte` | статика | политика обработки ПДн |
| `/consent` | `+page.svelte` | статика | согласие на обработку ПДн, отдельный документ |
| `/sitemap.xml` | `+server.ts` | `GET /home/` | |
| `/robots.txt` | `+server.ts` | `PUBLIC_APP_ENV` | не production: `Disallow: /` |
| `/healthz` | `+server.ts` | backend `/healthz` | 200 `ok` или 503 `degraded`; для мониторинга |
| `/dev/ui` | `+page.svelte` | нет | kitchen sink; 404 при `PUBLIC_APP_ENV=production` |
| ошибки | `+error.svelte` | нет | 404 и 5xx |

Якоря секций (контракт для навигации и E2E), в порядке на странице: `hero`, `about`, `catalog`, `works`, `materials`, `process`, `advantages`, `lead`, `contacts`.

### 10.2 Правила

- Svelte 5, только руны: `$props`, `$state`, `$derived`, `$effect` (минимум). Запрещено: `export let`, `$:`, `on:click`, `<slot>`, `$app/stores`. События атрибутами (`onclick`), сниппеты и `{@render}`, состояние страницы из `$app/state`.
- Серверный код только в `src/lib/server/` и `*.server.ts`. API-клиент и токен в браузер не попадают.
- Env только динамический: `$env/dynamic/private` (`API_INTERNAL_URL`, `INTERNAL_API_TOKEN`), `$env/dynamic/public` (`PUBLIC_*`). Один образ фронта работает и на staging, и в production. В dev фронт читает корневой `.env` (`envDir: '..'` в `vite.config.ts`).
- adapter-node в контейнере: `ORIGIN=https://<domain>` (иначе CSRF-проверка form actions за прокси отклоняет POST), `ADDRESS_HEADER=X-Forwarded-For`, `XFF_DEPTH=1` (один прокси, Caddy), чтобы `getClientAddress()` вернул IP посетителя.
- `hooks.server.ts`: `resolve(event, { preload })` добавляет `font` к `js` и `css`.
- Контент-тексты секций: типизированные данные в `src/lib/content/*.ts`. Юр. тексты: `src/lib/content/legal/*.svelte`.
- CSP: `kit.csp` в `svelte.config.js`, mode `auto`. Директивы: `default-src 'self'`, `script-src 'self'`, `img-src 'self' data:`, `font-src 'self'`, `style-src 'self' 'unsafe-inline'`, `connect-src 'self'`, `frame-ancestors 'none'`, `form-action 'self'`, `base-uri 'self'`.
- Внешних скриптов, шрифтов и виджетов нет (13.2).
- SSR-страницы без `Cache-Control`: новое фото видно сразу после загрузки.

### 10.3 API-клиент и типы

```ts
// frontend/src/lib/server/api.ts
import createClient from 'openapi-fetch';
import type { paths } from '$lib/types/api';
import { env } from '$env/dynamic/private';

export function createApi(fetchFn: typeof fetch, clientIp?: string) {
  return createClient<paths>({
    baseUrl: env.API_INTERNAL_URL,
    fetch: fetchFn, // SvelteKit event.fetch
    headers: {
      'X-Internal-Token': env.INTERNAL_API_TOKEN,
      ...(clientIp ? { 'X-Client-IP': clientIp } : {}),
    },
  });
}
```
Таймаут 5 с на запрос (`AbortSignal.timeout`). Ошибка сети или 5xx в `load`: `error(503)`.

`frontend/src/lib/types/api.d.ts`: генерирует `openapi-typescript` из `contracts/openapi.yaml`, руками не правится.

```ts
// frontend/src/lib/types/index.ts: the only place to import API types from
import type { components } from './api';
type S = components['schemas'];
export type ImageAsset = S['ImageAsset'];
export type SocialLink = S['SocialLink'];
export type SiteSettings = S['SiteSettings'];
export type CategorySummary = S['CategorySummary'];
export type CategoryDetail = S['CategoryDetail'];
export type GalleryItem = S['GalleryItem'];
export type HomeSlots = S['HomeSlots'];
export type HomeContent = S['HomeContent'];
export type LeadCreateRequest = S['LeadCreateRequest'];
export type LeadCreated = S['LeadCreated'];
export type ProductKind = S['ProductKindEnum'];
export type CategorySlug = S['CategorySlugEnum'];
```

### 10.4 Чистая логика (`src/lib/domain/`)

Модуль создаёт слайс из последней колонки.

| Модуль | Экспорт | Назначение | Слайс |
|---|---|---|---|
| `phone.ts` | `formatPhoneInput(raw: string): string` | маска ввода, 12.3 | S1-05 |
| `product-kind.ts` | `PRODUCT_KIND_LABELS` | метки видов, `satisfies Record<ProductKind, string>`: новый вид в OpenAPI без метки ломает svelte-check | S2-01 |
| `lead-errors.ts` | `mapLeadErrors(body: unknown): LeadFormErrors` | ошибки DRF → ошибки полей формы | S2-02 |
| `url.ts` | `absoluteUrl(origin: string, path: string): string` | абсолютные URL для canonical и OG | S2-08 |
| `text.ts` | `splitParagraphs(text: string): string[]` | описание категории → абзацы | S2-08 |
| `sitemap.ts` | `buildSitemap(origin: string, categories: CategorySummary[]): string` | XML карты сайта | S2-11 |

`LeadFormErrors = Partial<Record<'name' | 'phone' | 'product' | 'dimensions' | 'comment' | 'consent' | 'form', string>>`. Неизвестные поля DRF уходят в `form`.

### 10.5 Навигация данными

```ts
// frontend/src/lib/config/nav.ts
export type NavItem = { label: string; href: string };
export const NAV: NavItem[] = [
  { label: 'О компании', href: '/#about' },
  { label: 'Направления', href: '/#catalog' },
  { label: 'Галерея', href: '/#works' },
  { label: 'Материалы', href: '/#materials' },
  { label: 'Как мы работаем', href: '/#process' },
  { label: 'Контакты', href: '/#contacts' },
];
```
Меню меняется правкой массива, не разметки. Состав зафиксирован в S1-01 (v2) по шаблону.

## 11. UI-примитивы и layout

База: shadcn-svelte (Svelte 5, Tailwind 4), компоненты копируются CLI в `src/lib/components/ui/`. Поля формы нативные (`input`, `textarea`, `select`, `checkbox`): форма обязана работать без JS, а компоненты Bits UI без JS не переключаются.

```ts
// Button (shadcn-svelte)
{ variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'link'; size?: 'default' | 'sm' | 'lg' | 'icon';
  href?: string;                 // renders <a>
  type?: 'button' | 'submit'; disabled?: boolean;
  loading?: boolean;             // disabled + spinner + aria-busy
  onclick?: (e: MouseEvent) => void;
  class?: string; children: Snippet }

// Input (shadcn-svelte, native input)
{ name: string; id?: string; type?: 'text' | 'email' | 'tel'; value?: string /* $bindable */;
  required?: boolean; maxlength?: number; autocomplete?: string; placeholder?: string;
  'aria-invalid'?: boolean; 'aria-describedby'?: string; class?: string;
  autofocus?: boolean /* v6: first invalid field after a no-JS submit */ }

// Textarea (shadcn-svelte, native textarea): Input props + rows?: number (default 4)

// Select (own, native select)
{ name: string; id?: string; options: { value: string; label: string }[];
  value?: string /* $bindable */; placeholder?: string /* disabled empty option */;
  required?: boolean; 'aria-invalid'?: boolean; 'aria-describedby'?: string; autofocus?: boolean }

// Checkbox (own, native checkbox)
{ name: string; id?: string; checked?: boolean /* $bindable */; value?: string /* default "on" */;
  required?: boolean; 'aria-invalid'?: boolean; 'aria-describedby'?: string; autofocus?: boolean;
  children: Snippet /* label content, may contain links */ }

// PhoneInput (own): native input type="tel", inputmode="tel", autocomplete="tel",
// mask formatPhoneInput on input; without JS works as a plain field
{ name: string; id?: string; value?: string /* $bindable */; required?: boolean;
  'aria-invalid'?: boolean; 'aria-describedby'?: string; autofocus?: boolean }

// Field (own): label + control + hint + error
{ id: string; label: string; required?: boolean; hint?: string; error?: string;
  children: Snippet<[{ id: string; describedBy: string | undefined; invalid: boolean }]> }

// Alert (own)
{ tone: 'success' | 'error' | 'info'; title?: string; children: Snippet }
// success and info: role="status"; error: role="alert"

// Dialog (shadcn-svelte): Root, Trigger, Content, Header, Title, Description, Close. Title is required.
// Sheet (shadcn-svelte): mobile menu, side="right".

// ResponsiveImage (own)
{ image: ImageAsset | null; sizes: string;
  loading?: 'lazy' | 'eager' /* default 'lazy' */; fetchpriority?: 'high' | 'auto';
  aspect?: string /* CSS aspect-ratio for the empty placeholder */; class?: string }
// image: <img src srcset sizes width height alt decoding="async"> with background image.color
// null: <div aria-hidden="true"> with token background and aspect

// Container (own): { class?: string; children: Snippet }  max-w-7xl, side gutters px-5 md:px-8 (template)
// Section (own): { id?: string; title?: string; subtitle?: string; tone?: 'default' | 'muted' | 'inverted';
//                  headingLevel?: 2 | 3; class?: string; children: Snippet }  <section aria-labelledby>
```

Layout (`src/lib/components/layout/`):
- `Header`: `{ settings: SiteSettings; nav: NavItem[] }`. Логотип, меню, телефон ссылкой `tel:` (текстом с `xl`; до `lg`, где нет горизонтального меню, кнопка-иконка звонка, v7), CTA «Оставить заявку»: ссылка на `/lead`; с JS открывает LeadDialog (с S2-03).
- `MobileNav`: `{ nav: NavItem[]; phone: string }` на Sheet.
- `Footer`: `{ settings: SiteSettings; nav: NavItem[] }`. Контакты, меню, ссылки на `/privacy` и `/consent`, год.
- `SkipLink`: ссылка на `#main`.
- `Seo` (S2-08): `{ title: string; description: string; path: string; image?: ImageAsset | null; noindex?: boolean }`. Title, description, canonical, OG в `<svelte:head>`.

Токены: имена переменных shadcn-svelte в `src/app.css` (`--background`, `--foreground`, `--primary`, `--primary-foreground`, `--secondary`, `--secondary-foreground`, `--muted`, `--muted-foreground`, `--accent`, `--accent-foreground`, `--destructive`, `--border`, `--input`, `--ring`, `--radius`), `--success` (v7) и брендовые `--brand-vk`, `--brand-max`, `--brand-max-accent`, `--brand-foreground` (v9), связка через `@theme inline`. Шрифты: `--font-sans`, `--font-display`. Тёмной темы нет.

Значения (S1-01, из `template/src/index.css`):

| Токен | Значение | HEX |
|---|---|---|
| `--background` | `hsl(38 27% 97%)` | `#F9F8F5` |
| `--foreground` | `hsl(0 0% 17%)` | `#2B2B2B` |
| `--card`, `--popover` | `hsl(38 33% 99%)` | `#FDFDFC` |
| `--card-foreground`, `--popover-foreground` | `hsl(0 0% 17%)` | `#2B2B2B` |
| `--primary`, `--accent`, `--ring` | `hsl(27 22% 33%)` | `#675242` |
| `--primary-foreground`, `--accent-foreground` | `hsl(38 27% 97%)` | `#F9F8F5` |
| `--secondary` | `hsl(36 22% 92%)` | `#EFEBE6` |
| `--secondary-foreground` | `hsl(27 22% 24%)` | `#4B3C30` |
| `--muted` | `hsl(36 20% 94%)` | `#F3F0ED` |
| `--muted-foreground` | `hsl(30 7% 42%)` | `#736B64` |
| `--destructive` | `hsl(0 72% 48%)` | `#D32222` |
| `--border` | `hsl(36 18% 82%)` | `#D9D3C9` |
| `--input` | `hsl(30 7% 52%)` | `#8D857C` (v7: граница поля 3,4:1 к фону) |
| `--success` | `hsl(100 25% 32%)` | `#4B663D` (v7: Alert `success`) |
| `--brand-vk` | `#0077FF` | официальный логотип VK (v9: карточка «ВКонтакте») |
| `--brand-max` | `#471AFF` | брендбук MAX, «Синий гигант» (v9: карточка «MAX») |
| `--brand-max-accent` | `#9500FF` | брендбук MAX, «Пурпурная туманность» (v9: вторая точка градиента) |
| `--brand-foreground` | `#FFFFFF` | брендбук MAX, «Белый свет» (v9: текст и знак на брендовом фоне) |
| `--radius` | `0.9rem` | |
| `--font-display` | `'Cormorant Garamond Variable', ui-serif, Georgia, serif` | заголовки и цифры, начертания 300..500 |
| `--font-sans` | `'Manrope Variable', ui-sans-serif, system-ui, sans-serif` | текст и интерфейс |

Производные утилиты в `app.css` (только из токенов): `glass` (фон `--background` 78 %, рамка `--border` 45 %, blur 16px), `glass-dark` (фон `--foreground` 64 %), `joinery-line` (градиент по `--border`), тени `shadow-float`, `shadow-header`, `shadow-lift` (цвет `--foreground`). Анимация `reveal` и подъём `lift-hover` по шаблону, с учётом `prefers-reduced-motion`. Типографика и отступы: `template/STYLE-GUIDE.md`, разделы «Типографика», «Форма и отступы».

Правила UI:
- Есть примитив: самописный аналог запрещён.
- Цвета только через токены. Hex в компонентах запрещён.
- Брендовые токены (v9) живут только в карточках «ВКонтакте» и «MAX» секции контактов. Фирменный цвет не меняется, поэтому текст и знак на нём белые (`--brand-foreground`), а размер текста не меньше 24 px: белый на `--brand-vk` даёт 4,1:1 и проходит AA только как крупный.
- Иконки: `@lucide/svelte` или SVG из шаблона в `src/lib/icons/`. Там же знаки брендов из официальных брендбуков (v9).
- `/dev/ui` показывает каждый примитив во всех вариантах и состояниях.

## 12. Тексты и форматы формы

### 12.1 Поля

| Поле API | Подпись | Плейсхолдер | Обяз. | Ошибки (приходят с сервера) |
|---|---|---|---|---|
| `name` | ФИО | Иванов Иван Иванович | да | «Укажите ФИО»; «Слишком короткое имя»; «Не больше 120 символов» |
| `phone` | Телефон | +7 (___) ___-__-__ | да | «Укажите телефон»; «Проверьте номер телефона» |
| `product` | Что хотите заказать | Выберите | да | «Выберите, что хотите заказать» |
| `dimensions` | Примерные размеры | Стена 3,2 м, высота 2,6 м | нет | «Не больше 300 символов» |
| `comment` | Комментарий | Материал, цвет, сроки, пожелания | нет | «Не больше 2000 символов» |
| `consent` | Я даю согласие на обработку персональных данных (ссылка на `/consent`) | | да | «Нужно согласие на обработку персональных данных» |

- Все сообщения валидации API берутся из таблицы, включая случаи `required`, `blank`, `null`, `max_length`, `invalid`, `invalid_choice` (переопределить `error_messages` в сериализаторе). Дефолтных текстов DRF в ответе нет.
- `name`: trim, пробелы схлопываются. Пусто или нет ни одной буквы: «Укажите ФИО». Один символ: «Слишком короткое имя». Больше 120: «Не больше 120 символов».
- `phone`: пусто: «Укажите телефон». Больше 32 символов или `normalize_phone` вернул `None`: «Проверьте номер телефона».
- `dimensions`, `comment`: trim, управляющие символы удаляются (кроме `\n` и `\t`).
- `website`: honeypot. Поле скрыто (`aria-hidden` у обёртки, `tabindex="-1"`, `autocomplete="off"`).
- `source_url`: скрытое поле, `page.url.pathname + page.url.search`.
- `product`: на главной пустой плейсхолдер; на странице категории и на `/lead?product=<slug>` вид предвыбран.

### 12.2 Сообщения формы (фронтенд)

| Ситуация | Текст |
|---|---|
| Кнопка | «Отправить заявку» |
| Отправка | «Отправляем…» |
| Успех | «Спасибо! Заявка принята. Перезвоним в рабочее время.» |
| 429 | «Слишком много заявок с вашего адреса. Попробуйте позже или позвоните нам.» + телефон |
| 5xx или сеть | «Не получилось отправить заявку. Попробуйте ещё раз или позвоните нам.» + телефон |

### 12.3 Телефон

Бэкенд (`apps/core/phone.py`):
- `normalize_phone(raw) -> str | None`: `phonenumbers.parse(raw, "RU")`, `is_valid_number`, результат E.164. Иначе `None`. Исключений не бросает.
- `format_phone_display(e164) -> str`: `+7` → `+7 (999) 123-45-67`, остальные в формате INTERNATIONAL.

Фронтенд (`src/lib/domain/phone.ts`), `formatPhoneInput(raw)`:
1. `d` = цифры ввода. `plus` = первый непробельный символ ввода равен `+`.
2. `d` пуст: вернуть `"+"`, если `plus`, иначе `""`.
3. `plus` и `d[0] != '7'`: вернуть `"+"` + первые 15 цифр `d` без форматирования.
4. `d[0] == '8'`: заменить на `7`. Иначе, если `d[0] != '7'`: приписать `7` в начало.
5. `r` = цифры со 2-й по 11-ю. Результат: `"+7"`, затем `" (" + r[0:3]`, если `r` не пуст; `") " + r[3:6]`, если в `r` больше 3 цифр; `"-" + r[6:8]`, если больше 6; `"-" + r[8:10]`, если больше 8.

`contracts/fixtures/phone-cases.json` читают обе стороны. Минимальный набор (S1-04), дополняется по мере находок:
```json
[
  { "input": "+7 (999) 123-45-67", "masked": "+7 (999) 123-45-67", "e164": "+79991234567" },
  { "input": "8 999 123 45 67", "masked": "+7 (999) 123-45-67", "e164": "+79991234567" },
  { "input": "89991234567", "masked": "+7 (999) 123-45-67", "e164": "+79991234567" },
  { "input": "9991234567", "masked": "+7 (999) 123-45-67", "e164": "+79991234567" },
  { "input": "7-999-123-45-67", "masked": "+7 (999) 123-45-67", "e164": "+79991234567" },
  { "input": "+7 495 123-45-67", "masked": "+7 (495) 123-45-67", "e164": "+74951234567" },
  { "input": "+375 29 123-45-67", "masked": "+375291234567", "e164": "+375291234567" },
  { "input": "+7 999 123", "masked": "+7 (999) 123", "e164": null },
  { "input": "+", "masked": "+", "e164": null },
  { "input": "abc", "masked": "", "e164": null },
  { "input": "", "masked": "", "e164": null }
]
```
Проверки: фронт `formatPhoneInput(input) === masked`; бэк `normalize_phone(input) == e164` и `normalize_phone(masked) == e164`; для полных номеров `+7` `format_phone_display(e164) == masked`.

## 13. Безопасность и 152-ФЗ

### 13.1 Безопасность

- API только внутренний: Caddy отдаёт 404 на `/api/*`, Django требует `X-Internal-Token`.
- Админка: путь из `DJANGO_ADMIN_PATH` (в production не `admin/`); django-axes: 5 неудачных входов → блокировка на час по паре логин + IP, IP из `X-Forwarded-For` с одним доверенным прокси; стандартные валидаторы паролей; только HTTPS: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS`.
- Загрузки: тело запроса к админке до 200 МБ (Caddy), файл до 20 МБ, пакет до 20 файлов, лимит пикселей Pillow (раздел 9).
- Заголовки на Caddy: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`, HSTS только в production. CSP сайта: 10.2.
- Google Sheets: `valueInputOption=RAW` (formula injection).
- ПДн (ФИО, телефон, комментарий) живут только в Postgres, Google-таблице и админке. В логах, ошибках, алертах, `sheet_last_error` и фикстурах их нет. В тестах только фиктивные данные.
- Секреты: только env и файлы секретов на VPS, GitHub Secrets. В репозитории их нет. `.env` в `.gitignore`.

### 13.2 152-ФЗ (если оператор в РФ; владелец сверяет с юристом заказчика)

- С 1 июля 2025 сбор ПДн граждан РФ запрещено вести в иностранных базах данных. Первичная запись идёт в Postgres на VPS в РФ, форма пишет сначала туда.
- Google-таблица получает уже собранные данные: это трансграничная передача. Заказчик подаёт уведомление в Роскомнадзор до запуска, политика и согласие упоминают передачу в Google. Без подтверждения заказчика production с `SHEETS_BACKEND=google` не запускается (S2-12).
- С 1 сентября 2025 согласие на обработку ПДн оформляется отдельным документом. Страница `/consent`, чекбокс по умолчанию выключен, в заявке хранятся `consent_version` и `consent_at`.
- Политика обработки ПДн: страница `/privacy`.
- На сайте нет иностранных счётчиков, шрифтовых CDN, капч и встраиваемых карт. Шрифты self-hosted. Карта: ссылка `map_url`, не iframe. Публичный сайт не ставит cookies, баннер не нужен.
- Финальные юр. тексты даёт заказчик или юрист. По решению владельца от 2026-11-14 сессия пишет черновик политики ПДн и согласия: компонент показывает Alert `tone="info"` с текстом «Проект документа. Текст проверяет юрист.», маркер `LEGAL_TEXT_PENDING` остаётся в компоненте, `deploy.sh` с маркером останавливается и production не выкатывает (16.3). Реквизиты оператора и срок хранения сессия не выдумывает: в черновике они стоят в квадратных скобках заглушками, заказчик заменяет их на свои. Текст юриста приходит: заменить тело компонента, заполнить заглушки, снять комментарий с маркером и Alert, поднять `CONSENT_VERSION`.

## 14. Конфиг и `.env.example`

- Бэкенд читает окружение только в `config/settings.py` через хелперы `apps/core/env.py` (`env_str`, `env_bool`, `env_int`, `env_list`). Вне контейнера settings подгружает корневой `.env` (python-dotenv), существующие переменные не перезаписываются. Относительные пути считаются от `backend/`.
- Django: `LANGUAGE_CODE = "ru"`, `TIME_ZONE = "Europe/Moscow"`, `USE_TZ = True`, `STATIC_URL = "/django-static/"` (whitenoise), `MEDIA_URL = "/media/"`, `CACHES`: DatabaseCache с `MAX_ENTRIES = 10000`.
- Системная проверка `apps/core/checks.py` (уровень Error) валит `check --deploy` при `APP_ENV` в `staging` или `production`, если: `DJANGO_DEBUG=true`; `DJANGO_SECRET_KEY` пуст или равен dev-значению; `INTERNAL_API_TOKEN` короче 32 символов или равен dev-значению; `DJANGO_ADMIN_PATH=admin/`; `ENABLE_TEST_ENDPOINTS=true`; `SHEETS_BACKEND=google` без `GOOGLE_*`.
- Фронтенд читает окружение только через `$env/dynamic/*`.
- Makefile подключает корневой `.env` (`-include .env`, `export`).
- Dev-compose переопределяет только `POSTGRES_HOST=db`. E2E задаёт окружение в compose, пути данных в `/data`. Production читает `.env` рядом с `compose.prod.yml` (на VPS это `/opt/fabrika/app/.env`), `MEDIA_ROOT=/data/media` приходит из compose.

```dotenv
# common
APP_ENV=dev                               # dev | e2e | production

# vps; Caddy reads them from this file, empty outside production
DOMAIN=
ACME_EMAIL=

# postgres
POSTGRES_DB=fabrika
POSTGRES_USER=fabrika
POSTGRES_PASSWORD=fabrika
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# django; relative paths resolve from backend/
DJANGO_SECRET_KEY=dev-insecure-change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173
DJANGO_ADMIN_PATH=admin/
MEDIA_ROOT=./var/media
INTERNAL_API_TOKEN=dev-internal-token-change-me-0000000
LEAD_THROTTLE_RATE=5/hour
CONSENT_VERSION=2026-09-25
ENABLE_TEST_ENDPOINTS=true

# google sheets
SHEETS_BACKEND=fake                       # fake | google
SHEETS_FAKE_PATH=./var/fake-sheet.jsonl
# container: GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/google-sa.json
GOOGLE_SERVICE_ACCOUNT_FILE=
GOOGLE_SPREADSHEET_ID=
GOOGLE_WORKSHEET_TITLE=Заявки
SHEETS_TIMEZONE=Europe/Moscow
SHEETS_POLL_SECONDS=5
SHEETS_MAX_ATTEMPTS=12

# alerts (S2-05); empty ALERT_EMAIL disables alerts, empty EMAIL_HOST uses the console backend
ALERT_EMAIL=
EMAIL_HOST=
EMAIL_PORT=465
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_SSL=true
DEFAULT_FROM_EMAIL=

# sveltekit
API_INTERNAL_URL=http://localhost:8000
PUBLIC_SITE_URL=http://localhost:5173
PUBLIC_APP_ENV=dev                        # equals APP_ENV
# container: ORIGIN=https://<domain>, ADDRESS_HEADER=X-Forwarded-For, XFF_DEPTH=1
ORIGIN=
ADDRESS_HEADER=
XFF_DEPTH=

# e2e
E2E_BASE_URL=http://localhost:8080
E2E_API_URL=http://localhost:8000
```

Файлы на VPS: `/opt/fabrika/app/.env` и `/opt/fabrika/app/google-sa.json` рядом с `compose.prod.yml` в клоне репозитория. Оба в `.gitignore`, `git pull` их не трогает. Ключ монтируется read-only в `/run/secrets/google-sa.json`.

## 15. Миграции, справочники, сид, команды

### 15.1 Миграции

- Генерируются только `make migrations` (`manage.py makemigrations`) после правки схемы в разделе 6. Руками не правятся.
- Применяются в release-шаге деплоя.
- CI: `makemigrations --check --dry-run` и `migrate` на эфемерном Postgres 18.
- Только вперёд. Разрушающие изменения в два релиза: сначала расширить, потом сузить.
- Data-миграций нет: справочные данные создаёт `sync_reference_data`.

### 15.2 Справочные данные: `manage.py sync_reference_data`

Идемпотентна, создаёт только недостающее, существующие значения не перезаписывает:
- 5 строк `Category`: `slug` из `CATEGORY_SLUG_CHOICES`, `title` = метка, `position` = порядок в enum;
- 4 строки `SiteImage` (пустые слоты);
- `SiteSettings` с `id=1`;
- группы «Контент» (добавление, изменение, удаление и просмотр моделей `content`) и «Заявки» (просмотр `Lead`, `leads.retry_sheet_sync`).

Запускается в release-шаге и в `make seed`.

### 15.3 Демо-данные: `manage.py seed_demo`

- Живёт в `apps/core`. Работает только при `APP_ENV` в `dev`, `e2e`, `staging`. В production завершается с ошибкой и ничего не пишет.
- Картинки: фото из `template/` копируются в `backend/fixtures/demo/`; нет фото в шаблоне: генерируются Pillow (градиент в цветах токенов и подпись).
- Заполняет: 4 слота, обложки 5 категорий, 12 работ галереи (4 на главной), демо-контакты с `vk_url` и без `social_links` (v9), 3 демо-заявки (`pending`, `sent`, `failed`) с фиктивными данными.
- Идемпотентна. `--reset` пересоздаёт демо-данные.
- Фейковая Google-таблица и E2E работают на этих же данных.

### 15.4 Makefile

| Цель | Действие |
|---|---|
| `make dev` | `docker compose up -d db backend worker`; фронт отдельно: `pnpm -C frontend dev` |
| `make dev-down` | остановить dev-стек |
| `make migrations` | `makemigrations` |
| `make migrate` | `migrate` + `createcachetable` |
| `make gen` | `spectacular --file ../contracts/openapi.yaml`, затем `openapi-typescript` → `frontend/src/lib/types/api.d.ts` |
| `make seed` | `sync_reference_data` + `seed_demo` |
| `make fmt` | `prettier --write` + `ruff format` |
| `make check-fast` | `svelte-check` + `mypy` (перед коммитом) |
| `make test` | `vitest run` + `pytest` |
| `make gate` | всё, что проверяет CI, кроме E2E: формат, линт, типы, knip, юнит-тесты, build, миграции, drift |
| `make e2e` | `compose.e2e.yml` up, `seed_demo`, Playwright; до S1-10 Playwright против dev-стека (`E2E_BASE_URL=http://localhost:5173`) |

## 16. CI/CD и деплой

### 16.1 Окружения

| Окружение | Триггер | Адрес | Данные | Sheets |
|---|---|---|---|---|
| dev | локально | `localhost:5173` | `seed_demo` | fake |
| e2e | CI, `make e2e` | `localhost:8080` | `seed_demo` | fake (файл) |
| production | `deploy/deploy.sh` на VPS | `<domain>` | реальные | google, таблица заказчика |

### 16.2 Гейт на PR (`.github/workflows/ci.yml`, без деплоя)

Триггер: `pull_request` с типами `opened`, `synchronize`, `reopened`, `labeled`, `unlabeled`. Джобы `back`, `drift`, `e2e` начинают с `cp .env.example .env`.

Параллельные джобы:
- `front`: `pnpm install --frozen-lockfile`; `prettier --check .`; `eslint .`; `svelte-check --fail-on-warnings`; `knip`; `vitest run`; `pnpm build`.
- `back`: `uv sync --frozen`; `ruff format --check`; `ruff check`; `mypy`; сервис Postgres 18; `makemigrations --check --dry-run`; `migrate`; `pytest` (Hypothesis-профиль `ci`, Schemathesis).
- `drift`: `make gen`, затем `git diff --exit-code contracts/openapi.yaml frontend/src/lib/types/api.d.ts`.
- `e2e` (с S1-10): `docker compose -f compose.e2e.yml up --build --wait`, `seed_demo`, Playwright (Chromium: 1440 px и 360 px), отчёт артефактом при падении.
- `contract-guard`: `pytest scripts/`, затем `python scripts/contract_guard.py` (раздел 3).

Игнор-листы: `contracts/openapi.yaml` и `api.d.ts` исключены из prettier и eslint. knip игнорирует экспорты `src/lib/components/ui/**` и `src/lib/types/api.d.ts`.

Branch protection на `main`: только через PR; обязательные проверки `front`, `back`, `drift`, `contract-guard` с S1-03, `e2e` с S1-10; squash merge; обязательных аппрувов нет (один разработчик); ветка удаляется после мёрджа.

### 16.3 Деплой

Деплой запускает владелец на VPS. GitHub Actions только проверяет PR (16.2): доступа к серверу и секретов у CI нет, реестра образов тоже.

Подготовка VPS, один раз:
1. Docker с плагином compose; DNS-запись `<domain>` на IP сервера; порты 80 и 443 открыты.
2. `git clone https://github.com/<owner>/fabrika-uyuta.git /opt/fabrika/app`.
3. `/opt/fabrika/app/.env`: копия `.env.example` с production-значениями (раздел 14). Заполнить: `DOMAIN`, `ACME_EMAIL`, `POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY`, `INTERNAL_API_TOKEN` (от 32 символов), `DJANGO_DEBUG=false`, `DJANGO_ADMIN_PATH` не `admin/`, `ENABLE_TEST_ENDPOINTS=false`, `CONSENT_VERSION`, при боевой таблице `SHEETS_BACKEND=google` с `GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/google-sa.json` и `GOOGLE_SPREADSHEET_ID`, при алертах `ALERT_EMAIL` и `EMAIL_*`. Хосты, CSRF-источники и адрес сайта выводит compose из `DOMAIN` (16.5).
4. `/opt/fabrika/app/google-sa.json`: ключ сервисного аккаунта, если `SHEETS_BACKEND=google`.
5. `deploy/deploy.sh`, затем `manage.py createsuperuser` в контейнере backend.

Релиз: `git pull` в `/opt/fabrika/app`, затем `deploy/deploy.sh`:
1. поиск `LEGAL_TEXT_PENDING` в `frontend/src`: найден → стоп, деплой не идёт (13.2);
2. `docker compose -f compose.prod.yml build`;
3. `docker compose -f compose.prod.yml run --rm release`: `check --deploy`, `migrate --noinput`, `createcachetable`, `sync_reference_data`, `sheets_check` (при `SHEETS_BACKEND=google`). Ошибка: выход 1, старые контейнеры продолжают работать;
4. `up -d --remove-orphans --wait --wait-timeout 300`: ждёт healthy backend `/healthz` (БД и heartbeat воркера) и frontend `/healthz`. Не дождались: выход 1;
5. `smoke.sh https://<domain>`.

Откат: `git checkout <предыдущий тег или коммит>` и снова `deploy.sh`. Работает, потому что миграции только расширяющие (15.1).

Сборке фронта нужно около 2 ГБ оперативной памяти. На сервере меньшего размера владелец включает swap до первого деплоя.

### 16.4 Caddy и маршрутизация

Caddy стоит в том же `compose.prod.yml`, что и остальные сервисы: внешней сети и второго compose-файла нет. Он слушает 80 и 443, берёт сертификат Let's Encrypt на `{$DOMAIN}` с почтой `{$ACME_EMAIL}` и монтирует том media read-only в `/srv/media`. Маршрутизацию задаёт сниппет `deploy/caddy/site.caddy` с одним аргументом: путь админки. Сниппет импортируют оба Caddyfile: `deploy/caddy/Caddyfile` (production) и `deploy/caddy/Caddyfile.e2e` (e2e на `localhost:8080`).

| Путь | Куда | Примечание |
|---|---|---|
| `/api/*` | `respond 404` | API только внутренний |
| `/media/*` | `file_server` из `/srv/media` | `Cache-Control: public, max-age=31536000, immutable` |
| `/<DJANGO_ADMIN_PATH>*`, `/django-static/*` | `reverse_proxy backend:8000` | `request_body max_size 200MB` |
| остальное | `reverse_proxy frontend:3000` | |

Везде: `encode zstd gzip`, заголовки из 13.1, `header -Server`. Production добавляет HSTS. Сертификаты и внутреннее состояние Caddy лежат в томах `caddy-data` и `caddy-config`: при пересоздании контейнера сертификат не перевыпускается.

### 16.5 Образы

- Образы собираются из репозитория там, где запускаются: `compose.prod.yml` и `compose.e2e.yml` объявляют `build` с контекстом в корне. Реестра нет, `docker login` не нужен.
- backend: `python:3.13-slim`, uv, `uv sync --frozen --no-dev`, `collectstatic` на сборке, пользователь без root. Роли: web `gunicorn config.wsgi -k gthread -w 2 --threads 4 -t 120 -b 0.0.0.0:8000`; worker `python manage.py run_sheets_worker` (`stop_grace_period: 30s`); release `python manage.py release`.
- frontend: `node:24-slim`, сборка pnpm, `node build`, пользователь без root, `PORT=3000`.
- `compose.prod.yml`: caddy, db, backend, worker, frontend и одноразовый `release` в профиле `release` (в `up` он не входит, его запускает `deploy.sh` через `run --rm`); тома `pgdata`, `media`, `caddy-data`, `caddy-config`; наружу открыты только порты Caddy.
- Окружение production: `.env` рядом с `compose.prod.yml` держит секреты и решения, остальное задаёт compose. Из `DOMAIN` выводятся `DJANGO_ALLOWED_HOSTS` (`<domain>,backend,127.0.0.1`: первый для посетителей, второй для SvelteKit, третий для healthcheck), `DJANGO_CSRF_TRUSTED_ORIGINS`, `PUBLIC_SITE_URL` (ссылка на админку в письмах-алертах, 8.4) и `ORIGIN`. Compose также ставит `APP_ENV=production`, `PUBLIC_APP_ENV=production`, `MEDIA_ROOT=/data/media`, `POSTGRES_HOST=db`, `API_INTERNAL_URL=http://backend:8000`, `ADDRESS_HEADER=X-Forwarded-For`, `XFF_DEPTH=1`. Значения этих переменных в `.env` на production не влияют.
- `compose.e2e.yml`: те же образы из Dockerfile, тот же release-шаг; Caddy на `localhost:8080` (`Caddyfile.e2e`); backend публикует `8000` только для тестового эндпоинта; `APP_ENV=e2e`, `DJANGO_DEBUG=false`, `ORIGIN=http://localhost:8080`, `LEAD_THROTTLE_RATE=1000/hour`, `ENABLE_TEST_ENDPOINTS=true`, `SHEETS_BACKEND=fake`, `SHEETS_POLL_SECONDS=1`; backend и worker делят том `/data` (media, фейковая таблица).

### 16.6 Ограничения Claude Code (`.claude/settings.json`)

S1-02 создаёт файл с `deny` и строкой `Edit(/tech.md)` в `ask`. S1-11 добавляет остальные строки `ask`.
```json
{
  "permissions": {
    "deny": [
      "Edit(/backend/apps/*/migrations/**)",
      "Edit(/contracts/openapi.yaml)",
      "Edit(/frontend/src/lib/types/api.d.ts)",
      "Read(/.env)",
      "Read(//**/google-sa*.json)"
    ],
    "ask": [
      "Edit(/tech.md)",
      "Edit(/contracts/fixtures/**)",
      "Edit(/backend/apps/core/enums.py)",
      "Edit(/backend/apps/leads/sheets/row.py)",
      "Edit(/frontend/src/lib/types/index.ts)",
      "Edit(/frontend/src/lib/server/api.ts)",
      "Edit(/frontend/src/lib/components/ui/**)",
      "Edit(/.env.example)"
    ]
  }
}
```
Генераторы (`makemigrations`, `spectacular`, `openapi-typescript`) пишут эти файлы как подпроцессы, правила им не мешают. Правила запрещают ручную правку инструментами сессии и требуют подтверждения владельца на правку контрактов. Claude Code запускается из корня репозитория: пути с `/` отсчитываются от него.

## 17. Тесты

Тесты привязаны к слайсу и PR, не к стадии. Стадия: несколько слайсов и несколько PR, отдельной сущности «тесты на стадию» нет. Слайс мёрджится только с тестами, гейт красный без них.

Главная ловушка: нейросеть пишет код, потом пишет тесты, которые подтверждают, что код делает то, что делает, вместе с багами. Тесты зелёные и ничего не проверяют. Поэтому правило: тесты выводятся из критериев приёмки задачи (AC), не из реализации. Тест кодирует контракт, не зеркалит код.

Порядок: тесты из AC пишутся до кода. Локаторы Playwright по ролям, подписям и текстам из tech.md (`getByRole`, `getByLabel`), не по CSS-классам.

Трассировка: у каждого AC задачи есть минимум один тест с номером AC в имени: `test_ac3_retryable_error_schedules_retry`, `it('AC3: ...')`. Ревью сверяет список AC со списком тестов.

Обязательные типы тестов на слайс (где применимо):
1. Контрактные на стыках. Самые ценные.
   - API ↔ `openapi.yaml`: Schemathesis гоняет все операции против WSGI-приложения с тестовой БД: нет 5xx, ответы по схеме. Плюс drift-проверка в CI.
   - Фронт ↔ API: типы из `api.d.ts`, svelte-check.
   - Джоба ↔ таблица: фейковый клиент и есть тестовый шов, валидирует каждую строку через `validate_row` и падает, если слайс шлёт мусор.
   - Маска ↔ нормализация телефона: `contracts/fixtures/phone-cases.json` на обеих сторонах.
2. Идемпотентность джобов. Нейросеть почти всегда пишет неидемпотентный хендлер. На каждый хендлер тест: прогнать его дважды с тем же входом и проверить, что эффект ровно один. Плюс сценарий «строка записана, ответ потерян». Иначе дубли строк в таблице.
3. Путь ошибки. Внешний клиент вернул 500, 429, таймаут, 403. Проверяется через фейк, умеющий возвращать ошибку. На фронте: API ответил 400, 429, 5xx, сеть недоступна.
4. Property-based на чистой доменной логике. Hypothesis (Python) и fast-check (TS). «Попробуй сломать» работает буквально: генеришь входы, проверяешь инварианты (идемпотентность, границы, сохранение данных, отсутствие исключений).
5. E2E на UI-слайс: happy path, один путь ошибки, axe на затронутых страницах. У формы также сценарий без JS (`javaScriptEnabled: false`).

Где лежат: бэкенд `backend/apps/<app>/tests/test_*.py`; фронт: логика `src/**/*.test.ts`, компоненты `src/**/*.svelte.test.ts` рядом с кодом; E2E `frontend/tests/e2e/*.spec.ts`.

Правила:
- В юнит- и интеграционных тестах нет сети: pytest-socket (разрешён только Postgres), Google только через фейк или `responses`, `fetch` на фронте мокается.
- Hypothesis-профиль `ci`: `max_examples=200`, `deadline=None`, `derandomize=True`. fast-check: `numRuns: 200` в CI.
- Компонентные тесты: окружение из `sv add vitest` (браузерный режим с `vitest-browser-svelte` или jsdom с `@testing-library/svelte`). Выбор фиксируется в Changelog в S1-02, подходы не смешиваются.
- Картинки для тестов генерируются Pillow в самом тесте, бинарных фикстур нет.
- Покрытие строк не цель. Цель: каждый AC покрыт.
- Claude Code: план тестов из AC через skill `engineering:testing-strategy`, если он установлен.

## 18. Конвенции

### 18.1 Код

- Язык: код, идентификаторы, комментарии, коммиты, PR на английском. Тексты UI, `verbose_name` в админке и tech.md на русском.
- Python: ruff (line length 100; правила `E,F,I,B,UP,DJ,S,SIM,RUF`; `S101` разрешён в тестах), mypy strict для `apps/`, аннотации везде, только aware-время (`django.utils.timezone.now()`), логгер `logging.getLogger(__name__)`, без `print`. Запросы в селекторах с `select_related` и `prefetch_related`, число запросов API-view зафиксировано тестом (`django_assert_max_num_queries`).
- TypeScript: `strict`, `noUncheckedIndexedAccess`, без `any` (ошибка eslint), без `!` вне тестов. API-типы только из `$lib/types`.
- Svelte: `interface Props` для пропсов, компонент до ~200 строк, данные пропсами.
- Стили: утилиты Tailwind и токены, mobile-first, брейкпоинты Tailwind по умолчанию. `@apply` только внутри примитивов.
- Имена файлов: TS kebab-case, компоненты Svelte PascalCase, Python snake_case.

### 18.2 Коммиты

- Формат всегда Conventional Commits: `type(scope): summary`.
- `type` из закрытого набора: `feat|fix|test|refactor|chore|docs`.
- `scope`: `web`, `api`, `admin`, `leads`, `sheets`, `images`, `infra`, `ci`, `tech`.
- `summary`: императив, со строчной, без точки в конце, до ~50 символов, по делу.
- Тело только если нужно объяснить почему, а не что.
- Сессия коммитит сама по ходу работы: маленькие логические коммиты после каждого осмысленного шага, не один коммит в конце. Каждый коммит по возможности проходит `make check-fast`.
- Изменение контракта: коммит `docs(tech): vN <summary>` раньше коммитов, которые его используют (раздел 3).

### 18.3 Ветки и PR

- Ветка: имя из Linear («Copy git branch name») или `<type>/ABC-<n>-<slug>`.
- Заголовок PR: `type(scope): summary (ABC-<n>)`. При squash merge он становится коммитом в `main`, ID задачи связывает ветку, PR и задачу в Linear.
- Тело PR:
```
## What
<1-3 lines: what the slice does>

## Contracts
tech.md v<N>; touched: <sections> | none

## Tests
- AC1: <test name>
- AC2: <test name>

## UI
<screenshots, UI slices only>
```

### 18.4 Комментарии и проза

- Комментарии кратко и по делу: объясняют почему, не пересказывают код.
- Закомментированный код в PR не остаётся. `TODO` только с ID задачи Linear.
- Дисциплина `stop-slop` на коммиты, PR, комментарии и правки tech.md: активный залог или императив, конкретика, без em-dash, без филлеров.

## 19. Definition of Done и чек-лист ревью

### 19.1 Definition of Done задачи

- [ ] `make gate` зелёный локально, CI зелёный (включая `e2e` и `contract-guard`).
- [ ] Lint, типы, build проходят.
- [ ] Задача Linear привязана: ID в заголовке PR.
- [ ] Тесты по доктрине раздела 17: выведены из AC, у каждого AC тест с его номером в имени.
- [ ] У каждого хендлера джобы тест идемпотентности; у каждого затронутого стыка контрактный тест.
- [ ] Контракты не выдуманы: в теле PR версия tech.md; изменение контракта сопровождается бампом.
- [ ] UI: работает на 360 px и 1440 px, axe чистый, у формы проверен путь без JS.
- [ ] Нет ПДн в логах.
- [ ] После деплоя слайс проверен на `<domain>`.

### 19.2 Чек-лист ревью (механический, по каждому пункту)

Владелец проходит сам или через skill `engineering:code-review`.
1. Нет выдуманных типов, полей, эндпоинтов: всё есть в tech.md.
2. Сгенерированные файлы не правились руками, миграции сгенерированы, data-миграций нет.
3. Не тронуты файлы вне плана задачи. Замороженные пути только с бампом версии.
4. Тесты проверяют контракт и AC, а не реализацию: нет проверок внутренних вызовов и снапшотов деталей реализации.
5. UI из примитивов, без самописных кнопок и полей. Цвета только токенами.
6. У каждого хендлера джобы тест идемпотентности.
7. На стыке слайса контрактный тест.
8. Пути ошибок покрыты.
9. Нет ПДн в логах, ошибках, алертах.
10. Только Svelte 5 руны, нет `$app/stores`.
11. Число запросов API-view зафиксировано тестом.
12. Новые зависимости прошли через `CONTRACT GAP`.
13. Коммиты и PR по конвенции 18.

Решения, меняющие контракты или раскладку слайсов, оформляются ADR в `docs/adr/` через skill `engineering:architecture`, если он установлен. Сами контракты всё равно живут в tech.md.

## 20. Long-lead: внешние зависимости

Принцип: long-lead блокирует реальную интеграцию, не разработку. Разработка идёт против фейков с первого дня. Все пункты запускаются в день один, параллельно S1-01.

| Что | Кто | Блокирует | До готовности |
|---|---|---|---|
| Проект GCP, Sheets API, сервисный аккаунт, JSON-ключ | владелец | S2-04 на staging | фейк |
| Тестовая таблица для проверки, доступ сервисному аккаунту | владелец | S2-04 | фейк |
| Таблица заказчика с заголовками 8.1, доступ сервисному аккаунту | заказчик | S2-12 | тестовая таблица |
| Доступность `sheets.googleapis.com` с VPS | владелец | S2-04 | фейк |
| VPS (в РФ, если действует 152-ФЗ), Docker | владелец | S1-10 | локально |
| Домен и DNS: `<domain>` | заказчик, владелец | S1-10 | IP |
| Политика ПДн, текст согласия, уведомления в РКН (обработка, трансграничная передача) | заказчик, юрист | S2-11, S2-12 | маркер `LEGAL_TEXT_PENDING` |
| Контент: логотип, фото работ, тексты, контакты | заказчик | S2-06..S2-10 на живых данных | `seed_demo` |
| SMTP для алертов | владелец | S2-05 | console email backend |
| S3-совместимое хранилище в РФ для бэкапов | владелец | S2-12 | локальные бэкапы |
| Шаблон сайта (архив владельца, вне репозитория с v10) | владелец | S1-01 | нет |

## 21. Стадия 1: каркас

Задачи строго по порядку. Каждая задача: одна ветка, один PR.

### S1-01 Инвентаризация шаблона
- Вход: `template/`. Выход: правка только tech.md (v2): приложение А заполнено, токены со значениями, список ассетов (логотип, иконки, фото, шрифты), итоговые `SiteImageSlot`, `NAV`, якоря, статичные тексты секций.
- AC1: каждая видимая секция шаблона сопоставлена фиче и источнику данных (поле API или статичный текст).
- AC2: токены раздела 11 перечислены со значениями из шаблона, шрифты с пакетами `@fontsource/*` и кириллицей.
- AC3: изменения слотов, навигации и секций описаны в Changelog v2.
- Тесты: нет (документ).

### S1-02 Монорепо и тулинг
- Фронт: `pnpm dlx sv create frontend` (TypeScript; add-ons tailwindcss, eslint, prettier, vitest, playwright), adapter-node, `envDir: '..'`, shadcn-svelte init, knip, fast-check, `openapi-typescript`, `openapi-fetch`, `@fontsource/*`. Скрипты `package.json`: `format`, `format:check`, `lint`, `check`, `knip`, `test:unit`, `test:e2e`, `gen:api`, `build`.
- Бэк: uv, Django 5.2 (проект `config`, приложения `core`, `content`, `leads`), DRF, drf-spectacular, python-dotenv, ruff, mypy со stubs, pytest-django, Hypothesis, Schemathesis, responses, pytest-socket.
- Корень: `Makefile` (15.4), `.env.example` (14) целиком, `.editorconfig`, `.gitignore` (`.env`, `backend/var/`, `node_modules`, `.venv`), `.dockerignore`, `.claude/settings.json` (16.6), `compose.yml` (dev: `postgres:18` с томом в `/var/lib/postgresql`, backend `runserver`; worker добавляет S1-07).
- Vite proxy в dev: `/media`, `/django-static`, путь админки → `http://localhost:8000`.
- `.env` создаёт владелец: `cp .env.example .env` (Claude Code `.env` не читает и не пишет).
- AC1: `make dev` и `pnpm -C frontend dev` поднимают стек; главная открывается; админка открывается через Vite proxy.
- AC2: `make gate` проходит на пустом проекте.
- AC3: `template/` не меняется и исключён из всех инструментов.
- AC4: подход к компонентным тестам записан в Changelog.

### S1-03 CI-гейт и защита `main`
- `ci.yml` (16.2, без `e2e`), `scripts/contract_guard.py` с тестами, branch protection.
- AC1: тривиальный PR проходит все джобы.
- AC2: намеренно сломанный формат, линт, тип или тест красит соответствующую джобу.
- AC3: `contract_guard.py`: при `Каркас: не готов` печатает затронутые замороженные пути и выходит с 0; при `Каркас: готов` без бампа версии выходит с 1; с бампом или меткой `no-contract-change` выходит с 0.
- AC4: `main` принимает изменения только через PR с зелёными `front`, `back`, `drift`, `contract-guard`.
- Тесты: pytest на AC3 на временном git-репозитории (`scripts/test_contract_guard.py`); AC1, AC2, AC4 вручную, ссылки на прогоны в PR.

### S1-04 Контракты данных и API
- Модели раздела 6, начальные миграции `make migrations`, `sync_reference_data` (15.2), регистрация моделей в админке с русскими `verbose_name`.
- API v1 целиком (раздел 7): сериализаторы и view для всех операций, коды 400, 403, 404, 429 в схеме. Поведение: заглушки из таблицы раздела 7.
- `apps/core`: `env.py`, `checks.py`, `phone.py` (12.3), пермишен внутреннего токена, ключ клиента по `X-Client-IP`, `/healthz` (БД), команда `release`.
- `make gen`: `contracts/openapi.yaml`, `api.d.ts`. Руками: `src/lib/types/index.ts`, `src/lib/server/api.ts`, `contracts/fixtures/phone-cases.json` (набор 12.3).
- AC1: `openapi.yaml` содержит все операции и компоненты раздела 7 с точными именами; поля вида и категории ссылаются на `ProductKindEnum` и `CategorySlugEnum`.
- AC2: запрос без `X-Internal-Token` или с неверным получает 403 на каждой операции `/api/v1/`.
- AC3: `sync_reference_data` дважды подряд даёт те же количества (5 категорий, 4 слота, 1 строка настроек, 2 группы) и не перезаписывает правки.
- AC4: ограничения БД: вторая строка `SiteSettings`, `sent` без `sheet_synced_at`, телефон не E.164 → `IntegrityError`.
- AC5: `check --deploy` при `APP_ENV=production` падает по каждому условию раздела 14.
- AC6: `normalize_phone` и `format_phone_display` проходят все векторы `phone-cases.json`.
- Тесты: Schemathesis по всем операциям (нет 5xx, ответы по схеме); Hypothesis на `normalize_phone` (идемпотентна на своём выходе, не зависит от разделителей, `8` и `+7` дают одно значение, выход по шаблону E.164 или `None`, не бросает исключений); pytest на AC2..AC6.

### S1-05 UI-кит и layout
- Токены из S1-01 в `app.css`, шрифты self-hosted с кириллицей и preload, примитивы раздела 11, `src/lib/domain/phone.ts`, layout (Header, MobileNav, Footer, SkipLink), `NAV`, `/dev/ui`, `+error.svelte`. Layout берёт данные из заглушки `GET /site-settings/`.
- AC1: `/dev/ui` показывает каждый примитив во всех вариантах и состояниях (обычное, disabled, error, loading).
- AC2: меню шапки строится из `NAV`: правка массива меняет меню без правки разметки.
- AC3: `/dev/ui` отвечает 404 при `PUBLIC_APP_ENV=production`.
- AC4: axe на `/dev/ui` и на странице ошибки без serious и critical.
- AC5: поля формы на `/dev/ui` отправляют значения без JS.
- AC6: `formatPhoneInput` проходит все векторы `masked` из `phone-cases.json`.
- AC7: пустые поля `SiteSettings` скрывают телефон и контакты в шапке и подвале, пустых подписей нет.
- Тесты: компонентные на Field (error → `aria-invalid`, `aria-describedby`), ResponsiveImage (null → заглушка с aspect; image → `srcset`, `sizes`, `width`, `height`), Button (`loading` блокирует), Header (AC7); fast-check на `formatPhoneInput` (идемпотентна, только допустимые символы, для `+7` не больше 11 цифр, не бросает); vitest на AC6; Playwright: `/dev/ui` на 360 и 1440 px, axe, AC5.

### S1-06 Пайплайн изображений
- `apps/content/services/images.py` (раздел 9), `ImageAdminMixin`: валидация, превью в списке и форме, вызов `ingest_image` в `save_model`, очистка и удаление файлов.
- AC1: JPEG 4000×3000 с EXIF-поворотом и GPS → мастер ≤ 2560 по длинной стороне, варианты 640, 1280, 1920 в WebP, цвет `#rrggbb`, EXIF удалён, ориентация применена.
- AC2: ширина 1500 → варианты [640, 1280, 1500]; 600 → [600]; апскейла нет.
- AC3: больше 20 МБ, меньше 800 px по длинной стороне, больше 40 Мпикс или не JPEG/PNG/WebP → ошибка на русском, в media ничего не записано.
- AC4: замена фото удаляет старую папку после коммита; очистка и удаление записи удаляют папку; откат транзакции сохраняет старые файлы.
- Тесты: Hypothesis на `plan_variants` (непустой, строго возрастает, максимум = `min(w, 1920)`, все ≤ w), `fit_within`, `average_color_hex`; pytest на AC1..AC4.

### S1-07 Шов Google Sheets и воркер
- `apps/leads/sheets/` (`row.py`, `client.py`, `fake.py`), `apps/leads/worker.py` (`sync_lead`, `backoff_seconds`, цикл, heartbeat, SIGTERM), команда `run_sheets_worker`, сервис `worker` в `compose.yml`, heartbeat в `/healthz`, тестовый эндпоинт `/api/v1/test/fake-sheet/`. `get_sheets_client()` для `google` до S2-04 бросает `ImproperlyConfigured`.
- AC1: заявка `pending` → один цикл воркера → в фейке ровно одна строка, прошедшая `validate_row`; заявка `sent`, `sheet_synced_at` заполнен.
- AC2: `sync_lead` дважды для одной заявки → одна строка. Сценарий `lose_response_once` → после ретрая одна строка, заявка `sent`.
- AC3: фейк отвечает 429, 500 или таймаутом → заявка `pending`, `attempts + 1`, `next_attempt_at` в пределах `[now + 0,8·base, now + 1,2·base]`, где `base = min(30·2^(n−1), 3600)`; после `SHEETS_MAX_ATTEMPTS` → `failed`.
- AC4: фейк отвечает 403 → `failed` сразу, `sheet_last_error` содержит статус и класс ошибки, ПДн нет.
- AC5: два воркера параллельно на одной заявке → одна строка.
- AC6: текст `=1+1` в комментарии попадает в строку как текст без изменений.
- AC7: `/healthz` отвечает 503, если heartbeat старше 120 с, и 200 после цикла воркера.
- Тесты: Hypothesis на `backoff_seconds` (границы, монотонность базы, потолок 3600·1,2) и `build_row` (8 ячеек, форматы A, B, D, метка E); pytest на AC1..AC7, AC5 в `transaction=True` с двумя потоками.

### S1-08 Сид и dev-окружение
- `seed_demo` (15.3), `backend/fixtures/demo/`, `make seed`.
- AC1: `make seed` дважды → те же количества; `seed_demo --reset` пересоздаёт демо-данные.
- AC2: после сида в БД: 4 слота с фото, 5 категорий с обложками, 12 работ (4 на главной), демо-контакты, 3 демо-заявки (`pending`, `sent`, `failed`); у каждой картинки варианты и цвет по разделу 9.
- AC3: `seed_demo` при `APP_ENV=production` завершается с ошибкой и ничего не пишет.
- AC4: демо-заявка `pending` доходит воркером до `backend/var/fake-sheet.jsonl`.
- Тесты: pytest на AC1..AC4.

### S1-09 Эталонный слайс: Hero
- Сквозная вертикаль и образец для всех слайсов Стадии 2: заглушка `home.slots` заменяется поведением. Админка `SiteImage` (4 фиксированных слота, без добавления и удаления, превью, `ImageAdminMixin`), селектор `get_home_content` (часть `slots`), `+page.server.ts`, `Hero.svelte` на `ResponsiveImage` (`loading="eager"`, `fetchpriority="high"`, `sizes="(min-width: 1024px) 50vw, 100vw"` с v7), H1, подзаголовок и CTA из шаблона (`src/lib/content/home.ts`). CTA ведёт на `/lead` (роут появится в S2-01).
- AC1: фото, загруженное в слот `hero` в админке, появляется на главной с `srcset` из всех вариантов и атрибутами `width` и `height`.
- AC2: пустой слот `hero` → страница рендерится без ошибок, фон из токена, H1 и CTA на месте.
- AC3: фото hero является LCP-элементом и не грузится лениво.
- AC4: `GET /api/v1/home/` делает не больше 4 запросов к БД.
- Тесты: pytest (слоты, fallback alt, AC4 через `django_assert_max_num_queries`); компонентный `Hero.svelte.test.ts` (AC2: image и null); Playwright `home.spec.ts` (AC1, AC3 через `PerformanceObserver` для LCP).

### S1-10 Деплой на VPS
- Dockerfile бэка и фронта (16.5), frontend `/healthz`, `compose.prod.yml`, `deploy/deploy.sh`, `deploy/smoke.sh`, Caddy с `site.caddy`, `compose.e2e.yml` и `Caddyfile.e2e`, джоба `e2e` в CI и в обязательных проверках.
- AC1: `deploy.sh` на VPS собирает образы, прогоняет release-шаг и поднимает стек; `https://<domain>` отвечает 200, `robots.txt` вне production запрещает индексацию.
- AC2: маршрутизация по 16.4: снаружи `/api/v1/home/` → 404; путь админки → Django; первый `/media/` URL со страницы отдаётся Caddy с `immutable`.
- AC3: release-шаг выполняет `migrate`, `createcachetable`, `sync_reference_data`; упавшая миграция прерывает деплой, старые контейнеры работают.
- AC4: `git checkout <предыдущий тег>` и `deploy.sh` откатывают сайт.
- AC5: джоба `e2e` гоняет в CI все E2E из S1-05..S1-09.
- Тесты: `smoke.sh` проверяет AC2 после каждого деплоя; AC5 в CI; AC3 и AC4 вручную, лог в PR.
- v10: деплой переведён на единый `compose.prod.yml` со сборкой на VPS, staging и GHCR убраны (16.3).

### S1-11 Чек-лист «Каркас готов»

Все пункты зелёные, затем одним PR: бамп версии, строка `Каркас: готов` (contract-guard переходит в режим ошибки), строки `ask` из 16.6 в `.claude/settings.json`.
- [ ] CI зелёный на тривиальном PR, красный на сломанном (S1-03).
- [ ] Layout, навигация данными, страница ошибки в `main` (S1-05).
- [ ] UI-примитивы импортируются и отрендерены в `/dev/ui`, axe чистый (S1-05).
- [ ] Поверхность API объявлена целиком, заглушки проходят Schemathesis (S1-04).
- [ ] Воркер гоняет демо-джоб против фейка; тест идемпотентности зелёный (S1-07, S1-08).
- [ ] Фейк Google Sheets работает на сид-данных, тестовый эндпоинт доступен в E2E (S1-07, S1-08).
- [ ] Миграции проходят на эфемерном Postgres в CI, `makemigrations --check` чистый (S1-03, S1-04).
- [ ] Drift `openapi.yaml` и `api.d.ts` зелёный (S1-04).
- [ ] Эталонный слайс Hero в `main` и задеплоен на staging (S1-09, S1-10).
- [ ] Long-lead пункты раздела 20 запущены.
- [ ] Транспорт реального времени: не нужен, живых данных нет.

## 22. Стадия 2: фичи слайсами

Каждый слайс заменяет заглушки каркаса поведением, повторяет раскладку эталона Hero (раздел 5) и закрывается по DoD (19.1).

### S2-01 Заявка: сквозной путь
- Цель: посетитель отправляет заявку с главной и со страницы `/lead`, с JS и без; заявка сохраняется и доходит до фейковой таблицы.
- Бэкенд: `apps/leads/services/create_lead.py` (телефон через `normalize_phone` в E.164, `consent_at`, `consent_version`, `sheet_status=pending`), `LeadCreateView` вместо заглушки. Невалидный телефон: 400 «Проверьте номер телефона», не 500.
- Фронтенд: роут `/lead` (`load` читает `?product=`, `actions.default`), фича `lead-form` (`LeadForm.svelte`), секция `#lead` на главной, `src/lib/domain/product-kind.ts`.
- Контракты: 7 (`POST /leads/`), `LeadCreateRequest`, `LeadCreated`, 12.1, 12.2 (успех); примитивы Field, Input, PhoneInput, Select, Textarea, Checkbox, Button, Alert.
- Зависит от: S1-11.
- AC1: с JS: валидная форма на главной → текст успеха из 12.2 на месте формы без перезагрузки, форма очищена, в БД одна заявка.
- AC2: без JS: форма уходит на `/lead`, страница показывает тот же текст, в БД одна заявка.
- AC3: API отвечает 201 `{id}` = `public_id`; заявка сохранена с телефоном в E.164, `consent_at` = время запроса, `consent_version` = `CONSENT_VERSION`, `sheet_status=pending`.
- AC4: после цикла воркера строка заявки есть в фейковой таблице, колонки A..H по 8.1.
- AC5: `/lead?product=<slug>` открывается с предвыбранным видом; неизвестный `product` игнорируется.
- AC6: SvelteKit передаёт `X-Internal-Token` и `X-Client-IP`; браузер не делает запросов к `/api/`.
- Тесты: pytest на AC3 и число запросов; тест action с моком `fetch` (201, заголовки AC6); Playwright: AC1, AC2 (`javaScriptEnabled: false`), AC4 (через тестовый эндпоинт), AC5, AC6 (слушатель запросов страницы); axe на `/` и `/lead`.

### S2-02 Заявка: валидация, ошибки, защита от спама
- Бэкенд: правила 12.1 в сериализаторе и `create_lead` (`apps/core/text.py`: `clean_name`, `clean_text`), honeypot, троттлинг, `source_url`.
- Фронтенд: `src/lib/domain/lead-errors.ts`, ошибки полей, Alert уровня формы, защита от двойной отправки.
- Контракты: 7 (поведение POST), 12, `phone-cases.json`.
- Зависит от: S2-01.
- AC1: каждый вектор `phone-cases.json` через API: `input` → сохранён `e164` либо 400 с «Проверьте номер телефона».
- AC2: `consent` false или отсутствует → 400 с текстом из 12.1, заявка не создана.
- AC3: `name`, `dimensions`, `comment` очищаются по 12.1; ответы 400 содержат только тексты из 12.1.
- AC4: непустой `website` → 201 с валидным UUID, заявка не создана.
- AC5: шестой запрос за час с одного `X-Client-IP` → 429; другой IP не затронут.
- AC6: `source_url` с хостом сохраняется как path + query; длиннее 500 обрезается.
- AC7: 400 в UI → ошибка под каждым полем (`aria-invalid`, `aria-describedby`), значения сохранены, фокус на первом ошибочном поле; с JS и без.
- AC8: 429, 5xx и сетевая ошибка → Alert с текстом из 12.2 и телефоном из `SiteSettings`.
- AC9: во время отправки кнопка заблокирована, двойной клик даёт один запрос.
- Тесты: Hypothesis на `clean_name`, `clean_text` (идемпотентны, без управляющих символов и крайних пробелов, длина не растёт); fast-check на `mapLeadErrors` (любое тело → только известные ключи и строки); pytest на AC1..AC6; тест action с моком `fetch` (400, 429, 500, сеть); Playwright: AC7 с JS и без, сетевая ошибка через `page.route` на POST `/lead` (AC8), AC9.

### S2-03 Заявка: диалог и CTA
- Фронтенд: `LeadDialog.svelte`, `dialog.svelte.ts` (`open(product?)`, `close()`) в фиче `lead-form`, LeadDialog в `+layout.svelte`, CTA в шапке и hero открывают диалог.
- Контракты: примитивы Dialog, Button; `LeadForm` из S2-01.
- Зависит от: S2-01.
- AC1: CTA в шапке и hero с JS открывает диалог с формой; фокус в первом поле; Esc и кнопка закрытия возвращают фокус на CTA.
- AC2: без JS CTA ведёт на `/lead`.
- AC3: успешная отправка из диалога показывает текст успеха в диалоге; повторное открытие показывает чистую форму.
- AC4: `open(product)` открывает форму с предвыбранным видом.
- Тесты: vitest на `dialog.svelte.ts` (open, close, product); Playwright AC1..AC4; axe на открытом диалоге.

### S2-04 Google Sheets: боевой клиент
- `apps/leads/sheets/google.py` (транспорт 8.2), классификация ошибок, команда `sheets_check`, включение в release-шаг, тестовая таблица на staging.
- Контракты: 8.1..8.4.
- Зависит от: S2-01; long-lead: ключ сервисного аккаунта, тестовая таблица.
- AC1: `append` шлёт `valueInputOption=RAW`, `insertDataOption=INSERT_ROWS`, диапазон `'<title>'!A:H`, тело с одной строкой из 8 строковых ячеек.
- AC2: 408, 429, 5xx, таймаут, обрыв соединения → `SheetsRetryableError`; 400, 401, 403, 404 → `SheetsPermanentError`.
- AC3: `exists` находит ID в колонке A, пропускает заголовок, на пустом листе возвращает `False`.
- AC4: `sheets_check` выходит с 0 при A1:H1 = `HEADERS`; с 1 и понятным сообщением при расхождении, отсутствии доступа или листа.
- AC5: на staging заявка из формы появляется в тестовой таблице за 15 с; `=1+1` в комментарии виден как текст.
- Тесты: `responses` на AC1..AC4 с проверкой параметров запроса; табличный тест классификации ошибок; AC5 вручную на staging, скриншот в PR.

### S2-05 Заявки в админке и алерты
- `LeadAdmin`: список (дата, ФИО, телефон, что заказать, статус отправки, попытки), фильтры (статус, вид, дата), поиск (ФИО, телефон), карточка только на чтение, действие «Повторить отправку». Алерты по 8.4 в цикле воркера.
- Зависит от: S2-01.
- AC1: группа «Заявки» видит заявки только на чтение и может повторить отправку; группа «Контент» заявок не видит.
- AC2: «Повторить отправку»: `failed` → `pending`, `attempts=0`, `next_attempt_at=now`, `sheet_alerted_at=NULL`; заявки в других статусах действие не меняет.
- AC3: есть кандидаты алерта (8.4) → одно письмо на `ALERT_EMAIL` со списком `public_id` и ссылкой на админку, без ПДн; кандидатам ставится `sheet_alerted_at`.
- AC4: кандидат, появившийся через 10 минут после письма, уходит следующим письмом после окна 30 минут; заявка без нового перехода статуса повторно в письмо не попадает.
- AC5: ошибка SMTP → лог без ПДн, `sheet_alerted_at` не ставится, повтор не раньше чем через 5 минут.
- AC6: добавлять и править заявки в админке нельзя; удалять может только суперпользователь.
- Тесты: Hypothesis stateful (`RuleBasedStateMachine`) с операциями «успех воркера», «retryable», «permanent», «повтор из админки», «проверка алертов», «время +N минут» и инвариантами: только переходы из 8.4, у `sent` есть `sheet_synced_at`, письмо не чаще раза в 30 минут, без нового перехода заявка не попадает в письмо дважды; pytest на AC1..AC6 с `mail.outbox`.

### S2-06 Категории на главной
- `CategoryAdmin` (5 фиксированных строк, без добавления и удаления, `list_editable` для порядка и публикации, обложка с превью), `home.categories` вместо заглушки, фича `categories` (`CategoryGrid`, `CategoryCard`).
- Зависит от: S2-03.
- AC1: категории идут по `position`, скрытые не показываются.
- AC2: категория без обложки → карточка с цветовой заглушкой, без битой картинки.
- AC3: карточка ведёт на `/catalog/<slug>`; CTA карточки открывает диалог с предвыбранным видом, без JS ведёт на `/lead?product=<slug>`.
- AC4: `GET /home/` остаётся в пределах 4 запросов к БД.
- Тесты: pytest на селектор (порядок, публикация, AC4); компонентный `CategoryCard.svelte.test.ts` (cover и null); Playwright (AC1, AC3), axe.

### S2-07 Галерея работ на главной
- `GalleryItemAdmin` (миниатюры, фильтр по категории, `list_editable` для порядка, публикации и «На главной»), инлайн в `CategoryAdmin`, `home.featured` вместо заглушки, фича `gallery` (`GalleryGrid`, `Lightbox` на Dialog, `gallery.ts` с `nextIndex`).
- Зависит от: S2-06.
- AC1: на главной только опубликованные работы с «На главной», по `position`, не больше 12.
- AC2: клик → лайтбокс с самым широким вариантом; стрелки листают; Esc закрывает и возвращает фокус на миниатюру.
- AC3: без JS миниатюры ведут ссылкой на самый широкий вариант.
- AC4: картинки галереи грузятся лениво, `width` и `height` заданы.
- Тесты: Hypothesis на селектор (результат ⊆ опубликованные ∩ «На главной», упорядочен, ≤ 12); fast-check на `nextIndex(i, n, dir)` (в диапазоне, по кругу); Playwright AC2, AC3; axe.

### S2-08 Страницы категорий
- Роут `/catalog/[slug]`, `CategoryDetail` вместо заглушки, фича `category-page` (заголовок, описание абзацами, галерея категории, форма с предвыбранным видом), `Seo`, `src/lib/domain/url.ts`, `src/lib/domain/text.ts`.
- Зависит от: S2-01, S2-07.
- AC1: опубликованная категория → 200 с названием, описанием и галереей по порядку.
- AC2: неизвестный или скрытый slug → страница 404.
- AC3: `<title>` и description из `seo_*` с fallback; canonical и OG-картинка абсолютными URL.
- AC4: форма на странице отправляет `product` = slug категории.
- AC5: `GET /categories/{slug}/` делает не больше 3 запросов к БД.
- Тесты: pytest на детальный селектор, 404 и AC5; fast-check на `splitParagraphs` (нет пустых абзацев, текст без пробельных символов сохраняется) и `absoluteUrl` (начинается с origin, без двойных слэшей); Playwright AC1..AC4.

### S2-09 Пакетная загрузка в галерею
- Админ-вью «Загрузить фото» на странице категории: до 20 файлов, каждый через `ingest_image` в `GalleryItem` (опубликован, не на главной, позиция после текущего максимума).
- Зависит от: S2-07.
- AC1: 20 валидных файлов → 20 работ в порядке выбора, позиции после текущего максимума.
- AC2: 21 файл → ошибка, ничего не создано.
- AC3: один невалидный файл среди валидных → весь пакет отклонён со списком плохих файлов по именам, в media ничего не записано.
- AC4: 20 фото по 12 Мпикс обрабатываются на staging быстрее 60 с.
- Тесты: pytest на AC1..AC3 на сгенерированных картинках; AC4 замер на staging, результат в PR.

### S2-10 Статичные секции и контакты
- `GET /site-settings/` вместо заглушки, `SiteSettingsAdmin` (синглтон: без добавления и удаления, пункт меню сразу открывает форму), инлайн `SocialLink`, нормализация телефона при сохранении. Секции по карте шаблона (приложение А): о компании (слот `about`), материалы (слоты `material_ldsp`, `material_mdf`), как мы работаем, преимущества, контакты.
- Зависит от: S1-11.
- AC1: все секции карты шаблона на месте с якорями из 10.1.
- AC2: телефон в шапке, подвале и контактах: ссылка `tel:` с E.164, текст `phone_display`.
- AC3: пустые поля `SiteSettings` скрывают свои строки в секции контактов, пустых подписей и `undefined` нет.
- AC4: в админке один объект настроек; пункт меню открывает его форму; невалидный телефон не сохраняется.
- Тесты: Hypothesis на `format_phone_display` (российский E.164 → шаблон `+7 (XXX) XXX-XX-XX`, цифры сохранены); pytest на синглтон и AC4; компонентный тест контактов с пустыми полями; Playwright на переход по якорям, axe.

### S2-11 SEO, юридические страницы, ошибки
- `Seo` на всех страницах, JSON-LD `FurnitureStore` (name, url, telephone, address, image), `sitemap.xml` (`src/lib/domain/sitemap.ts`), `robots.txt`, `/privacy`, `/consent`, ссылка на согласие в форме, страницы 404 и 500, favicon и manifest из шаблона.
- Зависит от: S2-08, S2-10.
- AC1: у каждой страницы уникальные title и description, canonical, OG-теги.
- AC2: sitemap содержит ровно опубликованные категории и статичные страницы, URL абсолютные.
- AC3: `robots.txt` в production разрешает индексацию и указывает sitemap, в остальных окружениях запрещает всё.
- AC4: JSON-LD парсится и содержит обязательные поля.
- AC5: `/privacy` и `/consent` доступны из подвала и формы; `deploy.sh` останавливается, если в `frontend/src` есть `LEGAL_TEXT_PENDING`.
- Тесты: fast-check на `buildSitemap` (все опубликованные есть, скрытых нет, дублей нет, URL абсолютные); Playwright на мета-теги и JSON-LD, axe.

### S2-12 Запуск в production
- Production на VPS, домен, таблица заказчика, SMTP, бэкапы (`deploy/backup.sh`: ночной `pg_dump -Fc` и архив media, 14 дней локально и копия в S3-совместимое хранилище в РФ), `deploy/RESTORE.md`, внешний мониторинг `https://<domain>/healthz`, пользователи админки (владелец: суперпользователь; контент-менеджер: группа «Контент»; менеджер: группа «Заявки»), тег `v1.0.0`.
- Зависит от: S2-01..S2-11; long-lead: юр. тексты и уведомления в РКН, таблица заказчика, домен.
- AC1: `deploy.sh` на VPS поднимает стек из `compose.prod.yml`; сайт доступен по `https://<domain>`, сертификат от Let's Encrypt, наружу открыт только Caddy.
- AC2: Lighthouse mobile ≥ 90 во всех четырёх категориях для `/` и одной `/catalog/<slug>`.
- AC3: бэкап создаётся каждую ночь; восстановление на чистых контейнерах из последнего бэкапа возвращает заявки и media, шаги в `deploy/RESTORE.md`.
- AC4: тестовая заявка в production появляется в таблице заказчика, затем удаляется из БД и таблицы.
- AC5: заказчик подтвердил уведомления в РКН и передал юр. тексты; маркера `LEGAL_TEXT_PENDING` нет.
- AC6: мониторинг шлёт алерт, если `/healthz` недоступен или отвечает 503 дольше 5 минут (падение фронта, бэка, БД или воркера).
- Тесты: `smoke.sh` против production; отчёт Lighthouse в PR; AC3 и AC6 вручную, лог в PR.

## 23. Вне скоупа v1

- Редактирование текстов секций в админке: тексты в коде по шаблону.
- Мультиязычность, тёмная тема.
- Аналитика и счётчики: только российские сервисы и после юр. проверки, через `CONTRACT GAP`.
- Капча: при спаме добавить российскую капчу через `CONTRACT GAP`.
- Уведомления в мессенджеры, интеграция с CRM. Для оповещения менеджеров о новых строках подходят встроенные уведомления Google Таблиц.
- Онлайн-калькулятор стоимости.
- Загрузка HEIC.
- Автоудаление старых заявок: срок хранения согласовать с заказчиком.
- Транспорт реального времени.


## Приложение А. Карта шаблона (итог S1-01, v2)

Источник: `template/demo/index.html` (порядок секций как в `Home.jsx`), `template/STYLE-GUIDE.md`, `template/src/index.css`. Фон `muted` у секции: `bg-secondary/40`.

| # | Секция шаблона | Якорь | Фича | Данные | Фон |
|---|---|---|---|---|---|
| 1 | Шапка: логотип, меню, телефон, CTA | нет | `layout/Header`, `layout/MobileNav` | `NAV`, `SiteSettings` | прозрачная, `glass` после 24px скролла |
| 2 | Hero: H1, подзаголовок, 2 CTA, фото | `hero` | `hero` | `slots.hero`, `home.ts` | default |
| 3 | About: текст, 4 пункта, фото | `about` | `sections` (`About`) | `slots.about`, `home.ts` | default |
| 4 | Directions: 5 категорий | `catalog` | `categories` | `home.categories`, `home.ts` | muted |
| 5 | Gallery: работы, лайтбокс | `works` | `gallery` | `home.featured`, `home.ts` | default |
| 6 | Materials: ЛДСП, МДФ | `materials` | `sections` (`Materials`) | `slots.material_ldsp`, `slots.material_mdf`, `home.ts` | muted |
| 7 | Process: 5 шагов | `process` | `sections` (`Process`) | `home.ts` | default |
| 8 | Advantages: 4 карточки | `advantages` | `sections` (`Advantages`) | `home.ts` | muted |
| 9 | LeadForm | `lead` | `lead-form` (`LeadSection`, `LeadForm`) | `POST /leads/`, `home.ts`, раздел 12 | default |
| 10 | Contacts: 4 карточки, CTA | `contacts` | `sections` (`Contacts`) | `SiteSettings`, `home.ts` | muted |
| 11 | Footer | нет | `layout/Footer` | `NAV`, `SiteSettings`, юр. ссылки | `bg-primary` |

Статичные тексты (`src/lib/content/home.ts`, `src/lib/content/pages.ts`). Кавычки «» не входят в текст.

| Место | Текст |
|---|---|
| Hero, H1 | «Мебель на заказ в Вологде» |
| Hero, подзаголовок | «Кухни, шкафы, шкафы-купе, кухонные столы и офисная мебель, изготовленные под ваше пространство.» |
| Hero, CTA | «Оставить заявку» (`/lead`, с JS открывает LeadDialog); «Смотреть наши работы» (`/#works`) |
| About, надзаголовок и H2 | «О компании» / «Делаем мебель, которая подходит именно вашему дому» |
| About, текст | «Проектируем и изготавливаем мебель по размерам вашего помещения. Замер, проект, производство и монтаж делаем сами.» (черновик: в шаблоне заглушка, текст даёт заказчик) |
| About, пункты | «Замер и проект», «Собственное производство», «Доставка и сборка», «Гарантия на изделия» |
| Directions | «Направления производства» / «Что мы производим» / «Изготовляем мебель на заказ для дома и офиса: от кухни до систем хранения.» |
| Карточка категории | название и `short_description` из API; CTA «Оставить заявку» |
| Gallery | «Наши работы» / «Галерея реализованных проектов»; подпись миниатюры: метка категории и `title`; кнопки лайтбокса «Закрыть», «Назад», «Вперёд»; счётчик лайтбокса `<n> / <всего>` (v7) |
| Materials | «Материалы» / «С чем мы работаем»; «ЛДСП»: «Практичный материал для корпусной мебели с широкой палитрой декоров.»; «МДФ»: «Гладкие и фрезерованные фасады для кухонь и шкафов.» |
| Process | «Как мы работаем» / «Путь от заявки до готовой мебели»; 01 «Заявка»: «Вы оставляете контакты.»; 02 «Замер»: «Мастер приезжает на объект.»; 03 «Проект»: «Согласуем дизайн и смету.»; 04 «Производство»: «Изготавливаем изделие.»; 05 «Монтаж»: «Доставка и установка.» |
| Advantages | «Почему выбирают нас» / «Подход, который виден в деталях»; 01 «Точные размеры»: «Мебель делается под ваши замеры.»; 02 «Свой цех»: «Контролируем качество на каждом этапе.»; 03 «Фурнитура»: «Надёжные механизмы и аккуратные детали.»; 04 «Монтаж»: «Доставим и соберём на месте.» |
| LeadForm | «Заявка» / «Расскажите, какая мебель вам нужна» / «Оставьте контакты: мы свяжемся и обсудим детали вашего проекта.»; после успеха кнопка «Отправить ещё одну»; поля и сообщения: раздел 12 |
| Contacts | «Контакты» / «Свяжитесь с нами» / «Позвоните, напишите или оставьте заявку: ответим в рабочее время.»; брендовый блок над сеткой (v9): карточка-ссылка «ВКонтакте» (`vk_url`, знак и фон `--brand-vk`) и карточка «MAX» (номер текстом без ссылки, знак и градиент `--brand-max` → `--brand-max-accent`); подписи карточек сетки «Телефон», «Email», «Адрес», «Часы работы»; ссылка «Открыть на карте» (`map_url`); CTA «Заказать мебель» (`/lead`) |
| Шапка | логотип «Фабрика Уюта»; CTA «Оставить заявку»; кнопка мобильного меню и заголовок Sheet «Меню»; кнопка звонка до `lg`: `aria-label` «Позвонить» (v7) |
| SkipLink | «Перейти к содержанию» |
| Подвал | «Фабрика Уюта»; «Мебель на заказ для дома и офиса. Кухни, шкафы, столы и системы хранения, изготовленные под ваше пространство.»; «Навигация»; «Заявка»: «Оставьте заявку, и мы обсудим детали вашего будущего изделия.» + «Оставить заявку»; «© <год> Фабрика Уюта. Все права защищены.»; «Политика обработки персональных данных», «Согласие на обработку персональных данных» |
| `/catalog/<slug>` | ссылка «Все направления» (`/#catalog`); H1 = `title`; галерея «Наши работы», пустая: «Скоро здесь появятся фото работ.»; блок формы как LeadForm |
| `/lead` | H1 «Оставить заявку»; текст как у LeadForm |
| `/privacy`, `/consent` | H1 «Политика обработки персональных данных», «Согласие на обработку персональных данных»; до текста юриста: черновик по 13.2, плашка «Проект документа. Текст проверяет юрист.» и маркер `LEGAL_TEXT_PENDING` (v8) |
| 404 | «Страница не найдена» / «Возможно, её удалили или в ссылке опечатка.» / «На главную» |
| 5xx | «Что-то пошло не так» / «Попробуйте обновить страницу через минуту.» / «На главную» |

SEO (S2-08, S2-11):

| Страница | title | description |
|---|---|---|
| `/` | «Фабрика Уюта: мебель на заказ в Вологде» | «Кухни, шкафы, шкафы-купе, кухонные столы и офисная мебель на заказ в Вологде. ЛДСП и МДФ.» |
| `/catalog/<slug>` | «<seo_title> \| Фабрика Уюта» | `seo_description` |
| `/lead` | «Оставить заявку \| Фабрика Уюта» | «Заявка на изготовление мебели на заказ.» (`noindex`) |
| `/privacy` | «Политика обработки персональных данных \| Фабрика Уюта» | «Как Фабрика Уюта обрабатывает персональные данные.» |
| `/consent` | «Согласие на обработку персональных данных \| Фабрика Уюта» | «Текст согласия на обработку персональных данных.» |
| ошибка | «Страница не найдена \| Фабрика Уюта», «Ошибка \| Фабрика Уюта» | без description, `noindex` |

Ассеты:
- Логотип: текстовый, «Фабрика Уюта» шрифтом `--font-display`. Файла нет.
- Иконки: inline SVG шаблона совпадают с Lucide (`Menu`, `ArrowRight`, `ArrowUpRight`, `Check`, `X`, `ChevronLeft`, `ChevronRight`, `CircleCheck`, `Send`, `Phone`, `Mail`, `MapPin`, `Clock`), берутся из `@lucide/svelte`.
- Знаки брендов (v9): `src/lib/icons/VkLogo.svelte` (белая монограмма официального логотипа VK, `vk.company/data/VK-logo/`) и `src/lib/icons/MaxLogo.svelte` (белый знак из брендбука MAX, `go.max.ru/brandbook`). Знаки монохромные, пропорции и форму путей не меняем, ставим только на брендовый фон карточек контактов.
- Фото: файлов в шаблоне нет (hero и about ссылаются на Unsplash, остальное цветные заглушки). `seed_demo` генерирует картинки Pillow (15.3). Пустой слот или обложка: заглушка ResponsiveImage.
- Шрифты: Cormorant Garamond (есть `cyrillic`), Manrope вместо Plus Jakarta Sans (у Plus Jakarta Sans только `cyrillic-ext`, русские буквы шли бы системным шрифтом). Пакеты в разделе 4.
- Favicon и manifest: в шаблоне нет. S2-11 кладёт `static/favicon.svg` (буква «Ф» цветом `--primary` на `--background`) и `static/manifest.webmanifest`.
