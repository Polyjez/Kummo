-- One-off data copy for the hosted project only.
--
-- Local development does not need this: `pnpm exec supabase db reset` rebuilds the
-- database and reseeds from seed.sql. On the hosted project the public.* rows are real,
-- so copy them across BEFORE the 20260815120000_drop-legacy-public-tables.sql migration
-- runs.
--
-- Prerequisite: the kummo tables exist (20260816200000_kummo-application-tables.sql,
-- or the Alembic revision it replaced). Run as `postgres` from the SQL editor.
--
-- Column mapping:
--   public.shops -> kummo.vendors   (a vendor is the business *and* the shop)
--   public.users -> kummo.clients
--   *.shop_id    -> vendor_id
--   *.user_id    -> client_id
-- auth_user_id stays null: these rows predate authentication and get linked on first
-- login by the ensure_*_profile path.

BEGIN;

INSERT INTO kummo.vendors (id, created_at, name, address, phone, email, website, activity_type, picture)
SELECT id, created_at, name, address, phone, email, website, activity_type, picture
FROM public.shops;

INSERT INTO kummo.clients (id, created_at, first_name, last_name, email, age, interests, number_children)
SELECT id, created_at, first_name, last_name, email, age, interests, number_children
FROM public.users;

INSERT INTO kummo.children (id, created_at, client_id, first_name, last_name, age, interests, gender)
SELECT id, created_at, user_id, first_name, last_name, age, interests, gender
FROM public.children;

INSERT INTO kummo.activities (id, created_at, vendor_id, title, description, price, participants_max, duration, age_group, picture)
SELECT id, created_at, shop_id, title, description, price, participants_max, duration, age_group, picture
FROM public.activities;

INSERT INTO kummo.bookings (id, created_at, client_id, vendor_id, slot, quantity, total_price, status)
SELECT id, created_at, user_id, shop_id, slot, quantity, total_price, status
FROM public.bookings;

COMMIT;

-- Verify the counts match, then let the drop migration run.
--   SELECT 'vendors', count(*) FROM kummo.vendors
--   UNION ALL SELECT 'shops', count(*) FROM public.shops;
