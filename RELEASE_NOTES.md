# InsightFlow — Release Notes

## v1.1 — UI/UX Polish Release

This is a pure presentation-layer release. No business logic, routes, database
schema, or features changed — every improvement below is visual, structural
CSS, or template markup polish on top of the v1.0 feature set.

### Branding

- Established **purple** (`#7C3AED` light / `#A78BFA` dark) as the single
  InsightFlow brand accent, replacing the previous indigo. Applied
  consistently across the sidebar mark, buttons, links, active nav states,
  focus rings, chart accents, and the auth screen's gradient panel.
- Green (success), red (negative), and amber (warning) remain reserved
  exclusively for semantic status — never used decoratively.
- Chart categorical colors (used only for multi-series data like the
  category breakdown donut) are visually distinct from the brand accent so
  they read as data, not competing UI accents.

### Dashboard

- Header now reads **"Dashboard Overview"** with a **"Last updated today"**
  subtitle in the top bar, instead of a bare "Dashboard" label.
- All four KPI cards (and every other KPI card across the app — Revenue
  Analytics, Inventory, Customer Profile, Invoices, Admin Panel) now have a
  small contextual icon, consistent label/value/delta hierarchy, and a
  soft-colored icon badge that shifts with trend state (positive/negative).
- Large currency KPIs display compact values (e.g. `$149.5K`) with the exact
  figure available on hover via a native tooltip — exact values are still
  used everywhere else (tables, invoices, exports).
- Revenue trend chart loading state now dims and disables the range
  selector while refetching, instead of swapping data with no feedback.
- Category donut chart increased in visual presence (cutout reduced from
  68% → 60%), tighter legend spacing, and a subtle border between slices.

### Cards & Layout

- Increased card border radius (16px → 18px) and richer, layered shadows
  for a more premium, less flat appearance.
- Cards and KPI cards now lift slightly on hover (subtle `translateY` +
  shadow bloom) with smooth easing; disabled on touch/mobile to avoid
  sticky-hover artifacts.
- Increased spacing throughout: page content padding, section margins,
  grid gaps, and card internals all increased ~15-25% for better breathing
  room without feeling sparse.
- Sidebar navigation links now have a smooth active-state indicator bar
  and a subtle padding shift on hover.

### Buttons

- Refined padding, added a lift-and-shadow hover animation, and a subtle
  icon nudge on hover for Export PDF / Export Excel and all primary/
  secondary buttons.
- Buttons now have a tactile press state (slight scale-down on click).

### Tables

- Stronger row hover treatment (accent-tinted for clickable rows).
- Improved header typography (bolder, wider letter-spacing) and slightly
  increased cell padding for better scanability.
- "View all" / "Manage inventory" style links now use a shared
  `.link-accent` style with an animated underline on hover.

### Empty States

- Every empty state (search results, filtered tables, no-data lists)
  across every page now shows a soft circular icon badge instead of a bare
  icon, so empty results read as "designed" rather than "broken."
- Added a compact inline variant for empty states inside smaller table
  contexts (e.g. "No rep-attributed sales yet").

### Charts

- Centralized Chart.js defaults (animation easing/duration, tooltip
  styling — rounded corners, border, matched typography) so every chart
  across the app looks consistent without per-chart repetition.
- All charts fade/animate in smoothly on load and remain fully responsive.

### Motion & Micro-interactions

- Dashboard content fades in on page load.
- Theme toggle now performs a full reload after saving the preference so
  Chart.js canvases (which bake in colors at draw time) always match the
  active theme instead of looking stale until refresh.
- Filter badges (status pills) now have a hover state where previously
  they had none.

### Bug Fixes

- **Fixed:** Invoices page rendered all 500+ rows unpaginated (a 290KB+
  single response). Now paginated at 15/page with lightweight SQL
  aggregate queries powering the summary cards, independent of the
  current page/filter.
- **Fixed:** A CSS specificity conflict where a legacy `.empty-state svg`
  rule would have silently overridden the new empty-state icon badge
  sizing on any page rendered after this change — removed the dead rule.
- **Fixed:** KPI label spacing was structurally dependent on a wrapper
  element only added to the dashboard; made resilient so every KPI card
  on every page renders correctly regardless of markup variant.
- **Fixed:** Chart.js failed to load (`ReferenceError: Chart is not
  defined`) due to a pinned CDN version that wasn't actually hosted.
  Chart.js is now vendored locally (`static/js/vendor/chart.umd.js`) —
  zero external runtime dependency for charts.
- Replaced deprecated `datetime.utcnow()` calls across models, auth, and
  the seed script with a shared timezone-safe helper.

---

## v1.0 — Initial Release

Full-stack Flask business analytics dashboard: authentication & roles,
dashboard KPIs, sales & revenue analytics, inventory management, customer
directory, invoicing, admin panel, and PDF/Excel report export. Seeded with
realistic demo data. Docker-ready with gunicorn.
