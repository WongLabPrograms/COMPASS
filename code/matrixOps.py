#!/usr/bin/python

import random
import sys
import copy

def convertToNumeric(m, frequencies, multipliers):
    #Create a copy of the matrix passed to the function so the original
    #doesn't get changed.
    matrix = copy.deepcopy(m)
    #Loop through the matrix to convert the symbols to numeric values.
    for i in range(1,len(matrix)):
        for j in range(1,len(matrix[i])):
            value = 1.0
            x = matrix[i][j].split("*")
            for item in x:
                if item in frequencies:
                    value = value*frequencies[item]
                elif item in multipliers:
                    value = value*multipliers[item]
                else:
                    #If user included something not in values or multipliers, try to typecast
                    #it to a float. If that doesn't work, boot them.
                    try:
                        value = value * float(item)
                    except:
                        print "ERROR: Symbol " + item + " was found in matrix, but nowhere else in the control file. Exiting..."
                        sys.exit()
                matrix[i][j] = value

                #Check that there aren't any non-zeroes on the diagonal. 
                #If there are, boot the user out w/ appropriate error message.
                if i == j and matrix[i][j] != 0.0:
                    print "ERROR: Non-zero found on the diagonal. Exiting..."
                    sys.exit()
    return matrix


def normalizeMatrix(m, frequencies):
    #Create copy of the matrix passed so the original doesn't change.
    matrix = copy.deepcopy(m)
    matrix_total = 0.0
    #Get the total so we know what we need to divide things by.
    for i in range(1,len(matrix)):
        for j in range(1,len(matrix[i])):
            try:
                 matrix_total += float(matrix[i][j])*frequencies[matrix[i][0]]
            except:
                print "ERROR: Couldn't find transition probabilities for state " + matrix[i][0] + ". Please ensure it is present in Frequencies and Matrix. Exiting..."
                sys.exit()

    #Use the matrix total to get the conversion factor to one.
    for i in range(1,len(matrix)):
        for j in range(1,len(matrix[i])):
            matrix[i][j] = float(matrix[i][j])/matrix_total

    return matrix


#Gets transition probabilities for each state.
def getTransitionProbs(m):
    matrix = copy.deepcopy(m)
    to_state = matrix[0]
    probs = {} 
    for i in range(1,len(matrix)):
        current_state = matrix[i][0]
        total = 0.0
        p = []
        for j in range(1, len(matrix[i])):
            total += float(matrix[i][j])
            if to_state[j-1] != current_state:
                p.append(total)
        probs[current_state] = p

    return probs

#Find what transitions are available when in each state.
def availableTransitions(m):
    matrix = copy.deepcopy(m)
    to_state = matrix[0]
    available = {}
    for i in range(1,len(matrix)):
        current_state = matrix[i][0]
        a = []
        for j in range(1,len(matrix)):
            if to_state[j-1] != current_state:
                a.append(to_state[j-1])
        available[current_state] = a

    return available

#Test to make sure that the matrix is square.
#Output a warning if it isn't for whatever reason.
def is_square(matrix):
	is_square = True
	for i in range(1,len(matrix)):
		if len(matrix[i]) != len(matrix):	
			print "WARNING: Matrix may not be square, which could cause problems." 
			print "Please check line " + str(i) + " of your input matrix."
			is_square = False
	return is_square
