
OUTPUTDIR ?= $(realpath .)

all: pydist 

pydist: $(OUTPUTDIR)
	python3 ./setup.py sdist -d $(OUTPUTDIR)/dist > /dev/null

clean:
	-rm -rf ./dist

.PHONY: all pydist clean
