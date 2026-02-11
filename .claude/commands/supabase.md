---
description: Query Supabase database or manage Edge Functions
argument-hint: <query> | functions <list|deploy|logs> | auth <users|sessions>
---

Interact with Supabase projects using the supabase skill.

> [!IMPORTANT]
> Follow the rules in the [supabase] skill.

# Usage

## Query database
Provide a natural language query or SQL to execute against the database.

## Edge Functions
- `functions list` - list deployed functions
- `functions deploy <name>` - deploy a function
- `functions logs <name>` - view function logs

## Auth
- `auth users` - list recent users
- `auth sessions <user_id>` - view user sessions

# Prerequisites
- Supabase MCP server configured
- `SUPABASE_ACCESS_TOKEN` in `.env`
