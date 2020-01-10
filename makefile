
OUTPUTDIR ?= $(realpath .)

all: pydist 

pydist: $(OUTPUTDIR)
	python ./setup.py sdist -d $(OUTPUTDIR)/dist > /dev/null

.PHONY: all pydist 
