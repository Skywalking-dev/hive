#!/usr/bin/env bash
# Supabase project sync — cache schema, extensions, functions locally.
# Usage: supabase_sync.sh [project-ref]
#   If no ref given, uses SUPABASE_PROJECT_REF from .env or prompts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_DIR="${HIVE_DIR}/cache/supabase"

# Load .env
if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

# Resolve project ref
PROJECT_REF="${1:-${SUPABASE_PROJECT_REF:-}}"
if [[ -z "$PROJECT_REF" ]]; then
  echo "Available projects:"
  supabase projects list 2>/dev/null | grep -v "^$" || true
  die "Usage: supabase_sync.sh <project-ref>"
fi

# Resolve DB URL — need SUPABASE_DB_URL or construct from project ref
DB_URL="${SUPABASE_DB_URL:-}"
SUPABASE_ACCESS_TOKEN="${SUPABASE_ACCESS_TOKEN:-}"

PROJECT_DIR="${CACHE_DIR}/${PROJECT_REF}"
mkdir -p "$PROJECT_DIR"

echo "[sync] Project: ${PROJECT_REF}"
echo "[sync] Cache: ${PROJECT_DIR}"

# --- 1. Schema (tables, columns, types, constraints) ---
echo "[sync] Fetching schema..."

# Use Supabase Management API if we have access token
if [[ -n "$SUPABASE_ACCESS_TOKEN" ]]; then
  # Tables + columns via Management API
  curl -sS "https://api.supabase.com/v1/projects/${PROJECT_REF}/database/tables" \
    -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    | jq '.' > "${PROJECT_DIR}/tables_raw.json" 2>/dev/null || true
fi

# Use supabase CLI inspect for detailed schema
supabase inspect db --linked --project-ref "$PROJECT_REF" table-sizes 2>/dev/null \
  | tee "${PROJECT_DIR}/table_sizes.txt" > /dev/null || true

# Get full schema via supabase CLI inspect
SCHEMA_SQL=$(cat <<'EOSQL'
SELECT json_agg(t) FROM (
  SELECT
    table_schema,
    table_name,
    (
      SELECT json_agg(json_build_object(
        'column_name', c.column_name,
        'data_type', c.data_type,
        'udt_name', c.udt_name,
        'is_nullable', c.is_nullable,
        'column_default', c.column_default,
        'character_maximum_length', c.character_maximum_length
      ) ORDER BY c.ordinal_position)
      FROM information_schema.columns c
      WHERE c.table_schema = t.table_schema AND c.table_name = t.table_name
    ) AS columns,
    (
      SELECT json_agg(json_build_object(
        'constraint_name', tc.constraint_name,
        'constraint_type', tc.constraint_type
      ))
      FROM information_schema.table_constraints tc
      WHERE tc.table_schema = t.table_schema AND tc.table_name = t.table_name
    ) AS constraints
  FROM information_schema.tables t
  WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast', 'supabase_migrations', 'graphql', 'graphql_public', 'realtime', 'storage', '_realtime', 'pgsodium', 'pgsodium_masks', '_analytics', 'supabase_functions', 'net', 'pgbouncer')
    AND table_type = 'BASE TABLE'
  ORDER BY table_schema, table_name
) t;
EOSQL
)

if [[ -n "$SUPABASE_ACCESS_TOKEN" ]]; then
  SCHEMA_RESULT=$(curl -sS "https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query" \
    -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg q "$SCHEMA_SQL" '{query: $q}')" 2>/dev/null || echo "[]")
  echo "$SCHEMA_RESULT" | jq '.[0].json_agg // []' > "${PROJECT_DIR}/schema.json" 2>/dev/null || echo "[]" > "${PROJECT_DIR}/schema.json"
else
  echo "[]" > "${PROJECT_DIR}/schema.json"
  echo "[sync] Warning: No SUPABASE_ACCESS_TOKEN — schema query skipped. Set it for full sync."
fi

# --- 2. Extensions ---
echo "[sync] Fetching extensions..."

EXT_SQL="SELECT json_agg(json_build_object('name', extname, 'version', extversion, 'schema', extnamespace::regnamespace::text)) FROM pg_extension WHERE extname NOT IN ('plpgsql');"

if [[ -n "$SUPABASE_ACCESS_TOKEN" ]]; then
  EXT_RESULT=$(curl -sS "https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query" \
    -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg q "$EXT_SQL" '{query: $q}')" 2>/dev/null || echo "[]")
  echo "$EXT_RESULT" | jq '.[0].json_agg // []' > "${PROJECT_DIR}/extensions.json" 2>/dev/null || echo "[]" > "${PROJECT_DIR}/extensions.json"
else
  echo "[]" > "${PROJECT_DIR}/extensions.json"
fi

# --- 3. RLS Policies ---
echo "[sync] Fetching RLS policies..."

RLS_SQL="SELECT json_agg(json_build_object('table_schema', schemaname, 'table_name', tablename, 'policy_name', policyname, 'cmd', cmd, 'roles', roles, 'qual', qual)) FROM pg_policies WHERE schemaname NOT IN ('storage', 'auth', 'realtime', 'supabase_functions');"

if [[ -n "$SUPABASE_ACCESS_TOKEN" ]]; then
  RLS_RESULT=$(curl -sS "https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query" \
    -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg q "$RLS_SQL" '{query: $q}')" 2>/dev/null || echo "[]")
  echo "$RLS_RESULT" | jq '.[0].json_agg // []' > "${PROJECT_DIR}/rls_policies.json" 2>/dev/null || echo "[]" > "${PROJECT_DIR}/rls_policies.json"
else
  echo "[]" > "${PROJECT_DIR}/rls_policies.json"
fi

# --- 4. Edge Functions ---
echo "[sync] Fetching edge functions..."

if [[ -n "$SUPABASE_ACCESS_TOKEN" ]]; then
  curl -sS "https://api.supabase.com/v1/projects/${PROJECT_REF}/functions" \
    -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
    | jq '[.[] | {name: .name, slug: .slug, status: .status, created_at: .created_at}]' \
    > "${PROJECT_DIR}/functions.json" 2>/dev/null || echo "[]" > "${PROJECT_DIR}/functions.json"
else
  echo "[]" > "${PROJECT_DIR}/functions.json"
fi

# --- 5. Project metadata ---
echo "[sync] Fetching project metadata..."

if [[ -n "$SUPABASE_ACCESS_TOKEN" ]]; then
  curl -sS "https://api.supabase.com/v1/projects/${PROJECT_REF}" \
    -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
    | jq '{name: .name, region: .region, status: .status, database: {host: .database.host, version: .database.version}, created_at: .created_at}' \
    > "${PROJECT_DIR}/meta.json" 2>/dev/null || echo "{}" > "${PROJECT_DIR}/meta.json"
else
  echo "{}" > "${PROJECT_DIR}/meta.json"
fi

# Add sync timestamp
jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '. + {last_sync: $ts}' "${PROJECT_DIR}/meta.json" > "${PROJECT_DIR}/meta.json.tmp" \
  && mv "${PROJECT_DIR}/meta.json.tmp" "${PROJECT_DIR}/meta.json"

# --- Summary ---
echo ""
echo "[sync] Done. Files:"
ls -la "${PROJECT_DIR}/"
echo ""

# Print quick summary
echo "=== Quick Summary ==="
echo "Tables: $(jq 'length' "${PROJECT_DIR}/schema.json" 2>/dev/null || echo 0)"
echo "Extensions: $(jq 'length' "${PROJECT_DIR}/extensions.json" 2>/dev/null || echo 0)"
echo "RLS Policies: $(jq 'length' "${PROJECT_DIR}/rls_policies.json" 2>/dev/null || echo 0)"
echo "Edge Functions: $(jq 'length' "${PROJECT_DIR}/functions.json" 2>/dev/null || echo 0)"

# Check critical extensions for agent service
echo ""
echo "=== Critical Extensions Check ==="
for ext in pgsodium pg_cron pgvector; do
  if jq -e ".[] | select(.name == \"$ext\")" "${PROJECT_DIR}/extensions.json" > /dev/null 2>&1; then
    echo "  $ext: ENABLED"
  else
    echo "  $ext: NOT FOUND"
  fi
done
