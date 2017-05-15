This folder shows an example of a mutation-selection model as described in Yang and
Nielsen's 2008 paper "Mutation-selection models of codon substitution and their use to
estimate selective strengths on codon usage."

The strength of selection varies over the tree, with unmarked branches having a medium
population size, branches marked with $1 having a small population size (weaker
selection), and branches marked with $2 having larger population sizes (stronger
selection).

To run:
python ../../code/wrap_COMPASS.py mutsel.txt
