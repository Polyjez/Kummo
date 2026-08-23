# ADR 0005 — Localization: English source, JSON catalogues, no library

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-23 |
| **Deciders** | Architect |

## Context

The site was written in German only, with the text inline in seven HTML pages and in `js/app.js` / `js/auth.js`. It has to be available in at least English and German, and the person maintaining the translations is not a developer: they must be able to add or correct text without touching HTML, JavaScript, or a build step. More languages should cost a file, not a refactor.

The frontend is deliberately framework-free and bundler-free, so anything that assumes a build pipeline (message extraction, compiled catalogues, `.po` files) is out of place. Vendoring i18next would work but adds ~50 KB of third-party code to a browser bundle that today has zero dependencies, for features (namespaces, backends, context) this site does not use.

## Decision

- **English is the source language.** The text written in the markup is English; it is also what a visitor sees if a catalogue fails to load.
- **One JSON catalogue per language**, `static/i18n/<lang>.json`, in the format i18next uses: nested keys, `{{name}}` interpolation, `_one` / `_other` plural suffixes. A translator copies `en.json`, translates the values, and drops it in.
- **A small runtime**, `static/js/i18n.js` (~200 lines), resolves keys. Markup carries `data-i18n`, `data-i18n-html` and `data-i18n-attr` attributes; page scripts call the global `t(key, options)` shorthand it defines.
- **Language selection** is: an explicit choice (remembered in `localStorage` under `kummo_lang`) → the browser's `Accept-Language` → English. An EN/DE switcher sits in the header of every page, and switching reloads the page.
- **A missing key falls back** to the same key in English, and then to the key itself.
- **Only the interface is translated.** Vendor-entered content — activity titles, descriptions, addresses — is shown as it was entered. Localizing it needs a schema change and a per-language vendor form, and is not in scope here.

## Consequences

- Adding a language is one file plus one entry in `SUPPORTED` in `i18n.js`; no build, no dependency, no backend change.
- The catalogue format stays compatible with i18next and with translation tools that speak it (Weblate, Crowdin), so moving to a library or a translation platform later is not a rewrite.
- `test/i18n.test.js` guards the two failure modes a non-technical workflow produces: a key present in one catalogue but not the other, and a key used in a page that no catalogue defines.
- A visitor whose language is not English sees the English markup for the instant before the catalogue is applied. Accepted: the catalogues are a few kilobytes and served from the same origin.
- The pages are one set of files for all languages, so there is no per-language URL. This is a deliberate trade of SEO reach for simplicity; if indexed per-language pages become a requirement, that is a routing change in `main.py` plus `hreflang` tags, and the catalogues are unaffected.
