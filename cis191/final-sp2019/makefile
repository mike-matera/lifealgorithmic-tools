
all: install

install: final-sp2019
	mkdir -p ../../static/boxes/cis191-final-sp19
	cp Vagrantfile ../../static/boxes/cis191-final-sp19
	cp final-sp2019 ../../static/boxes/cis191-final-sp19

final-sp2019: final-sp2019.py
	armor final-sp2019.py

lib:
	make -C ../../ html
	cp ../../static/dist/lifealgorithmic-0.0.1.tar.gz .
