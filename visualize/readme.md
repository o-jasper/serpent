# Visualizing based on pydot and the AST tree/LLL

#### Control flow graph
The `GraphCode().control_flow` is what i wanted to make, the other one was created
because it is relatively easy.

Note that.

1. If it leads to a `return` or `stop` computation ends there.
2. Otherwise trace back and follow consecutive body lines.

#### Straight graph
Note that the `GraphCode().straight` visualization, loses a lot of information.
Because it doesnt show the order of the arguments.

Also have trouble making nodes with the same names not be the same one.
(You'd say that is the default)

Looking to make something that visualizes the control flow, rather than the
AST tree. That would actually be useful.

## TODO
* More/nicer themes.. Particularly an Ethereum theme would be nice.

* Graphically indicate `return`, `stop`, or return back into body.

* Handle comments.

* Further out:
  + More direct control of positioning?
  + Make it workable with other presentation?

* Really closer to the parser/write/ast stuff.
  + infix-like printing (Serpent-like) i.e `a + b` instead of `(+ a b)`
  + Identify identical paths.

* Tricky:
  + Decorate `if`, `when`, `unless`, `for`? (Apparently no html)
  + Edges back to body. Tricky, and probably not very enlightening.
  
