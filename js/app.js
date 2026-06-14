// Kummo — loads data from Supabase and drives every page.
// Note: DB-mapped field names (titre, prix, nom, adresse, age_group,
// participants_max, duree, disponibilites, shop_id, ...) mirror the Supabase
// columns and are kept as-is. UI strings stay in German.
console.log('app.js loaded');
let shops = [];
let activities = [];

// localStorage keys (preferences, bookings, favorites)
const STORAGE_PREFS = 'kummo_prefs';
const STORAGE_BOOKINGS = 'kummo_bookings';
const STORAGE_FAVORITES = 'kummo_favorites';

function initApp() {
  console.log('initApp() called');
  if (!window.supabase) {
    console.error('Supabase not initialized! Check that the SDK is loaded in the HTML.');
    return;
  }
  // Make sure window.supabase.from is available
  if (typeof window.supabase.from === 'function') {
    console.log('window.supabase.from is available, calling loadData()');
    loadData();
  } else {
    console.error('window.supabase.from is not a function!');
  }
}

// =============================================
// 1. Load data from Supabase
// =============================================
async function loadData() {
  console.log('loadData() START');
  try {
    console.log('Loading data from Supabase...');

    // Use window.supabase directly (no local variable)
    console.log('Requesting shops...');
    const { data: shopsData, error: shopsError } = await window.supabase
      .from('shops')
      .select('*');

    console.log('Shops query result:', { shopsData, shopsError });

    if (shopsError) throw shopsError;

    // Load activities
    console.log('Requesting activities...');
    const { data: activitiesData, error: activitiesError } = await window.supabase
      .from('activities')
      .select('*');

    console.log('Activities query result:', { activitiesData, activitiesError });

    if (activitiesError) throw activitiesError;

    shops = shopsData;
    activities = activitiesData;
    console.log('Data loaded successfully:', { shops, activities });
    initPage();
  } catch (error) {
    console.error('Error while loading data:', error);
    showLoadError();
  }
}

function showLoadError() {
  const hint =
    window.location.protocol === 'file:'
      ? ' Bitte starten Sie einen lokalen Server (z. B. Live Server) und öffnen http://localhost:5500'
      : '';
  const msg = `<p class="empty-state" style="color:#DC562E">Aktivitäten konnten nicht geladen werden.${hint}</p>`;
  const el =
    document.getElementById('featured-activities') ||
    document.getElementById('search-results') ||
    document.getElementById('activity-detail');
  if (el) el.innerHTML = msg;
}

// =============================================
// 2. Initialize the page based on the URL
// =============================================
function initPage() {
  const path = window.location.pathname;

  if (path.includes('aktivitaet.html')) {
    showActivityDetail();
    return;
  }
  if (path.includes('profil.html')) {
    initProfilePage();
    return;
  }
  if (path.includes('business.html')) {
    // Do nothing here: business.html runs its own code
    return;
  }
  if (path.includes('admin.html')) {
    initAdminDashboard();
    return;
  }
  if (path.includes('suchen.html')) {
    initSearchPage();
    return;
  }
  if (path.includes('index.html') || path.endsWith('/')) {
    showActivityList('featured-activities', activities.slice(0, 6));
    initHomeSearch();
  }
}

// =============================================
// 3. Enrich an activity with its shop data
// =============================================
function enrichActivity(activity) {
  const shop = shops.find((s) => s.id === activity.shop_id);
  return {
    ...activity,
    adresse: shop ? shop.adresse : 'Adresse unbekannt',
    shopName: shop ? shop.nom : 'Anbieter unbekannt',
    photo: activity.photo || (shop ? shop.photo : 'https://via.placeholder.com/400x250'),
    shop,
  };
}

// =============================================
// 4. Build the HTML for an activity card
// =============================================
function activityCardHtml(activity) {
  const a = enrichActivity(activity);
  return `
    <article class="activity-card">
      <img src="${a.photo}" alt="${a.titre}" loading="lazy">
      <div class="activity-card-body">
        <div class="activity-meta">
          <span class="tag">${a.shopName}</span>
          <span class="tag tag-age">${a.age_group}</span>
        </div>
        <h3>${a.titre}</h3>
        <p>📍 ${a.adresse}</p>
        <p>💰 ${a.prix} € · 👥 ${a.participants_max} · ⏳ ${a.duree}</p>
        <a class="btn btn-primary btn-sm stretched-link" href="aktivitaet.html?id=${a.id}">Details & Buchen</a>
      </div>
    </article>`;
}

// =============================================
// 5. Render a grid of activities
// =============================================
function renderActivityGrid(containerId, list) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!list.length) {
    container.innerHTML = '<p class="empty-state">Keine Aktivitäten gefunden.</p>';
    return;
  }
  container.innerHTML = list.map(activityCardHtml).join('');
}

function showActivityList(containerId, list) {
  renderActivityGrid(containerId, list);
}

// =============================================
// 6. Filter activities
// =============================================
function filterActivities(filters) {
  return activities.filter((activity) => {
    const enriched = enrichActivity(activity);
    const q = (filters.q || '').toLowerCase().trim();

    if (q) {
      const haystack = `${activity.titre} ${activity.description} ${enriched.shopName}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }

    if (filters.age && filters.age !== 'all') {
      const age = activity.age_group.toLowerCase();
      if (filters.age === '0-5' && !age.includes('3') && !age.includes('5') && !age.includes('0')) return false;
      if (filters.age === '6-12' && !age.includes('6') && !age.includes('12')) return false;
      if (filters.age === '13-18' && !age.includes('18') && !age.includes('13')) return false;
      if (filters.age === 'senioren' && !age.includes('senior')) return false;
    }

    if (filters.maxPrice && activity.prix > Number(filters.maxPrice)) return false;

    if (filters.category && filters.category !== 'all') {
      const offering = (enriched.shop?.type_activites || []).join(' ').toLowerCase();
      const text = `${activity.titre} ${activity.description}`.toLowerCase();
      const cat = filters.category;
      if (cat === 'kunst' && !/mal|töpf|illustr|van gogh|impression|druck|kunst|diy/.test(text) && !offering.includes('kunst')) return false;
      if (cat === 'natur' && !/natur|tier|park|steine|dino/.test(text) && !offering.includes('natur')) return false;
      if (cat === 'wissenschaft' && !/wissenschaft|experiment|museum|forscher|steine|dino/.test(text) && !offering.includes('wissenschaft')) return false;
      if (cat === 'geburtstagsfeier' && !offering.includes('geburtstag')) return false;
      if (cat === 'feriencamp' && !offering.includes('camp') && !offering.includes('ferien')) return false;
      if (cat === 'sport' && !/sport|fußball|yoga|bewegung/.test(text)) return false;
    }

    return true;
  });
}

// =============================================
// 7. Search and filter handling
// =============================================
function readFiltersFromForm(form) {
  const fd = new FormData(form);
  return {
    q: fd.get('q') || '',
    age: fd.get('age') || 'all',
    category: fd.get('category') || 'all',
    maxPrice: fd.get('maxPrice') || '',
  };
}

function buildSearchUrl(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v && v !== 'all') params.set(k, v);
  });
  const qs = params.toString();
  return `suchen.html${qs ? `?${qs}` : ''}`;
}

function initHomeSearch() {
  const form = document.getElementById('home-search');
  if (!form) return;
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    window.location.href = buildSearchUrl(readFiltersFromForm(form));
  });
}

function initSearchPage() {
  const params = new URLSearchParams(window.location.search);
  const filters = {
    q: params.get('q') || '',
    category: params.get('category') || 'all',
    age: params.get('age') || 'all',
    maxPrice: params.get('maxPrice') || '',
  };

  const form = document.getElementById('filter-form');
  if (form) {
    if (filters.q) form.querySelector('[name="q"]').value = filters.q;
    if (filters.category) form.querySelector('[name="category"]').value = filters.category;
    if (filters.age) form.querySelector('[name="age"]').value = filters.age;
    if (filters.maxPrice) form.querySelector('[name="maxPrice"]').value = filters.maxPrice;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const f = readFiltersFromForm(form);
      renderActivityGrid('search-results', filterActivities(f));
      updateMapHint(filterActivities(f).length);
    });
  }

  const results = filterActivities(filters);
  renderActivityGrid('search-results', results);
  updateMapHint(results.length);
}

function updateMapHint(count) {
  const map = document.getElementById('map-hint');
  if (map) map.textContent = `🗺️ ${count} Aktivitäten in Berlin — Google Maps beim Go-Live einbinden`;
}

// =============================================
// 8. Activity detail view
// =============================================
function showActivityDetail() {
  const params = new URLSearchParams(window.location.search);
  const activityId = params.get('id');
  const container = document.getElementById('activity-detail');

  if (!activityId || !container) {
    if (container) container.innerHTML = '<p class="empty-state">Aktivität nicht gefunden.</p>';
    return;
  }

  const activity = activities.find((a) => a.id === activityId);
  if (!activity) {
    container.innerHTML = '<p class="empty-state">Aktivität nicht gefunden. <a href="suchen.html">Zurück zur Suche</a></p>';
    return;
  }

  const a = enrichActivity(activity);
  document.title = `${a.titre} — Kummo`;

  container.innerHTML = `
    <div class="detail-hero">
      <img class="gallery-main" src="${a.photo}" alt="${a.titre}">
      <div class="detail-info">
        <div class="activity-meta">
          <span class="tag">${a.shopName}</span>
          <span class="tag tag-age">${a.age_group}</span>
        </div>
        <h1>${a.titre}</h1>
        <p class="rating">⭐ ${a.rating || 'Noch nicht bewertet'}</p>
        <p class="price-large">${a.prix} € <span style="font-size:1rem;font-weight:600">pro Person</span></p>
        <p>📍 ${a.adresse}</p>
        <p>👥 Max. ${a.participants_max} Teilnehmer · ⏳ ${a.duree}</p>
        <p>${a.description}</p>
        <div style="margin-top:1.5rem">
          <h3>Verfügbare Termine</h3>
          <div class="disponibilites">
            ${a.disponibilites.map((d) => `<span class="tag">${d}</span>`).join('')}
          </div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin-top:1.5rem">
          <button type="button" class="btn btn-primary" id="open-booking">Jetzt buchen</button>
          <button type="button" class="btn btn-outline" id="toggle-fav">${getFavorites().includes(a.id) ? '★ Favorit' : '☆ Merken'}</button>
        </div>
      </div>
    </div>
    <div class="map-panel">
      <div class="map-placeholder">Karte: ${a.adresse}</div>
    </div>
    <section class="section">
      <h2>Das könnte euch auch gefallen</h2>
      <div class="activity-grid" id="similar-activities"></div>
    </section>`;

  const similar = activities
    .filter((x) => x.id !== activity.id && x.shop_id === activity.shop_id)
    .slice(0, 3);
  renderActivityGrid('similar-activities', similar.length ? similar : activities.filter((x) => x.id !== activity.id).slice(0, 3));

  document.getElementById('open-booking')?.addEventListener('click', () => openBookingModal(a));
  document.getElementById('toggle-fav')?.addEventListener('click', (e) => {
    toggleFavorite(a.id);
    e.target.textContent = getFavorites().includes(a.id) ? '★ Favorit' : '☆ Merken';
  });
}

// =============================================
// 9. Booking modal
// =============================================
function openBookingModal(activity) {
  let overlay = document.getElementById('booking-modal');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'booking-modal';
    overlay.className = 'modal-overlay';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('open');
    });
  }

  const slots = activity.disponibilites
    .map((s) => `<option value="${s}">${s}</option>`)
    .join('');

  overlay.innerHTML = `
    <div class="modal" role="dialog" aria-labelledby="booking-title">
      <h2 id="booking-title">Buchung: ${activity.titre}</h2>
      <form id="booking-form">
        <div class="form-row"><label for="b-name">Name</label><input id="b-name" name="name" required autocomplete="name"></div>
        <div class="form-row"><label for="b-email">E-Mail</label><input id="b-email" name="email" type="email" required autocomplete="email"></div>
        <div class="form-row"><label for="b-slot">Termin</label><select id="b-slot" name="slot" required>${slots}</select></div>
        <div class="form-row"><label for="b-qty">Personen</label><input id="b-qty" name="qty" type="number" min="1" max="${activity.participants_max}" value="2" required></div>
        <button type="submit" class="btn btn-primary" style="width:100%;margin-top:0.5rem">Buchen (${activity.prix} € / Person)</button>
        <button type="button" class="btn btn-outline" style="width:100%;margin-top:0.5rem" data-close>Abbrechen</button>
      </form>
    </div>`;

  overlay.classList.add('open');
  overlay.querySelector('[data-close]').addEventListener('click', () => overlay.classList.remove('open'));
  overlay.querySelector('#booking-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const qty = Number(fd.get('qty'));
    addBooking({
      activityId: activity.id,
      activityName: activity.titre,
      name: fd.get('name'),
      email: fd.get('email'),
      slot: fd.get('slot'),
      qty,
      total: activity.prix * qty,
      status: 'bestätigt',
      date: new Date().toISOString(),
    });
    overlay.classList.remove('open');
    alert(`Danke, ${fd.get('name')}! Ihre Buchung ist bestätigt.`);
  });
}

// =============================================
// 10. Preferences, bookings and favorites
// =============================================
function getPrefs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_PREFS) || '{}');
  } catch {
    return {};
  }
}

function savePrefs(prefs) {
  localStorage.setItem(STORAGE_PREFS, JSON.stringify(prefs));
}

function getBookings() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_BOOKINGS) || '[]');
  } catch {
    return [];
  }
}

function addBooking(booking) {
  const list = getBookings();
  list.unshift(booking);
  localStorage.setItem(STORAGE_BOOKINGS, JSON.stringify(list));
}

function getFavorites() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_FAVORITES) || '[]');
  } catch {
    return [];
  }
}

function toggleFavorite(id) {
  let favs = getFavorites();
  favs = favs.includes(id) ? favs.filter((x) => x !== id) : [...favs, id];
  localStorage.setItem(STORAGE_FAVORITES, JSON.stringify(favs));
  return favs;
}

// =============================================
// 11. Page-specific initializers
// =============================================
function initProfilePage() {
  const form = document.getElementById('prefs-form');
  const prefs = getPrefs();
  if (form) {
    if (prefs.name) form.name.value = prefs.name;
    if (prefs.email) form.email.value = prefs.email;
    if (prefs.age) form.age.value = prefs.age;
    if (prefs.maxBudget) form.maxBudget.value = prefs.maxBudget;
    if (prefs.location) form.location.value = prefs.location;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      savePrefs(Object.fromEntries(fd.entries()));
      alert('Einstellungen gespeichert.');
      renderActivityGrid('recommendations', getRecommendations(getPrefs()));
    });
  }

  renderActivityGrid('recommendations', getRecommendations(getPrefs()));

  const bookingsEl = document.getElementById('booking-history');
  const bookings = getBookings();
  if (bookingsEl) {
    bookingsEl.innerHTML = bookings.length
      ? `<div class="table-wrap"><table><thead><tr><th>Aktivität</th><th>Termin</th><th>Preis</th><th>Status</th></tr></thead><tbody>
        ${bookings.map((b) => `<tr><td>${b.activityName}</td><td>${b.slot}</td><td>${b.total} €</td><td>${b.status}</td></tr>`).join('')}
      </tbody></table></div>`
      : '<p>Noch keine Buchungen.</p>';
  }

  const favIds = getFavorites();
  renderActivityGrid('favorites-list', activities.filter((a) => favIds.includes(a.id)));
}

function getRecommendations(prefs) {
  let list = [...activities];
  if (prefs.maxBudget) list = list.filter((a) => a.prix <= Number(prefs.maxBudget));
  if (prefs.age) list = filterActivities({ age: prefs.age });
  return list.slice(0, 6);
}

// =============================================
// 12. Admin dashboard
// =============================================
function initAdminDashboard() {
  document.getElementById('admin-business-count')?.replaceChildren(
    document.createTextNode(String(shops.length))
  );
  document.getElementById('admin-activity-count')?.replaceChildren(
    document.createTextNode(String(activities.length))
  );
  document.getElementById('admin-booking-count')?.replaceChildren(
    document.createTextNode(String(getBookings().length))
  );
  document.getElementById('admin-revenue')?.replaceChildren(
    document.createTextNode(`${getBookings().reduce((s, b) => s + b.total, 0)} €`)
  );

  const bizTable = document.getElementById('admin-businesses');
  if (bizTable) {
    bizTable.innerHTML = shops
      .map((b) => {
        const count = activities.filter((a) => a.shop_id === b.id).length;
        return `<tr><td>${b.nom}</td><td>${b.email}</td><td>${count}</td><td>—</td></tr>`;
      })
      .join('');
  }

  const resTable = document.getElementById('admin-reservations');
  if (resTable) {
    const bookings = getBookings();
    resTable.innerHTML = bookings.length
      ? bookings
          .map((b) => {
            const act = activities.find((a) => a.id === b.activityId);
            return `<tr><td>—</td><td>${act ? enrichActivity(act).shopName : '—'}</td><td>${b.activityName}</td><td>${b.name}</td><td>${b.slot}</td><td>${b.status}</td><td>${b.total} €</td></tr>`;
          })
          .join('')
      : '<tr><td colspan="7">Noch keine Buchungen</td></tr>';
  }
}

// =============================================
// 13. Navigation and chatbot
// =============================================
function initNav() {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav-main');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
    });
  }
}

function initChatbot() {
  const fab = document.getElementById('chat-fab');
  const panel = document.getElementById('chat-panel');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');
  if (!fab || !panel) return;

  fab.addEventListener('click', () => panel.classList.toggle('open'));

  document.getElementById('chat-send')?.addEventListener('click', () => {
    if (!input?.value.trim()) return;
    messages.innerHTML += `<div><strong>Sie:</strong> ${input.value}</div>`;
    const t = input.value.toLowerCase();
    let reply = 'Fragen Sie z. B. „Wie buche ich?" oder „Aktivitäten für Kleinkinder?"';
    if (t.includes('buch')) reply = 'Aktivität wählen → „Jetzt buchen" → Termin und Personenzahl eingeben.';
    if (t.includes('klein') || t.includes('3') || t.includes('5')) reply = 'Für Kleinkinder: Filter „0–5 Jahre" oder Aktivitäten wie Kamishibai (ab 3 Jahre).';
    messages.innerHTML += `<div class="bot"><strong>Kummo:</strong> ${reply}</div>`;
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
  });
}

// =============================================
// 14. Logout handling
// =============================================
function logout() {
  localStorage.removeItem('user_type');
  localStorage.removeItem('user_id');
  localStorage.removeItem('shop_session');
  window.location.href = 'index.html';
}

async function updateLogoutButton() {
  const logoutBtn = document.getElementById('logout-btn');
  if (!logoutBtn) return;

  // Uses window.supabase (already initialized in the HTML) — v2 API
  const { data } = (await window.supabase?.auth?.getUser()) || { data: {} };
  const user = data?.user;
  logoutBtn.style.display = user ? 'inline' : 'none';
  if (user) logoutBtn.onclick = logout;
}

// =============================================
// Final initialization
// =============================================
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOMContentLoaded - calling initApp()');
  initNav();
  initChatbot();
  initApp(); // Calls initApp() to verify window.supabase before loading data
  updateLogoutButton();
});

// =============================================
// Test/debug API exposure.
// No effect on browser usage: just attaches an object to globalThis.
// =============================================
if (typeof globalThis !== 'undefined') {
  globalThis.KummoApp = {
    enrichActivity,
    activityCardHtml,
    filterActivities,
    buildSearchUrl,
    getRecommendations,
    getPrefs,
    savePrefs,
    getBookings,
    addBooking,
    getFavorites,
    toggleFavorite,
    STORAGE_PREFS,
    STORAGE_BOOKINGS,
    STORAGE_FAVORITES,
    // Test-only: replaces the data loaded from Supabase.
    __setData: (shopList, activityList) => {
      shops = shopList;
      activities = activityList;
    },
  };
}
