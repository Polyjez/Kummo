// =============================================
// Kummo authentication client.
//
// Talks only to /api/auth/*. The session lives in HttpOnly cookies set by the
// backend, so there is no token to read, store or attach here — every call just
// needs credentials: 'same-origin' so the browser sends the cookies along.
// =============================================

const AUTH_BASE = '/api/auth';

// Thrown for any non-2xx response, carrying the backend's message so callers can
// show it to the user. German text belongs in the UI, not here.
class AuthError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'AuthError';
    this.status = status;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${AUTH_BASE}${path}`, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (res.status === 204) return null;

  let body = null;
  try {
    body = await res.json();
  } catch (err) {
    body = null;
  }

  if (!res.ok) {
    throw new AuthError(errorMessage(res.status, body), res.status);
  }
  return body;
}

// Maps a failed response onto something a user can act on.
function errorMessage(status, body) {
  if (status === 409) return 'Diese E-Mail-Adresse ist bereits registriert.';
  if (status === 401) return 'E-Mail oder Passwort ist falsch.';
  if (status === 422) return 'Bitte überprüft die eingegebenen Daten.';
  if (status === 502) return 'Der Anmeldedienst ist gerade nicht erreichbar.';
  if (body && typeof body.detail === 'string') return body.detail;
  return 'Es ist ein Fehler aufgetreten. Bitte versucht es erneut.';
}

function post(path, payload) {
  return request(path, { method: 'POST', body: JSON.stringify(payload) });
}

function registerClient({ email, password, firstName, lastName }) {
  return post('/register/client', {
    email,
    password,
    first_name: firstName,
    last_name: lastName,
  });
}

function registerVendor({ email, password, name, address, activityType, phone, website }) {
  return post('/register/vendor', {
    email,
    password,
    name,
    address,
    activity_type: activityType,
    phone: phone || null,
    website: website || null,
  });
}

function login({ email, password }) {
  return post('/login', { email, password });
}

function logout() {
  return request('/logout', { method: 'POST' });
}

// Resolves to the CurrentUser, or null when nobody is signed in. A 401 here is the
// normal anonymous case, not a failure worth throwing over.
async function currentUser() {
  try {
    return await request('/me');
  } catch (err) {
    if (err instanceof AuthError && (err.status === 401 || err.status === 404)) return null;
    throw err;
  }
}

// =============================================
// The page-wide session.
//
// A page asks for the session from several places (the header, the page guard,
// the profile form), so the request is made once and shared. Resolving it is also
// the moment the locally cached data is checked against the account it belongs to.
// =============================================
let sessionPromise = null;

function session() {
  if (!sessionPromise) {
    sessionPromise = currentUser().then((user) => {
      syncLocalAccount(user);
      return user;
    });
  }
  return sessionPromise;
}

// Only used by the tests and by logout: the session cannot change within a page
// otherwise, since every auth transition navigates away.
function resetSession() {
  sessionPromise = null;
}

// =============================================
// Account-scoped local data.
//
// Preferences, bookings and favorites live in localStorage under `kummo_*` keys.
// They belong to one account, but localStorage belongs to the browser, so signing
// in as somebody else would otherwise show the previous user's data. The account
// the cached data was written for is recorded here, and anything left over from a
// different one is dropped.
// =============================================
const ACCOUNT_KEY = 'kummo_account';

function clearLocalData() {
  for (const key of Object.keys(localStorage)) {
    if (key.startsWith('kummo_')) localStorage.removeItem(key);
  }
}

function syncLocalAccount(user) {
  const owner = localStorage.getItem(ACCOUNT_KEY);
  const current = user ? user.id : null;
  if (owner === current) return;

  clearLocalData();
  if (current) localStorage.setItem(ACCOUNT_KEY, current);
}

// =============================================
// Page access.
// =============================================

// The page that belongs to a role: where the session badge leads, and where a
// signed-in user is sent when the page they asked for is not for them. A vendor has
// no client page and a client has no dashboard. `admin` is listed for the day the
// backend grows the role — today `/api/auth/me` only ever returns client or vendor.
const ROLE_HOME = { client: 'client.html', vendor: 'vendor.html', admin: 'admin.html' };

function homeFor(user) {
  return ROLE_HOME[user.role] ?? 'index.html';
}

// Guards a page: anonymous visitors go to login.html, and a signed-in user whose
// role does not match is sent to their own home rather than asked to sign in
// again. Resolves to the user when the page may render, null when it is leaving.
async function requireUser(role) {
  const user = await session();
  if (!user) {
    window.location.href = 'login.html';
    return null;
  }
  if (role && user.role !== role) {
    window.location.href = homeFor(user);
    return null;
  }
  return user;
}

// =============================================
// Session indicator in the header.
//
// Every page ships the same nav, so the "who is signed in" rendering lives here
// rather than in app.js: vendor.html and login.html run their own inline
// scripts and would otherwise each need a copy.
// =============================================

// German, because this is user-facing.
const ROLE_LABELS = { client: 'Kunde', vendor: 'Anbieter' };

function initials(displayName) {
  const words = displayName.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return '?';
  const letters = words.length === 1 ? words[0].slice(0, 1) : words[0][0] + words[words.length - 1][0];
  return letters.toUpperCase();
}

// The badge is the way to the user's own page: the nav no longer carries a link
// per role, so whoever is signed in clicks their name to get there.
function sessionBadge(user) {
  const badge = document.createElement('a');
  badge.className = 'nav-session';
  badge.href = homeFor(user);
  badge.setAttribute('aria-label', `Angemeldet als ${user.display_name} (${ROLE_LABELS[user.role] ?? user.role})`);
  badge.title = user.email;

  const avatar = document.createElement('span');
  avatar.className = 'nav-session-avatar';
  avatar.setAttribute('aria-hidden', 'true');
  avatar.textContent = initials(user.display_name);

  const name = document.createElement('span');
  name.className = 'nav-session-name';
  name.textContent = user.display_name;

  const role = document.createElement('span');
  role.className = 'nav-session-role';
  role.textContent = ROLE_LABELS[user.role] ?? user.role;

  badge.append(avatar, name, role);
  return badge;
}

// Reflects the session into the header: the badge, the "Anmelden" link and the
// "Abmelden" button. `user` is the CurrentUser, or null when nobody is signed in.
function renderSessionStatus(user) {
  const slot = document.getElementById('session-status');
  const loginLink = document.getElementById('login-link');
  const logoutBtn = document.getElementById('logout-btn');

  if (slot) {
    slot.replaceChildren(...(user ? [sessionBadge(user)] : []));
    slot.hidden = !user;
  }
  if (loginLink) loginLink.hidden = Boolean(user);
  if (logoutBtn) logoutBtn.hidden = !user;
}

// Signs out and returns to the homepage — the only page that is meaningful
// without a session.
async function logoutAndLeave() {
  try {
    await logout();
  } catch (err) {
    console.log('Logout failed, leaving the page anyway:', err);
  }
  resetSession();
  clearLocalData();
  window.location.href = 'index.html';
}

// Fills the header on load. A failure here must not take the page down, so an
// unreachable backend simply renders as "signed out".
async function initSessionHeader() {
  const hasHeader = ['session-status', 'login-link', 'logout-btn'].some((id) => document.getElementById(id));
  if (!hasHeader) return;

  document.getElementById('logout-btn')?.addEventListener('click', (e) => {
    e.preventDefault();
    logoutAndLeave();
  });

  let user = null;
  try {
    user = await session();
  } catch (err) {
    console.log('Could not read the session:', err);
  }
  renderSessionStatus(user);
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSessionHeader);
  } else {
    initSessionHeader();
  }
}

if (typeof globalThis !== 'undefined') {
  globalThis.KummoAuth = {
    AuthError,
    errorMessage,
    registerClient,
    registerVendor,
    login,
    logout,
    currentUser,
    session,
    resetSession,
    homeFor,
    requireUser,
    renderSessionStatus,
    initSessionHeader,
  };
}
