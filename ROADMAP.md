# RePlayList — Roadmap

Status of this fork's work and what's planned next. This fork extends the
upstream project with a local library cache, multi-account support, and a
resumable, quota-aware Spotify→YouTube migration.

## Current capabilities

### CLI (`python backend/cli.py …`)
- `auth <spotify|youtube>` — OAuth login; tokens stored per account in `tokens.json`.
- `accounts [platform]` — list stored accounts with stats; `use <platform> <id>` — switch active account.
- `extract <platform> [--account]` / `update <platform> [--account]` — pull a full library to local JSON (`data/<platform>/<account_id>/`) and incrementally sync changes.
- `list` / `tracks` / `search` / `preview` / `transfer` — playlist inspection and cross-platform transfer.
- `yt-copy --from <id> --to <id> --playlist <id>` — copy a playlist between two YouTube accounts (direct video-id copy).
- `migrate --source-account <sp> --target-account <yt> [--max-units N] [--limit N]` — resumable, quota-budgeted migration of all Spotify playlists to a YouTube account.

### Under the hood
- **Token auto-refresh** — access tokens are renewed from the refresh token before any token-using command (no browser re-auth needed day to day).
- **Match cache** (`data/cache/match_cache.json`) — global Spotify-id → YouTube-id mapping; cache hits skip the (expensive) YouTube search. Positives kept forever, negatives expire after 30 days.
- **Candidate scoring** — the YouTube matcher scores up to 50 search candidates by title/artist instead of taking the first result.
- **Artist channel resolution** (`data/cache/artist_channels.json`) — for frequent artists, resolve their "Artist - Topic" channel once and match their tracks against the channel's uploads locally (amortizing searches).
- **Quota budget** — `migrate` spends an estimated quota-unit budget per run (`--max-units`, default 9500 of 10,000/day).
- **Resumable state** (`data/migrations/*.json`) — progress is persisted per playlist; runs continue where they left off and never duplicate.

### Automation
- A Windows scheduled task (`RePlayList-Migrate`) runs `migrate` daily, surviving reboots and retrying on failure.

## Roadmap / TODO

### 1. Sync app (replace the Windows scheduled task) — primary
Turn the migration into a first-class app instead of an OS scheduled task:
- Internal scheduler/daemon, or drive it through the existing **SvelteKit frontend + FastAPI backend**.
- **Dashboard** showing, **per account** (Spotify and each YouTube account): number of playlists and number of tracks/items.
- **Sync status**: percent complete, in-progress / remaining, last run time, estimated quota units spent, and errors.
- Read from `data/migrations/*.json` and the local extracts.
- Integrate token refresh and surface the (currently weekly) YouTube re-auth prompt in-app.

### 2. Shared / hosted match cache
A community/hosted Spotify-id → YouTube-id mapping consulted before spending any API quota, with validation of returned video ids (handle deleted/region-blocked) and coverage limits for niche tracks.

### 3. Duration-based scoring
Use track duration to disambiguate YouTube candidates (requires an extra `videos.list?part=contentDetails` call, so weigh the added quota cost).

## Notes / known constraints
- The Google OAuth app is in **Testing** mode: YouTube refresh tokens expire ~7 days, so YouTube needs a manual `auth youtube` roughly weekly until the app is verified/published.
- Spotify restricted `GET /playlists/{id}/tracks` (403); the code uses `GET /playlists/{id}/items`.
- YouTube quota is 10,000 units/day; an insert costs ~50, so the practical floor is ~200 tracks/day even with searches fully optimized away.
