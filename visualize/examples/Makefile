
default: run

run:
	python2 examples_straight_graph.py

slow_and_may_fail: sg_Bank.png sg_kv.png sg_NameReg.png sg_Splitter.png sg_SubCurrency.png

%.png: %.svg
	convert $< $@


