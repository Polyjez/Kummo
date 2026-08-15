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

// Redirects to login.html when there is no session; resolves to the user otherwise.
async function requireUser(role) {
  const user = await currentUser();
  if (!user || (role && user.role !== role)) {
    window.location.href = 'login.html';
    return null;
  }
  return user;
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
    requireUser,
  };
}
