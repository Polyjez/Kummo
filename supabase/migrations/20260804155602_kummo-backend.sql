-- DDL role: used only by Alembic, from CI/deploy
create role kummo_migrator with login password '6TgkGDacgEFNwR@M';

-- `postgres` is not a superuser on Supabase, so it can only create objects owned
-- by kummo_migrator (and alter that role's default privileges below) if it is a
-- member of the role.
grant kummo_migrator to postgres;

create schema kummo authorization kummo_migrator;

-- Runtime role: DML only, no DDL, no BYPASSRLS
create role kummo_app with login password '3bX!748fHPuFh9MN';
grant usage on schema kummo to kummo_app;

alter default privileges for role kummo_migrator in schema kummo
  grant select, insert, update, delete on tables to kummo_app;
alter default privileges for role kummo_migrator in schema kummo
  grant usage, select on sequences to kummo_app;