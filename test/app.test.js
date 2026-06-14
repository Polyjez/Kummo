// @vitest-environment jsdom
//
// Regression tests for js/app.js.
// app.js is a "classic" script (loaded via <script> in the browser).
// We import it here for its side effect: it attaches its API to globalThis.KummoApp.
import { describe, it, expect, beforeEach } from 'vitest';
import '../js/app.js';

const app = globalThis.KummoApp;

const clone = (x) => JSON.parse(JSON.stringify(x));

const shops = [
  {
    id: 's1',
    name: 'Lila Farbe',
    address: 'Kreuzberg, Berlin',
    picture: 'shop.jpg',
    activity_type: ['Kunst'],
  },
];

const activities = [
  {
    id: 'a1',
    shop_id: 's1',
    title: 'Van Gogh Malkurs',
    description: 'Malen wie die Großen',
    price: 25,
    participants_max: 8,
    duration: '2 Stunden',
    age_group: '6-12 Jahre',
    picture: 'a1.jpg',
  },
  {
    // shop_id points to a missing shop -> exercises the fallback
    id: 'a2',
    shop_id: 's2',
    title: 'Fußball Camp',
    description: 'Sport für alle',
    price: 50,
    participants_max: 20,
    duration: '3 Stunden',
    age_group: '6-12 Jahre',
  },
];

beforeEach(() => {
  app.__setData(clone(shops), clone(activities));
  localStorage.clear();
});

describe('STORAGE constants', () => {
  it('are defined (regression: ReferenceError on the profile page)', () => {
    expect(app.STORAGE_PREFS).toBeTruthy();
    expect(app.STORAGE_BOOKINGS).toBeTruthy();
    expect(app.STORAGE_FAVORITES).toBeTruthy();
  });
});

describe('enrichActivity', () => {
  it('joins the shop via shop_id', () => {
    const e = app.enrichActivity(activities[0]);
    expect(e.shopName).toBe('Lila Farbe');
    expect(e.address).toBe('Kreuzberg, Berlin');
  });

  it('uses a fallback when the shop is missing', () => {
    const e = app.enrichActivity(activities[1]);
    expect(e.shopName).toBe('Anbieter unbekannt');
    expect(e.address).toBe('Adresse unbekannt');
  });
});

describe('activityCardHtml', () => {
  it('interpolates values and never emits a literal ${ (regression: escaped template literals)', () => {
    const html = app.activityCardHtml(activities[0]);
    expect(html).toContain('Van Gogh Malkurs');
    expect(html).toContain('Kreuzberg, Berlin');
    expect(html).toContain('25 €');
    expect(html).toContain('Lila Farbe');
    expect(html).not.toContain('${');
  });
});

describe('buildSearchUrl', () => {
  it('encodes only meaningful filters and emits no literal ${ (regression)', () => {
    const url = app.buildSearchUrl({ q: 'malen', age: 'all', category: 'kunst', maxPrice: '' });
    expect(url.startsWith('suchen.html?')).toBe(true);
    expect(url).toContain('q=malen');
    expect(url).toContain('category=kunst');
    expect(url).not.toContain('age=all');
    expect(url).not.toContain('${');
  });

  it('returns the bare page when there are no filters', () => {
    expect(app.buildSearchUrl({ age: 'all', category: 'all' })).toBe('suchen.html');
  });
});

describe('filterActivities', () => {
  it('searches free text across title/description/shop', () => {
    expect(app.filterActivities({ q: 'van gogh' }).map((a) => a.id)).toEqual(['a1']);
  });

  it('applies a maximum price', () => {
    expect(app.filterActivities({ maxPrice: '30' }).map((a) => a.id)).toEqual(['a1']);
  });

  it('filters by category (shop offering + text)', () => {
    expect(app.filterActivities({ category: 'kunst' }).map((a) => a.id)).toEqual(['a1']);
  });

  it('returns everything when no filter is set', () => {
    expect(app.filterActivities({}).length).toBe(2);
  });
});

describe('localStorage helpers', () => {
  it('round-trips preferences', () => {
    app.savePrefs({ name: 'Anna', maxBudget: '30' });
    expect(app.getPrefs()).toEqual({ name: 'Anna', maxBudget: '30' });
  });

  it('adds bookings most-recent-first', () => {
    app.addBooking({ activityId: 'a1', total: 50 });
    app.addBooking({ activityId: 'a2', total: 100 });
    const list = app.getBookings();
    expect(list).toHaveLength(2);
    expect(list[0].activityId).toBe('a2');
  });

  it('toggles a favorite on then off', () => {
    app.toggleFavorite('a1');
    expect(app.getFavorites()).toContain('a1');
    app.toggleFavorite('a1');
    expect(app.getFavorites()).not.toContain('a1');
  });
});
