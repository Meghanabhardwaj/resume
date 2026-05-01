.PHONY: build clean compile dev docker generate help

RESUME_JOBNAME ?= Meghana_SWE_Resume_2YOE

help:
	@echo "Available targets:"
	@echo "  generate   - Generate TeX partials and JSON metadata from resume.yaml"
	@echo "  build      - Build Docker image and compile resume"
	@echo "  compile    - Compile resume only (requires Docker image)"
	@echo "  docker     - Build Docker image only"
	@echo "  clean      - Remove generated PDF files"
	@echo "  dev        - Clean and recompile the resume"

build: docker compile

docker:
	docker build -t latex-builder .docker

generate:
	python3 scripts/generate_resume.py

compile: generate
	docker run --rm -v "$(PWD):/data" latex-builder -jobname="$(RESUME_JOBNAME)" main.tex

clean:
	rm -f *.pdf *.aux *.log *.out

dev:
	make clean && make compile
