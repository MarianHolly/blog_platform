# Frontend

Astro 6 SSR application. Lives in `frontend/`.

---

## Configuration

```js
// astro.config.mjs
export default defineConfig({
    site: 'http://localhost:4321',
    output: 'server',        // full SSR — all pages rendered on request
    integrations: [sitemap()],
    vite: { plugins: [tailwindcss()] },
});
```

`output: 'server'` means every page is rendered server-side on each request. This keeps content always fresh from the Django API without needing a rebuild when articles are published.

---

## Pages

| Route | File | Description |
|---|---|---|
| `/` | `pages/index.astro` | Home — 6 latest articles + first page of bulletins |
| `/articles` | `pages/articles/index.astro` | Paginated article list with search |
| `/articles/[slug]` | `pages/articles/[slug].astro` | Article detail + comments |
| `/bulletins` | `pages/bulletins/index.astro` | Paginated bulletin list with search |
| `/bulletins/[slug]` | `pages/bulletins/[slug].astro` | Bulletin detail + its articles |

All pages redirect to the list page if the requested resource is not found (404 from API).

---

## API Client (`src/lib/api.ts`)

Single source of truth for all backend communication. All fetch calls go through `apiFetch()` which handles base URL, auth headers, and error throwing.

### Types exported

```typescript
Author, Profile, BulletinSummary, BulletinDetail,
ArticleSummary, ArticleDetail, Comment,
PaginatedResponse<T>, TokenPair
```

### Functions exported

**Auth**
- `login(username, password) → TokenPair`
- `refreshToken(refresh) → { access }`

**Articles**
- `getArticles(params?, token?) → PaginatedResponse<ArticleSummary>`
- `getArticle(slug, token?) → ArticleDetail`
- `likeArticle(slug, token) → void`
- `bookmarkArticle(slug, token) → void`

**Bulletins**
- `getBulletins(params?, token?) → PaginatedResponse<BulletinSummary>`
- `getBulletin(slug, token?) → BulletinDetail`
- `subscribeToBulletin(slug, token) → void`

**Comments**
- `getComments(articleId, token?) → PaginatedResponse<Comment>`
- `createComment(articleId, content, token) → Comment`
- `deleteComment(id, token) → void`

The `token?` parameter is optional — public endpoints work without it.

---

## Components

### `BaseLayout.astro`
HTML document shell. Imports `global.css`, renders `<Header>` and `<Footer>`, wraps content in a `max-w-5xl` centered container.

Props: `title: string`, `description?: string`

### `Header.astro`
Sticky top navigation with links to Home, Articles, Bulletins, and a Sign in button. Active link is highlighted in blue based on `Astro.url.pathname`.

### `Footer.astro`
Minimal footer with copyright year and nav links.

### `ArticleCard.astro`
Summary card for an article. Displays title, subtitle, bulletin name, author, date, likes, comments. Title links to `/articles/[slug]`.

Props: `article: ArticleSummary`

### `Pagination.astro`
Numeric page navigation. Renders nothing if only one page. Builds URLs using `URLSearchParams` against the current `baseUrl`.

Props: `currentPage`, `totalCount`, `pageSize`, `baseUrl`

---

## Styling

Tailwind CSS 4 via `@tailwindcss/vite` plugin. No separate config file needed — Tailwind 4 uses CSS-first configuration.

`src/styles/global.css` contains:
- `@import "tailwindcss"` — base import
- `.prose` utility classes — applied to article `content` HTML rendered via `set:html`. Styles headings, links, lists, blockquotes, code blocks, images.

---

## Environment

`PUBLIC_API_URL` (in `frontend/.env`) is the only required variable. Astro exposes it to server-side code via `import.meta.env.PUBLIC_API_URL`.

```
PUBLIC_API_URL=http://localhost:8000
```

In Docker, this is overridden to `http://web:8000` (Django service name) in `docker-compose.yml`.

---

## What Is Not Yet Implemented

| Feature | Notes |
|---|---|
| Login / register pages | Auth flow — JWT token storage and management |
| User profile page | Show profile, articles, subscriptions |
| Like / bookmark buttons | Require auth — client-side interaction |
| Comment form | Requires auth |
| Writer dashboard | Article management |
| Subscribe button | Requires auth |
| Error pages (404, 500) | Custom Astro error pages |
| RSS feed | `@astrojs/rss` is installed, not wired up |
