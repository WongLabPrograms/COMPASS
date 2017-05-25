This example shows how to partition data into different models across sites and branches.

To run: wrap_COMPASS.py partition_control.txt

Most branches of the tree in the first partition will be simulated under an HKY model,
while all branches marked with a $1 will be simulated under a REV model. In the second
partition this flips, and unmarked branches are simulated under a REV model while marked
branches are simulated under an HKY model.


