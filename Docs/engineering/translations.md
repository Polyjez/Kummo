# Translating the interface

Kummo's interface is available in **English** and **German**. All of the text a visitor
sees lives in two files — no code, no build step, no restart:

```
static/i18n/en.json    ← English, the source language
static/i18n/de.json    ← German
```

Editing them needs nothing more than a text editor. This page is written for whoever
maintains the wording, technical or not.

## What a file looks like

```json
{
  "common": {
    "nav": {
      "activities": "Activities",
      "login": "Sign in"
    }
  },
  "home": {
    "hero_title": "An unforgettable moment for the whole family"
  }
}
```

Each line has two halves:

| Half | Example | May I change it? |
|---|---|---|
| the **key**, left of the colon | `"login":` | **No.** It is how the page finds the text. |
| the **value**, right of the colon | `"Sign in"` | **Yes.** This is what the visitor reads. |

The same key exists in every language file. `common.nav.login` is `"Sign in"` in
`en.json` and `"Anmelden"` in `de.json`, and that is the whole mechanism.

## The five rules

1. **Only ever change the text inside the quotes on the right.** Leave keys, colons,
   commas and braces exactly where they are.
2. **Keep `{{placeholders}}` exactly as written.** `"Thank you, {{name}}!"` becomes
   *Thank you, Anna!* on the page. Move it around the sentence if the grammar needs it,
   but never rename it or drop it — `{{name}}` is a name, `{{count}}` a number,
   `{{price}}` a price.
3. **Change every language file together.** A new key added to `en.json` must be added
   to `de.json` too, and a key deleted from one must be deleted from the other.
4. **A double quote inside the text has to be escaped** as `\"` — or use typographic
   quotes (`“ ”`, `„ “`), which is what the existing text does and reads better anyway.
5. **Save the file as UTF-8** so that `ä ö ü ß €` survive. Any modern editor does this
   by default.

## Words that come in a singular and a plural

Some sentences count something. They appear as a **pair** of keys ending in `_one` and
`_other`:

```json
"map_hint_one":   "🗺️ {{count}} activity in Berlin",
"map_hint_other": "🗺️ {{count}} activities in Berlin"
```

`_one` is used when the number is exactly 1, `_other` in every other case. Translate
both, and keep both — the page asks for `map_hint` and the right one is picked for it.

## Checking your work

From the project folder:

```sh
pnpm test
```

This verifies the two things that go wrong in practice: that every language file has
**the same keys** as `en.json`, and that no page asks for a key that nobody defines. If
a key is missing, the test names it.

Then look at the site: start Kummo, and **reload the page with `Ctrl+Shift+R`** — a
normal reload can show you the browser's cached copy and make a correct change look like
it did nothing.

Two safety nets, so a mistake is never a broken page:

- a key you have not translated yet falls back to the English text;
- if a language file cannot be read at all, the whole site falls back to English.

## Which language a visitor gets

In this order:

1. the language they picked with the **EN / DE switch** in the page header — remembered
   in their browser afterwards;
2. otherwise their browser's preferred language, if we have it;
3. otherwise English.

## Adding a language

1. Copy `static/i18n/en.json` to `static/i18n/<code>.json` — `fr.json` for French,
   `tr.json` for Turkish, using the two-letter [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) code.
2. Translate the values.
3. Add the code to the `SUPPORTED` list at the top of `static/js/i18n.js`:
   `const SUPPORTED = ['en', 'de', 'fr'];`
4. Add a button for it to the `lang-switch` block in the page headers, next to EN and DE.

Steps 3 and 4 are the only ones that touch code, and they are one line each.

## What is *not* in these files

The activities themselves — their titles, descriptions and addresses — are written by the
vendors in the vendor dashboard and are shown exactly as they were entered. They are
content, not interface, and translating them needs a database change; that is still an
open point (DEC-04), tracked in [implementation status §3.9](implementation-status.md).

Developer-facing text — log messages, `console.log`, code comments — is English and is
never translated.

## For developers

The mechanics behind these files are in
[ADR 0005](../decisions/0005-localization-json-catalogues.md); the conventions for adding
a *new* string (markup attributes, the `t()` helper, codes vs. text in stored data) are in
the project's `CLAUDE.md`.
