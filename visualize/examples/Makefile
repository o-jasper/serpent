
default: sg cf

sg: ../visualize.py examples_straight_graph.py
	python2 examples_straight_graph.py

cf: ../visualize.py examples_control_flow_graph.py
	python2 examples_control_flow_graph.py

png: sg_png cf_png

sg_png:
	sh conv.sh sg
cf_png:
	sh conv.sh cf

%.png: %.svg
	convert $< $@


