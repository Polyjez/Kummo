-- Application tables now live in the `kummo` schema and are owned by Alembic
-- (see backend/alembic/versions/0001_kummo_schema.py). The backend reaches them
-- through asyncpg as `kummo_app`, not through PostgREST, so the anon grants that
-- exposed them to the Data API are obsolete along with the tables themselves.
--
-- Drop order follows the foreign keys: children/bookings/activities reference
-- users and shops.

DROP TABLE IF EXISTS public.bookings;
DROP TABLE IF EXISTS public.children;
DROP TABLE IF EXISTS public.activities;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.shops;
