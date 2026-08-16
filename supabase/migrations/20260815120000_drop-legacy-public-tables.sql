-- Application tables now live in the `kummo` schema. The backend reaches them
-- through asyncpg as `kummo_app`, not through PostgREST, so the anon grants that
-- exposed them to the Data API are obsolete along with the tables themselves.
--
-- The migrations that created public.shops/users/children/activities/bookings have
-- been removed, so on a fresh `supabase db reset` this is a no-op. It still matters
-- for databases provisioned before the move — the hosted project above all, where the
-- rows are real: run supabase/snippets/migrate-public-to-kummo.sql there first.
--
-- Drop order follows the foreign keys: children/bookings/activities reference
-- users and shops.

DROP TABLE IF EXISTS public.bookings;
DROP TABLE IF EXISTS public.children;
DROP TABLE IF EXISTS public.activities;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.shops;
