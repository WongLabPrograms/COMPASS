#!/usr/bin/python

from Bio import Phylo
import os
from Bio import AlignIO
import sys
import random
from decimal import *
import copy
import numpy as np

#Takes the current state, the transition probablilities (generated by
#matrixOps.getTransitionProbs) and available states to transition to
#(generated by matrixOps.availableTransitions)
#Returns whatever the new state should be according to the
#transitions probabilities.
def mutate(current_state, transitions, available):
    new_state = ""
    total = transitions[current_state][len(transitions[current_state])-1]
    r = random.uniform(0,total)
    for i in range(len(transitions[current_state])):
        if r < transitions[current_state][i]:
            new_state = available[current_state][i]
            break
    return new_state
        
#Finds how long to wait until the next event.
#Takes the current state and the transition probabilities
#(generated by matrixOps.getTransitionProbs) and returns
#a waiting time
def waiting_time(current_state, transitions):
    try:
        rate_away = transitions[current_state][len(transitions[current_state])-1]
    except:
        print "ERROR: Couldn't find transition probabilities for state " + current_state + ". Ensure that it is found in Frequencies and Matrix. Exiting..."
        sys.exit()
    u = np.random.uniform(0,1)
    dt = (-1*np.log(1-u))/rate_away
    dt = round(dt,6)
    return dt

#Takes the frequencies and give a root state for the tree.
def get_root_state(frequencies):
    getcontext().prec = 8
    freqs = copy.deepcopy(frequencies)
    total = Decimal(0)
    root_state = ""
    for state in freqs:
        total += Decimal(freqs[state])
        freqs[state] = total
    r = random.uniform(0,1)
    if total > 1.000001 or total < 0.99999:
        print "Sum of frequencies = " + str(total)
        print "ERROR: Sum of frequencies does not add to 1.0\nExiting..."
        sys.exit()
    for state in freqs:
        if r < freqs[state]:
            root_state = state
            break
    return root_state

#Sets up the gamma distribution. Takes the alpha value (positive float) and the number
#of categories (positive integer >= 1).
def gammaSetup(alpha,numCategories):
    #Do some error checking.
    if alpha < 0.0:
        print "ERROR: Alpha value must be a positive number. Number entered was " + str(alpha) + ". Exiting..."
        sys.exit()
    
    if numCategories < 1:
        print "ERROR: Number of categories must be at least 1. Number entered was " + str(numCategories) + ". Exiting..."
        sys.exit()

    #Then actually get your gamma distribution set up.
    gamma_dist = np.random.gamma(alpha,1.0/alpha,100000)
    gamma_dist = np.sort(gamma_dist)
    categories = np.array_split(gamma_dist,numCategories)
    gamma_values = {}
    i = 1
    for category in categories:
        gamma_values[i] = np.mean(category)
        i += 1

    return gamma_values

#Checks that the number of models present in the tree is equal 
#to the number of parameter files specified.
def numModelCheck(tree,freqs):
    z = tree.find_clades()
    models = []
    for branch in z:
        bName = str(branch.name)
        if "$" in bName:
            model = ""
            index = bName.index("$")
            for s in range(index + 1,len(bName)):
                model += bName[s]
            model = int(model)
        else:
            model = 0
        if model not in models:
            models.append(model)

    if len(models) != len(freqs):
        print "ERROR: Unequal numbers of models found in tree and parameter files."
        print "Found " + str(len(models)) + " models in the tree file."
        print "Found " + str(len(freqs)) + " models in parameter files. "
        print "Numbers must be equal. Exiting..."
        sys.exit()

#Finds the maximum depth of a BioPython tree.
#Necessary for the scheme used to simulate. 
def get_tree_depth(tree):
    z = tree.find_clades()
    x = tree.depths(unit_branch_lengths=True)
    maxdepth = 0
    for item in z:
        if x[item] > maxdepth:
            maxdepth = x[item]

    return maxdepth


def simulate(tree,freqs,matrices,available, seqLength=100, alpha=1.0,numCategories=4,gammaInfo = False, outfile = "simulated", invariant = 0.0, mapping = False, contGamma = False,outputFormat = "phylip"):
    
    #Check that the right number of models are present.
    numModelCheck(tree,freqs)

    #Check that invariant sites is what it's allowed to be.
    if invariant < 0 or invariant > 1:
        print "Proportion of invariant sites must be between 0 and 1. Number entered was " + str(invariant) + ". Exiting..."
        sys.exit()

    z = tree.find_clades()
    #Setup the array that will hold the sequences.
    seqs = []
    for j in range(seqLength):
        for branch in z:
            if branch.is_terminal():
                seqs.append(str(branch) + "\t")
    
    #Find the maxdepth of the tree.

    maxdepth = get_tree_depth(tree)

    #Setup your gamma value distribution.
    gamma_dist = gammaSetup(alpha,numCategories) 
    

    #Output File with info about number of sites.
    if gammaInfo == True:
        f = open(outfile + "_gammainfo.txt","w")
    #Now actually get going with the simulation.
    for j in range(seqLength):
        newtree = copy.deepcopy(tree)
        states = []
        for i in range(maxdepth + 1):
            states.append("")
        i = 0

        #For whatever reason BioPython forces this to be called each time through.
        z = newtree.find_clades()
        x = newtree.depths(unit_branch_lengths=True)
        #Select gamma category for the site you're currently at.
        if contGamma == True:
            gamma_multiplier = np.random.gamma(alpha,1.0/alpha,1)
        else:
            r = random.randint(1,numCategories)
            gamma_multiplier = gamma_dist[r]
        
        #Add in invariant sites.
        num = random.uniform(0,1)
        if num < invariant:
            gamma_multiplier = 0.0

        if gammaInfo == True:
            f.write("Site" + str(j) + ". Gamma Value = " + str(gamma_multiplier))

        num_events = 0
        for branch in z:
            #Step before 1: Figure out which model you're going to be using on this branch.
            bName = str(branch.name)
            if "$" in bName:
                model = ""
                index = bName.index("$")
                for s in range(index + 1,len(bName)):
                    model += bName[s]
                model = int(model)
            else:
                model = 0
            
            #Step one: Assign a state to the root of the tree.
            if branch.branch_length == None:
                root_state = get_root_state(freqs[model])
                states[0] = root_state
                branch.name = "_" + root_state
            #Everything that isn't the root needs to get evolved! 
            else:
                if branch.name == None:
                    branch.name = ""
                distance_travelled = 0.0
                length = branch.branch_length
                distance = waiting_time(states[x[branch] - 1], matrices[model])
                distance_travelled += distance
                #Don't forget to factor in the gamma multiplier!
                length *= gamma_multiplier

                #If there's still room on the branch, keep evolving.
                if distance_travelled < length:
                    name = []
                    branch.name = branch.name + "_"
                    old_state = states[x[branch] - 1]
                    name.append(old_state)
                    while distance_travelled < length:
                        num_events += 1
                        remaining_distance = length - distance_travelled
                        new_state = mutate(old_state,matrices[model], available[model])
                        states[x[branch]] = new_state
                        name.append(new_state + ":" + str(distance/gamma_multiplier) + ":")
                        distance = waiting_time(new_state,matrices[model])
                        distance_travelled += distance
                        old_state = new_state
                    name.append(str(remaining_distance/gamma_multiplier) + ":")
                    name.append(new_state + ":")
                    for q in range(len(name)-1,-1,-1):
                        branch.name += name[q]

                #If nothing happened.
                else:
                    states[x[branch]] = states[x[branch] - 1]
                    branch.name = branch.name + "_" + states[x[branch]] + ":" + str(branch.branch_length) + ":" + states[x[branch]]
            #If the branch is terminal, need to print out the state to the alignment.
            if branch.is_terminal():
                seqs[i] += states[x[branch]]
                i += 1
            branch.branch_length = None
        
        #Output a substitution mapping for each site, if desired.
        if mapping == True:
            Phylo.write(newtree, outfile + "_" + str(j) + ".map","newick")
            ff = open(outfile + "_" + str(j) + ".map")
            formatting_fix = ff.readlines()
            ff.close()
            formatting_fix[0] = formatting_fix[0].replace(":0.00000","")
            formatting_fix[0] = formatting_fix[0].replace("\'","")
            ff = open(outfile + "_" + str(j) + ".map","w")
            ff.write(formatting_fix[0])
            ff.close()

        #More gamma information output.
        if gammaInfo == True:
            f.write(". Number of events: " + str(num_events) + "\n")

    #Closing files is important.
    if gammaInfo == True:
        f.close()

    #Writes output in phylip format.
    f = open(outfile + ".phy","w")
    seqlen = len(seqs[0].split()[1])
    f.write(str(i) + "\t" + str(seqlen) + "\n")
    for seq in seqs:
        #Need to remove branch model tags.
        if "$" in seq:
            seqName = seq.split()[0]
            index = seqName.index("$")
            for q in range(index):
                f.write(seqName[q])
            f.write("\t")
            f.write(seq.split()[1] + "\n")
        else:    
            f.write(seq + "\n")
    f.close()

    #Option to output in other file formats.
    if outputFormat != "phylip":
        alignment = AlignIO.read(outfile + ".phy","phylip-relaxed")
        f = open(outfile + "." + outputFormat,"w")
        try:
            f.write(alignment.format(outputFormat))
            f.close()
        except:
            print "Output format entered was not valid. Output format requested was: " + outputFormat + ". Please see manual for allowed formats. Your alignment is still available here in phylip (.phy) format. Exiting..."
            f.close()
            os.remove(outfile + "." + outputFormat)
            sys.exit()
        os.remove(outfile + ".phy")
