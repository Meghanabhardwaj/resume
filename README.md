# Aditya Jindal Resume

Welcome to my resume repository. This repository contains my resume written in TeX, with reusable section partials and a shared formatting layer for easier maintenance.

## Prerequisites

- [Docker](https://docs.docker.com/)
- [Git](https://git-scm.com/)

## Contents

- [`main.tex`](./main.tex): The main TeX file for the resume.
- [`formatting.sty`](./formatting.sty): The shared style file for formatting and PDF metadata support.
- [`sections/`](./sections/): Individual TeX files for each resume section.
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

<p>3. <strong>Compile the resume</strong>:</p>

```sh
docker run --rm -v "$(pwd):/data" latex-builder -jobname="Aditya_SWE_Resume_2YOE" main.tex
```

You can also use:

```sh
make build
```

> [!NOTE]
> `jobname` controls the output filename. Change it if you want a different PDF name.

## Make Commands

Use the included `Makefile` targets for common workflows:

```sh
make help
```

Shows the available targets.

```sh
make docker
```

Builds the local Docker image used for LaTeX compilation.

```sh
make compile
```

Compiles the resume PDF using the existing Docker image.

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

- **Content**: Update [`main.tex`](./main.tex) and the files in [`sections/`](./sections/).
- **Formatting**: Modify [`formatting.sty`](./formatting.sty) to change appearance and layout.
- **Structured data**: Update [`schema.json`](./schema.json) and [`resume.json`](./resume.json) to keep them aligned with the visible resume content.

## Releases

> [!IMPORTANT]
> GitHub Actions automatically builds and releases the resume on every push to `main`.

Download the latest compiled PDF from the [Releases](https://github.com/adityaongit/resume/releases/latest) page.

## License

This project is licensed under the Apache-2.0 License. See [`LICENSE`](./LICENSE) for details.
