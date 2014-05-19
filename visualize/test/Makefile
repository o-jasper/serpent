
default: control_flow.svg straight.svg

%.svg: test_%.py
	python2 $<

%.png: %svg
	convert $< $@
