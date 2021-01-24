all: proj2.pdf
proj2.dvi: proj2.tex
	latex proj2.tex

proj2.ps: proj2.dvi
	dvips proj2.dvi

proj2.pdf: proj2.ps
	ps2pdf proj2.ps

.PHONY: clean
clean:
	rm -fr *.aux *.log *.tex# *.ps *.dvi *.out