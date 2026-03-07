# Aditya Jindal Resume

This repository contains my resume in LaTeX, organized into reusable section partials and a shared formatting layer for easier maintenance.

## Prerequisites

- [Docker](https://docs.docker.com/)
- [Git](https://git-scm.com/)

## Repository Layout

- [`main.tex`](./main.tex): Entry point for the resume.
- [`formatting.sty`](./formatting.sty): Shared styling and layout helpers.
- [`sections/`](./sections/): Section-wise content files.
- [`schema.json`](./schema.json): Structured resume metadata in Schema.org JSON-LD format.
- [`resume.json`](./resume.json): Resume data in JSON Resume format.

## Usage

Clone the repository:

```sh
git clone git@github.com:adityaongit/resume.git
```

Or via HTTPS:

```sh
git clone https://github.com/adityaongit/resume.git
```

Build the Docker image:

```sh
docker build -t latex-builder .docker
```

Compile the resume:

```sh
docker run --rm -v "$(pwd):/data" latex-builder -jobname="Aditya_SWE_Resume_2YOE" main.tex
```

You can also use:

```sh
make build
```

## Output

The compiled PDF is generated as `Aditya_SWE_Resume_2YOE.pdf`.

## Customization

- Update content in [`sections/`](./sections/).
- Adjust styling in [`formatting.sty`](./formatting.sty).
- Keep [`resume.json`](./resume.json) and [`schema.json`](./schema.json) aligned with the visible resume content.

## Releases

GitHub Actions builds and releases the resume from `main`.

Latest release:

https://github.com/adityaongit/resume/releases/latest

## License

Licensed under Apache-2.0. See [`LICENSE`](./LICENSE).
