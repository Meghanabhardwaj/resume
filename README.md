# Aditya Jindal Resume

Welcome to my resume repository. This repository contains my resume written in TeX, with reusable section partials and a shared formatting layer for easier maintenance.

## Prerequisites

- [Docker](https://docs.docker.com/)
- [Git](https://git-scm.com/)
- [yq](https://github.com/mikefarah/yq)

## Contents

- [`main.tex`](./main.tex): The main TeX file for the resume.
- [`formatting.sty`](./formatting.sty): The shared style file for formatting and PDF metadata support.
- [`resume.yaml`](./resume.yaml): The single source of truth for resume content and metadata.
- [`scripts/generate_resume.py`](./scripts/generate_resume.py): Generates LaTeX partials and embedded JSON files from [`resume.yaml`](./resume.yaml).
- [`sections/`](./sections/): Generated TeX files for each resume section.
- [`schema.json`](./schema.json): Schema.org JSON-LD structured data embedded in the PDF.
- [`resume.json`](./resume.json): JSON Resume structured data embedded in the PDF for ATS parsers.

> [!NOTE]
> This repository uses a custom Docker image for compiling the resume, ensuring consistency and reproducibility across environments.

## How to Use

<p>1. <strong>Clone the repository</strong>:</p>

```sh
git clone git@github.com:adityaongit/resume.git
```

Or via HTTPS:

```sh
git clone https://github.com/adityaongit/resume.git
```

<p>2. <strong>Build the Docker image</strong>:</p>

```sh
docker build -t latex-builder .docker
```

<p>3. <strong>Generate the derived artifacts</strong>:</p>

```sh
make generate
```

<p>4. <strong>Compile the resume</strong>:</p>

```sh
docker run --rm -v "$(pwd):/data" latex-builder -jobname="Aditya_SWE_Resume_2YOE" main.tex
```

You can also use:

```sh
make compile
```

> [!NOTE]
> `make compile` and `make build` regenerate all derived artifacts automatically before compiling.

## Authoring Flow

Edit [`resume.yaml`](./resume.yaml) only.

Supported inline formatting inside prose fields such as bullets and achievements:

- `**bold**`
- `_italic_`
- `[label](https://example.com)`

Generated artifacts:

- [`sections/header.tex`](./sections/header.tex)
- [`sections/experience.tex`](./sections/experience.tex)
- [`sections/skills.tex`](./sections/skills.tex)
- [`sections/projects.tex`](./sections/projects.tex)
- [`sections/achievements.tex`](./sections/achievements.tex)
- [`sections/education.tex`](./sections/education.tex)
- [`generated/metadata.tex`](./generated/metadata.tex)
- [`resume.json`](./resume.json)
- [`schema.json`](./schema.json)

These files are regenerated automatically by `make compile` and `make build`. Do not edit them manually.

## Make Commands

Use the included `Makefile` targets for common workflows:

```sh
make help
```

Shows the available targets.

```sh
make generate
```

Regenerates the TeX partials and JSON metadata from [`resume.yaml`](./resume.yaml).

```sh
make docker
```

Builds the local Docker image used for LaTeX compilation.

```sh
make compile
```

Regenerates artifacts and compiles the resume PDF using the existing Docker image.

```sh
make build
```

Builds the Docker image and compiles the resume.

```sh
make clean
```

Removes generated PDF and LaTeX auxiliary files.

```sh
make dev
```

Cleans previous artifacts and recompiles the resume.

## Metadata

The compiled PDF contains embedded metadata across multiple standards, making it easier for ATS systems, semantic crawlers, and document parsers to consume:

| Standard           | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| XMP / Dublin Core  | Title, author, keywords, rights, language, and dates             |
| IPTC Core          | Contact email, URL, and address                                  |
| Schema.org JSON-LD | Person, occupation, education, projects, and skills metadata     |
| JSON Resume        | Open standard resume data for ATS-compatible parsing             |

Verify the PDF metadata after compiling:

```sh
exiftool -xmp:all Aditya_SWE_Resume_2YOE.pdf
```

List embedded attachments:

```sh
pdfdetach -list Aditya_SWE_Resume_2YOE.pdf
```

## Customization

- **Content**: Update [`resume.yaml`](./resume.yaml) and regenerate the derived files.
- **Formatting**: Modify [`formatting.sty`](./formatting.sty) to change appearance and layout.
- **Document wiring**: [`main.tex`](./main.tex) controls section order and PDF attachments.
- **Structured data**: [`resume.json`](./resume.json), [`schema.json`](./schema.json), and [`generated/metadata.tex`](./generated/metadata.tex) are derived from [`resume.yaml`](./resume.yaml).

## Releases

> [!IMPORTANT]
> GitHub Actions automatically builds and releases the resume on every push to `main`.

Download the latest compiled PDF from the [Releases](https://github.com/adityaongit/resume/releases/latest) page.

## License

This project is licensed under the Apache-2.0 License. See [`LICENSE`](./LICENSE) for details.
