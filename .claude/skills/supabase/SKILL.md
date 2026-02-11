---
name: supabase
description: Query Supabase database and manage projects via MCP. Use when user needs database queries, migrations, auth operations, or logs. Triggers on SQL, table names, auth, migrations.
allowed-tools: Read, mcp__supabase__execute_sql, mcp__supabase__list_migrations, mcp__supabase__get_logs, mcp__supabase__generate_typescript_types
---

# Supabase MCP

Interact with Supabase projects via the Supabase MCP server.

## Prerequisites
- Supabase MCP server configured in `.mcp.json`
- Project linked via MCP config

## MCP Tools Available

### Execute SQL
```
mcp__supabase__execute_sql
```
Run SQL queries against the database.

### List Migrations
```
mcp__supabase__list_migrations
```
View migration history and status.

### Get Logs
```
mcp__supabase__get_logs
```
Fetch project logs (API, auth, functions).

### Generate Types
```
mcp__supabase__generate_typescript_types
```
Generate TypeScript types from database schema.

## Safety Rules

1. Always use `LIMIT` on SELECT queries
2. Never run DDL (CREATE, DROP, ALTER) without explicit approval
3. Prefer read-only operations
4. Filter by tenant/org when applicable

## Common Queries

```sql
-- List recent users
SELECT id, email, created_at
FROM auth.users
ORDER BY created_at DESC
LIMIT 20;

-- Check table schema
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'your_table';

-- Count by status
SELECT status, COUNT(*)
FROM orders
GROUP BY status;
```

## Common Tables

| Table | Purpose |
|-------|---------|
| `auth.users` | User accounts |
| `public.profiles` | User profiles |
| `public.organizations` | Orgs/tenants |

## Logs

Use `mcp__supabase__get_logs` with service filter:
- `api` - API gateway logs
- `auth` - Authentication logs
- `functions` - Edge function logs
- `postgres` - Database logs
