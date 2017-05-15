#!/usr/bin/python

import sys
import readControl
import copy
from Bio import Phylo
import matrixOps
import evolve
import argparse

parser = argparse.ArgumentParser(description = "This program simulates evolution of discrete characters along a user-provided tree.")
parser.add_argument("-t","--treefile",required=True,help="File containing the tree along which you wish to simulate your sequences. Must be in newick format, or a format specified with the --tree_format option.")
parser.add_argument("-p","--parameters",required=True,nargs = "+", help = "List of parameter files, separated by a space. Specifying more than one allows for use of different models on different branches of the tree.")
parser.add_argument("-tf","--tree_format",type=str,default="newick",help="Input format for your phylogenetic tree. Available options: nexus, nexml, phyloxml, cdao. NOTE: Not yet tested, but should work.")
parser.add_argument("-ns","--number_sites",type=int,default=100,help="Number of sites you wish to have in your alignment. Default value is 100.")
parser.add_argument("-m","--mapping",default=False,action="store_true",help="If enabled, will create mappings of which substitutions occurred when along the tree in .map files, one for each site.")
parser.add_argument("-g","--gamma",default=False,action="store_true",help="If enabled, will create a file with information on the gamma category for each site, as well as the number of events that occurred at that site.")
parser.add_argument("-gcat","--gamma_categories",type=int,default=4,help="Number of gamma categories. Default is 4.")
parser.add_argument("-a","--alpha",type=float,default=1.0,help="Alpha value for the gamma distribution. Default value is 1.0")
parser.add_argument("-cg","--cont_gamma",default=False,action="store_true",help="If enabled, distribution of rates among sites will follow a continuous gamma distribution. If both this option and the number of gamma categories option are enabled, this option will take precedence.")
parser.add_argument("-is","--invariant_sites",type=float,default=0.0,help="Proportion of sites in your alignment you wish to be invariant. Must be a float between zero and 1.")
parser.add_argument("-of","--output_format",default="fasta",help="Output format for the MSA generated. Must be one of the options available in BioPython.")
parser.add_argument("-nr","--number_replicates",type=int,default=1,help="Number of replicates you wish to have of your sequence. Default is 1.")
parser.add_argument("-o","--output_name",type=str,default="simulated",help="Name of your output file.")

args = parser.parse_args()

#Read in all the user parameters.
freqs = []
matrix = []
multipliers = []
transitions = []
avail = []
for param in args.parameters:
	freqs.append(readControl.getFrequencies(param))
	matrix.append(readControl.getMatrix(param))
	multipliers.append(readControl.getMultipliers(param))

#Get the matrix converted to usable state.
for i in range(len(matrix)):
	matrix[i] = matrixOps.convertToNumeric(matrix[i],freqs[i],multipliers[i])
	matrix[i] = matrixOps.normalizeMatrix(matrix[i],freqs[i])
	if (matrixOps.is_square(matrix[i]) == False):
		print "This matrix is found in file " + args.parameters[i] 
	transitions.append(matrixOps.getTransitionProbs(matrix[i]))
	avail.append(matrixOps.availableTransitions(matrix[i]))


#Read in the tree provided by the user.
try:
    tree = Phylo.read(args.treefile,args.tree_format)
except:
    print "ERROR: Couldn't read input tree " + args.treefile + " in " + args.tree_format + " format. Please verify your tree and try again. Exiting..."
    sys.exit()

#Simulate!
for i in range(args.number_replicates):
    name = args.output_name + str(i + 1)
    evolve.simulate(tree, freqs, transitions, avail, outputFormat = args.output_format,seqLength=args.number_sites,outfile = name ,invariant = args.invariant_sites, mapping = args.mapping, contGamma = args.cont_gamma,numCategories=args.gamma_categories,alpha = args.alpha,gammaInfo = args.gamma)
