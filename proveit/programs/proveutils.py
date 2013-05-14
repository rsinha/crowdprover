import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant, LoopInvariant

def computeTrace(meta, binary,inputs):
        trace = {}
       
	trace['inputs'] = []
	meta = open(meta, 'r').readlines()
	for line in meta:
		elements = line.rstrip().split(',')
		varname = ""
		vardefault = ""
		for element in elements:
			element_t = element.split(':')[0]
			element_v = element.split(':')[1]
			if element_t == 'name':
				varname = element_v
			elif element_t == 'default':
				vardefault = element_v
		trace['inputs'] += [{'name':varname, 'default':vardefault}]
		

	procOptions = [binary]
	procOptions += [str(0)] #entire program
	for inp in inputs:
		procOptions += [str(inp)]
        proc = subprocess.Popen(procOptions,stdout=subprocess.PIPE)
        loopCounter = 0 
        while True:
                line = proc.stdout.readline()
                if line != '': 
                        elements = line.split(',')
			trace['numvars'] = len(elements) - 1
                        if loopCounter == 0:
                                trace['length'] = 0 
                                trace['values'] = []
                                for element in elements:
                                        element_t = element.split(':')[0]
                                        element_v = element.split(':')[1]
                                        if element_t == "line":
                                                trace['firstLine'] = int(element_v)
                                                trace['lines'] = [element_v]
                                        else:
                                                trace['values'] += [{'name':element_t, 'values':[element_v.rstrip()], 'alias': nameToAlias(element_t)}]
                        else:
                                for element in elements:
                                        element_t = element.split(':')[0]
                                        element_v = element.split(':')[1]
                                        if element_t == "line":
                                                trace['lines'] += [element_v]
                                        else:
                                                for var in trace['values']:
                                                        if var['name'] == element_t:
                                                                var['values'] += [element_v.rstrip()]
                                                                break
      
      
                        print line.rstrip()
                        trace['length'] += 1
                        loopCounter = loopCounter + 1 
                else:
                        break
        return trace




def computeThreeTraces(meta, binary, loopid, inputs):
        trace = {}
       
	trace['inputs'] = []
	meta = open(meta, 'r').readlines()
	for line in meta:
		elements = line.rstrip().split(',')
		varname = ""
		vardefault = ""
		for element in elements:
			element_t = element.split(':')[0]
			element_v = element.split(':')[1]
			if element_t == 'name':
				varname = element_v
			elif element_t == 'default':
				vardefault = element_v
		trace['inputs'] += [{'name':varname, 'default':vardefault}]
		
        loopCounter = 0 
	for inp in inputs:
		procOptions = [binary]
		procOptions += [str(loopid)]
		procOptions += [str(inp)]
        	proc = subprocess.Popen(procOptions,stdout=subprocess.PIPE)
        	while True:
                	line = proc.stdout.readline()
       		        if line != '': 
                        	elements = line.split(',')
				trace['numvars'] = len(elements) - 1
                        	if loopCounter == 0:
                                	trace['length'] = 0 
                                	trace['values'] = []
                                	for element in elements:
                                        	element_t = element.split(':')[0]
                                        	element_v = element.split(':')[1]
                                        	if element_t == "line":
                                                	trace['firstLine'] = int(element_v)
                                                	trace['lines'] = [element_v]
                                        	else:
                                                	trace['values'] += [{'name':element_t, 'values':[element_v.rstrip()], 'alias': nameToAlias(element_t)}]
                        	else:
                                	for element in elements:
                                        	element_t = element.split(':')[0]
                                        	element_v = element.split(':')[1]
                                        	if element_t == "line":
                                                	trace['lines'] += [element_v]
                                        	else:
                                                	for var in trace['values']:
                                                        	if var['name'] == element_t:
                                                                	var['values'] += [element_v.rstrip()]
                                                                	break
      
      
                        	print line.rstrip()
                        	trace['length'] += 1
                        	loopCounter = loopCounter + 1 
                	else:
                        	break
        return trace

def nameToAlias(name):
	return '_'.join(name.split('->'))

def absoluteBinary(binary):
	return "proveit/bin/" + binary

def absoluteSource(source):
	return "proveit/programs/static/code/" + source

def absoluteMeta(source):
	return "proveit/programs/static/code/" + source + ".meta"
