# Makefile for JCAP submission
# Compile with: make pdf

pdf:
	pdflatex main.tex
	bibtex main
	pdflatex main.tex
	pdflatex main.tex

clean:
	rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lot *.lof

view:
	open main.pdf || xdg-open main.pdf || start main.pdf

all: clean pdf view

.PHONY: pdf clean view all