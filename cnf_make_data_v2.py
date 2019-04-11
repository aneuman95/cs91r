from z3 import *
import sys, argparse, re, inspect
import numpy as np
import random
import string
from statistics import mean 

# set seeds
#seed = 1
#random.seed(seed)
#np.random.seed(seed)

CONTRADICTS = 0
NEUTRAL = 1
ENTAILS = 2

#when num_clauses is large relative to num_variables, we get valid because p is never satisfiable (false)
#when num_clauses is small relative to num_variables, we get sat (premise is sat, hypoth is unsat)
#when p is valid and q is Not(p), we get unsat 

def cnf_make_formula(num_variables,num_clauses,clause_length):
    #create list of literals to sample from 
    var_labels = [i for i in range(num_variables)]
    variables = np.array(['x' + str(s) for s in var_labels])

    #generate clauses 
    clauses = []
    for i in range(num_clauses):
        #randomly sample a random number of literals  
        clause_len = np.random.randint(low=1,high=clause_length+1)
        literals = [Bool(np.random.choice(variables)) for x in range(clause_len)]
        #randomly negate each literal 
        for j in range(len(literals)):
            if np.random.uniform() < 0.5:
                literals[j] = Not(literals[j])
        clauses.append(Or(literals))
    return(And(clauses))

def check(p,q):
    #check if expression is valid, satisfiable, or unsatisfiable
    s = Solver()
    s.add(Not(Implies(p,q)))
    if s.check() == unsat:
        return("valid")
    else:
    	s = Solver()
    	s.add(Implies(p,q))
    	if s.check() == unsat:
    		return("unsat")
    	else:
    		return("sat")

#generates unsat examples 
def make_unsat(num_examples, num_variables, num_clauses, clause_length):
    premises = []
    hypoths = []
    #discard examples that don't evaluate to unsat 
    while (len(premises) < num_examples):
        p = cnf_make_formula(num_variables,num_clauses,clause_length)
        s = Solver()
        s.add(Not(p))
        if s.check() == unsat:
            q = cnf_make_formula(num_variables,7*num_variables,3)
            if check(p,q) == "unsat":
                premises.append(p)
                hypoths.append(q)
    return premises, hypoths

#generates sat examples 
def make_sat(num_examples, num_variables, num_clauses, clause_length):
    premises = []
    hypoths = []
    #discard examples that don't evaluate to sat 
    while (len(premises) < num_examples):
        p = cnf_make_formula(num_variables,num_clauses,clause_length)
        q = cnf_make_formula(num_variables,num_clauses,clause_length)
        if check(p,q) == "sat":
            premises.append(p)
            hypoths.append(q)
    return premises, hypoths

#generates valid examples 
def make_valid(num_examples, num_variables, num_clauses, clause_length):
    premises = []
    hypoths = []
    #discard examples that don't evaluate to valid 
    while (len(premises) < num_examples):
        p = cnf_make_formula(num_variables,num_clauses,clause_length)
        q = cnf_make_formula(num_variables,num_clauses,clause_length)
        if check(p,q) == "valid":
            premises.append(p)
            hypoths.append(q)
    return premises, hypoths

#check average number of valid premises 
def make_valid_premise(num_examples, num_variables, num_clauses, clause_length):
    #count valid premises 
    count = []
    for i in range(num_examples):
        p = cnf_make_formula(num_variables,num_clauses,clause_length)
        s = Solver()
        s.add(Not(p))
        if s.check() == unsat:
            count.append(1)
            #print(p)
        else:
            count.append(0)
    return mean(count)

def make_unsat_hypoth(num_examples, num_variables, num_clauses, clause_length):
    #count valid premises 
    count = []
    for i in range(num_examples):
        q = cnf_make_formula(num_variables,num_clauses,clause_length)
        s = Solver()
        s.add(q)
        if s.check() == unsat:
            count.append(1)
            #print(p)
        else:
            count.append(0)
    return mean(count)

#need to add variables for sat, valid, and unsat inputs 
def make_data(num_examples):
	#generate examples 
	print("finding sat examples...")
	sat_premises, sat_hypoths = make_sat(num_examples,10,20,3)
	print("finding valid examples...")
	valid_premises, valid_hypoths = make_valid(num_examples,10,50,3)
	print("finding unsat examples...")
	unsat_premises, unsat_hypoths = make_unsat(num_examples,10,2,3)

	#store data in dictionary 
	data = {'hypoths':[], 'premises':[], 'lbls':[]}
	data['premises'] = data['premises'] + (sat_premises + valid_premises + unsat_premises)
	data['hypoths'] = data['hypoths'] + (sat_hypoths + valid_hypoths + unsat_hypoths)
	for _ in sat_premises:
		data['lbls'].append(NEUTRAL)
	for _ in valid_premises:
		data['lbls'].append(ENTAILS)
	for _ in unsat_premises:
		data['lbls'].append(CONTRADICTS) 

	return data

#this function almost never generates unsat examples
def make_data2(num_examples,num_variables,num_clauses,clause_length):
	#store data in dictionary 
    data = {'hypoths':[], 'premises':[], 'lbls':[]}

    for i in range(num_examples):
    	#make premise
	    p = cnf_make_formula(num_variables,num_clauses,clause_length)
	    data['premises'].append(p)

        #make hypothesis
	    q = cnf_make_formula(num_variables,num_clauses,clause_length)
	    data['hypoths'].append(q)

	    #check entailment 
	    label = check(p,q)
	    if label == "valid":
	    	data['lbls'].append(ENTAILS)
	    elif label == "sat":
	    	data['lbls'].append(NEUTRAL)
	    else:
	    	data['lbls'].append(CONTRADICTS)

    return data 


def test_data():
    #keep track of stats 
    stats = dict()

    for i in range(5,70,5):
        data = make_data2(100,10,i,3)
        stats[i] = ["CONTRADICTS: " + str(data['lbls'].count(0)), "NEUTRAL: " + str(data['lbls'].count(1)), "ENTAILS: " + str(data['lbls'].count(2))]

    return stats

def test_valid_premises():
    #keep track of stats 
    stats = dict()

    for i in range(1,10,1):
        count = make_valid_premise(1000,10,i,3)
        stats[i] = count

    return stats

def test_unsat_hypoths():
    #keep track of stats 
    stats = dict()

    count = make_unsat_hypoth(1000,10,10,3)
    stats[10] = count

#    for i in range(1,10,1):
#        count = make_valid_premise(1000,10,i,3)
#        stats[i] = count

    return stats

stats = test_data()
valid_premise_stats = test_valid_premises()
unsat_hypoths_stats = test_unsat_hypoths()
print(stats)
print(valid_premise_stats)
print(unsat_hypoths_stats)
 

#Tests 

#data = make_data2(100, 10, 20, 3)
#print("CONTRADICTS: " + str(data['lbls'].count(0)))
#print("NEUTRAL: " + str(data['lbls'].count(1)))
#print("ENTAILS: " + str(data['lbls'].count(2)))


#print(data['lbls'])
#print(data['premises'][4])
#s = Solver()
#s.add(data['premises'][4])
#print(s.check())
#print(data['hypoths'][4])
#s = Solver()
#s.add(data['hypoths'][4])
#print(s.check())
#s = Solver()
#s.add(Not(Implies(data['premises'][4],data['hypoths'][4])))
#print(s.check())

#print(make_valid_premise(1000,10,2,3))

#prem, hypoth = make_unsat(1,20,2,3)
#print(prem)
#print(len(hypoth)

#d = make_data(100)
#print(d)

#p,h = make_unsat(1)
#print(p)
#print(h)

#p = cnf_make_formula(10,50,3)
#q = cnf_make_formula(10,50,3)
#result = check(p,q)
#solve(p)
#solve(q)
#print(result)
#solve(Or(Not(p),q))

#x = Bool('x')
#p = Or(x,Not(x))
#q = Not(p)
#if check(p,q) == "unsat":
#	print(check(p,q))
#solve(Not(Implies(p,q))
