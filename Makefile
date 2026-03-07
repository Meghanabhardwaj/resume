.PHONY: build clean help

help:
	@echo "Available targets:"
	@echo "  build      - Build Docker image and compile resume"
	@echo "  compile    - Compile resume only (requires Docker image)"
	@echo "  docker     - Build Docker image only"
	@echo "  clean      - Remove generated PDF files"

build: docker compile

docker:
	docker build -t latex-builder .docker

compile:
	docker run --rm -v "$(PWD):/data" latex-builder -jobname="Aditya_SWE_Resume_2YOE" main.tex

clean:
	rm -f *.pdf *.aux *.log *.out

dev:
	make clean && make compile
