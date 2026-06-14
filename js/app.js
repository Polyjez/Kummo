// Kummo — Charge les données depuis Supabase et gère toutes les pages
console.log('app.js est chargé !');
let magasins = [];
let activites = [];

// Clés localStorage (préférences, réservations, favoris)
const STORAGE_PREFS = 'kummo_prefs';
const STORAGE_BOOKINGS = 'kummo_bookings';
const STORAGE_FAVORITES = 'kummo_favorites';

function initApp() {
  console.log('initApp() est appelée');
  if (!window.supabase) {
    console.error("Supabase non initialisé ! Vérifiez que le SDK est chargé dans le HTML.");
    return;
  }
  // Vérifier que window.supabase.from est disponible
  if (typeof window.supabase.from === 'function') {
    console.log('window.supabase.from est disponible, appel de loadData()');
    loadData();
  } else {
    console.error("window.supabase.from n'est pas une fonction !");
  }
}

// =============================================
// 1. Charge les données depuis Supabase
// =============================================
async function loadData() {
  console.log('loadData() START');
  try {
    console.log('Début du chargement des données depuis Supabase...');

    // ✅ Utiliser window.supabase DIRECTEMENT (sans variable locale)
    console.log('Envoi de la requête pour les shops...');
    const { data: shopsData, error: shopsError } = await window.supabase
      .from('shops')
      .select('*');

    console.log('Résultat de la requête shops:', { shopsData, shopsError });

    if (shopsError) throw shopsError;

    // Charge les activités
    console.log('Envoi de la requête pour les activités...');
    const { data: activitiesData, error: activitiesError } = await window.supabase
      .from('activities')
      .select('*');

    console.log('Résultat de la requête activities:', { activitiesData, activitiesError });

    if (activitiesError) throw activitiesError;

    magasins = shopsData;
    activites = activitiesData;
    console.log('Données chargées avec succès:', { magasins, activites });
    initPage();
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error);
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
// 2. Initialise la page en fonction de l'URL
// =============================================
function initPage() {
  const path = window.location.pathname;

  if (path.includes('aktivitaet.html')) {
    afficherDetailActivite();
    return;
  }
  if (path.includes('profil.html')) {
    initProfilePage();
    return;
  }
  if (path.includes('business.html')) {
    // Ne rien faire ici : business.html gère son propre code
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
    afficherListeActivites('featured-activities', activites.slice(0, 6));
    initHomeSearch();
  }
}

// =============================================
// 3. Enrichit une activité avec les données du magasin
// =============================================
function enrichActivite(activite) {
  const magasin = magasins.find((m) => m.id === activite.shop_id);
  return {
    ...activite,
    adresse: magasin ? magasin.adresse : 'Adresse unbekannt',
    nom_magasin: magasin ? magasin.nom : 'Anbieter unbekannt',
    photo: activite.photo || (magasin ? magasin.photo : 'https://via.placeholder.com/400x250'),
    magasin,
  };
}

// =============================================
// 4. Génère le HTML pour une carte d'activité
// =============================================
function activityCardHtml(activite) {
  const a = enrichActivite(activite);
  return `
    <article class="activity-card">
      <img src="${a.photo}" alt="${a.titre}" loading="lazy">
      <div class="activity-card-body">
        <div class="activity-meta">
          <span class="tag">${a.nom_magasin}</span>
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
// 5. Affiche une grille d'activités
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

function afficherListeActivites(containerId, list) {
  renderActivityGrid(containerId, list);
}

// =============================================
// 6. Filtre les activités
// =============================================
function filterActivites(filters) {
  return activites.filter((activite) => {
    const enriched = enrichActivite(activite);
    const q = (filters.q || '').toLowerCase().trim();

    if (q) {
      const haystack = `${activite.titre} ${activite.description} ${enriched.nom_magasin}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }

    if (filters.age && filters.age !== 'all') {
      const age = activite.age_group.toLowerCase();
      if (filters.age === '0-5' && !age.includes('3') && !age.includes('5') && !age.includes('0')) return false;
      if (filters.age === '6-12' && !age.includes('6') && !age.includes('12')) return false;
      if (filters.age === '13-18' && !age.includes('18') && !age.includes('13')) return false;
      if (filters.age === 'senioren' && !age.includes('senior')) return false;
    }

    if (filters.maxPrice && activite.prix > Number(filters.maxPrice)) return false;

    if (filters.category && filters.category !== 'all') {
      const offre = (enriched.magasin?.type_activites || []).join(' ').toLowerCase();
      const text = `${activite.titre} ${activite.description}`.toLowerCase();
      const cat = filters.category;
      if (cat === 'kunst' && !/mal|töpf|illustr|van gogh|impression|druck|kunst|diy/.test(text) && !offre.includes('kunst')) return false;
      if (cat === 'natur' && !/natur|tier|park|steine|dino/.test(text) && !offre.includes('natur')) return false;
      if (cat === 'wissenschaft' && !/wissenschaft|experiment|museum|forscher|steine|dino/.test(text) && !offre.includes('wissenschaft')) return false;
      if (cat === 'geburtstagsfeier' && !offre.includes('geburtstag')) return false;
      if (cat === 'feriencamp' && !offre.includes('camp') && !offre.includes('ferien')) return false;
      if (cat === 'sport' && !/sport|fußball|yoga|bewegung/.test(text)) return false;
    }

    return true;
  });
}

// =============================================
// 7. Gestion des filtres et de la recherche
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
      renderActivityGrid('search-results', filterActivites(f));
      updateMapHint(filterActivites(f).length);
    });
  }

  const results = filterActivites(filters);
  renderActivityGrid('search-results', results);
  updateMapHint(results.length);
}

function updateMapHint(count) {
  const map = document.getElementById('map-hint');
  if (map) map.textContent = `🗺️ ${count} Aktivitäten in Berlin — Google Maps beim Go-Live einbinden`;
}

// =============================================
// 8. Affichage des détails d'une activité
// =============================================
function afficherDetailActivite() {
  const params = new URLSearchParams(window.location.search);
  const activiteId = params.get('id');
  const container = document.getElementById('activity-detail');

  if (!activiteId || !container) {
    if (container) container.innerHTML = '<p class="empty-state">Aktivität nicht gefunden.</p>';
    return;
  }

  const activite = activites.find((a) => a.id === activiteId);
  if (!activite) {
    container.innerHTML = '<p class="empty-state">Aktivität nicht gefunden. <a href="suchen.html">Zurück zur Suche</a></p>';
    return;
  }

  const a = enrichActivite(activite);
  document.title = `${a.titre} — Kummo`;

  container.innerHTML = `
    <div class="detail-hero">
      <img class="gallery-main" src="${a.photo}" alt="${a.titre}">
      <div class="detail-info">
        <div class="activity-meta">
          <span class="tag">${a.nom_magasin}</span>
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

  const similar = activites
    .filter((x) => x.id !== activite.id && x.shop_id === activite.shop_id) // shop_id au lieu de magasin_id
    .slice(0, 3);
  renderActivityGrid('similar-activities', similar.length ? similar : activites.filter((x) => x.id !== activite.id).slice(0, 3));

  document.getElementById('open-booking')?.addEventListener('click', () => openBookingModal(a));
  document.getElementById('toggle-fav')?.addEventListener('click', (e) => {
    toggleFavorite(a.id);
    e.target.textContent = getFavorites().includes(a.id) ? '★ Favorit' : '☆ Merken';
  });
}

// =============================================
// 9. Modale de réservation
// =============================================
function openBookingModal(activite) {
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

  const slots = activite.disponibilites
    .map((s) => `<option value="${s}">${s}</option>`)
    .join('');

  overlay.innerHTML = `
    <div class="modal" role="dialog" aria-labelledby="booking-title">
      <h2 id="booking-title">Buchung: ${activite.titre}</h2>
      <form id="booking-form">
        <div class="form-row"><label for="b-name">Name</label><input id="b-name" name="name" required autocomplete="name"></div>
        <div class="form-row"><label for="b-email">E-Mail</label><input id="b-email" name="email" type="email" required autocomplete="email"></div>
        <div class="form-row"><label for="b-slot">Termin</label><select id="b-slot" name="slot" required>${slots}</select></div>
        <div class="form-row"><label for="b-qty">Personen</label><input id="b-qty" name="qty" type="number" min="1" max="${activite.participants_max}" value="2" required></div>
        <button type="submit" class="btn btn-primary" style="width:100%;margin-top:0.5rem">Buchen (${activite.prix} € / Person)</button>
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
      activityId: activite.id,
      activityName: activite.titre,
      name: fd.get('name'),
      email: fd.get('email'),
      slot: fd.get('slot'),
      qty,
      total: activite.prix * qty,
      status: 'bestätigt',
      date: new Date().toISOString(),
    });
    overlay.classList.remove('open');
    alert(`Danke, ${fd.get('name')}! Ihre Buchung ist bestätigt.`);
  });
}

// =============================================
// 10. Gestion des préférences, réservations et favoris
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
// 11. Initialisation des pages spécifiques
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
  renderActivityGrid('favorites-list', activites.filter((a) => favIds.includes(a.id)));
}

function getRecommendations(prefs) {
  let list = [...activites];
  if (prefs.maxBudget) list = list.filter((a) => a.prix <= Number(prefs.maxBudget));
  if (prefs.age) list = filterActivites({ age: prefs.age });
  return list.slice(0, 6);
}

// =============================================
// 12. Dashboard Admin
// =============================================
function initAdminDashboard() {
  document.getElementById('admin-business-count')?.replaceChildren(
    document.createTextNode(String(magasins.length))
  );
  document.getElementById('admin-activity-count')?.replaceChildren(
    document.createTextNode(String(activites.length))
  );
  document.getElementById('admin-booking-count')?.replaceChildren(
    document.createTextNode(String(getBookings().length))
  );
  document.getElementById('admin-revenue')?.replaceChildren(
    document.createTextNode(`${getBookings().reduce((s, b) => s + b.total, 0)} €`)
  );

  const bizTable = document.getElementById('admin-businesses');
  if (bizTable) {
    bizTable.innerHTML = magasins
      .map((b) => {
        const count = activites.filter((a) => a.shop_id === b.id).length;
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
            const act = activites.find((a) => a.id === b.activityId);
            return `<tr><td>—</td><td>${act ? enrichActivite(act).nom_magasin : '—'}</td><td>${b.activityName}</td><td>${b.name}</td><td>${b.slot}</td><td>${b.status}</td><td>${b.total} €</td></tr>`;
          })
          .join('')
      : '<tr><td colspan="7">Noch keine Buchungen</td></tr>';
  }
}

// =============================================
// 13. Navigation et chatbot
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
// 14. Gestion de la déconnexion
// =============================================
function logout() {
  localStorage.removeItem('user_type');
  localStorage.removeItem('user_id');
  localStorage.removeItem('magasin_connecte');
  window.location.href = 'index.html';
}

async function updateLogoutButton() {
  const logoutBtn = document.getElementById('logout-btn');
  if (!logoutBtn) return;

  // Utilise window.supabase (déjà initialisé dans le HTML) — API v2
  const { data } = (await window.supabase?.auth?.getUser()) || { data: {} };
  const user = data?.user;
  logoutBtn.style.display = user ? 'inline' : 'none';
  if (user) logoutBtn.onclick = logout;
}

// =============================================
// Initialisation finale
// =============================================
document.addEventListener('DOMContentLoaded', () => {  // ✅ Pas de paramètre
  console.log('DOMContentLoaded - initApp() est appelée');
  initNav();
  initChatbot();
  initApp();  // ✅ Appelle initApp() pour vérifier window.supabase avant de charger les données
  updateLogoutButton();
});

// =============================================
// Exposition de l'API pour les tests (et le débogage).
// Sans effet sur l'usage navigateur : attache simplement un objet à window.
// =============================================
if (typeof globalThis !== 'undefined') {
  globalThis.KummoApp = {
    enrichActivite,
    activityCardHtml,
    filterActivites,
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
    // Test-only : remplace les données chargées depuis Supabase.
    __setData: (shops, acts) => {
      magasins = shops;
      activites = acts;
    },
  };
}