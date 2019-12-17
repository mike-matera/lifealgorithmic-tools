
OUTPUTDIR = $(realpath ../../source/_static)/code/cis191

BOXES = cis-191/Vagrantfile fedora-desktop-disks/Vagrantfile
BOX_TARGETS = $(addprefix $(OUTPUTDIR)/, $(BOXES))

html: $(BOX_TARGETS)

$(OUTPUTDIR)/%: %
	mkdir -p $(dir $@)
	cp $* $@

clean:
	echo "Nothing to clean"

.PHONY: html clean
