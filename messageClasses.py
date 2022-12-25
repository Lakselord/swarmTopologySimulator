# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 10:42:40 2022

@author: frederik
"""

class eventQueue:
    def __init__(self):
        self.events = []

    def addEvent(self, event):
        index = 0
        for e in self.events:
            if e.simulationStep == event.simulationStep and e.messageType > event.messageType:
                index = self.events.index(e)
                break
            
            elif e.simulationStep > event.simulationStep:
                index = self.events.index(e)
                break

        if index != 0:
            self.events.insert(index, event)
            
        else:
            self.events.append(event)
    
    def getNextEvent(self):
        nextEvent = self.events[0]
        
        return nextEvent
    
    def removeEvent(self, event):
        self.events.remove(event)

class event:
    def __init__(self, simulationStep, position, messageType, messageData):
        self.simulationStep = simulationStep
        self.position = position
        self.messageType = messageType
        self.messageData = messageData
        
class heartbeatMessage:
    def __init__(self, swarmID, electionID, nodeID, nodeDepth, neighborhood):
        self.swarmID = swarmID
        self.electionID = electionID
        self.nodeID = nodeID
        self.nodeDepth = nodeDepth
        self.neighborhood = neighborhood

class electionMessage:
    def __init__(self, electionID, nodeID, hopCount):
        self.electionID = electionID
        self.nodeID = nodeID
        self.hopCount = hopCount
        
class childMessage:
    def __init__(self, electionID, nodeID, parentID):
        self.electionID = electionID
        self.nodeID = nodeID
        self.parentID = parentID
        
class descendantsMessage:
    def __init__(self, electionID, nodeID, parentID, noDescendants):
        self.electionID = electionID
        self.nodeID = nodeID
        self.parentID = parentID
        self.noDescendants = noDescendants
        
class electionSizeMessage:
    def __init__(self, electionID, nodeID, electionSize, neighbors, hopCount):
        self.electionID = electionID
        self.nodeID = nodeID
        self.electionSize = electionSize
        self.neighbors = neighbors
        self.hopCount = hopCount
        
class ackMessage:
    def __init__(self, electionID, nodeID, parentID, bestCandidate, nodeWeight, avrSignalStrength):
        self.electionID = electionID
        self.nodeID = nodeID
        self.parentID = parentID
        self.bestCandidate = bestCandidate
        self.nodeWeight = nodeWeight
        self.avrSignalStrength = avrSignalStrength
        
class leaderMessage:
    def __init__(self, electionID, sourceNodeID, swarmSize, leaderID, hopCount):
        self.electionID = electionID
        self.sourceNodeID = sourceNodeID
        self.swarmSize = swarmSize
        self.leaderID = leaderID
        self.hopCount = hopCount
        
class leaderHeartbeatMessage:
    def __init__(self, swarmID, leaderID, swarmSize, maxSwarmDepth, timeStamp, hopCount):
        self.swarmID = swarmID
        self.leaderID = leaderID
        self.swarmSize = swarmSize
        self.maxSwarmDepth = maxSwarmDepth
        self.timeStamp = timeStamp
        self.hopCount = hopCount
        
class depthDiscoveryMessage:
    def __init__(self, swarmID, leaderID, hopCount):
        self.swarmID = swarmID
        self.leaderID = leaderID
        self.hopCount = hopCount
        
class discoveryAckMessage:
    def __init__(self, swarmID, nodeID, nodeDepth, deeperNodes):
        self.swarmID = swarmID
        self.nodeID = nodeID
        self.nodeDepth = nodeDepth
        self.deeperNodes = deeperNodes
        
class mergeInvestigationMessage:
    def __init__(self, swarmID, swarmSize, maxSwarmDepth, senderDepth):
        self.swarmID = swarmID
        self.swarmSize = swarmSize
        self.maxSwarmDepth = maxSwarmDepth
        self.senderDepth = senderDepth
        
class potentialMergeMessage:
    def __init__(self, swarmID, pmSwarmID, requiredHops, hopCount):
        self.swarmID = swarmID
        self.pmSwarmID = pmSwarmID
        self.requiredHops = requiredHops
        self.hopCount = hopCount
        
class mergeRequestMessage:
    def __init__(self, senderSwarmID, receiverSwarmID, leaderID, relayerDepth, requiredHops, hopCount):
        self.senderSwarmID = senderSwarmID
        self.receiverSwarmID = receiverSwarmID
        self.leaderID = leaderID
        self.relayerDepth = relayerDepth
        self.requiredHops = requiredHops
        self.hopCount = hopCount
        
class mergeAcceptMessage:
    def __init__(self, senderSwarmID, receiverSwarmID, relayerDepth, hopCount, members):
        self.senderSwarmID = senderSwarmID
        self.receiverSwarmID = receiverSwarmID
        self.relayerDepth = relayerDepth
        self.hopCount = hopCount
        self.members = members
        
class swarmChangeMessage:
    def __init__(self, oldSwarmID, newSwarmID, newLeaderID, hopCount):
        self.oldSwarmID = oldSwarmID
        self.newSwarmID = newSwarmID
        self.newLeaderID = newLeaderID
        self.hopCount = hopCount
        
class mergeElectionMessage:
    def __init__(self, swarmID, nodeID, swarmSize, neighbors, hopCount):
        self.swarmID = swarmID
        self.nodeID = nodeID
        self.swarmSize = swarmSize
        self.neighbors = neighbors
        self.hopCount = hopCount
        
class mergeChildMessage:
    def __init__(self, swarmID, nodeID, mergeParentID):
        self.swarmID = swarmID
        self.nodeID = nodeID
        self.mergeParentID = mergeParentID
    
class mergeAckMessage:
    def __init__(self, swarmID, nodeID, mergeParentID, bestCandidateID, nodeWeight, avrSignalStrength):
        self.swarmID = swarmID
        self.nodeID = nodeID
        self.mergeParentID = mergeParentID
        self.bestCandidateID = bestCandidateID
        self.nodeWeight = nodeWeight
        self.avrSignalStrength = avrSignalStrength
        
class mergeLeaderMessage:
    def __init__(self, swarmID, leaderID, hopCount):
        self.swarmID = swarmID
        self.leaderID = leaderID
        self.hopCount = hopCount