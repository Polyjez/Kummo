import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { vi } from 'vitest'

// Node 22 exposes an experimental localStorage global that is `undefined`
// unless --localstorage-file is set, shadowing jsdom's implementation.
// Stub it with a working in-memory store when jsdom hasn't provided one.
if (!globalThis.localStorage) {
  const store = {}
  vi.stubGlobal('localStorage', {
    getItem: (k) => (Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v) },
    removeItem: (k) => { delete store[k] },
    clear: () => { Object.keys(store).forEach((k) => delete store[k]) },
    get length() { return Object.keys(store).length },
    key: (i) => Object.keys(store)[i] ?? null,
  })
}

// Prevent actual network calls — tests use __setData to inject fixtures.
vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('fetch is not available in tests'))))

// The UI text. app.js and auth.js resolve every string through the catalogue, so
// it has to be there before they run. `fetch` is stubbed out above, so the
// English catalogue is read from disk and injected instead of loaded over HTTP —
// the tests then assert the real strings a visitor sees, not placeholders.
await import('../static/js/i18n.js')
globalThis.KummoI18n.__setCatalog(
  'en',
  JSON.parse(readFileSync(resolve(process.cwd(), 'static/i18n/en.json'), 'utf8'))
)
