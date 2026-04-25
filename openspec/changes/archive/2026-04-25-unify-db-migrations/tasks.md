## 1. Backend Migration Audit

- [x] 1.1 Compare `backend/app/db/models.py` against `backend/alembic/versions/20260418_0001_initial.py` for tables, columns, nullability, indexes, foreign keys, and unique constraints
- [x] 1.2 Confirm the Alembic revision graph has exactly one head and no branch conflicts
- [x] 1.3 Confirm `backend/alembic/env.py` reads `DATABASE_URL` consistently for SQLite and PostgreSQL targets

## 2. Backend Migration Implementation

- [x] 2.1 Update the existing initial migration only if it differs from the current SQLAlchemy model schema, preserving existing table and constraint names
- [x] 2.2 Add a migration verification test that applies Alembic to a clean test database and asserts the expected tables exist
- [x] 2.3 Add schema assertions for key constraints and indexes that protect users, projects, questionnaire answers, and generated files
- [x] 2.4 Update backend test setup to use Alembic-created schema where practical, or add an explicit migration test if full fixture migration would make tests unstable

## 3. Backend Documentation

- [x] 3.1 Document the local migration commands for checking current revision and upgrading to head
- [x] 3.2 Document that SQLAlchemy models and Alembic revisions must be kept in sync when schema changes are introduced

## 4. Frontend Scope

- [x] 4.1 Confirm no frontend code or UI behavior changes are required for this migration unification

## 5. Verification

- [x] 5.1 Run Alembic history/current/upgrade checks against a clean SQLite database
- [x] 5.2 Run backend tests to confirm existing auth, project, generation, preview/edit, and export flows still pass
- [x] 5.3 Run available backend lint or type checks for touched backend files
