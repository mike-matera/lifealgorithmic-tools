
OUTPUTDIR = $(realpath ../source/_static)/code

html: pydist
	$(MAKE) -C cis191 html
	$(MAKE) -C cis194 html

pydist:
	python ./setup.py sdist -d $(OUTPUTDIR)/dist > /dev/null

clean:
	-rm -rf $(OUTPUTDIR)

.PHONY: html pydist clean $(SUBDIRS) cis191
