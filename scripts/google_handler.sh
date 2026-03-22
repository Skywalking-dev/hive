#!/usr/bin/env bash
# google_handler.sh — Unified Google API handler (bash + curl + jq)
# Replaces: google_calendar_handler.py, google_drive_handler.py,
#           google_docs_handler.py, gmail_handler.py
#
# Usage: google_handler.sh <service> <action> [options]
# Services: auth, calendar, drive, docs, gmail

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths & env
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${HIVE_DIR}/.env"
CACHE_DIR="${HIVE_DIR}/cache"
TOKEN_CACHE="${CACHE_DIR}/google_token.json"

# Load .env if present
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^\s*#' "${ENV_FILE}" | grep -v '^\s*$' | xargs)
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

err_json() {
  printf '{"success":false,"error":%s}\n' "$(printf '%s' "$1" | jq -Rs .)"
  exit 1
}

ok_json() {
  # $1 = compact JSON value for "data"
  printf '{"success":true,"data":%s}\n' "$1"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || err_json "Required command not found: $1"
}

require_cmd curl
require_cmd jq

# URL-encode a string (POSIX-safe via jq)
urlencode() {
  printf '%s' "$1" | jq -sRr @uri
}

# ---------------------------------------------------------------------------
# OAuth token management
# ---------------------------------------------------------------------------

# Resolve credentials with fallback chain:
#   GOOGLE_CLIENT_ID > GMAIL_CLIENT_ID
#   GOOGLE_CLIENT_SECRET > GMAIL_CLIENT_SECRET
#   Per-service refresh tokens: GOOGLE_<SERVICE>_REFRESH_TOKEN > GOOGLE_REFRESH_TOKEN > GMAIL_REFRESH_TOKEN
_get_client_id() {
  local svc="${1:-}"
  local var="GOOGLE_$(echo "$svc" | tr '[:lower:]' '[:upper:]')_CLIENT_ID"
  echo "${!var:-${GOOGLE_CLIENT_ID:-${GMAIL_CLIENT_ID:-}}}"
}

_get_client_secret() {
  local svc="${1:-}"
  local var="GOOGLE_$(echo "$svc" | tr '[:lower:]' '[:upper:]')_CLIENT_SECRET"
  echo "${!var:-${GOOGLE_CLIENT_SECRET:-${GMAIL_CLIENT_SECRET:-}}}"
}

_get_refresh_token() {
  local svc="${1:-}"
  local var="GOOGLE_$(echo "$svc" | tr '[:lower:]' '[:upper:]')_REFRESH_TOKEN"
  echo "${!var:-${GOOGLE_REFRESH_TOKEN:-${GMAIL_REFRESH_TOKEN:-}}}"
}

# Fetch a fresh access token; write to cache; print token to stdout
auth_refresh() {
  local svc="${1:-}"
  local client_id client_secret refresh_token

  client_id="$(_get_client_id "$svc")"
  client_secret="$(_get_client_secret "$svc")"
  refresh_token="$(_get_refresh_token "$svc")"

  [[ -z "$client_id" ]]      && err_json "GOOGLE_CLIENT_ID (or GMAIL_CLIENT_ID) not set"
  [[ -z "$client_secret" ]]  && err_json "GOOGLE_CLIENT_SECRET (or GMAIL_CLIENT_SECRET) not set"
  [[ -z "$refresh_token" ]]  && err_json "No refresh token found for service: ${svc:-default}"

  local resp
  resp=$(curl -sf -X POST "https://oauth2.googleapis.com/token" \
    -d "client_id=${client_id}" \
    -d "client_secret=${client_secret}" \
    -d "refresh_token=${refresh_token}" \
    -d "grant_type=refresh_token") || err_json "Token refresh request failed"

  local token
  token=$(echo "$resp" | jq -r '.access_token // empty')
  [[ -z "$token" ]] && err_json "No access_token in response: $(echo "$resp" | jq -c .)"

  mkdir -p "${CACHE_DIR}"
  local expires_in
  expires_in=$(echo "$resp" | jq -r '.expires_in // 3600')
  local expiry
  expiry=$(( $(date +%s) + expires_in - 60 ))  # 60s buffer

  jq -n \
    --arg token "$token" \
    --arg svc "${svc:-default}" \
    --argjson expiry "$expiry" \
    '{"access_token":$token,"service":$svc,"expires_at":$expiry}' > "${TOKEN_CACHE}"

  echo "$token"
}

# Get cached token or refresh; print token to stdout
get_token() {
  local svc="${1:-}"

  if [[ -f "${TOKEN_CACHE}" ]]; then
    local cached_svc cached_token cached_expiry now
    cached_svc=$(jq -r '.service // "default"' "${TOKEN_CACHE}")
    cached_token=$(jq -r '.access_token // empty' "${TOKEN_CACHE}")
    cached_expiry=$(jq -r '.expires_at // 0' "${TOKEN_CACHE}")
    now=$(date +%s)

    # Reuse cache only when service matches (all services use same credential set)
    if [[ -n "$cached_token" && "$cached_expiry" -gt "$now" ]]; then
      echo "$cached_token"
      return
    fi
  fi

  auth_refresh "$svc"
}

cmd_auth_refresh() {
  local token
  token=$(auth_refresh "")
  ok_json "$(jq -n --arg t "$token" '{"access_token":$t,"cached":"'${TOKEN_CACHE}'"}')"
}

cmd_auth_status() {
  if [[ ! -f "${TOKEN_CACHE}" ]]; then
    ok_json '{"valid":false,"reason":"no cached token"}'
    return
  fi
  local expiry now
  expiry=$(jq -r '.expires_at // 0' "${TOKEN_CACHE}")
  now=$(date +%s)
  if [[ "$expiry" -gt "$now" ]]; then
    local secs=$(( expiry - now ))
    ok_json "$(jq -n --argjson s "$secs" '{"valid":true,"expires_in_seconds":$s}')"
  else
    ok_json '{"valid":false,"reason":"token expired"}'
  fi
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

# $1=url $2=token  → prints response body
http_get() {
  local url="$1" token="$2"
  curl -sf -H "Authorization: Bearer ${token}" "$url" || {
    local code=$?
    err_json "GET ${url} failed (curl exit ${code})"
  }
}

# $1=url $2=token $3=json_body  → prints response body
http_post() {
  local url="$1" token="$2" body="$3"
  curl -sf -X POST \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$url" || {
    local code=$?
    err_json "POST ${url} failed (curl exit ${code})"
  }
}

# $1=url $2=token $3=json_body  → prints response body
http_patch() {
  local url="$1" token="$2" body="$3"
  curl -sf -X PATCH \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$url" || {
    local code=$?
    err_json "PATCH ${url} failed (curl exit ${code})"
  }
}

# $1=url $2=token  → exits 0/1
http_delete() {
  local url="$1" token="$2"
  curl -sf -X DELETE \
    -H "Authorization: Bearer ${token}" \
    -o /dev/null \
    -w "%{http_code}" \
    "$url" | grep -q "^2" || {
    err_json "DELETE ${url} failed"
  }
}

# $1=url $2=token $3=raw_multipart_body $4=boundary → prints response body
http_post_multipart() {
  local url="$1" token="$2" body_file="$3" boundary="$4"
  curl -sf -X POST \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: multipart/related; boundary=${boundary}" \
    --data-binary "@${body_file}" \
    "$url" || {
    local code=$?
    err_json "POST multipart ${url} failed (curl exit ${code})"
  }
}

# $1=url $2=token $3=output_path  — downloads binary to file
http_download() {
  local url="$1" token="$2" out="$3"
  curl -sf -H "Authorization: Bearer ${token}" -o "$out" "$url" || {
    local code=$?
    err_json "Download ${url} failed (curl exit ${code})"
  }
}

# ---------------------------------------------------------------------------
# Extract IDs from URLs
# ---------------------------------------------------------------------------

extract_file_id() {
  local input="$1"
  # Try known URL patterns
  local id
  id=$(echo "$input" | grep -oE '/file/d/([a-zA-Z0-9_-]+)' | grep -oE '[a-zA-Z0-9_-]+$' | head -1)
  [[ -n "$id" ]] && { echo "$id"; return; }
  id=$(echo "$input" | grep -oE '/document/d/([a-zA-Z0-9_-]+)' | grep -oE '[a-zA-Z0-9_-]+$' | head -1)
  [[ -n "$id" ]] && { echo "$id"; return; }
  id=$(echo "$input" | grep -oE '/spreadsheets/d/([a-zA-Z0-9_-]+)' | grep -oE '[a-zA-Z0-9_-]+$' | head -1)
  [[ -n "$id" ]] && { echo "$id"; return; }
  id=$(echo "$input" | grep -oE '/presentation/d/([a-zA-Z0-9_-]+)' | grep -oE '[a-zA-Z0-9_-]+$' | head -1)
  [[ -n "$id" ]] && { echo "$id"; return; }
  id=$(echo "$input" | grep -oE '/folders/([a-zA-Z0-9_-]+)' | grep -oE '[a-zA-Z0-9_-]+$' | head -1)
  [[ -n "$id" ]] && { echo "$id"; return; }
  id=$(echo "$input" | grep -oE '[?&]id=([a-zA-Z0-9_-]+)' | grep -oE '=([a-zA-Z0-9_-]+)' | tr -d '=' | head -1)
  [[ -n "$id" ]] && { echo "$id"; return; }
  # Assume already an ID
  echo "$input"
}

# Local time helpers (TZ = America/Argentina/Buenos_Aires, offset -03:00)
now_iso() {
  date -u '+%Y-%m-%dT%H:%M:%S-03:00' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S-03:00'
}

today_start() {
  # Start of today in -03:00
  local d
  d=$(TZ="America/Argentina/Buenos_Aires" date '+%Y-%m-%d' 2>/dev/null || date '+%Y-%m-%d')
  echo "${d}T00:00:00-03:00"
}

today_end() {
  local d
  d=$(TZ="America/Argentina/Buenos_Aires" date '+%Y-%m-%d' 2>/dev/null || date '+%Y-%m-%d')
  echo "${d}T23:59:59-03:00"
}

# Add N days to today; returns YYYY-MM-DD
add_days() {
  local n="$1"
  # macOS: date -v+Nd; GNU: date -d "+N days"
  if date -v+1d > /dev/null 2>&1; then
    TZ="America/Argentina/Buenos_Aires" date -v+"${n}"d '+%Y-%m-%d'
  else
    date -d "+${n} days" '+%Y-%m-%d'
  fi
}

# ---------------------------------------------------------------------------
# CALENDAR
# ---------------------------------------------------------------------------

CALENDAR_BASE="https://www.googleapis.com/calendar/v3"

_format_event() {
  # $1 = raw event JSON string
  echo "$1" | jq '{
    id: .id,
    summary: (.summary // "(Sin titulo)"),
    description: (.description // ""),
    location: (.location // ""),
    start: (.start.dateTime // .start.date),
    end: (.end.dateTime // .end.date),
    isAllDay: (if .start.date != null and .start.dateTime == null then true else false end),
    status: (.status // "confirmed"),
    htmlLink: (.htmlLink // ""),
    hangoutLink: (.hangoutLink // ""),
    attendees: [.attendees[]? | {email:.email, name:(.displayName//""), responseStatus:(.responseStatus//"needsAction")}],
    organizer: {email:(.organizer.email//""), name:(.organizer.displayName//"")},
    recurrence: (.recurrence // [])
  }'
}

calendar_list() {
  local calendar="${1:-primary}" days="${2:-7}"
  local token start end
  token=$(get_token "calendar")
  start=$(today_start)
  local end_date
  end_date=$(add_days "$days")
  end="${end_date}T23:59:59-03:00"

  local params
  params="timeMin=$(urlencode "$start")&timeMax=$(urlencode "$end")&singleEvents=true&orderBy=startTime&maxResults=100"
  local cal_enc
  cal_enc=$(urlencode "$calendar")
  local resp
  resp=$(http_get "${CALENDAR_BASE}/calendars/${cal_enc}/events?${params}" "$token")

  local events
  events=$(echo "$resp" | jq '[.items[]? | {
    id: .id,
    summary: (.summary // "(Sin titulo)"),
    description: (.description // ""),
    location: (.location // ""),
    start: (.start.dateTime // .start.date),
    end: (.end.dateTime // .end.date),
    isAllDay: (if .start.date != null and .start.dateTime == null then true else false end),
    status: (.status // "confirmed"),
    htmlLink: (.htmlLink // ""),
    hangoutLink: (.hangoutLink // ""),
    attendees: [.attendees[]? | {email:.email, name:(.displayName//""), responseStatus:(.responseStatus//"needsAction")}],
    organizer: {email:(.organizer.email//""), name:(.organizer.displayName//"")},
    recurrence: (.recurrence // [])
  }]')

  ok_json "$(jq -n \
    --argjson events "$events" \
    --arg start "$start" \
    --arg end "$end" \
    '{"period":{"start":$start,"end":$end},"count":($events|length),"events":$events}')"
}

calendar_today() {
  local calendar="${1:-primary}"
  local token start end
  token=$(get_token "calendar")
  start=$(today_start)
  end=$(today_end)

  local params
  params="timeMin=$(urlencode "$start")&timeMax=$(urlencode "$end")&singleEvents=true&orderBy=startTime&maxResults=100"
  local cal_enc
  cal_enc=$(urlencode "$calendar")
  local resp
  resp=$(http_get "${CALENDAR_BASE}/calendars/${cal_enc}/events?${params}" "$token")

  local events
  events=$(echo "$resp" | jq '[.items[]? | {
    id: .id,
    summary: (.summary // "(Sin titulo)"),
    description: (.description // ""),
    location: (.location // ""),
    start: (.start.dateTime // .start.date),
    end: (.end.dateTime // .end.date),
    isAllDay: (if .start.date != null and .start.dateTime == null then true else false end),
    status: (.status // "confirmed"),
    htmlLink: (.htmlLink // ""),
    hangoutLink: (.hangoutLink // ""),
    attendees: [.attendees[]? | {email:.email, name:(.displayName//""), responseStatus:(.responseStatus//"needsAction")}],
    organizer: {email:(.organizer.email//""), name:(.organizer.displayName//"")},
    recurrence: (.recurrence // [])
  }]')

  ok_json "$(jq -n \
    --argjson events "$events" \
    --arg start "$start" \
    --arg end "$end" \
    '{"period":{"start":$start,"end":$end},"count":($events|length),"events":$events}')"
}

calendar_week() {
  calendar_list "${1:-primary}" 7
}

calendar_get() {
  local event_id="$1" calendar="${2:-primary}"
  local token
  token=$(get_token "calendar")
  local cal_enc ev_enc
  cal_enc=$(urlencode "$calendar")
  ev_enc=$(urlencode "$event_id")
  local resp
  resp=$(http_get "${CALENDAR_BASE}/calendars/${cal_enc}/events/${ev_enc}" "$token")
  local event
  event=$(echo "$resp" | jq '{
    id: .id,
    summary: (.summary // "(Sin titulo)"),
    description: (.description // ""),
    location: (.location // ""),
    start: (.start.dateTime // .start.date),
    end: (.end.dateTime // .end.date),
    isAllDay: (if .start.date != null and .start.dateTime == null then true else false end),
    status: (.status // "confirmed"),
    htmlLink: (.htmlLink // ""),
    hangoutLink: (.hangoutLink // ""),
    attendees: [.attendees[]? | {email:.email, name:(.displayName//""), responseStatus:(.responseStatus//"needsAction")}],
    organizer: {email:(.organizer.email//""), name:(.organizer.displayName//"")},
    recurrence: (.recurrence // [])
  }')
  ok_json "$event"
}

calendar_calendars() {
  local token
  token=$(get_token "calendar")
  local resp
  resp=$(http_get "${CALENDAR_BASE}/users/me/calendarList" "$token")
  local cals
  cals=$(echo "$resp" | jq '[.items[]? | {
    id: .id,
    summary: (.summary // ""),
    description: (.description // ""),
    primary: (.primary // false),
    accessRole: (.accessRole // ""),
    backgroundColor: (.backgroundColor // "")
  }]')
  ok_json "$(jq -n --argjson c "$cals" '{"calendars":$c}')"
}

calendar_freebusy() {
  local start_date="$1" end_date="$2"
  local token
  token=$(get_token "calendar")
  local body
  body=$(jq -n \
    --arg ts "${start_date}T00:00:00-03:00" \
    --arg te "${end_date}T23:59:59-03:00" \
    '{"timeMin":$ts,"timeMax":$te,"items":[{"id":"primary"}]}')
  local resp
  resp=$(http_post "${CALENDAR_BASE}/freeBusy" "$token" "$body")
  local busy
  busy=$(echo "$resp" | jq '[.calendars.primary.busy[]? | {start:.start,end:.end}]')
  ok_json "$(jq -n \
    --arg s "$start_date" \
    --arg e "$end_date" \
    --argjson busy "$busy" \
    '{"period":{"start":$s,"end":$e},"busySlots":$busy,"busyCount":($busy|length)}')"
}

calendar_search() {
  local query="$1" calendar="${2:-primary}" days="${3:-30}"
  local token
  token=$(get_token "calendar")
  local start end end_date
  start=$(today_start)
  end_date=$(add_days "$days")
  end="${end_date}T23:59:59-03:00"

  local params
  params="timeMin=$(urlencode "$start")&timeMax=$(urlencode "$end")&q=$(urlencode "$query")&singleEvents=true&orderBy=startTime&maxResults=50"
  local cal_enc
  cal_enc=$(urlencode "$calendar")
  local resp
  resp=$(http_get "${CALENDAR_BASE}/calendars/${cal_enc}/events?${params}" "$token")
  local events
  events=$(echo "$resp" | jq '[.items[]? | {
    id: .id,
    summary: (.summary // "(Sin titulo)"),
    description: (.description // ""),
    location: (.location // ""),
    start: (.start.dateTime // .start.date),
    end: (.end.dateTime // .end.date),
    isAllDay: (if .start.date != null and .start.dateTime == null then true else false end),
    status: (.status // "confirmed"),
    htmlLink: (.htmlLink // ""),
    hangoutLink: (.hangoutLink // ""),
    attendees: [.attendees[]? | {email:.email, name:(.displayName//""), responseStatus:(.responseStatus//"needsAction")}],
    organizer: {email:(.organizer.email//""), name:(.organizer.displayName//"")},
    recurrence: (.recurrence // [])
  }]')
  ok_json "$(jq -n \
    --arg q "$query" \
    --argjson d "$days" \
    --argjson events "$events" \
    '{"query":$q,"days":$d,"count":($events|length),"events":$events}')"
}

calendar_create() {
  # Args parsed from flags by caller
  local summary="$1" start="$2" end="$3"
  local description="${4:-}" location="${5:-}" calendar="${6:-primary}"
  local token
  token=$(get_token "calendar")

  local body
  body=$(jq -n \
    --arg s "$summary" \
    --arg start "$start" \
    --arg end "$end" \
    --arg desc "$description" \
    --arg loc "$location" \
    '{
      summary: $s,
      description: $desc,
      location: $loc,
      start: {dateTime: $start},
      end: {dateTime: $end}
    }')

  local cal_enc
  cal_enc=$(urlencode "$calendar")
  local resp
  resp=$(http_post "${CALENDAR_BASE}/calendars/${cal_enc}/events" "$token" "$body")
  ok_json "$(echo "$resp" | jq '{
    id: .id,
    summary: .summary,
    htmlLink: .htmlLink,
    start: (.start.dateTime // .start.date),
    end: (.end.dateTime // .end.date)
  }')"
}

calendar_delete() {
  local event_id="$1" calendar="${2:-primary}"
  local token
  token=$(get_token "calendar")
  local cal_enc ev_enc
  cal_enc=$(urlencode "$calendar")
  ev_enc=$(urlencode "$event_id")
  http_delete "${CALENDAR_BASE}/calendars/${cal_enc}/events/${ev_enc}" "$token"
  ok_json "$(jq -n --arg id "$event_id" '{"deleted":true,"eventId":$id}')"
}

# ---------------------------------------------------------------------------
# DRIVE
# ---------------------------------------------------------------------------

DRIVE_BASE="https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD_BASE="https://www.googleapis.com/upload/drive/v3"
DRIVE_FILE_FIELDS="id,name,mimeType,modifiedTime,createdTime,size,webViewLink,owners,parents"

ALLOWED_DOMAINS="publica.la"

_drive_format_file() {
  echo "$1" | jq '{
    id: .id,
    name: (.name // ""),
    mimeType: (.mimeType // ""),
    modifiedTime: (.modifiedTime // ""),
    createdTime: (.createdTime // ""),
    size: .size,
    url: (.webViewLink // ""),
    owner: (if (.owners|length) > 0 then .owners[0].emailAddress else "" end),
    parents: (.parents // [])
  }'
}

_drive_mime_filter() {
  case "$1" in
    doc)    echo "mimeType='application/vnd.google-apps.document'" ;;
    sheet)  echo "mimeType='application/vnd.google-apps.spreadsheet'" ;;
    pdf)    echo "mimeType='application/pdf'" ;;
    folder) echo "mimeType='application/vnd.google-apps.folder'" ;;
    *)      echo "" ;;
  esac
}

drive_list() {
  local limit="${1:-10}" file_type="${2:-all}" folder_id="${3:-}"
  local token
  token=$(get_token "drive")

  local q="trashed=false"
  local mime_clause
  mime_clause=$(_drive_mime_filter "$file_type")
  [[ -n "$mime_clause" ]] && q="${q} and ${mime_clause}"
  [[ -n "$folder_id" ]] && q="${q} and '${folder_id}' in parents"

  local params
  params="q=$(urlencode "$q")&orderBy=modifiedTime+desc&pageSize=${limit}&fields=files(${DRIVE_FILE_FIELDS})"
  local resp
  resp=$(http_get "${DRIVE_BASE}/files?${params}" "$token")

  local files
  files=$(echo "$resp" | jq "[.files[]? | {
    id: .id,
    name: (.name // \"\"),
    mimeType: (.mimeType // \"\"),
    modifiedTime: (.modifiedTime // \"\"),
    createdTime: (.createdTime // \"\"),
    size: .size,
    url: (.webViewLink // \"\"),
    owner: (if (.owners|length) > 0 then .owners[0].emailAddress else \"\" end),
    parents: (.parents // [])
  }]")
  ok_json "$(jq -n --argjson f "$files" --argjson c "$(echo "$files" | jq 'length')" --arg t "$file_type" \
    '{"count":$c,"type":$t,"files":$f}')"
}

drive_search() {
  local query="$1" limit="${2:-10}" file_type="${3:-all}"
  local token
  token=$(get_token "drive")

  # Escape single quotes
  local safe_q="${query//\'/\\\'}"
  local q="trashed=false and (name contains '${safe_q}' or fullText contains '${safe_q}')"
  local mime_clause
  mime_clause=$(_drive_mime_filter "$file_type")
  [[ -n "$mime_clause" ]] && q="${q} and ${mime_clause}"

  local params
  params="q=$(urlencode "$q")&orderBy=modifiedTime+desc&pageSize=${limit}&fields=files(${DRIVE_FILE_FIELDS})"
  local resp
  resp=$(http_get "${DRIVE_BASE}/files?${params}" "$token")

  local files
  files=$(echo "$resp" | jq "[.files[]? | {
    id: .id,
    name: (.name // \"\"),
    mimeType: (.mimeType // \"\"),
    modifiedTime: (.modifiedTime // \"\"),
    createdTime: (.createdTime // \"\"),
    size: .size,
    url: (.webViewLink // \"\"),
    owner: (if (.owners|length) > 0 then .owners[0].emailAddress else \"\" end),
    parents: (.parents // [])
  }]")
  ok_json "$(jq -n --arg q "$query" --argjson f "$files" --argjson c "$(echo "$files" | jq 'length')" --arg t "$file_type" \
    '{"query":$q,"type":$t,"count":$c,"files":$f}')"
}

drive_get() {
  local id_or_url="$1"
  local file_id
  file_id=$(extract_file_id "$id_or_url")
  local token
  token=$(get_token "drive")

  local fields="id,name,mimeType,modifiedTime,createdTime,size,webViewLink,owners,parents,shared,sharingUser,permissions,description"
  local resp
  resp=$(http_get "${DRIVE_BASE}/files/${file_id}?fields=$(urlencode "$fields")" "$token")

  ok_json "$(echo "$resp" | jq '{
    id: .id,
    name: (.name // ""),
    mimeType: (.mimeType // ""),
    modifiedTime: (.modifiedTime // ""),
    createdTime: (.createdTime // ""),
    size: .size,
    url: (.webViewLink // ""),
    owner: (if (.owners|length) > 0 then .owners[0].emailAddress else "" end),
    parents: (.parents // []),
    description: (.description // ""),
    shared: (.shared // false),
    permissions: [.permissions[]? | {id:.id,type:.type,role:.role,emailAddress:(.emailAddress//""),displayName:(.displayName//"")}]
  }')"
}

drive_download() {
  local id_or_url="$1" output="${2:-}"
  local file_id
  file_id=$(extract_file_id "$id_or_url")
  local token
  token=$(get_token "drive")

  # Get metadata
  local meta
  meta=$(http_get "${DRIVE_BASE}/files/${file_id}?fields=id,name,mimeType,size" "$token")
  local mime_type file_name
  mime_type=$(echo "$meta" | jq -r '.mimeType // ""')
  file_name=$(echo "$meta" | jq -r '.name // "download"')

  local url
  case "$mime_type" in
    "application/vnd.google-apps.document")
      url="${DRIVE_BASE}/files/${file_id}/export?mimeType=$(urlencode 'application/pdf')"
      [[ -z "$output" ]] && output="${file_name}.pdf"
      ;;
    "application/vnd.google-apps.spreadsheet")
      url="${DRIVE_BASE}/files/${file_id}/export?mimeType=$(urlencode 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')"
      [[ -z "$output" ]] && output="${file_name}.xlsx"
      ;;
    "application/vnd.google-apps.presentation")
      url="${DRIVE_BASE}/files/${file_id}/export?mimeType=$(urlencode 'application/pdf')"
      [[ -z "$output" ]] && output="${file_name}.pdf"
      ;;
    *)
      url="${DRIVE_BASE}/files/${file_id}?alt=media"
      [[ -z "$output" ]] && output="$file_name"
      ;;
  esac

  http_download "$url" "$token" "$output"
  local size
  size=$(wc -c < "$output" | tr -d ' ')
  ok_json "$(jq -n \
    --arg fid "$file_id" \
    --arg fname "$file_name" \
    --arg mime "$mime_type" \
    --arg out "$output" \
    --argjson sz "$size" \
    '{"fileId":$fid,"fileName":$fname,"mimeType":$mime,"outputPath":$out,"size":$sz}')"
}

drive_upload() {
  local file_path="$1" folder_id="${2:-}" name="${3:-}"
  [[ ! -f "$file_path" ]] && err_json "File not found: ${file_path}"

  local file_name
  file_name="${name:-$(basename "$file_path")}"

  # Guess MIME type
  local mime_type
  mime_type=$(file --mime-type -b "$file_path" 2>/dev/null || echo "application/octet-stream")

  local token
  token=$(get_token "drive")

  # Build metadata JSON
  local metadata
  if [[ -n "$folder_id" ]]; then
    metadata=$(jq -n --arg n "$file_name" --arg f "$folder_id" '{"name":$n,"parents":[$f]}')
  else
    metadata=$(jq -n --arg n "$file_name" '{"name":$n}')
  fi

  local boundary="boundary_gdrive_hive_upload"
  local tmp_body
  tmp_body=$(mktemp)

  {
    printf -- "--%s\r\n" "$boundary"
    printf "Content-Type: application/json; charset=UTF-8\r\n\r\n"
    echo "$metadata"
    printf "\r\n--%s\r\n" "$boundary"
    printf "Content-Type: %s\r\n\r\n" "$mime_type"
  } > "$tmp_body"
  cat "$file_path" >> "$tmp_body"
  printf "\r\n--%s--" "$boundary" >> "$tmp_body"

  local url="${DRIVE_UPLOAD_BASE}/files?uploadType=multipart&fields=id,name,mimeType,webViewLink,size"
  local resp
  resp=$(http_post_multipart "$url" "$token" "$tmp_body" "$boundary")
  rm -f "$tmp_body"

  ok_json "$(echo "$resp" | jq '{
    fileId: .id,
    name: .name,
    mimeType: .mimeType,
    url: .webViewLink,
    size: .size
  }')"
}

drive_mkdir() {
  local name="$1" parent="${2:-}"
  local token
  token=$(get_token "drive")

  local metadata
  if [[ -n "$parent" ]]; then
    metadata=$(jq -n --arg n "$name" --arg p "$parent" \
      '{"name":$n,"mimeType":"application/vnd.google-apps.folder","parents":[$p]}')
  else
    metadata=$(jq -n --arg n "$name" \
      '{"name":$n,"mimeType":"application/vnd.google-apps.folder"}')
  fi

  local resp
  resp=$(http_post "${DRIVE_BASE}/files?fields=id,name,webViewLink" "$token" "$metadata")
  ok_json "$(echo "$resp" | jq '{folderId:.id,name:.name,url:.webViewLink}')"
}

drive_move() {
  local file_id_or_url="$1" new_folder_id="$2"
  local file_id
  file_id=$(extract_file_id "$file_id_or_url")
  local token
  token=$(get_token "drive")

  # Get current parents
  local meta
  meta=$(http_get "${DRIVE_BASE}/files/${file_id}?fields=id,name,parents" "$token")
  local current_parents
  current_parents=$(echo "$meta" | jq -r '.parents // [] | join(",")')

  local params="addParents=$(urlencode "$new_folder_id")&removeParents=$(urlencode "$current_parents")&fields=id,name,parents,webViewLink"
  local resp
  resp=$(http_patch "${DRIVE_BASE}/files/${file_id}?${params}" "$token" "{}")
  ok_json "$(echo "$resp" | jq '{fileId:.id,name:.name,newParents:.parents,url:.webViewLink}')"
}

drive_share() {
  local file_id_or_url="$1" email="$2" role="${3:-reader}" allow_external="${4:-false}"
  local file_id
  file_id=$(extract_file_id "$file_id_or_url")

  # Domain check
  local domain
  domain="${email##*@}"
  domain="${domain,,}"
  if [[ "$allow_external" != "true" && "$domain" != "$ALLOWED_DOMAINS" ]]; then
    err_json "Domain '${domain}' not allowed. Allowed: ${ALLOWED_DOMAINS}. Pass --allow-external to override."
  fi

  local token
  token=$(get_token "drive")
  local body
  body=$(jq -n --arg e "$email" --arg r "$role" '{"type":"user","role":$r,"emailAddress":$e}')
  local resp
  resp=$(http_post "${DRIVE_BASE}/files/${file_id}/permissions" "$token" "$body")
  ok_json "$(echo "$resp" | jq --arg fid "$file_id" --arg e "$email" --arg r "$role" \
    '{permissionId:.id,fileId:$fid,email:$e,role:$r}')"
}

drive_folders() {
  local parent="${1:-}"
  local token
  token=$(get_token "drive")

  local q="mimeType='application/vnd.google-apps.folder' and trashed=false"
  [[ -n "$parent" ]] && q="${q} and '${parent}' in parents"

  local params
  params="q=$(urlencode "$q")&orderBy=name&pageSize=100&fields=files(id,name,modifiedTime,webViewLink,parents)"
  local resp
  resp=$(http_get "${DRIVE_BASE}/files?${params}" "$token")
  local folders
  folders=$(echo "$resp" | jq '[.files[]? | {id:.id,name:(.name//""),modifiedTime:(.modifiedTime//""),url:(.webViewLink//""),parents:(.parents//[])}]')
  ok_json "$(jq -n --argjson f "$folders" --argjson c "$(echo "$folders" | jq 'length')" --arg p "$parent" \
    '{"count":$c,"parentId":$p,"folders":$f}')"
}

# ---------------------------------------------------------------------------
# DOCS
# ---------------------------------------------------------------------------

DOCS_API_BASE="https://docs.googleapis.com/v1/documents"
DOCS_DRIVE_BASE="https://www.googleapis.com/drive/v3/files"
DOCS_DRIVE_UPLOAD="https://www.googleapis.com/upload/drive/v3/files"

DOCS_MIME_TYPES_md="text/markdown"
DOCS_MIME_TYPES_txt="text/plain"
DOCS_MIME_TYPES_html="text/html"
DOCS_MIME_TYPES_pdf="application/pdf"
DOCS_MIME_TYPES_docx="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOCS_MIME_TYPES_epub="application/epub+zip"

_docs_export_mime() {
  local fmt="$1"
  local varname="DOCS_MIME_TYPES_${fmt}"
  echo "${!varname:-}"
}

docs_read() {
  local id_or_url="$1"
  local doc_id
  doc_id=$(extract_file_id "$id_or_url")
  local token
  token=$(get_token "docs")

  # Try markdown export first, fallback to plain text
  local content
  local export_url="${DOCS_DRIVE_BASE}/${doc_id}/export?mimeType=$(urlencode 'text/markdown')"
  content=$(curl -sf -H "Authorization: Bearer ${token}" "$export_url" 2>/dev/null) || {
    export_url="${DOCS_DRIVE_BASE}/${doc_id}/export?mimeType=$(urlencode 'text/plain')"
    content=$(http_get "$export_url" "$token")
  }

  local meta
  meta=$(http_get "${DOCS_DRIVE_BASE}/${doc_id}?fields=id,name,modifiedTime,createdTime,webViewLink" "$token")

  ok_json "$(jq -n \
    --arg did "$doc_id" \
    --arg title "$(echo "$meta" | jq -r '.name // ""')" \
    --arg url "$(echo "$meta" | jq -r '.webViewLink // ""')" \
    --arg mod "$(echo "$meta" | jq -r '.modifiedTime // ""')" \
    --arg created "$(echo "$meta" | jq -r '.createdTime // ""')" \
    --arg content "$content" \
    '{"documentId":$did,"title":$title,"url":$url,"modifiedTime":$mod,"createdTime":$created,"content":$content}')"
}

docs_read_rich() {
  local id_or_url="$1"
  local doc_id
  doc_id=$(extract_file_id "$id_or_url")
  local token
  token=$(get_token "docs")

  local doc
  doc=$(http_get "${DOCS_API_BASE}/${doc_id}?suggestionsViewMode=PREVIEW_SUGGESTIONS_ACCEPTED" "$token")

  # Count suggestions by looking for suggestedInsertionIds/Deletion in raw doc
  local suggestions_doc
  suggestions_doc=$(http_get "${DOCS_API_BASE}/${doc_id}?suggestionsViewMode=SUGGESTIONS_INLINE" "$token")
  local sug_count
  sug_count=$(echo "$suggestions_doc" | jq '
    [.. | objects | select(has("suggestedInsertionIds") or has("suggestedDeletionIds"))] | length
  ')

  # Export as markdown for content
  local content
  content=$(curl -sf -H "Authorization: Bearer ${token}" \
    "${DOCS_DRIVE_BASE}/${doc_id}/export?mimeType=$(urlencode 'text/markdown')" 2>/dev/null) || \
    content=$(http_get "${DOCS_DRIVE_BASE}/${doc_id}/export?mimeType=$(urlencode 'text/plain')" "$token")

  ok_json "$(jq -n \
    --arg did "$doc_id" \
    --arg title "$(echo "$doc" | jq -r '.title // ""')" \
    --arg url "https://docs.google.com/document/d/${doc_id}/edit" \
    --arg rev "$(echo "$doc" | jq -r '.revisionId // ""')" \
    --argjson sc "$sug_count" \
    --arg content "$content" \
    '{"documentId":$did,"title":$title,"url":$url,"revisionId":$rev,"suggestionsCount":$sc,"content":$content}')"
}

docs_create() {
  local title="$1" body="${2:-}"
  local token
  token=$(get_token "docs")

  if [[ -z "$body" ]]; then
    # Empty doc via Docs API
    local resp
    resp=$(http_post "$DOCS_API_BASE" "$token" "$(jq -n --arg t "$title" '{"title":$t}')")
    ok_json "$(echo "$resp" | jq --arg t "$title" '{
      documentId: .documentId,
      title: (.title // $t),
      url: ("https://docs.google.com/document/d/" + .documentId + "/edit")
    }')"
    return
  fi

  # Convert markdown to HTML and upload via multipart
  # Basic inline markdown->html conversion in bash (covers common cases)
  local html
  html=$(echo "$body" | awk '
  BEGIN { in_list=0; in_code=0 }
  /^```/ {
    if (in_code) { print "</pre>"; in_code=0 }
    else {
      if (in_list) { print "</ul>"; in_list=0 }
      print "<pre>"; in_code=1
    }
    next
  }
  in_code { gsub(/&/,"\\&amp;"); gsub(/</,"\\&lt;"); gsub(/>/,"\\&gt;"); print; next }
  /^[[:space:]]*$/ {
    if (in_list) { print "</ul>"; in_list=0 }
    next
  }
  /^######[[:space:]]/ { if(in_list){print "</ul>";in_list=0}; sub(/^######[[:space:]]*/,""); gsub(/&/,"\\&amp;"); print "<h6>"$0"</h6>"; next }
  /^#####[[:space:]]/  { if(in_list){print "</ul>";in_list=0}; sub(/^#####[[:space:]]*/,""); gsub(/&/,"\\&amp;"); print "<h5>"$0"</h5>"; next }
  /^####[[:space:]]/   { if(in_list){print "</ul>";in_list=0}; sub(/^####[[:space:]]*/,""); gsub(/&/,"\\&amp;"); print "<h4>"$0"</h4>"; next }
  /^###[[:space:]]/    { if(in_list){print "</ul>";in_list=0}; sub(/^###[[:space:]]*/,""); gsub(/&/,"\\&amp;"); print "<h3>"$0"</h3>"; next }
  /^##[[:space:]]/     { if(in_list){print "</ul>";in_list=0}; sub(/^##[[:space:]]*/,""); gsub(/&/,"\\&amp;"); print "<h2>"$0"</h2>"; next }
  /^#[[:space:]]/      { if(in_list){print "</ul>";in_list=0}; sub(/^#[[:space:]]*/,""); gsub(/&/,"\\&amp;"); print "<h1>"$0"</h1>"; next }
  /^[[:space:]]*[-*+][[:space:]]/ { if(!in_list){print "<ul>"; in_list=1}; sub(/^[[:space:]]*[-*+][[:space:]]*/,""); print "<li>"$0"</li>"; next }
  /^[[:space:]]*[0-9]+\.[[:space:]]/ { if(!in_list){print "<ul>"; in_list=1}; sub(/^[[:space:]]*[0-9]+\.[[:space:]]*/,""); print "<li>"$0"</li>"; next }
  { if(in_list){print "</ul>"; in_list=0}; print "<p>"$0"</p>" }
  END { if(in_list) print "</ul>" }
  ')

  local full_html="<!DOCTYPE html><html><head><meta charset='utf-8'><title>${title}</title></head><body>${html}</body></html>"

  local boundary="boundary_gdocs_hive_create"
  local metadata
  metadata=$(jq -n --arg t "$title" '{"name":$t,"mimeType":"application/vnd.google-apps.document"}')
  local tmp_body
  tmp_body=$(mktemp)
  {
    printf -- "--%s\r\n" "$boundary"
    printf "Content-Type: application/json; charset=UTF-8\r\n\r\n"
    echo "$metadata"
    printf "\r\n--%s\r\n" "$boundary"
    printf "Content-Type: text/html; charset=UTF-8\r\n\r\n"
    echo "$full_html"
    printf "\r\n--%s--" "$boundary"
  } > "$tmp_body"

  local url="${DOCS_DRIVE_UPLOAD}?uploadType=multipart&fields=id,name,webViewLink"
  local resp
  resp=$(http_post_multipart "$url" "$token" "$tmp_body" "$boundary")
  rm -f "$tmp_body"

  ok_json "$(echo "$resp" | jq '{documentId:.id,title:.name,url:.webViewLink}')"
}

docs_update() {
  local id_or_url="$1" markdown_body="$2" replace="${3:-false}"
  local doc_id
  doc_id=$(extract_file_id "$id_or_url")
  local token
  token=$(get_token "docs")

  local doc
  doc=$(http_get "${DOCS_API_BASE}/${doc_id}" "$token")
  local end_index
  end_index=$(echo "$doc" | jq '[.body.content[]? | .endIndex // 0] | max // 1 | . | floor')

  local requests_json="[]"

  if [[ "$replace" == "true" && "$end_index" -gt 2 ]]; then
    local del_end=$(( end_index - 1 ))
    requests_json=$(jq -n --argjson e "$del_end" '[{"deleteContentRange":{"range":{"startIndex":1,"endIndex":$e}}}]')
    end_index=1
  fi

  # Insert text line by line
  local insert_at=1
  [[ "$replace" != "true" ]] && insert_at=$(( end_index - 1 ))

  local lines_requests="[]"
  local current_index=$insert_at

  while IFS= read -r line || [[ -n "$line" ]]; do
    local insert_text="${line}\n"
    local text_len=${#insert_text}
    lines_requests=$(echo "$lines_requests" | jq \
      --arg text "${line}
" \
      --argjson idx "$current_index" \
      '. + [{"insertText":{"location":{"index":$idx},"text":$text}}]')
    current_index=$(( current_index + ${#line} + 1 ))
  done <<< "$markdown_body"

  local all_requests
  all_requests=$(echo "$requests_json" | jq --argjson lr "$lines_requests" '. + $lr')

  local count
  count=$(echo "$all_requests" | jq 'length')
  if [[ "$count" -eq 0 ]]; then
    ok_json "$(jq -n --arg did "$doc_id" '{"documentId":$did,"message":"No content to update"}')"
    return
  fi

  local batch_body
  batch_body=$(jq -n --argjson r "$all_requests" '{"requests":$r}')
  local resp
  resp=$(http_post "${DOCS_API_BASE}/${doc_id}:batchUpdate" "$token" "$batch_body")
  ok_json "$(echo "$resp" | jq \
    --arg did "$doc_id" \
    --arg title "$(echo "$doc" | jq -r '.title // ""')" \
    --argjson c "$count" \
    '{documentId:(.documentId//$did),title:$title,url:("https://docs.google.com/document/d/"+(.documentId//$did)+"/edit"),updatesApplied:$c}')"
}

docs_list() {
  local limit="${1:-10}"
  local token
  token=$(get_token "docs")
  local params
  params="q=$(urlencode "mimeType='application/vnd.google-apps.document' and trashed=false")&orderBy=modifiedTime+desc&pageSize=${limit}&fields=files(id,name,modifiedTime,createdTime,webViewLink,owners)"
  local resp
  resp=$(http_get "${DOCS_DRIVE_BASE}?${params}" "$token")
  local docs
  docs=$(echo "$resp" | jq '[.files[]? | {
    documentId: .id,
    title: (.name // ""),
    modifiedTime: (.modifiedTime // ""),
    createdTime: (.createdTime // ""),
    url: (.webViewLink // ""),
    owner: (if (.owners|length)>0 then .owners[0].emailAddress else "" end)
  }]')
  ok_json "$(jq -n --argjson d "$docs" --argjson c "$(echo "$docs" | jq 'length')" '{"count":$c,"documents":$d}')"
}

docs_search() {
  local query="$1" limit="${2:-10}"
  local token
  token=$(get_token "docs")
  local q="mimeType='application/vnd.google-apps.document' and trashed=false and (name contains '${query}' or fullText contains '${query}')"
  local params
  params="q=$(urlencode "$q")&orderBy=modifiedTime+desc&pageSize=${limit}&fields=files(id,name,modifiedTime,createdTime,webViewLink,owners)"
  local resp
  resp=$(http_get "${DOCS_DRIVE_BASE}?${params}" "$token")
  local docs
  docs=$(echo "$resp" | jq '[.files[]? | {
    documentId: .id,
    title: (.name // ""),
    modifiedTime: (.modifiedTime // ""),
    createdTime: (.createdTime // ""),
    url: (.webViewLink // ""),
    owner: (if (.owners|length)>0 then .owners[0].emailAddress else "" end)
  }]')
  ok_json "$(jq -n --arg q "$query" --argjson d "$docs" --argjson c "$(echo "$docs" | jq 'length')" \
    '{"query":$q,"count":$c,"documents":$d}')"
}

docs_export() {
  local id_or_url="$1" fmt="${2:-md}" output="${3:-}"
  local doc_id
  doc_id=$(extract_file_id "$id_or_url")
  local token
  token=$(get_token "docs")

  local mime
  mime=$(_docs_export_mime "$fmt")
  [[ -z "$mime" ]] && err_json "Unsupported format: ${fmt}. Supported: md txt html pdf docx epub"

  local url="${DOCS_DRIVE_BASE}/${doc_id}/export?mimeType=$(urlencode "$mime")"

  case "$fmt" in
    pdf|docx|epub)
      # Binary: write to file or stdout
      if [[ -n "$output" ]]; then
        http_download "$url" "$token" "$output"
        ok_json "$(jq -n --arg did "$doc_id" --arg f "$fmt" --arg o "$output" \
          '{"documentId":$did,"format":$f,"outputPath":$o}')"
      else
        # Stream binary to stdout — caller should redirect
        curl -sf -H "Authorization: Bearer ${token}" "$url"
        exit 0
      fi
      ;;
    md)
      local content
      content=$(curl -sf -H "Authorization: Bearer ${token}" "$url" 2>/dev/null) || {
        local fallback="${DOCS_DRIVE_BASE}/${doc_id}/export?mimeType=$(urlencode 'text/plain')"
        content=$(http_get "$fallback" "$token")
      }
      ok_json "$(jq -n --arg did "$doc_id" --arg f "$fmt" --arg c "$content" \
        '{"documentId":$did,"format":$f,"content":$c}')"
      ;;
    *)
      local content
      content=$(http_get "$url" "$token")
      ok_json "$(jq -n --arg did "$doc_id" --arg f "$fmt" --arg c "$content" \
        '{"documentId":$did,"format":$f,"content":$c}')"
      ;;
  esac
}

# ---------------------------------------------------------------------------
# GMAIL
# ---------------------------------------------------------------------------

GMAIL_BASE="https://gmail.googleapis.com/gmail/v1/users/me"

_gmail_call() {
  local endpoint="$1" method="${2:-GET}" body="${3:-}"
  local token
  token=$(get_token "gmail")
  local url="${GMAIL_BASE}/${endpoint}"

  if [[ "$method" == "DELETE" ]]; then
    local code
    code=$(curl -sf -X DELETE \
      -H "Authorization: Bearer ${token}" \
      -o /dev/null \
      -w "%{http_code}" \
      "$url" 2>/dev/null || echo "000")
    if [[ "$code" =~ ^2 ]] || [[ "$code" == "204" ]]; then
      echo "{}"
      return
    fi
    err_json "DELETE ${url} failed with HTTP ${code}"
  fi

  if [[ -n "$body" ]]; then
    curl -sf -X "$method" \
      -H "Authorization: Bearer ${token}" \
      -H "Content-Type: application/json" \
      -d "$body" \
      "$url" || err_json "Gmail API ${method} ${endpoint} failed"
  else
    curl -sf -X "$method" \
      -H "Authorization: Bearer ${token}" \
      "$url" || err_json "Gmail API GET ${endpoint} failed"
  fi
}

_gmail_msg_headers() {
  # $1 = message JSON, extract From/To/Subject/Date
  echo "$1" | jq '{
    id: .id,
    from: ((.payload.headers // []) | map(select(.name == "From")) | .[0].value // ""),
    to:   ((.payload.headers // []) | map(select(.name == "To"))   | .[0].value // ""),
    subject: ((.payload.headers // []) | map(select(.name == "Subject")) | .[0].value // ""),
    date:    ((.payload.headers // []) | map(select(.name == "Date"))    | .[0].value // ""),
    snippet: (.snippet // ""),
    labels:  (.labelIds // [])
  }'
}

_gmail_extract_body() {
  # Extract text/plain body from payload using jq recursion
  echo "$1" | jq -r '
    def extract:
      if .mimeType == "text/plain" and (.body.data? // "" | length) > 0
      then .body.data | gsub("-";"+") | gsub("_";"/") | @base64d
      elif .parts? then (.parts[] | extract) // ""
      else ""
      end;
    .payload | extract // (.payload.body.data? // "" | if length > 0 then gsub("-";"+") | gsub("_";"/") | @base64d else "" end)
  '
}

_build_raw_email() {
  local to="$1" subject="$2" body="$3"
  local raw
  raw="To: ${to}\r\nSubject: ${subject}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n${body}"
  # base64url encode
  printf '%s' "$(printf '%b' "$raw")" | base64 | tr '+/' '-_' | tr -d '='
}

gmail_list() {
  local limit="${1:-10}" query="${2:-}" unread_only="${3:-false}"
  local q="in:inbox"
  [[ "$unread_only" == "true" ]] && q="${q} is:unread"
  [[ -n "$query" ]] && q="$query"

  local resp
  resp=$(_gmail_call "messages?q=$(urlencode "$q")&maxResults=${limit}")
  local msgs
  msgs=$(echo "$resp" | jq -r '.messages[]?.id // empty')

  local detailed="[]"
  while IFS= read -r msg_id; do
    [[ -z "$msg_id" ]] && continue
    local detail
    detail=$(_gmail_call "messages/${msg_id}?format=metadata&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Subject&metadataHeaders=Date")
    local item
    item=$(echo "$detail" | jq '{
      id: .id,
      from: ((.payload.headers // []) | map(select(.name == "From")) | .[0].value // ""),
      to:   ((.payload.headers // []) | map(select(.name == "To"))   | .[0].value // ""),
      subject: ((.payload.headers // []) | map(select(.name == "Subject")) | .[0].value // ""),
      date:    ((.payload.headers // []) | map(select(.name == "Date"))    | .[0].value // ""),
      snippet: (.snippet // ""),
      labels: (.labelIds // [])
    }')
    detailed=$(echo "$detailed" | jq --argjson i "$item" '. + [$i]')
  done <<< "$msgs"

  ok_json "$(jq -n --argjson d "$detailed" --argjson c "$(echo "$detailed" | jq 'length')" --arg q "$q" \
    '{"count":$c,"query":$q,"messages":$d}')"
}

gmail_search() {
  local query="$1" limit="${2:-10}"
  local resp
  resp=$(_gmail_call "messages?q=$(urlencode "$query")&maxResults=${limit}")
  local msgs
  msgs=$(echo "$resp" | jq -r '.messages[]?.id // empty')

  local detailed="[]"
  while IFS= read -r msg_id; do
    [[ -z "$msg_id" ]] && continue
    local detail
    detail=$(_gmail_call "messages/${msg_id}?format=metadata&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Subject&metadataHeaders=Date")
    local item
    item=$(echo "$detail" | jq '{
      id: .id,
      from: ((.payload.headers // []) | map(select(.name == "From")) | .[0].value // ""),
      to:   ((.payload.headers // []) | map(select(.name == "To"))   | .[0].value // ""),
      subject: ((.payload.headers // []) | map(select(.name == "Subject")) | .[0].value // ""),
      date:    ((.payload.headers // []) | map(select(.name == "Date"))    | .[0].value // ""),
      snippet: (.snippet // ""),
      labels: (.labelIds // [])
    }')
    detailed=$(echo "$detailed" | jq --argjson i "$item" '. + [$i]')
  done <<< "$msgs"

  ok_json "$(jq -n --argjson d "$detailed" --argjson c "$(echo "$detailed" | jq 'length')" --arg q "$query" \
    '{"count":$c,"query":$q,"messages":$d}')"
}

gmail_read() {
  local message_id="$1"
  local resp
  resp=$(_gmail_call "messages/${message_id}?format=full")

  local body
  body=$(_gmail_extract_body "$resp")

  ok_json "$(echo "$resp" | jq \
    --arg body "$body" \
    '{
      id: .id,
      threadId: .threadId,
      from:    ((.payload.headers // []) | map(select(.name == "From"))    | .[0].value // ""),
      to:      ((.payload.headers // []) | map(select(.name == "To"))      | .[0].value // ""),
      subject: ((.payload.headers // []) | map(select(.name == "Subject")) | .[0].value // ""),
      date:    ((.payload.headers // []) | map(select(.name == "Date"))    | .[0].value // ""),
      labels: (.labelIds // []),
      body: $body
    }')"
}

gmail_draft() {
  local to="$1" subject="$2" body="$3"
  [[ -z "$subject" ]] && err_json "subject is required"
  local encoded
  encoded=$(_build_raw_email "$to" "$subject" "$body")
  local req_body
  req_body=$(jq -n --arg r "$encoded" '{"message":{"raw":$r}}')
  local resp
  resp=$(_gmail_call "drafts" "POST" "$req_body")
  ok_json "$(echo "$resp" | jq '{draftId:.id,messageId:.message.id}')"
}

gmail_draft_update() {
  local draft_id="$1" to="${2:-}" subject="${3:-}" body="${4:-}"

  # Get existing draft to fill missing fields
  local existing
  existing=$(_gmail_call "drafts/${draft_id}")
  local ex_to ex_subject ex_body
  ex_to=$(echo "$existing" | jq -r '.message.payload.headers // [] | map(select(.name == "To")) | .[0].value // ""')
  ex_subject=$(echo "$existing" | jq -r '.message.payload.headers // [] | map(select(.name == "Subject")) | .[0].value // ""')
  ex_body=$(_gmail_extract_body "$(echo "$existing" | jq '.message')")

  [[ -z "$to" ]] && to="$ex_to"
  [[ -z "$subject" ]] && subject="$ex_subject"
  [[ -z "$body" ]] && body="$ex_body"

  local encoded
  encoded=$(_build_raw_email "$to" "$subject" "$body")
  local req_body
  req_body=$(jq -n --arg r "$encoded" '{"message":{"raw":$r}}')
  local resp
  resp=$(_gmail_call "drafts/${draft_id}" "PUT" "$req_body")
  ok_json "$(echo "$resp" | jq '{draftId:.id,messageId:.message.id}')"
}

gmail_draft_delete() {
  local draft_id="$1"
  _gmail_call "drafts/${draft_id}" "DELETE" > /dev/null
  ok_json "$(jq -n --arg id "$draft_id" '{"draftId":$id,"deleted":true}')"
}

gmail_drafts_list() {
  local limit="${1:-10}"
  local resp
  resp=$(_gmail_call "drafts?maxResults=${limit}")

  local drafts="[]"
  while IFS= read -r draft_id; do
    [[ -z "$draft_id" ]] && continue
    local detail
    detail=$(_gmail_call "drafts/${draft_id}")
    local message
    message=$(echo "$detail" | jq '.message')
    local item
    item=$(echo "$detail" | jq '{
      id: .id,
      messageId: .message.id,
      threadId: .message.threadId,
      to: ((.message.payload.headers // []) | map(select(.name == "To")) | .[0].value // ""),
      subject: ((.message.payload.headers // []) | map(select(.name == "Subject")) | .[0].value // ""),
      snippet: (.message.snippet // "")
    }')
    drafts=$(echo "$drafts" | jq --argjson i "$item" '. + [$i]')
  done <<< "$(echo "$resp" | jq -r '.drafts[]?.id // empty')"

  ok_json "$(jq -n --argjson d "$drafts" --argjson c "$(echo "$drafts" | jq 'length')" '{"count":$c,"drafts":$d}')"
}

gmail_send() {
  local to="$1" subject="$2" body="$3"
  [[ -z "$subject" ]] && err_json "subject is required"
  local encoded
  encoded=$(_build_raw_email "$to" "$subject" "$body")
  local req_body
  req_body=$(jq -n --arg r "$encoded" '{"raw":$r}')
  local resp
  resp=$(_gmail_call "messages/send" "POST" "$req_body")
  ok_json "$(echo "$resp" | jq '{messageId:.id,threadId:.threadId}')"
}

gmail_labels() {
  local resp
  resp=$(_gmail_call "labels")
  local labels
  labels=$(echo "$resp" | jq '[.labels[]? | {id:.id,name:.name,type:(.type//"user")}]')
  ok_json "$(jq -n --argjson l "$labels" '{"labels":$l}')"
}

gmail_create_label() {
  local name="$1"
  local body
  body=$(jq -n --arg n "$name" '{"name":$n,"labelListVisibility":"labelShow","messageListVisibility":"show"}')
  local resp
  resp=$(_gmail_call "labels" "POST" "$body")
  ok_json "$(echo "$resp" | jq '{id:.id,name:.name}')"
}

gmail_apply_label() {
  local label_id="$1"
  shift
  local message_ids=("$@")
  local results="[]"
  for msg_id in "${message_ids[@]}"; do
    local body
    body=$(jq -n --arg lid "$label_id" '{"addLabelIds":[$lid]}')
    local r
    r=$(_gmail_call "messages/${msg_id}/modify" "POST" "$body" 2>/dev/null) && {
      results=$(echo "$results" | jq --arg id "$msg_id" '. + [{"messageId":$id,"success":true}]')
    } || {
      results=$(echo "$results" | jq --arg id "$msg_id" '. + [{"messageId":$id,"success":false}]')
    }
  done
  local successful
  successful=$(echo "$results" | jq '[.[] | select(.success)] | length')
  ok_json "$(jq -n \
    --arg lid "$label_id" \
    --argjson r "$results" \
    --argjson p "$(echo "$results" | jq 'length')" \
    --argjson s "$successful" \
    '{"labelId":$lid,"processed":$p,"successful":$s,"results":$r}')"
}

gmail_organize() {
  local label_name="$1" query="$2"
  # Find or create label
  local labels_resp label_id created="false"
  labels_resp=$(_gmail_call "labels")
  label_id=$(echo "$labels_resp" | jq -r --arg n "$label_name" \
    '.labels[]? | select(.name | ascii_downcase == ($n | ascii_downcase)) | .id' | head -1)

  if [[ -z "$label_id" ]]; then
    local new_label
    new_label=$(_gmail_call "labels" "POST" "$(jq -n --arg n "$label_name" '{"name":$n,"labelListVisibility":"labelShow","messageListVisibility":"show"}')")
    label_id=$(echo "$new_label" | jq -r '.id')
    created="true"
  fi

  local search_resp msg_ids
  search_resp=$(_gmail_call "messages?q=$(urlencode "$query")&maxResults=100")
  msg_ids=$(echo "$search_resp" | jq -r '.messages[]?.id // empty')

  if [[ -z "$msg_ids" ]]; then
    ok_json "$(jq -n \
      --arg ln "$label_name" \
      --arg lid "$label_id" \
      --arg c "$created" \
      --arg q "$query" \
      '{"labelName":$ln,"labelId":$lid,"labelCreated":($c=="true"),"query":$q,"messagesFound":0,"messagesLabeled":0}')"
    return
  fi

  local count=0
  while IFS= read -r msg_id; do
    [[ -z "$msg_id" ]] && continue
    _gmail_call "messages/${msg_id}/modify" "POST" \
      "$(jq -n --arg lid "$label_id" '{"addLabelIds":[$lid]}')" > /dev/null 2>&1 && (( count++ )) || true
  done <<< "$msg_ids"

  local found
  found=$(echo "$msg_ids" | grep -c '.' || true)
  ok_json "$(jq -n \
    --arg ln "$label_name" \
    --arg lid "$label_id" \
    --arg c "$created" \
    --arg q "$query" \
    --argjson found "$found" \
    --argjson labeled "$count" \
    '{"labelName":$ln,"labelId":$lid,"labelCreated":($c=="true"),"query":$q,"messagesFound":$found,"messagesLabeled":$labeled}')"
}

gmail_create_filter() {
  local label_name="$1" query="$2"
  # Find or create label
  local labels_resp label_id
  labels_resp=$(_gmail_call "labels")
  label_id=$(echo "$labels_resp" | jq -r --arg n "$label_name" \
    '.labels[]? | select(.name | ascii_downcase == ($n | ascii_downcase)) | .id' | head -1)

  if [[ -z "$label_id" ]]; then
    local new_label
    new_label=$(_gmail_call "labels" "POST" "$(jq -n --arg n "$label_name" '{"name":$n,"labelListVisibility":"labelShow","messageListVisibility":"show"}')")
    label_id=$(echo "$new_label" | jq -r '.id')
  fi

  # Parse query into criteria
  local criteria="{}"
  local from_val to_val subj_val
  from_val=$(echo "$query" | grep -oE 'from:([^ ]+)' | cut -d: -f2 | head -1)
  to_val=$(echo "$query" | grep -oE '\bto:([^ ]+)' | cut -d: -f2 | head -1)
  subj_val=$(echo "$query" | grep -oE 'subject:(.+?)( |$)' | sed 's/subject://' | head -1 | xargs)

  if [[ -n "$from_val" ]]; then
    criteria=$(jq -n --arg f "$from_val" '{"from":$f}')
  elif [[ -n "$to_val" ]]; then
    criteria=$(jq -n --arg t "$to_val" '{"to":$t}')
  elif [[ -n "$subj_val" ]]; then
    criteria=$(jq -n --arg s "$subj_val" '{"subject":$s}')
  else
    criteria=$(jq -n --arg q "$query" '{"query":$q}')
  fi

  local body
  body=$(jq -n --argjson c "$criteria" --arg lid "$label_id" \
    '{"criteria":$c,"action":{"addLabelIds":[$lid]}}')
  local resp
  resp=$(_gmail_call "settings/filters" "POST" "$body")
  ok_json "$(echo "$resp" | jq \
    --arg ln "$label_name" \
    --arg lid "$label_id" \
    --argjson crit "$criteria" \
    '{filterId:.id,labelName:$ln,labelId:$lid,criteria:$crit}')"
}

gmail_list_filters() {
  local resp
  resp=$(_gmail_call "settings/filters")
  local filters
  filters=$(echo "$resp" | jq '[.filter[]? | {id:.id,criteria:.criteria,action:.action}]')
  ok_json "$(jq -n --argjson f "$filters" '{"filters":$f}')"
}

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

usage() {
  cat <<EOF
google_handler.sh <service> <action> [options]

Services & Actions:
  auth   refresh                    Refresh OAuth token
  auth   status                     Check token validity

  calendar today [--calendar=id]
  calendar week  [--calendar=id]
  calendar list  [--days=7] [--calendar=id]
  calendar get   <event_id> [--calendar=id]
  calendar calendars
  calendar freebusy <start> <end>   YYYY-MM-DD dates
  calendar search <query> [--days=30] [--calendar=id]
  calendar create --summary=X --start=ISO --end=ISO [--desc=X] [--loc=X] [--calendar=id]
  calendar delete <event_id> [--calendar=id]

  drive list   [--limit=10] [--type=all|doc|sheet|pdf|folder] [--folder-id=X]
  drive search <query> [--limit=10] [--type=all]
  drive get    <id_or_url>
  drive download <id_or_url> [--output=path]
  drive upload <path> [--folder-id=X] [--name=X]
  drive mkdir  <name> [--parent=X]
  drive move   <file_id> <folder_id>
  drive share  <file_id> <email> [--role=reader|writer] [--allow-external]
  drive folders [--parent=X]

  docs read   <id_or_url> [--rich]
  docs create <title> [--body="md"] [--body-stdin]
  docs update <id_or_url> --body="md" [--replace] [--body-stdin]
  docs list   [--limit=10]
  docs search <query> [--limit=10]
  docs export <id_or_url> [--format=md|txt|html|pdf|docx|epub] [--output=path]

  gmail list   [--query=X] [--max=10] [--unread]
  gmail read   <message_id>
  gmail send   <to> <subject> <body>
  gmail draft  <to> <subject> <body>
  gmail draft-update  <draft_id> [--to=X] [--subject=X] [--body=X] [--body-stdin]
  gmail draft-delete  <draft_id>
  gmail drafts [--max=10]
  gmail search <query> [--max=10]
  gmail labels
  gmail create-label <name>
  gmail apply-label  <label_id> <msg_id>...
  gmail organize     <label_name> <query>
  gmail create-filter <label_name> <query>
  gmail list-filters

Env vars (in hive/.env):
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
  Per-service overrides: GOOGLE_CALENDAR_REFRESH_TOKEN, GOOGLE_DRIVE_REFRESH_TOKEN,
                         GOOGLE_DOCS_REFRESH_TOKEN, GMAIL_REFRESH_TOKEN
  Fallbacks: GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET
EOF
}

main() {
  local service="${1:-}"
  local action="${2:-}"

  [[ -z "$service" ]] && { usage; exit 1; }

  # Parse remaining args into positional array and --flag=value map
  shift 2 2>/dev/null || shift $#
  declare -A FLAGS
  POSITIONAL=()
  for arg in "$@"; do
    if [[ "$arg" == --* ]]; then
      local key="${arg%%=*}"
      local val="${arg#*=}"
      key="${key#--}"
      # normalize hyphens to underscores
      key="${key//-/_}"
      if [[ "$arg" == "$key" || "$arg" == "--${key}" ]]; then
        FLAGS["$key"]="true"
      else
        FLAGS["$key"]="$val"
      fi
    else
      POSITIONAL+=("$arg")
    fi
  done

  flag() { echo "${FLAGS[$1]:-}"; }
  pos()  { echo "${POSITIONAL[$1]:-}"; }

  case "$service" in
    auth)
      case "$action" in
        refresh) cmd_auth_refresh ;;
        status)  cmd_auth_status ;;
        *) err_json "Unknown auth action: ${action}" ;;
      esac
      ;;

    calendar)
      case "$action" in
        today)     calendar_today "$(flag calendar)" ;;
        week)      calendar_week  "$(flag calendar)" ;;
        list)      calendar_list  "$(flag calendar)" "$(flag days)" ;;
        get)       calendar_get   "$(pos 0)" "$(flag calendar)" ;;
        calendars) calendar_calendars ;;
        freebusy)  calendar_freebusy "$(pos 0)" "$(pos 1)" ;;
        search)    calendar_search "$(pos 0)" "$(flag calendar)" "$(flag days)" ;;
        create)
          calendar_create \
            "$(flag summary)" \
            "$(flag start)" \
            "$(flag end)" \
            "$(flag desc)" \
            "$(flag loc)" \
            "$(flag calendar)"
          ;;
        delete)    calendar_delete "$(pos 0)" "$(flag calendar)" ;;
        *) err_json "Unknown calendar action: ${action}" ;;
      esac
      ;;

    drive)
      case "$action" in
        list)     drive_list "$(flag limit)" "$(flag type)" "$(flag folder_id)" ;;
        search)   drive_search "$(pos 0)" "$(flag limit)" "$(flag type)" ;;
        get)      drive_get "$(pos 0)" ;;
        download) drive_download "$(pos 0)" "$(flag output)" ;;
        upload)   drive_upload "$(pos 0)" "$(flag folder_id)" "$(flag name)" ;;
        mkdir)    drive_mkdir "$(pos 0)" "$(flag parent)" ;;
        move)     drive_move "$(pos 0)" "$(pos 1)" ;;
        share)    drive_share "$(pos 0)" "$(pos 1)" "$(flag role)" "$(flag allow_external)" ;;
        folders)  drive_folders "$(flag parent)" ;;
        *) err_json "Unknown drive action: ${action}" ;;
      esac
      ;;

    docs)
      case "$action" in
        read)
          local rich="${FLAGS[rich]:-false}"
          if [[ "$rich" == "true" ]]; then
            docs_read_rich "$(pos 0)"
          else
            docs_read "$(pos 0)"
          fi
          ;;
        create)
          local body_content=""
          if [[ "${FLAGS[body_stdin]:-false}" == "true" ]] || \
             { [[ -z "${FLAGS[body]:-}" ]] && ! tty -s 2>/dev/null; }; then
            body_content=$(cat -)
          else
            body_content="${FLAGS[body]:-}"
          fi
          docs_create "$(pos 0)" "$body_content"
          ;;
        update)
          local body_content=""
          if [[ "${FLAGS[body_stdin]:-false}" == "true" ]] || \
             { [[ -z "${FLAGS[body]:-}" ]] && ! tty -s 2>/dev/null; }; then
            body_content=$(cat -)
          else
            body_content="${FLAGS[body]:-}"
          fi
          docs_update "$(pos 0)" "$body_content" "${FLAGS[replace]:-false}"
          ;;
        list)   docs_list "$(flag limit)" ;;
        search) docs_search "$(pos 0)" "$(flag limit)" ;;
        export) docs_export "$(pos 0)" "$(flag format)" "$(flag output)" ;;
        *) err_json "Unknown docs action: ${action}" ;;
      esac
      ;;

    gmail)
      case "$action" in
        list)          gmail_list "$(flag max)" "$(flag query)" "$(flag unread)" ;;
        search)        gmail_search "$(pos 0)" "$(flag max)" ;;
        read)          gmail_read "$(pos 0)" ;;
        send)          gmail_send "$(pos 0)" "$(pos 1)" "$(pos 2)" ;;
        draft)         gmail_draft "$(pos 0)" "$(pos 1)" "$(pos 2)" ;;
        draft-update)
          local body_content="${FLAGS[body]:-}"
          if [[ "${FLAGS[body_stdin]:-false}" == "true" ]] || \
             { [[ -z "$body_content" ]] && ! tty -s 2>/dev/null; }; then
            body_content=$(cat -)
          fi
          gmail_draft_update "$(pos 0)" "$(flag to)" "$(flag subject)" "$body_content"
          ;;
        draft-delete)  gmail_draft_delete "$(pos 0)" ;;
        drafts)        gmail_drafts_list "$(flag max)" ;;
        labels)        gmail_labels ;;
        create-label)  gmail_create_label "$(pos 0)" ;;
        apply-label)
          local label_id="${POSITIONAL[0]}"
          local msg_ids=("${POSITIONAL[@]:1}")
          gmail_apply_label "$label_id" "${msg_ids[@]}"
          ;;
        organize)      gmail_organize "$(pos 0)" "$(pos 1)" ;;
        create-filter) gmail_create_filter "$(pos 0)" "$(pos 1)" ;;
        list-filters)  gmail_list_filters ;;
        *) err_json "Unknown gmail action: ${action}" ;;
      esac
      ;;

    help|--help|-h)
      usage
      ;;

    *)
      err_json "Unknown service: ${service}. Use: auth calendar drive docs gmail"
      ;;
  esac
}

main "$@"
