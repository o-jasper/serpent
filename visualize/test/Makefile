
default: test

test: test_control_flow.py test_straight.py

%.svg: test_%.py
	python2 $<

%.png: %svg
	convert $< $@
