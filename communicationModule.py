# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 10:15:14 2022

@author: frederik
"""

from messageClasses import event
from messageClasses import heartbeatMessage
from messageClasses import electionMessage
from messageClasses import childMessage
from messageClasses import ackMessage
from messageClasses import leaderMessage
from messageClasses import leaderHeartbeatMessage
from messageClasses import depthDiscoveryMessage
from messageClasses import discoveryAckMessage
from messageClasses import mergeInvestigationMessage
from messageClasses import potentialMergeMessage
from messageClasses import mergeRequestMessage
from messageClasses import mergeAcceptMessage
from messageClasses import swarmChangeMessage
from messageClasses import descendantsMessage
from messageClasses import electionSizeMessage
from messageClasses import mergeElectionMessage
from messageClasses import mergeChildMessage
from messageClasses import mergeAckMessage
from messageClasses import mergeLeaderMessage

class communicationModule:
    
    def __init__(self, communicationRange):
        self.communicationRange = communicationRange
        self.nodes = []
        self.messagesSend = 0
        
    def updateNodelist(self, nodes, ID):
        for i in nodes:
            if i.id != ID:
                self.nodes.append(i)   
    
    def sendHeartbeat(self, simulationStep, position, swarmID, electionID, nodeID, nodeDepth, neighborhood):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 1
        messageData = heartbeatMessage(swarmID, electionID, nodeID, nodeDepth, neighborhood)
        heartbeatEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(heartbeatEvent)
                        
    def sendElectionMessage(self, simulationStep, position, electionID, nodeID, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 2
        messageData = electionMessage(electionID, nodeID, hopCount)
        electionMessageEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(electionMessageEvent)
            
    def sendChildMessage(self, timestamp, position, electionID, nodeID, parentID):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 3
        messageData = childMessage(electionID, nodeID, parentID)
        childMessageEvent = event(timestamp, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(childMessageEvent)
            
    def sendAckMessage(self, timestamp, position, electionID, nodeID, parentID, bestCandidateID, nodeWeight, avrSignalStrength):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 4
        messageData = ackMessage(electionID, nodeID, parentID, bestCandidateID, nodeWeight, avrSignalStrength)
        ackMessageEvent = event(timestamp, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(ackMessageEvent)
               
    def sendLeaderMessage(self, timestamp, position, electionID, sourceNodeID, swarmSize, leaderID, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 5
        messageData = leaderMessage(electionID, sourceNodeID, swarmSize, leaderID, hopCount)
        leaderMessageEvent = event(timestamp, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(leaderMessageEvent)
            
    def sendLeaderHeartbeat(self, simulationStep, position, swarmID, leaderID, swarmSize, maxSwarmDepth, timestamp, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 6 
        messageData = leaderHeartbeatMessage(swarmID, leaderID, swarmSize, maxSwarmDepth, timestamp, hopCount)
        leaderHeartbeatEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(leaderHeartbeatEvent)
            
    def sendDepthDiscoveryMessage(self, simulationStep, position, swarmID, leaderID, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 7
        messageData = depthDiscoveryMessage(swarmID, leaderID, hopCount)
        depthDiscoveryEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(depthDiscoveryEvent)
            
    def sendDiscoveryAckMessage(self, simulationStep, position, swarmID, nodeID, nodeDepth, deeperNodes):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 8
        messageData = discoveryAckMessage(swarmID, nodeID, nodeDepth, deeperNodes)
        discoveryAckEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(discoveryAckEvent)
    
    def sendMergeInvestigation(self, simulationStep, position, swarmID, swarmSize, maxSwarmDepth, ownDepth):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 9
        messageData = mergeInvestigationMessage(swarmID, swarmSize, maxSwarmDepth, ownDepth)
        mergeRequestEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeRequestEvent)
            
    def sendPotentialMerge(self, simulationStep, position, ownSwarmID, potentialMergeSwarmID, requiredHops, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 10
        messageData = potentialMergeMessage(ownSwarmID, potentialMergeSwarmID, requiredHops, hopCount)
        potentialMergeEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(potentialMergeEvent)
    
    def sendMergeRequest(self, simulationStep, position, senderSwarmID, receiverSwarmID, leaderID, ownDepth, requiredHops, hopCount):
        self.messagesSend += 1
        nodes= self.nodes
        messageType = 11
        messageData = mergeRequestMessage(senderSwarmID, receiverSwarmID, leaderID, ownDepth, requiredHops, hopCount)
        mergeRequestEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeRequestEvent)
    
    def sendMergeAccept(self, simulationStep, position, senderSwarmID, receiverSwarmID, ownDepth, hopCount, members):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 12
        messageData = mergeAcceptMessage(senderSwarmID, receiverSwarmID, ownDepth, hopCount, members)
        mergeAcceptEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeAcceptEvent)
            
    def sendSwarmChange(self, simulationStep, position, oldSwarmID, newSwarmID, newLeader, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 13
        messageData = swarmChangeMessage(oldSwarmID, newSwarmID, newLeader, hopCount)
        swarmChangeEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(swarmChangeEvent)
            
    def sendDescendants(self, simulationStep, position, electionID, nodeID, parentID, noDescendants):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 14
        messageData = descendantsMessage(electionID, nodeID, parentID, noDescendants)
        descendantsEvent = event(simulationStep, position, messageType, messageData)     
        for node in nodes:
            node.eventQueue.addEvent(descendantsEvent)

    def sendElectionSize(self, simulationStep, position, electionID, nodeID, electionSize, neighbors, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 15
        messageData = electionSizeMessage(electionID, nodeID, electionSize, neighbors, hopCount)
        electionSizeEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(electionSizeEvent)
            
    def sendMergeElection(self, simulationStep, position, swarmID, nodeID, swarmSize, neighbors, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 16
        messageData = mergeElectionMessage(swarmID, nodeID, swarmSize, neighbors, hopCount)
        mergeElectionEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeElectionEvent)
            
    def sendMergeChild(self, simulationStep, position, swarmID, nodeID, mergeParentID):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 17
        messageData = mergeChildMessage(swarmID, nodeID, mergeParentID)
        mergeChildEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeChildEvent)
            
    def sendMergeAck(self, simulationStep, position, swarmID, nodeID, mergeParentID, bestCandidateID, nodeWeight, avrSignalStrength):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 18
        messageData = mergeAckMessage(swarmID, nodeID, mergeParentID, bestCandidateID, nodeWeight, avrSignalStrength)
        mergeAckEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeAckEvent)
            
    def sendMergeLeader(self, simulationStep, position, swarmID, leaderID, hopCount):
        self.messagesSend += 1
        nodes = self.nodes
        messageType = 19
        messageData = mergeLeaderMessage(swarmID, leaderID, hopCount)
        mergeLeaderMessage(swarmID, leaderID, hopCount)
        mergeLeaderEvent = event(simulationStep, position, messageType, messageData)
        for node in nodes:
            node.eventQueue.addEvent(mergeLeaderEvent)
        