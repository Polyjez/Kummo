// @vitest-environment jsdom
//
// Tests de non-régression pour js/app.js.
// app.js est un script « classique » (chargé via <script> dans le navigateur).
// On l'importe ici pour ses effets de bord : il attache son API à globalThis.KummoApp.
import { describe, it, expect, beforeEach } from 'vitest';
import '../js/app.js';

const app = globalThis.KummoApp;

const clone = (x) => JSON.parse(JSON.stringify(x));

const shops = [
  {
    id: 's1',
    nom: 'Lila Farbe',
    adresse: 'Kreuzberg, Berlin',
    photo: 'shop.jpg',
    type_activites: ['Kunst'],
  },
];

const activities = [
  {
    id: 'a1',
    shop_id: 's1',
    titre: 'Van Gogh Malkurs',
    description: 'Malen wie die Großen',
    prix: 25,
    participants_max: 8,
    duree: '2 Stunden',
    age_group: '6-12 Jahre',
    photo: 'a1.jpg',
    disponibilites: ['15.06.2026 14:00'],
  },
  {
    // shop_id pointe vers un magasin absent -> teste le repli
    id: 'a2',
    shop_id: 's2',
    titre: 'Fußball Camp',
    description: 'Sport für alle',
    prix: 50,
    participants_max: 20,
    duree: '3 Stunden',
    age_group: '6-12 Jahre',
    disponibilites: [],
  },
];

beforeEach(() => {
  app.__setData(clone(shops), clone(activities));
  localStorage.clear();
});

describe('constantes STORAGE', () => {
  it('sont définies (régression : ReferenceError sur la page profil)', () => {
    expect(app.STORAGE_PREFS).toBeTruthy();
    expect(app.STORAGE_BOOKINGS).toBeTruthy();
    expect(app.STORAGE_FAVORITES).toBeTruthy();
  });
});

describe('enrichActivite', () => {
  it('rattache le magasin via shop_id', () => {
    const e = app.enrichActivite(activities[0]);
    expect(e.nom_magasin).toBe('Lila Farbe');
    expect(e.adresse).toBe('Kreuzberg, Berlin');
  });

  it('utilise un repli quand le magasin est absent', () => {
    const e = app.enrichActivite(activities[1]);
    expect(e.nom_magasin).toBe('Anbieter unbekannt');
    expect(e.adresse).toBe('Adresse unbekannt');
  });
});

describe('activityCardHtml', () => {
  it('interpole les valeurs et n\'émet jamais un ${ littéral (régression : template literals échappés)', () => {
    const html = app.activityCardHtml(activities[0]);
    expect(html).toContain('Van Gogh Malkurs');
    expect(html).toContain('Kreuzberg, Berlin');
    expect(html).toContain('25 €');
    expect(html).toContain('Lila Farbe');
    expect(html).not.toContain('${');
  });
});

describe('buildSearchUrl', () => {
  it('encode uniquement les filtres utiles et n\'émet pas de ${ littéral (régression)', () => {
    const url = app.buildSearchUrl({ q: 'malen', age: 'all', category: 'kunst', maxPrice: '' });
    expect(url.startsWith('suchen.html?')).toBe(true);
    expect(url).toContain('q=malen');
    expect(url).toContain('category=kunst');
    expect(url).not.toContain('age=all');
    expect(url).not.toContain('${');
  });

  it('renvoie la page nue sans filtres', () => {
    expect(app.buildSearchUrl({ age: 'all', category: 'all' })).toBe('suchen.html');
  });
});

describe('filterActivites', () => {
  it('recherche le texte libre dans titre/description/magasin', () => {
    expect(app.filterActivites({ q: 'van gogh' }).map((a) => a.id)).toEqual(['a1']);
  });

  it('applique un prix maximum', () => {
    expect(app.filterActivites({ maxPrice: '30' }).map((a) => a.id)).toEqual(['a1']);
  });

  it('filtre par catégorie (offre du magasin + texte)', () => {
    expect(app.filterActivites({ category: 'kunst' }).map((a) => a.id)).toEqual(['a1']);
  });

  it('renvoie tout sans filtre', () => {
    expect(app.filterActivites({}).length).toBe(2);
  });
});

describe('helpers localStorage', () => {
  it('sauvegarde et relit les préférences', () => {
    app.savePrefs({ name: 'Anna', maxBudget: '30' });
    expect(app.getPrefs()).toEqual({ name: 'Anna', maxBudget: '30' });
  });

  it('ajoute les réservations, la plus récente en premier', () => {
    app.addBooking({ activityId: 'a1', total: 50 });
    app.addBooking({ activityId: 'a2', total: 100 });
    const list = app.getBookings();
    expect(list).toHaveLength(2);
    expect(list[0].activityId).toBe('a2');
  });

  it('active puis désactive un favori', () => {
    app.toggleFavorite('a1');
    expect(app.getFavorites()).toContain('a1');
    app.toggleFavorite('a1');
    expect(app.getFavorites()).not.toContain('a1');
  });
});
