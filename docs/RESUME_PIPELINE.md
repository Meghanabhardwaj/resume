# Resume Pipeline — End-to-End Flow & Verification

This doc explains exactly how a change to `resume.yaml` reaches `adysfolio.vercel.app/resume`, how to verify each hop is healthy, and how to fix it when it isn't.

## The Pipeline

```
1. local edit (resume.yaml / formatting.sty)
       │
       ▼
2. git push origin main
       │
       ▼
3. GitHub Actions: .github/workflows/release.yml
       │  ├─ run scripts/generate_resume.py     → regenerate sections/*.tex, resume.json, schema.json
       │  ├─ build PDF in latex-builder Docker  → Aditya_SWE_Resume_2YOE.pdf
       │  ├─ create GitHub Release v<run_number> with the PDF attached
       │  └─ POST to portfolio /api/revalidate-resume   ← cache bust
       ▼
4. github.com/adityaongit/resume/releases/latest/download/Aditya_SWE_Resume_2YOE.pdf
       │  (always redirects to the asset on the latest release)
       ▼
5. adysfolio.vercel.app /api/resume → fetchResume() → fetch(GitHub URL)
       │  Two caches sit in front:
       │    - Next.js fetch cache (Vercel Data Cache)  tagged "resume", revalidate=3600
       │    - Vercel edge cache for the route          Cache-Control: public, max-age=3600
       ▼
6. browser → /resume page → <PdfViewer file="/api/resume">
```

## Required configuration (one-time)

| Where | Name | Type | Value |
|---|---|---|---|
| Resume GitHub repo, Settings → Variables | `PORTFOLIO_REVALIDATE_URL` | repository variable | `https://adysfolio.vercel.app/api/revalidate-resume` |
| Resume GitHub repo, Settings → Secrets | `PORTFOLIO_REVALIDATE_SECRET` | repository secret | random string (e.g. `openssl rand -hex 32`) |
| Vercel portfolio project, Settings → Env Vars | `RESUME_REVALIDATE_SECRET` | Production env var | **same** value as above |

The two `*_SECRET` values must match byte-for-byte. If they drift, the workflow's curl will get `401 Unauthorized` and the cache won't bust.

If `PORTFOLIO_REVALIDATE_URL` is empty, the workflow's revalidation step is skipped silently — it never breaks the build.

## Verifying the pipeline, hop by hop

### Hop 3 — did CI run, and did it succeed?

```bash
curl -s "https://api.github.com/repos/adityaongit/resume/actions/runs?per_page=3" \
  | python3 -c "import json,sys;[print(r['created_at'],r['status'],r['conclusion'],r['head_commit']['message'][:60]) for r in json.load(sys.stdin)['workflow_runs']]"
```

What you want: a `completed success` row whose timestamp is after your push. If it failed, open the run in the Actions tab; the most common failure is the TeX Live mirror going stale.

### Hop 4 — is the latest release the one CI just published?

```bash
curl -s "https://api.github.com/repos/adityaongit/resume/releases/latest" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['tag_name'],d['name'],d['published_at'])"
```

The `tag_name` should be `v<run_number>` of the run from the previous step.

### Hop 4 → 5 — does the redirect URL serve the right bytes?

```bash
curl -sIL "https://github.com/adityaongit/resume/releases/latest/download/Aditya_SWE_Resume_2YOE.pdf" \
  | grep -iE "etag|last-modified|content-length|location" | tail -6
```

Capture this `ETag` and `Last-Modified`; they're the source of truth.

### Hop 5 — is the website serving those same bytes?

```bash
curl -sI "https://adysfolio.vercel.app/api/resume" \
  | grep -iE "etag|last-modified|content-length|x-vercel-cache"
```

Compare ETag/Last-Modified against what GitHub returned. If they match, you're done. If not, the website is stale — go to the next section.

## Busting a stale cache manually

```bash
SECRET=$(security find-generic-password -a "$USER" -s "portfolio-revalidate-secret" -w)
curl -fsS -X POST "https://adysfolio.vercel.app/api/revalidate-resume" \
  -H "Authorization: Bearer $SECRET"
# Expected: {"ok":true,"revalidated":["resume"],"at":...}
```

(One-time setup of the keychain entry:
`security add-generic-password -a "$USER" -s "portfolio-revalidate-secret" -w "<paste secret>"`)

A successful response invalidates:

- `revalidateTag("resume")` — the upstream fetch cache
- `revalidatePath("/api/resume")` — the route's Vercel edge cache
- `revalidatePath("/api/resume/download")` — the download endpoint
- `revalidatePath("/resume")` — the page itself

After that, the very next request to the website refetches GitHub and re-caches the new bytes.

### What does **not** work

- **Hard refresh / incognito.** Both caches are server-side; the browser never sees them.
- **Empty Git commit + redeploy.** Vercel's Data Cache (where Next.js fetch results live) persists across deploys, so a rebuild does not invalidate the tagged fetch.
- **Waiting an hour.** It eventually does work, but only because `revalidate: 3600` triggers a stale-while-revalidate background refresh — not because the deploy refreshed anything.

## Standard editing workflow

1. Edit `resume.yaml` (use the `resume-bullets` skill for any new bullets).
2. `python3 scripts/generate_resume.py && make compile` — verify the PDF renders correctly. Hard rule: every project/role bullet must fit on one rendered line.
3. Commit in logical units and push to `main`.
4. Watch the Actions tab; CI should finish in 2–4 minutes.
5. Verify with the two `curl -sI` commands above that the website ETag matches GitHub.
6. If they match: done. If they don't, run the manual revalidate curl.

## Paths-filter on the workflow

The release workflow is path-filtered. Pushes touching only the following paths trigger a build:

```
**.tex   **.cls   **.sty   **.json   **.yaml   scripts/**   .docker/**
```

`README.md`, `CLAUDE.md`, `docs/**`, `.claude/**` do **not** trigger a build. That's intentional — these don't affect the PDF and shouldn't churn release tags.

## Troubleshooting cheat sheet

| Symptom | Likely cause | Fix |
|---|---|---|
| Push didn't fire CI | File path didn't match the path filter | Touch a `**.yaml` / `**.sty` / etc. file, push again |
| CI red on "Build Resume" | TeX Live mirror down or package missing | Update `.docker/Dockerfile` mirror; rebuild image |
| CI green but no new release | Path filter excluded *all* changed files | Same as the first row |
| Release URL serves old PDF | Looking at a specific tag, not `/latest/` | Use `releases/latest/download/...` |
| Website ETag != GitHub ETag | Vercel Data Cache hasn't invalidated | Run the manual revalidate curl |
| Manual curl returns 401 | Secret mismatch between Vercel and GH | Compare and re-set |
| Manual curl returns 500 | `RESUME_REVALIDATE_SECRET` not set on Vercel | Add env var, redeploy |
| Manual curl returns 200 but website still stale | The page itself is statically rendered and bypassing the route | Confirm with `x-vercel-cache: MISS` header; if it's HIT, also `revalidatePath("/")` |
