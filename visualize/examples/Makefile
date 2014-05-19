
default: sg cf

sg: sg_png
cf: cf_png

VISUALIZE=../bin/code_visualize.py

sg/sg_%.png: %.lsp
	$(VISUALIZE) sg $< $@

cf/cf_%.png: %.lsp
	$(VISUALIZE) cf $< $@

sg/sg_%.svg: %.lsp
	$(VISUALIZE) sg $< $@

cf/cf_%.svg: %.lsp
	$(VISUALIZE) cf $< $@

png: sg_png cf_png

sg_svg: sg/sg_Bank.svg sg/sg_kv.svg sg/sg_NameReg.svg sg/sg_Splitter.svg sg/sg_SubCurrency.svg
sg_png: sg/sg_Bank.png sg/sg_kv.png sg/sg_NameReg.png sg/sg_Splitter.png sg/sg_SubCurrency.png

cf_svg: cf/cf_Bank.svg cf/cf_kv.svg cf/cf_NameReg.svg cf/cf_Splitter.svg cf/cf_SubCurrency.svg
cf_png: cf/cf_Bank.png cf/cf_kv.png cf/cf_NameReg.png cf/cf_Splitter.png cf/cf_SubCurrency.png
