# Visualizing based on pydot and the AST tree/LLL

#### Control flow graph
The `GraphCode().control_flow` is what i wanted to make, the other one was created
because it is relatively easy.

#### Straight graph
Note that the `GraphCode().straight` visualization, loses a lot of information.
Because it doesnt show the order of the arguments.

Also have trouble making nodes with the same names not be the same one.
(You'd say that is the default)

Looking to make something that visualizes the control flow, rather than the
AST tree. That would actually be useful.

## TODO
* LLL is not case sensitive.
* `(lll ...)` from inside statements seem to produce more edges and nodes than
  it should.
* More/nicer themes.. Particularly an Ethereum theme would be nice.
* Handle comments.
* Further out:
  + More direct control of positioning?
  + Make it workable with presentation?
