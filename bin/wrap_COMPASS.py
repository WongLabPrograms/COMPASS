#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
from Bio import AlignIO
import argparse

parser = argparse.ArgumentParser(description = "Wrapper for COMPASS that allows for partitioning to occur, in the event that different models need to be run for different portions of the alignment.")
parser.add_argument("control_file",help="Control file. Please see manual for description, as the options available are extensive.")
parser.add_argument("-tf","--tree_format",type=str,default="newick",help="Input format for your phylogenetic tree. Default is newick, but other available options are nexus, nexml, phyloxml, and cdao. All partitions must have trees in the same format.")
parser.add_argument("-o","--output_name",type=str,default="simulated",help="Base name for your simulated sequences.")
parser.add_argument("-nr","--number_replicates",type=int,default=1,help="Number of times you wish to create your partitioned alignment.")
parser.add_argument("-of","--output_format",type=str,default="fasta",help="Format for your output aligment file.")

args=parser.parse_args()

output_name = args.output_name

#Get directory path.
#dir_path = os.path.dirname(os.path.realpath(__file__))

try:
	f = open(args.control_file)
except:
	print "Couldn't find your control file: " + args.control_file + ". Please check the name and try again. Exiting..."
	sys.exit()

lines = f.readlines()
f.close()

alignments = []

total_sites = 0
for j in range(args.number_replicates):
	#This loop goes through the control file and appends 
	#each part of the alignment to an array that contains the alignments.
	alignments.append([])
	for i in range(1,len(lines)):
		info = lines[i].split()
		if len(info) == 8:
			matrix = info[0]
                        m = matrix.split(",")
			tree = info[1]
			sites = info[2]
			total_sites += int(sites)
			gamma = info[3]
			alpha = info[4]
			invar = info[5]
			g_info = info[6]
			mappings = info[7]
			#This takes care of disc vs cont gamma
			cmd = "COMPASS.py -t " + tree + " -p"
			for matrix in m:
				cmd += " " + matrix
			if gamma == "0":
				cmd += " -ns " + sites + " -cg -a " + alpha + " -is " + invar + " -o " + output_name + str(j + 1) + "_" + str(i) + " -tf " + args.tree_format
			else:
				cmd += " -ns " + sites + " -gcat " + gamma + " -a " + alpha + " -is " + invar + " -o " + output_name + str(j + 1) + "_" + str(i) +" -tf " + args.tree_format
			#Now add mappings and gamma info options.
			if g_info == "1":
				cmd += " -g"
			if mappings == "1":
				cmd += " -m"
			print subprocess.check_output(cmd,shell=True),
			try:
				alignments[j].append(AlignIO.read(output_name + str(j + 1) + "_" + str(i) + "1.fasta","fasta"))
				os.remove(output_name + str(j + 1) + "_" + str(i) + "1.fasta")
			except:
				sys.exit()
num_species = len(alignments[0][0])
#Then output each replicate.
for j in range(args.number_replicates):
	seqs = []
	seqnames = []
	for i in range(num_species):
		seqs.append("")	
		seqnames.append("")
	for alignment in alignments[j]:
		i = 0
		for record in alignment:
			seqs[i] += record.seq
			seqnames[i] = record.id
			i += 1

	f = open(output_name + str(j + 1) + ".fasta", "w")
	for i in range(len(seqs)):
		f.write(">" + seqnames[i] + "\n")
		f.write(str(seqs[i]) + "\n")

	f.close()
	if args.output_format != "fasta":
		a = AlignIO.read(output_name + str(j+1) + ".fasta","fasta")
		f = open(output_name + str(j+1) + "." + args.output_format,"w")
		f.write(a.format(args.output_format))
		f.close()
		os.remove(output_name + str(j+1) + ".fasta")
