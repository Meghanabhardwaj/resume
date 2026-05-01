# Resume Workflow Guide

A plain-English reminder of how this repo turns a YAML file into a PDF resume.

## Source of truth: `resume.yaml`

**Only edit `resume.yaml`.** Everything else is generated. The `sections/*.tex` files and `resume.json` are *outputs* — if you edit them by hand, your changes get overwritten the next time you run `make generate`.

## What gets generated from it

`scripts/generate_resume.py` reads `resume.yaml` and writes:

- `sections/header.tex`, `experience.tex`, `skills.tex`, `projects.tex`, `education.tex`, `achievements.tex` — the LaTeX partials
- `generated/metadata.tex` — build metadata
- `resume.json` — a JSON mirror of the resume (used by the web editor / for machine-readable consumption)

`main.tex` is the LaTeX entry point that `\input`s those section files. `formatting.sty` is the styling.

## What the other files are

- `app.py` + `static/` — the Flask web editor UI (`docker-compose.yml` runs it)
- `schema.json` / `editor_schema.json` — JSON Schema describing the YAML structure, used by the editor for validation
- `Dockerfile` (in `.docker/`) — the LaTeX-builder image used to compile the PDF

## The Make targets, in plain English

| Command | What it does |
|---|---|
| `make generate` | YAML → tex partials + resume.json. No PDF yet. |
| `make docker` | Builds the LaTeX-builder Docker image (one-time, or after Dockerfile changes). |
| `make compile` | Runs `generate`, then runs the Docker image to compile `main.tex` → `Meghana_SWE_Resume_2YOE.pdf`. |
| `make build` | `docker` + `compile` — full first-time setup. |
| `make dev` | `clean` + `compile` — your normal "I edited the YAML, give me a fresh PDF" command. |
| `make clean` | Deletes the PDF and LaTeX aux files. |
| `make help` | Prints the list. |

## Typical loop

1. Edit `resume.yaml` (or use the web editor, which writes the YAML for you).
2. Run `make dev`.
3. Open `Meghana_SWE_Resume_2YOE.pdf`.

The reason there are "so many" commands is just decomposition: `build` = first time, `dev` = day-to-day, and the others (`generate`, `compile`, `docker`, `clean`) are the individual steps exposed so you can run them in isolation when debugging.
