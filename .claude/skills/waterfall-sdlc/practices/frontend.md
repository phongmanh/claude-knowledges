# Frontend best practices (web, any stack)

Engineering practices for browser-based clients, grouped by quality attribute.

- **Targets and verification:** [quality-attributes.md](quality-attributes.md).
- **Where these practices apply in the lifecycle:**
  - design decisions: [Phase 2](../phases/2-system-design.md) and [Phase 3](../phases/3-detailed-design.md);
  - coding: [Phase 4](../phases/4-implementation.md);
  - tests: [Phase 5](../phases/5-testing.md);
  - release: [Phase 6](../phases/6-deployment.md).

## Architecture & maintainability
- **Choose a rendering strategy per route.** The options are client-side, server-side, static, incremental or streaming. Decide from SEO, personalisation and performance needs, and record the decision in an ADR. Public, indexable content should never depend on client-only rendering.
- **Component-driven architecture with a design system.**
  - The design system provides design tokens (colour, type, spacing) and accessible primitive components.
  - Features are built by composing these.
  - The result is one source of truth for look and behaviour.
- **Keep server state separate from UI state.**
  - Fetched data lives in a cache layer with clear keys and invalidation rules.
  - Local UI state stays local.
  - Avoid global state by default.
- **Generate a typed API client from the contract**, so the frontend and backend can't drift apart silently.
- **Code structure:**
  - Organise folders by feature, with clear module boundaries.
  - Use strict typing and linting.
  - Allow no ad-hoc colours or spacing outside the tokens.
- **Set a dependency budget.** Every library must earn its bytes and its maintenance cost.
- **Use micro-frontends only when several independent teams must deploy separately.** They add real complexity.

## Testability
- **Follow the test pyramid:**
  - **Unit tests** for logic: utilities, state, data transformation.
  - **Component tests** that render and interact the way users do, finding elements by role, label and text rather than CSS classes.
  - **A few end-to-end tests** for the critical journeys.
- **Mock the network at the HTTP layer**, using contract-based mocks, not internal modules.
- **Visual regression tests** for design-system components.
- **Automated accessibility assertions** in component and end-to-end tests. They catch only part of the issues, so manual checks are still needed.
- **Keep tests deterministic:** fake timers, a fixed locale and time zone, seeded data.
- **Use test IDs only** where accessible queries can't do the job.

## Performance
- **Targets.** Core Web Vitals "good" at p75: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1. Add per-route budgets (JS/CSS size, image weight, request count) and **enforce them in CI**.
- **Ship less JavaScript:**
  - Split code by route.
  - Lazy-load content below the fold and rarely used features.
  - Tree-shake.
  - Audit heavy dependencies.
- **Images:**
  - Responsive `srcset`/`sizes` and modern formats (e.g. AVIF, WebP).
  - Lazy-load images below the fold.
  - Set explicit width and height (or an aspect ratio) so the layout doesn't shift.
  - Prioritise the image that drives LCP.
- **Fonts:** subset them, preload the critical ones, choose a `font-display` strategy, and limit the number of families and weights.
- **Main thread:**
  - Keep tasks under 50 ms by breaking up long work.
  - Move heavy computation to web workers.
  - Avoid layout thrashing.
- **Lists:** virtualise long lists, and paginate or load incrementally.
- **Caching and delivery:**
  - Content-hashed, immutable assets with long cache lifetimes, served from a CDN.
  - Compression (Brotli or gzip) and HTTP/2 or HTTP/3.
  - Preconnect and preload only for resources proven to be critical.
- **Third-party scripts** often make pages slow. Keep them few, each with an owner and a review. Load them async, deferred, or behind a facade.
- **Measure both in the lab** (a throttled mid-tier device) **and in the field** (real-user monitoring).

## Scalability
- **Offload to the CDN and edge.** Serve static and cacheable pages without hitting the origin servers, with correct `Cache-Control` and `ETag` headers.
- **Reduce request volume:**
  - Deduplicate and cache identical requests in the client.
  - Debounce or throttle requests that users trigger rapidly, such as search-as-you-type.
- **Back off on HTTP 429/503**, and honour `Retry-After`.
- **Scale the codebase as well as the traffic.** Use module boundaries, a shared design system, ownership for each area, and consistent conventions.

## Reliability
- **Error boundaries** go around each independent part of the page, with a useful fallback and a retry. One failing widget must not blank the whole page.
- **Progressive enhancement** for core flows, where SEO, accessibility or resilience demand it.
- **Poor networks:**
  - Set timeouts and show a retry UI.
  - Use optimistic updates with rollback.
  - Add offline caching (a service worker) if the SRS requires offline use.
- **Recover from chunk-load failures after a deploy.** Retry, then reload. Users with an old tab open will request files that have since changed.
- **Prevent double submission:** disable the action while it's pending, and send an idempotency key. Keep form input when an error occurs.
- **Feature flags and kill switches** for risky features.

## Security
- **XSS:**
  - Rely on the framework's automatic output escaping, and avoid raw-HTML APIs.
  - If HTML must be rendered, sanitise it with a vetted sanitiser.
  - Adopt Trusted Types where supported.
- **Content Security Policy:** strict and nonce- or hash-based. No `unsafe-inline` or `unsafe-eval`. Report violations.
- **Sessions:**
  - Prefer a backend-for-frontend with **httpOnly, Secure, SameSite** cookies.
  - **Don't store tokens in localStorage or sessionStorage.** Any injected script can read them.
  - For public clients, use the OAuth authorisation code flow with PKCE.
- **CSRF:** when cookies authenticate requests, use SameSite cookies plus anti-CSRF tokens on state-changing requests.
- **Clickjacking:** set `frame-ancestors` in the CSP (or `X-Frame-Options`).
- **Headers:** HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`.
- **Third-party code:** Subresource Integrity for externally hosted scripts; lockfiles and dependency scanning.
- **Nothing secret goes in the bundle.** Every file sent to the browser is public, including build-time environment variables.
- **URLs and messages:**
  - Validate and encode URL parameters.
  - Put redirect targets on an allow-list, so there are no open redirects.
  - Check the `origin` on `postMessage`.
  - Keep sensitive data out of URLs and analytics.
- **Client-side validation is for UX only.** The server validates everything again.

## Privacy
- **Consent:**
  - Load non-essential cookies, analytics and ad tags **only after consent**, region by region.
  - Make withdrawing consent as easy as giving it.
- **Trackers and PII:**
  - Minimise third-party trackers.
  - Never send PII to analytics.
  - Mask sensitive fields in session-replay tools, or don't use those tools.
- **Global Privacy Control:** honour it where the law requires.
- **Browser storage:** set a retention period for data kept there, and clear it on logout.

## Accessibility & UX
Target WCAG 2.2 AA.

- **Semantic HTML first:** buttons, links, headings in order, lists and landmarks. Use ARIA only to fill gaps that native elements can't (the first rule of ARIA).
- **Keyboard:**
  - Everything is operable by keyboard, in a logical focus order.
  - The focus indicator is visible and not hidden by sticky elements.
  - Provide a skip link, and no keyboard traps.
- **Focus management:** move focus sensibly on route changes. When a dialog opens, keep focus inside it; when it closes, return focus to where it was.
- **Forms:**
  - Visible labels and instructions.
  - Errors identified in text, linked to their fields, with suggested fixes.
  - `autocomplete` attributes, and no asking for the same data twice.
- **Alternatives and contrast:**
  - Text alternatives for images; captions and transcripts for media.
  - Contrast ≥ 4.5:1, or 3:1 for large text and UI components.
- **Reflow and motion:**
  - Content reflows at 320 CSS px without horizontal scrolling, and text resizes to 200%.
  - Respect `prefers-reduced-motion`.
- **Pointer input:** targets ≥ 24×24 CSS px (SC 2.5.8), and an alternative to every dragging movement.
- **Dynamic content and authentication:**
  - Announce dynamic changes with live regions.
  - Make authentication accessible: no cognitive puzzles without an alternative.
- **Custom widgets** (menus, tabs, comboboxes) follow the WAI-ARIA Authoring Practices.

## Internationalisation
- **Messages:** externalise them in ICU message format (plurals, gender, select), and never concatenate them.
- **Formatting:** format for the locale with the platform `Intl` APIs. Handle time zones explicitly and store times in UTC.
- **Direction and layout:**
  - Set the `lang` and `dir` attributes.
  - Use CSS logical properties (`margin-inline-start`, not `margin-left`) so layouts work right-to-left.
  - Keep text out of images, and build layouts that tolerate text expansion.
- **Locale routing:** route by locale, with `hreflang`, for SEO.

## SEO
- **Indexable pages are server-rendered or static HTML.**
- **Metadata and URLs:**
  - A unique `<title>` and meta description on each page.
  - Canonical URLs that are clean and stable.
- **Discovery:**
  - An XML sitemap and a `robots.txt`.
  - Structured data (schema.org) where relevant.
  - Open Graph and social metadata.
- **Performance and mobile-friendliness affect ranking.** Core Web Vitals are part of SEO.
- **Status codes:** return the correct ones (404, 410, 301). Indexable content never relies on client-side-only redirects.

## Observability
- **Real-user monitoring** of Core Web Vitals and navigation timings, broken down by page, device and release.
- **JavaScript error tracking**, with source maps uploaded **privately** rather than served publicly.
- **Analytics and correlation:** follow the tracking plan, respect consent, and send a correlation ID with API calls.
- **Synthetic monitoring** of critical journeys from several regions, plus a dashboard for each release.

## Delivery & release
- **CI checks:** lint, type check, unit and component tests, build, bundle budgets, accessibility checks and performance budgets.
- **Preview environments:** one per PR where feasible, for review and testing.
- **Build once.** Inject each environment's configuration at deploy time or runtime, not by rebuilding per environment.
- **Deploy and roll back:**
  - Deploy atomically, with immutable hashed assets, short-cache HTML and CDN invalidation.
  - Roll back by re-pointing to the previous build.
- **Browser support targets** are declared in configuration and reviewed periodically.

## Compatibility
- **Browser matrix:** base it on real audience data (e.g. the last two versions of evergreen browsers, plus the mobile browsers your users have).
- **Feature detection:** use it with targeted polyfills only where needed, never user-agent sniffing.
- **Responsive design:** build mobile-first. Test on real devices, especially mobile Safari and low-end Android phones.
- **Print styles:** add them if users print, e.g. invoices or tickets.
