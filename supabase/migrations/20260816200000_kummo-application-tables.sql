-- Application tables for the `kummo` schema.
--
-- Previously created by Alembic; the Supabase CLI is now the single DDL tool, so this
-- is the baseline (ADR 0004). `bookings` is deliberately absent: it existed in the
-- Alembic revision but no route ever read or wrote it, and the frontend keeps bookings
-- in localStorage. It comes back with the feature.
--
-- No `set role` anywhere -- see 20260804155602_kummo-backend.sql for why that would
-- break `db push`. Tables are owned by the role the CLI connects as, and `kummo_app`
-- gets its DML from the explicit grant at the bottom.

create table kummo.vendors (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  -- Links to a Supabase Auth user. Unique, but no foreign key: `auth.users`
  -- belongs to GoTrue's own role. Null for vendors that predate authentication.
  auth_user_id    uuid unique,
  name            text not null,
  address         text not null,
  phone           text,
  email           text not null,
  website         text,
  activity_type   text[] not null,
  picture         text
);

create table kummo.clients (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  auth_user_id    uuid unique,
  first_name      text not null,
  last_name       text not null,
  email           text not null,
  -- Enrichment fields: not collected at registration.
  age             integer,
  interests       text[],
  number_children integer
);

create table kummo.activities (
  id               uuid primary key default gen_random_uuid(),
  created_at       timestamptz not null default now(),
  vendor_id        uuid not null references kummo.vendors (id),
  title            text not null,
  description      text,
  price            real,
  participants_max integer not null,
  duration         text not null,
  age_group        text,
  picture          text not null
);

-- Every migration that adds a table to `kummo` repeats this line. One explicit grant
-- is easier to follow -- and harder to get wrong -- than default privileges that only
-- fire for one particular creating role.
grant select, insert, update, delete on all tables in schema kummo to kummo_app;
