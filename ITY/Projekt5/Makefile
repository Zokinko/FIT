PROJ=proj5

.PHONY: pdflatex

$(PROJ).pdf: $(PROJ).ps
	ps2pdf $^


$(PROJ).ps: $(PROJ).dvi
	dvips $^


$(PROJ).dvi: $(PROJ).tex
	latex $^
	latex $^


pdflatex: $(PROJ).tex
	pdflatex $^
	pdflatex $^