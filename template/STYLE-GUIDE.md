# Фабрика Уюта — гайд по стилю

Стиль восстановлен из исходников сайта (`index.css`, `tailwind.config.js` и компоненты секций).
Характер: тёплый «деревянный» минимализм — кремовый фон, шоколадно-коричневый акцент,
высококонтрастная антиква в заголовках, матовое стекло на карточках, крупные скругления.

## Цвета (светлая тема — единственная, что используется на сайте)

| Токен | HSL (как в CSS) | HEX |
|---|---|---|
| `background` | `38 27% 97%` | `#F9F8F5` |
| `foreground` | `0 0% 17%` | `#2B2B2B` |
| `card` | `38 33% 99%` | `#FDFDFC` |
| `primary / accent / ring` | `27 22% 33%` | `#675242` |
| `primary-foreground` | `38 27% 97%` | `#F9F8F5` |
| `secondary` | `36 22% 92%` | `#EFEBE6` |
| `secondary-foreground` | `27 22% 24%` | `#4B3C30` |
| `muted` | `36 20% 94%` | `#F3F0ED` |
| `muted-foreground` | `30 7% 42%` | `#736B64` |
| `destructive` | `0 72% 48%` | `#D32222` |
| `border / input` | `36 18% 82%` | `#D9D3C9` |
| `chart-1` | `27 22% 33%` | `#675242` |
| `chart-2` | `36 22% 52%` | `#A08A6A` |
| `chart-3` | `173 25% 39%` | `#4B7C77` |
| `chart-4` | `43 30% 66%` | `#C2B48E` |
| `chart-5` | `12 30% 55%` | `#AF786A` |

Дополнительно (захардкожено в `.glass`, `.glass-dark` и тенях):
- стекло: фон `rgba(249,247,242,.78)`, рамка `rgba(209,199,183,.45)`, blur 16px, saturate 130%
- тёмное стекло: фон `rgba(44,44,44,.64)`, рамка `rgba(209,199,183,.16)`, blur 16px
- тень плавающих плашек: `0 30px 60px -30px rgba(44,44,44,.45)`; шапка при скролле: `0 18px 50px -30px rgba(44,44,44,.5)`
- тень при hover карточки: `0 36px 70px -36px rgba(44,44,44,.32)`

Тёмная тема (`.dark`) в CSS — стандартная заготовка shadcn и на сайте не используется.

## Шрифты (Google Fonts)

- Заголовки и цифры: **Cormorant Garamond** (300–700, italic 400) — `font-heading`, `font-display`
- Текст и интерфейс: **Plus Jakarta Sans** (300–700) — `font-body`
- У h1–h4 `letter-spacing: -0.02em`; у body `font-feature-settings: "ss01","cv01"`

Подключение:
```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

## Типографика (классы из компонентов)

| Роль | Классы |
|---|---|
| H1 (hero) | `font-heading text-[2.75rem] leading-[1.05] sm:text-6xl lg:text-[5rem] font-light text-primary text-balance` |
| H2 секции | `font-heading text-4xl sm:text-5xl lg:text-6xl font-light text-primary leading-[1.08] text-balance` |
| H2 «О компании» | то же, но `lg:text-[3.5rem]` |
| H3 карточки | `font-heading text-2xl text-primary` (в материалах — `text-3xl`) |
| Надзаголовок секции | `text-xs font-medium uppercase tracking-widest text-muted-foreground mb-4` |
| Лид/описание | `text-lg text-muted-foreground leading-relaxed` |
| Большие номера | `font-heading text-4xl|5xl font-light text-primary/25` |

## Форма и отступы

- Контейнер: `mx-auto max-w-7xl px-5 md:px-8`
- Секция: `py-24 md:py-32`; чередование фона: обычный → `bg-secondary/40`
- Радиусы: кнопки и чипы `rounded-full`; карточки `rounded-[1.5rem]`/`[1.75rem]`; крупные медиа и форма `rounded-[2rem]`; плашки поверх фото `rounded-2xl`
- Сетки: `gap-5 md:gap-7`; hero и «О компании» — 2 колонки (`lg:grid-cols-12` / `lg:grid-cols-2`)
- Фото: пропорции `aspect-[4/5]`, поверх — градиент `from-primary/80 via-primary/15 to-transparent`

## Компоненты

- **Кнопка primary**: `rounded-full bg-primary px-7 py-4 text-base font-medium text-primary-foreground hover:bg-primary/90`, иконка сдвигается на hover (`group-hover:translate-x-1`)
- **Кнопка secondary**: `rounded-full glass px-7 py-4 text-primary hover:bg-secondary/60`
- **Чип фильтра**: активный `bg-primary text-primary-foreground`, неактивный `glass text-foreground/75 hover:text-primary`
- **Карточка**: `rounded-[1.5rem] glass p-7 lift-hover`
- **Поле формы**: только нижняя линия `border-b border-border focus:border-primary`, прозрачный фон, подпись — uppercase `tracking-widest`
- **Шапка**: фиксированная «пилюля»; в верхней позиции прозрачная, после 24px скролла — `glass` и тень
- **Футер**: `bg-primary text-primary-foreground`, вторичный текст — `text-primary-foreground/50…/80`
- **Линия стыка** `.joinery-line`: горизонтальный градиент по токену `border` (блок «Процесс»)

## Анимации

- `.reveal` + `.is-visible`: появление 0.9s `cubic-bezier(.16,1,.3,1)`, сдвиг 28px и scale .985; задержки в сетках `i*70ms` / `i*80ms`
- `.lift-hover`: подъём на 6px за 0.55s
- Zoom изображений на hover: `duration-700 group-hover:scale-105`
- Учтён `prefers-reduced-motion`

## Порядок секций главной (по `Home.jsx`)

Header → Hero → About → Directions → Gallery → Materials → Process → Advantages → LeadForm → Contacts → Footer.
Фон чередуется: `Directions`, `Materials`, `Advantages`, `Contacts` — `bg-secondary/40`, остальные — основной.
Данные приходят из сущностей `FurnitureCategory`, `Material`, `GalleryItem`, `SiteContent` (при пустом ответе — `DEFAULT_*` из `siteData`).

## Админ-панель (`Admin.jsx`)

- Каркас: `min-h-screen bg-secondary/30 flex`
- Сайдбар: `w-64 bg-card border-r border-border`, на мобильных выезжает (`translate-x`), затемнение `bg-primary/30`
- Логотип: `font-heading text-xl text-primary`, подпись `text-xs text-muted-foreground`
- Пункт меню: `rounded-xl px-3 py-2.5 text-sm font-medium`; активный `bg-primary text-primary-foreground`, остальные `text-foreground/75 hover:bg-secondary`
- «Выйти»: `text-destructive/80 hover:text-destructive`
- Верхняя панель: `sticky top-0 glass border-b border-border px-5 md:px-8 py-4`, заголовок `font-heading text-2xl text-primary`
- Контент: `p-5 md:p-8 max-w-6xl mx-auto`

## Авторизация (Login, Register, ForgotPassword, OAuthConsent)

Построена на shadcn/ui (`Button`, `Input`, `Label`, `InputOTP`) и `AuthLayout`. Тексты в исходниках английские.
- Кнопки и поля: высота `h-12`; поля с иконкой слева `pl-10`
- Ошибка: `p-3 rounded-lg bg-destructive/10 text-destructive text-sm`
- Разделитель «or»: линия `border-border`, подпись `bg-card px-3 text-xs uppercase text-muted-foreground`
- Ссылки: `text-primary font-medium hover:underline`
- Радиус shadcn-элементов берётся из `--radius` (0.9rem): `rounded-md` = 0.9rem − 2px

> Стили `AuthLayout` и базовые стили shadcn-компонентов в присланных файлах отсутствуют — в демо они восстановлены
> (см. README). Если пришлёте `AuthLayout.jsx`, `components/ui/button.jsx`, `input.jsx`, я сверю точнее.
