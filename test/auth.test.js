// @vitest-environment jsdom
//
// Regression tests for js/auth.js.
// Like app.js it is a classic script: importing it attaches globalThis.KummoAuth.
import { describe, it, expect, beforeEach, vi } from 'vitest';
import '../static/js/auth.js';

const auth = globalThis.KummoAuth;

// Records every fetch call and replies with whatever the test queued.
function stubFetch(responses) {
  const calls = [];
  globalThis.fetch = vi.fn(async (url, options = {}) => {
    calls.push({ url, options });
    const next = responses.shift() ?? { status: 200, body: {} };
    return {
      ok: next.status >= 200 && next.status < 300,
      status: next.status,
      json: async () => {
        if (next.body === undefined) throw new Error('no body');
        return next.body;
      },
    };
  });
  return calls;
}

const user = { id: 'c1', email: 'anna@example.de', role: 'client', display_name: 'Anna Schmidt' };

beforeEach(() => {
  vi.restoreAllMocks();
});

describe('request plumbing', () => {
  it('sends cookies on every call (the session lives in HttpOnly cookies)', async () => {
    const calls = stubFetch([{ status: 200, body: user }]);

    await auth.currentUser();

    expect(calls[0].options.credentials).toBe('same-origin');
  });

  it('posts JSON to the right endpoint', async () => {
    const calls = stubFetch([{ status: 200, body: user }]);

    await auth.login({ email: 'anna@example.de', password: 'geheim123' });

    expect(calls[0].url).toBe('/api/auth/login');
    expect(calls[0].options.method).toBe('POST');
    expect(JSON.parse(calls[0].options.body)).toEqual({
      email: 'anna@example.de',
      password: 'geheim123',
    });
  });

  it('handles a 204 with no body', async () => {
    stubFetch([{ status: 204, body: undefined }]);

    await expect(auth.logout()).resolves.toBeNull();
  });
});

describe('registration payloads', () => {
  it('maps client fields onto the API names', async () => {
    const calls = stubFetch([{ status: 201, body: user }]);

    await auth.registerClient({
      email: 'anna@example.de',
      password: 'geheim123',
      firstName: 'Anna',
      lastName: 'Schmidt',
    });

    expect(calls[0].url).toBe('/api/auth/register/client');
    expect(JSON.parse(calls[0].options.body)).toEqual({
      email: 'anna@example.de',
      password: 'geheim123',
      first_name: 'Anna',
      last_name: 'Schmidt',
    });
  });

  it('maps vendor fields and nulls out empty optionals', async () => {
    const calls = stubFetch([{ status: 201, body: user }]);

    await auth.registerVendor({
      email: 'info@werkstatt.de',
      password: 'geheim123',
      name: 'Kreativwerkstatt',
      address: 'Oranienstraße 1',
      activityType: ['kunst'],
      phone: '',
      website: '',
    });

    expect(calls[0].url).toBe('/api/auth/register/vendor');
    expect(JSON.parse(calls[0].options.body)).toEqual({
      email: 'info@werkstatt.de',
      password: 'geheim123',
      name: 'Kreativwerkstatt',
      address: 'Oranienstraße 1',
      activity_type: ['kunst'],
      phone: null,
      website: null,
    });
  });
});

describe('currentUser', () => {
  it('returns the user when signed in', async () => {
    stubFetch([{ status: 200, body: user }]);

    await expect(auth.currentUser()).resolves.toEqual(user);
  });

  it('returns null when anonymous rather than throwing', async () => {
    stubFetch([{ status: 401, body: { detail: 'Not authenticated' } }]);

    await expect(auth.currentUser()).resolves.toBeNull();
  });

  it('returns null when the account has no profile yet', async () => {
    stubFetch([{ status: 404, body: { detail: 'No profile linked to this account' } }]);

    await expect(auth.currentUser()).resolves.toBeNull();
  });

  it('still throws on a server error', async () => {
    stubFetch([{ status: 502, body: { detail: 'boom' } }]);

    await expect(auth.currentUser()).rejects.toThrow(auth.AuthError);
  });
});

describe('error messages', () => {
  it('are in German for the cases a user can hit', () => {
    expect(auth.errorMessage(409, {})).toMatch(/bereits registriert/);
    expect(auth.errorMessage(401, {})).toMatch(/falsch/);
    expect(auth.errorMessage(422, {})).toMatch(/überprüft/);
    expect(auth.errorMessage(502, {})).toMatch(/nicht erreichbar/);
  });

  it('falls back to the backend detail, then to a generic message', () => {
    expect(auth.errorMessage(400, { detail: 'Passwort zu schwach' })).toBe('Passwort zu schwach');
    expect(auth.errorMessage(400, null)).toMatch(/Fehler/);
  });

  it('surfaces the mapped message on a rejected login', async () => {
    stubFetch([{ status: 401, body: { detail: 'Wrong email or password.' } }]);

    await expect(
      auth.login({ email: 'anna@example.de', password: 'falsch' })
    ).rejects.toThrow(/falsch/);
  });
});

describe('session indicator in the header', () => {
  // The nav every page ships, reduced to the parts the indicator touches.
  function renderNav() {
    document.body.innerHTML = `
      <nav class="nav-main">
        <span class="nav-session" id="session-status" hidden></span>
        <a href="login.html" id="login-link">Anmelden</a>
        <a href="#" id="logout-btn" hidden>Abmelden</a>
      </nav>`;
    return {
      status: document.getElementById('session-status'),
      loginLink: document.getElementById('login-link'),
      logoutBtn: document.getElementById('logout-btn'),
    };
  }

  it('shows the name, the role and the Abmelden link when signed in', () => {
    const { status, loginLink, logoutBtn } = renderNav();

    auth.renderSessionStatus(user);

    expect(status.hidden).toBe(false);
    expect(status.querySelector('.nav-session-name').textContent).toBe('Anna Schmidt');
    expect(status.querySelector('.nav-session-role').textContent).toBe('Kunde');
    expect(loginLink.hidden).toBe(true);
    expect(logoutBtn.hidden).toBe(false);
  });

  it('labels a vendor as Anbieter and exposes the email as the tooltip', () => {
    const { status } = renderNav();

    auth.renderSessionStatus({ ...user, role: 'vendor', display_name: 'Kita Sonnenschein' });

    expect(status.querySelector('.nav-session-role').textContent).toBe('Anbieter');
    expect(status.firstElementChild.title).toBe('anna@example.de');
  });

  it('derives the avatar initials from the display name', () => {
    const { status } = renderNav();

    auth.renderSessionStatus(user);
    expect(status.querySelector('.nav-session-avatar').textContent).toBe('AS');

    auth.renderSessionStatus({ ...user, display_name: 'Kummo' });
    expect(status.querySelector('.nav-session-avatar').textContent).toBe('K');
  });

  it('falls back to the Anmelden link when nobody is signed in', () => {
    const { status, loginLink, logoutBtn } = renderNav();
    auth.renderSessionStatus(user);

    auth.renderSessionStatus(null);

    expect(status.hidden).toBe(true);
    expect(status.children.length).toBe(0);
    expect(loginLink.hidden).toBe(false);
    expect(logoutBtn.hidden).toBe(true);
  });

  it('fills the header from /api/auth/me on load', async () => {
    const { status, loginLink } = renderNav();
    const calls = stubFetch([{ status: 200, body: user }]);

    await auth.initSessionHeader();

    expect(calls[0].url).toBe('/api/auth/me');
    expect(status.querySelector('.nav-session-name').textContent).toBe('Anna Schmidt');
    expect(loginLink.hidden).toBe(true);
  });

  it('renders as signed out when the session cannot be read', async () => {
    const { status, loginLink } = renderNav();
    stubFetch([{ status: 502, body: { detail: 'boom' } }]);

    await auth.initSessionHeader();

    expect(status.hidden).toBe(true);
    expect(loginLink.hidden).toBe(false);
  });
});
