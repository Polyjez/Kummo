-- One-off reset of the hosted project's migration state. Run as `postgres` from the
-- SQL editor, then `pnpm exec supabase db push` to replay the corrected migrations.
--
-- WHY THIS EXISTS
-- A `db push` on 2026-08-16 applied 20260804155602 and 20260815120000, then failed on
-- 20260816200000 with "permission denied for schema supabase_migrations". The cause was
-- a `set local role` / `reset role` pair in that migration: the CLI records each applied
-- migration with an INSERT into supabase_migrations *inside the migration's own
-- transaction*, and the role switch was still in effect when it ran. The migrations no
-- longer change role (see 20260804155602_kummo-backend.sql).
--
-- That left the hosted project half-migrated: the roles and an empty `kummo` schema
-- owned by kummo_migrator exist, the legacy `public.*` tables were dropped, and the
-- history records two migrations whose files have since been rewritten. This clears all
-- of it so the corrected chain applies from scratch.
--
-- READ BEFORE RUNNING
-- This drops the `kummo` schema and both roles. Confirm the project holds nothing you
-- still need -- and that any recovery from backup has already happened -- first.

begin;

-- `postgres` is NOT a superuser on Supabase. It created these roles, so PG16+ gives it
-- ADMIN OPTION on them implicitly -- but admin is not membership, and without membership
-- it cannot act as kummo_migrator and so cannot alter, reassign or drop anything the
-- role owns. Granting membership is what makes every statement below possible; this is
-- the step whose absence produces "must be owner of schema kummo".
grant kummo_migrator to postgres;
grant kummo_app to postgres;

-- Hand back everything the roles own, in this database, so they can be dropped.
-- REASSIGN covers the `kummo` schema itself along with any tables inside it.
reassign owned by kummo_migrator, kummo_app to postgres;

-- Now `postgres` owns the schema and can drop it. Empty as of the failed push; CASCADE
-- keeps this correct if a later attempt got further.
drop schema if exists kummo cascade;

-- REASSIGN moved ownership but left granted privileges and default ACLs behind --
-- including the `alter default privileges for role kummo_migrator` from the original
-- 20260804155602. DROP OWNED clears those, which DROP ROLE requires.
drop owned by kummo_migrator;
drop role if exists kummo_migrator;

drop owned by kummo_app;
drop role if exists kummo_app;

-- Forget the applied migrations. Their files were rewritten, so the recorded versions no
-- longer correspond to what is on disk; leaving them would make `db push` skip the very
-- migrations that need to run.
delete from supabase_migrations.schema_migrations
 where version in ('20260804155602', '20260815120000', '20260816200000');

commit;

-- Expected afterwards: no `kummo` schema, no kummo_* roles, an empty history. Verify:
--
--   select nspname from pg_namespace where nspname = 'kummo';               -- 0 rows
--   select rolname from pg_roles where rolname like 'kummo%';               -- 0 rows
--   select version from supabase_migrations.schema_migrations order by 1;   -- 0 rows
--
-- Then run `pnpm exec supabase db push`.
