
OUTPUTDIR ?= $(realpath .)

all: pydist 

pydist: $(OUTPUTDIR)
	python3 ./setup.py sdist -d $(OUTPUTDIR)/dist > /dev/null

.PHONY: all pydist 
