# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 16:22:00 2022

@author: frederik
"""

class Neighbor:
    def __init__(self, nodeID, depth, signalStrength, counter):
        self.nodeID = nodeID
        self.depth = depth
        self.signalStrength = signalStrength
        self.counter = counter
        
class ExtendedNeighbor:
    def __init__(self, nodeID, depth, source, counter):
        self.nodeID = nodeID
        self.depth = depth
        self.source = source
        self.counter = counter
        
class DeeperNode:
    def __init__(self, nodeID, depth):
        self.nodeID = nodeID
        self.depth = depth
        

class Member:
    def __init__(self, nodeID, depth):
        self.nodeID = nodeID
        self.depth = depth
        
class Leader:
    def __init__(self, leaderID, counter):
        self.leaderID = leaderID
        self.counter = counter
        
class Child:
    def __init__(self, childID, bestCandidate, nodeWeight, avrSignalStrength):
        self.childID = childID
        self.bestCandidate = bestCandidate
        self.nodeWeight = nodeWeight
        self.avrSignalStrength = avrSignalStrength
        
class bestCandidate:
    def __init__(self, candidateID, nodeWeight, avrSignalStrength):
        self.candidateID = candidateID
        self.nodeWeight = nodeWeight
        self.avrSignalStrength = avrSignalStrength

class Swarm:
    def __init__(self, ID):
        self.members = []
        self.max_depth = 0 
        self.size = 0
        self.id = ID
        self.is_changed = False
        
    def add_member(self, nodeID, nodeDepth):
        self.members.append(Member(nodeID, nodeDepth))
        self.size = len(self.members)
        self.max_depth = max(self.max_depth, nodeDepth)
        self.is_changed = True
        

    def _recalculate_depth(self):
        if not self.members:
            self.max_depth = 0
        else:
            self.max_depth = max([m.depth for m in self.members])


    def remove_member(self, nodeID):
        for member in self.members:
            if member.nodeID == nodeID:
                self.members.remove(member)
                break
                
        # recalculate depth
        self._recalculate_depth()  
        self.size = len(self.members)
        self.is_changed = True
        
    def update_depth(self, nodeID, depth):
        for member in self.members:
            if member.nodeID == nodeID:
                member.depth = depth
                
        self.is_changed = True
        self._recalculate_depth()


class swarmManager:
    
    def __init__(self, numberOfSwarms):    
        self.swarms = []
        for i in range(numberOfSwarms):
            self.swarms.append(Swarm(i))
            
        
    
    def getSwarmInformation(self, swarmID):
        swarm = self.swarms[swarmID-1]
        
        return swarm.members, swarm.size+1, swarm.max_depth 
         
    def checkForUpdate(self, swarmID):
        swarm = self.swarms[swarmID-1]
        changed = swarm.is_changed
        swarm.is_changed = False
        
        return changed
        
    def removeMember(self, swarmID, nodeID):
        swarm = self.swarms[swarmID-1]
        swarm.remove_member(nodeID)
        
        sourcefile = open('swarmmanagerError.txt', 'a')
        print("Removes: " + str(nodeID), file= sourcefile)
        print("From swarm:" + str(swarmID), file = sourcefile)
        sourcefile.close
        

    def addMember(self, swarmID, nodeID):
        swarm = self.swarms[swarmID-1]
        swarm.add_member(nodeID, 0)
        
        sourcefile = open('swarmmanagerError.txt', 'a')
        print("Adds: " + str(nodeID), file= sourcefile)
        print("To swarm:" + str(swarmID), file = sourcefile)
        sourcefile.close
        
        
    def updateMember(self, swarmID, nodeID, newDepth):
        swarm = self.swarms[swarmID-1]
        swarm.update_depth(nodeID, newDepth)
        
            