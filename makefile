
OUTPUTDIR = $(realpath ../source)/code

all: pydist
	# $(MAKE) -C cis194 html

$(OUTPUTDIR):
	mkdir $(OUTPUTDIR) 

pydist: $(OUTPUTDIR)
	python ./setup.py sdist -d $(OUTPUTDIR)/dist > /dev/null

clean:
	-rm -rf $(OUTPUTDIR)

.PHONY: html pydist clean $(SUBDIRS) cis191
