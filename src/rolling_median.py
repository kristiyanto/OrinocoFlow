#!/usr/bin/python3

###########################################################
# Daniel Kristiyanto, danielkr@uw.edu
#
# Summer, 2016
#
# A graph to find a money transfer transaction in Venmo
# Please refer readme.md for more detailed usage and information
#
###########################################################

import os
import sys
import json
import datetime as dt
from collections import Counter


'''
===== CLASSES ====
'''

class Graph:
    def __init__(self, out='output.txt', verbose=False):
        self.vertices = {}
        self.edges = {}
        self.outputFile = out
        self.median = 0.00
        self.timeWindow = timeWindow
        self.verbose = verbose
    
    ## Function to add a node. A none instance is required
    def addNode(self, node):
        if not isinstance(node, Node): raise ValueError(\
            'Adding a node error: A node must be a node instance.')
        if node.actor not in self.vertices: 
            self.vertices[node.actor] = node
            if len(self.vertices) == 1: 
                self.currMaxTime = node.created_time
                self.curMinTime = self.currMaxTime - dt.timedelta(seconds=self.timeWindow)
            return True
        return False

    ## Function to add an egde, if conditions in isValid() met
    ## Changes trigger graph pruning and rolling median calculation
    def addTarget(self, node, target, **kwargs):
        if not isinstance(node, Node): raise ValueError(\
            'Adding a node error: A node must be a node instance.')
        if self.isValid(node, target, node.created_time):
            self.vertices[node.actor].addTarget((target, node.created_time))
            self.currMaxTime = self.updateMaxTime()
            self.curMinTime = self.currMaxTime - dt.timedelta(seconds=self.timeWindow)
            self.prune()
            self.updateMedian()
            return True
        else:
            self.prune()
            if self.verbose: print("Rejected: " + node.actor + ', ' \
            + node.created_time.strftime(timeFormat))
            return False

    ## Filtering incoming edges/transactions
    ## e.g: timestamps, if actor is valid,
    ## or if transactions is already existed (hence, replace it if newer)
    def isValid(self, node, target, created_time):
        if node.actor not in self.vertices and target in self.vertices: return False
        if node.created_time < self.curMinTime: return False
        if (target in [n[0] for n in self.vertices[node.actor].getTargets()]):
            return self.vertices[node.actor].replaceTarget(target, created_time)
        elif(target in self.vertices and node.actor in [n[0] for n in self.vertices[target].getTargets()]):
            return self.vertices[target].replaceTarget(node.actor, created_time)
        else:
            return True

    ## Returning current time window for the graph (min and max timestamps)    
    def getWindow(self):
        return (self.curMinTime, self.currMaxTime)
    
    ## Scan through the graph to get the maximum timestamps
    def updateMaxTime(self):
        for v in list(self.vertices):
            if len(v) < 1 : return self.currMaxTime
            if self.currMaxTime < self.vertices[v].getMaxTime():
                self.currMaxTime = self.vertices[v].getMaxTime()
        return self.currMaxTime
    
    ## A static call returning current maximum timstamp
    def getMaxTime(self):
        return self.currMaxTime if self.currMaxTime else self.updateMaxTime()
    
    ## Scan through the graph to compute the rolling median 
    def updateMedian(self):
        egdeList = list()
        for v in self.vertices:
            egdeList.extend([n[0] for n in self.vertices[v].getTargets()])
            egdeList.extend([v]*len(self.vertices[v].getTargets()))
        unique = Counter(egdeList)
        self.edges = unique          
        unique = sorted([n for n in list(unique.values())])
        self.median = median(unique)
        return(self.median)

    ## Static call retruning current roll median, and save it to output file
    def getMedian(self, write=True, display=False):
        if write: 
            with open(self.outputFile, "a") as o: o.write('{0:.2f} \n'.format(self.median))
        if self.verbose:
            print(self.median)
        return self.median

    ## Returning list of the current egdes (mainly for log purposes)
    def getEgdeList(self):
        return self.edges
    
    ## Pruning the graph
    def prune(self):
        for v in list(self.vertices):
            self.vertices[v].updateTargets(self.getWindow()[0])
            if not self.vertices[v].getTargets() : 
                del self.vertices[v]
        return self.updateMaxTime()

    ## Returning the graph connections for log purposes
    def printGraph(self):
        txt = ""
        for v in self.vertices:
            txt = txt + ('Actor: {} \n Targets: {} \n'.format(v, \
            [(i[0], i[1].strftime("%I:%M:%S")) for i in self.vertices[v].targets]))
        return txt
                

            
class Node:
    ## By default, a vertex (node) does not have any egdes/target
    ## Until an egde is spesifically added. A node can have multiple egdes
    
    def __init__(self, actor, created_time, target, **kwargs):
        self.targets = list()
        self.initialTarget = target
        self.actor = actor
        self.totalTargets = 0
        self.created_time = dt.datetime.strptime(created_time, timeFormat)
        self.timewindow = timeWindow
        self.nodeMaxTime = self.created_time
    
    ## Function to add a new egde
    def addTarget(self, target):
        self.targets.append(target)
        if target[1] > self.nodeMaxTime: self.nodeMaxTime = target[1]
    
    ## If an egde already existed, and the incoming has a newer timstamps
    ## delete the egde so the graph can proceed adding the new egde
    def replaceTarget(self, target, created_time):
        for t in self.targets:
            if t[0] == target and t[1] < created_time:
                self.targets.remove(t)
                return True
            else:
                return False
            
    ## Function to prune expiring egdes
    def updateTargets(self, minTime):
        newTargets = list()
        newTimes = list()
        for t in self.targets:
            if t[1] > minTime: 
                newTargets.append(t)
                newTimes.append(t[1])
        self.targets = newTargets
        if not self.nodeMaxTime: self.nodeMaxTime  = max(newTimes)
    
    ## A static call returning the list of this node's connection/egdes
    def getTargets(self):
        return self.targets
    
    ## A static call returning maximum timestamps for each egdes
    def getMaxTime(self):
        return self.created_time if not self.targets else self.nodeMaxTime

    

'''
===== FUNCTIONS ====
'''
    
## Function to compute a median given a list    
def median(vector):
    if not isinstance(vector, list): raise ValueError('Input must be a list.')
    vector = sorted(vector)
    a = len(vector)
    b = a - 1
    return (vector[a//2] + vector[b//2]) / 2.0



## Function to record a detailed state of the current graph to a log file. 
def logItems(graph, write=True, file='log.txt', verbose=False):
    if not isinstance(graph, Graph): raise ValueError( \
    'Log error: Log input must be a graph instance.')
    Min = graph.getWindow()[0].strftime("%I:%M:%S")
    Max = graph.getWindow()[1].strftime("%I:%M:%S")
    txt = "MEDIAN: {} \n Sorted Egdes: {} \n Edges: \n {} \
        \n\n Time Window: {} {} \n\n Transactions: \n {} \
        ------- \n \n".format( \
        graph.getMedian(write=False, display=False), \
        sorted([n for n in list(graph.getEgdeList().values())]), \
        graph.getEgdeList(), \
        Min, Max, \
        graph.printGraph()) 
    if verbose: print(txt)
    if write: 
        with open(file, "a") as o: o.write(txt)

                        
            
## Making sure the specified files are readable and or writeable            
def filesLookup(inputFile, logFile='log.txt', outputFile='output.txt'):
    if not os.path.exists(inputFile): 
        raise ValueError('Input file: {} not found.'.format(inputFile))
        
        try:
            json = json.loads(open(inputFile, 'r').readline())
            if ('actor', 'created_time', 'target') in list(json.keys()): pass
        except:
            sys.exit('Input file: {} does not have required json fields.'.format(inputFile))

    try:
        open(outputFile, 'w').close()
        return True
    except:
        raise ValueError('Unable to write output files.')
        
    try:
        open(logFile, 'w').close()
    except:
        pass

'''
===== MAIN FILE ====
'''
        
def main():
    global timeFormat
    global timeWindow
    
    ## The following global variables must be defined
    ## Time Window is the cuttoff time in seconds
    timeFormat = '%Y-%m-%dT%H:%M:%S%fZ'
    timeWindow = 60
    
    ## Reading through the arguments
    inputFile = sys.argv[1].strip() if len(sys.argv)>1 else 'venmo-trans.txt'
    outputFile = sys.argv[2].strip() if len(sys.argv)>2 else 'output.txt' 
    logFile = sys.argv[3].strip() if len(sys.argv)>3 else None
    
    ## Get the files ready
    if logFile:
        filesLookup(outputFile=outputFile, inputFile=inputFile, logFile=logFile) 
    else:
        filesLookup(outputFile=outputFile, inputFile=inputFile) 
    
    ## This is the canvas
    g = Graph(out=outputFile, verbose=False)
    
    ## Reading through the input file
    with open(inputFile) as f:
        for line in f:
            entry = json.loads(line)
            
            # Skip incomplete entries
            if(entry['created_time'] and entry['target'] and entry['actor']):
                
                # 1) Convert json to a node instance
                newNode = Node(**entry)
                
                # 2) Add the node to the graph
                g.addNode(newNode)
                
                # 3) Add an egde to the node
                g.addTarget(newNode, **entry)
                
                # 4) Write the median to a File 
                g.getMedian(write=True)
                
                # 5) If asked (nicely), log the current graph state
                if logFile: logItems(g, write=True, verbose=False, file=logFile)            
  
if __name__ == "__main__": main()
