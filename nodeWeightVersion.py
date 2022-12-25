# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 15:30:43 2022

@author: frederik
"""

import random
import math
import numpy as np
import communicationModule as cm
from swarmManager import Member
from swarmManager import Neighbor
from swarmManager import Child
from swarmManager import ExtendedNeighbor
from swarmManager import Leader
from swarmManager import DeeperNode
from swarmManager import bestCandidate
from messageClasses import eventQueue

class Node:
    
    def __init__(self, InitPosition, MaxSpeed, HopCount, WorkSpaceSize, ID, SimulationTime, swarmManager):
        """Init function for the node class"""
        #User specified parameters
        self.position = InitPosition
        self.maxSpeed = MaxSpeed
        self.hopCount = HopCount-1
        self.workSpaceSize = WorkSpaceSize
        self.simulationTime = SimulationTime
        self.id = ID
        
        #Hard coded parameters
        self.measurementsPerSec = 60
        self.communicationRange = 200
        self.heartbeatinterval = 1
        
        #Keeps track of steps taken
        self.simulationSteps = 0
        self.timeWithoutLeader = 0
        self.timeToLoseLeader = 0
        self.timeIsolated = 0
        self.timeInElection = 0
        self.timeDoingMerge = 0
        self.timeAsLeader = 0
        self.timeDoingMergeElection = 0
        self.numberOfLeaderElections = 0
        self.numberOfMerges = 0
        self.topologyChangesDuringElection = 0
        
        self.info = []
        
        self.swarmSynchronizationStep = 0 
        self.swarmSynchronized = False
        
        #Roles
        self.isLeader = False
        self.isCouncilOfLeadersMember = False
        
        #State flags
        self.inSwarm = False
        self.inElection = False
        self.tester = False 
        self.isSourceNode = False
        
        self.ackSend = False
        self.ackStep = 0
        self.childSend = False
        self.childStep = 0
        self.descendantsSend = False
        self.descendantsStep = 0
        self.discoverySend = False
        self.discoveryStep = 0
        self.discoveryAckSend = False
        self.discoveryAckStep = 0
        
        self.doingMerge = False
        self.mergeRequestStep = 0
        self.mergeRequestReceived = False
        self.mergeAcceptStep = 0
        self.mergeID = 0 
        
        self.doingMergeElection = False 
        self.mergeElectionStep = 0
        self.mergeChildStep = 0
        self.awaitingMergeAck = []
        self.mergeAckStep = 0
        self.mergeAckSend = False
        
        self.descendants = 0
        
        #Lists 
        self.eventQueue = eventQueue()
        self.neighborhood = []
        self.children = []
        self.awaitingAck = []
        self.awaitingDescendants = []
        self.councilOfLeaders = []
        self.role = []
        self.swarmMembers = []
        self.deeperNodes = []
        self.extendedNeighborhood = []
        
        self.parent = 0
        self.leader = Leader(0, 0)
        self.leaderHbTimestamp = 0
        self.bestCandidate = bestCandidate(0, 0, 0)
        self.electionID = 0
        self.electionHopCount = 0
        self.electionSize = 0
        
        self.swarmID = 0
        self.swarmDepth = 0
        self.swarmMaxDepth = 0
        self.swarmSize = 0
        
        #Variables used for capability computation
        self.batteryLevel = 100
        self.connectivity = 0
        self.averageSignalStrength = 0
        self.nodeWeight = 0
        
        #Communication module used to send massages to other nodes
        self.communicationModule = cm.communicationModule(self.communicationRange)
        
        self.swarmManager = swarmManager
        
        
        #Set initial destination, direction and speed to 0
        self.destination = (0, 0)
        self.direction = 0
        self.speed = 0
        
        #Arrays for storing position data
        self.PositionsX = []
        self.PositionsY = []
        self.PositionsX.append(self.position[0])
        self.PositionsY.append(self.position[1])
        self.role.append(0.1)
        
        #Get a destination for each node
        self.newDestination()
        
    def newDestination(self):
        """Create new destination and speed and calculate direction of node"""
        #Generate random x and y coordinate within the workspace
        newDestinationX = random.randint(0, self.workSpaceSize)
        newDestinationY = random.randint(0, self.workSpaceSize)
        
        #Calculate the direction from current position to the new destination and get new speed
        self.direction = math.atan2(newDestinationY-self.position[1], newDestinationX-self.position[0])
        self.destination = (newDestinationX, newDestinationY)
        self.speed = self.maxSpeed
        
    def updatePosition(self):
        """Calculate change in position, update position, save new position and increment simulation step"""
        #Get current position
        currentX = self.position[0]
        currentY = self.position[1]
        
        #Calculate the change in x and y 
        deltaX = 1/self.measurementsPerSec * self.speed * math.cos(self.direction)
        deltaY = 1/self.measurementsPerSec * self.speed * math.sin(self.direction)
        
        #Update position and increment simulation step
        self.position = (currentX + deltaX, currentY + deltaY)
        self.PositionsX.append(self.position[0])
        self.PositionsY.append(self.position[1])
        self.simulationSteps += 1
        
    def checkCommunicationRange(self, position):
        
        distance = math.sqrt(pow(position[0] - self.position[0], 2) + pow(position[1] - self.position[1], 2))
        
        if distance < self.communicationRange:
            return True
        
        else: 
            return False
        
    def signalStrength(self, position):
        
        distance = math.sqrt(pow(position[0] - self.position[0], 2) + pow(position[1] - self.position[1], 2))
        signalStrength = ((self.communicationRange - distance) / self.communicationRange) * 100 
        
        return signalStrength
            
    def updateNeighborhood(self, neighborID, nodeDepth, signalStrength):
        """Update neighborhood list"""
            #Check if neighborhood list is empty
        if not self.neighborhood:
            self.neighborhood.append(Neighbor(neighborID, nodeDepth, signalStrength, 0))
            self.updateConnectivity()
                
            #Check if the node is already part of the neighborhood
        else:
            partOfneighborhood = False
            for neighbor in self.neighborhood:
               
                if neighbor.nodeID == neighborID:
                    neighbor.counter = 0
                    neighbor.depth = nodeDepth
                    neighbor.signalStrength = signalStrength
                    partOfneighborhood = True
                    break

                #If not part of niegborhood add to neighborhood
            if not partOfneighborhood:
                self.updateConnectivity()
                self.neighborhood.append(Neighbor(neighborID, nodeDepth, signalStrength, 0))
                    
            #Update the connectivity as changes has happened to the neighborhood
        self.updateConnectivity()                                    
            
    def incrementNeighborhood(self):
        #Check if the neighborhood is not empty 
        if self.neighborhood:
            #Increment missed heartbeat counter
            for neighbor in self.neighborhood:
                neighbor.counter += 1
             
            for neighbor in self.neighborhood:
                
                if neighbor.counter > 2: #Check if more than 2 heartbeats have been missed and remove from different lists
                    self.neighborhood.remove(neighbor)
                    
                    if self.inElection:
                
                        if self.parent == neighbor.nodeID: #Check if node lost parent 
                            self.isSourceNode = True
                            self.electionSize = len(self.children)+self.descendants+1
                            self.childStep = self.simulationSteps+2
                            self.topologyChangesDuringElection += 1
                        
                        if self.children:
                            
                            for child in self.children: #Check if node lost a child 
                                if neighbor.nodeID == child.childID:
                                    self.children.remove(child)
                                    self.topologyChangesDuringElection += 1
                                    break
                            
                            for a in self.awaitingAck: #Check if node was waiting for that child
                                if neighbor.nodeID == a:
                                    self.awaitingAck.remove(a)
                                    break           
                                
                            for d in self.awaitingDescendants:
                                if neighbor.nodeID == d:
                                    self.awaitingDescendants.remove(d)
                                    break
                    
                    if self.doingMergeElection:             
                        
                        if self.parent == neighbor.nodeID:
                            self.isLeader = True
                            self.mergeChildStep = self.simulationSteps+2
                            self.topologyChangesDuringElection += 1
                            
                        if self.children:
                            for child in self.children: #Check if node lost a child 
                                if neighbor.nodeID == child.childID:
                                    self.children.remove(child)
                                    self.topologyChangesDuringElection += 1
                                    break
                                
                            for a in self.awaitingMergeAck:
                                if neighbor.nodeID == a:
                                    self.awaitingMergeAck.remove(a)
                            
                             
        if self.inSwarm and not self.isLeader:
            self.leader.counter += 1
            
            if self.leader.counter > 2: #if leader has been lost
                self.lostLeader()
                
        if self.extendedNeighborhood:
                    for extendedNeighbor in self.extendedNeighborhood:
                        extendedNeighbor.counter += 1
                    
                    for extendedNeighbor in self.extendedNeighborhood:
                        if extendedNeighbor.counter > 2:
                            self.extendedNeighborhood.remove(extendedNeighbor)
            
    def resetElection(self):
        self.descendantsSend = False
        self.descendantsStep = 0
        self.bestCandidate = bestCandidate(0, 0, 0)
        self.electionHopCount = 0
        self.electionID = 0
        self.electionSize = 0
        self.inElection = False
        self.isSourceNode = False
        self.parent = 0
        self.childStep = 0
        self.childSend = False
        self.children = []
        self.awaitingAck = []
        self.awaitingDescendants = []
        self.deeperNodes = []
        self.ackSend = False
        self.ackStep = 0
        
    def resetDepthDiscovery(self):
        self.discoveryStep = 0
        self.discoveryAckStep = 0
        self.discoveryAckSend = False
        self.swarmSynchronizationStep = 0
        self.deeperNodes = []
        
    def resetMerge(self):
        self.doingMerge = False
        self.mergeID = 0
        self.mergeRequestStep = 0
        self.mergeRequestReceived = False
        self.mergeAcceptStep = 0
        
    def resetMergeElection(self):
        self.doingMergeElection = False 
        self.mergeElectionStep = 0
        self.mergeChildStep = 0
        self.awaitingMergeAck = []
        self.mergeAckStep = 0
        self.mergeAckSend = False
        self.children = []
        
    def lostLeader(self):
        
        self.swarmManager.removeMember(self.swarmID, self.id)
        
        self.inSwarm = False
        self.tester = True
        self.swarmID = 0
        self.electionID = 0 
        self.leader = Leader(0,0)
        self.neighborhood = []
        self.extendedNeighborhood = []
        self.swarmDepth = 0
        self.swarmMaxDepth = 0 
        self.swarmSize = 0
        self.resetDepthDiscovery()
        self.resetMerge()
        self.resetMergeElection()
        self.doingMerge = False
        self.doingMergeElection = False
        self.timeWithoutLeader += (self.heartbeatinterval*self.measurementsPerSec*2)
        self.timeToLoseLeader += (self.heartbeatinterval*self.measurementsPerSec*2)
                
    def updateBatteryLevel(self):
        #Check if node is leader and then update battery level
        if self.isLeader:
            self.batteryLevel -= 0.00127
            
        else:
            self.batteryLevel -= 0.00111
    
    def updateConnectivity(self):
        #Calculate he combined signal strength
        extendedNeighbors = []
        for extendedNeighbor in self.extendedNeighborhood:
            if extendedNeighbor.nodeID not in extendedNeighbors:
                extendedNeighbors.append(extendedNeighbor.nodeID)
            
        self.connectivity = len(extendedNeighbors) + len(self.neighborhood)
        
    def updateAverageSignalStrength(self):
        
        combinedSignalStrength = 0
        
        if not self.neighborhood:
            print("test")
        
        for neighbor in self.neighborhood:
            combinedSignalStrength += neighbor.signalStrength
            
        self.averageSignalStrength = combinedSignalStrength/len(self.neighborhood)
        
    def updateExtendedNeighborhood(self, nodeID, nodeDepth, source):
        
        if not self.extendedNeighborhood:#if list is empty
            self.extendedNeighborhood.append(ExtendedNeighbor(nodeID, nodeDepth, source, 0))
            self.updateConnectivity()
            
        else:#Check if already part of list
            alreadyInList = False
            for extendedNeighbor in self.extendedNeighborhood:
                if extendedNeighbor.nodeID == nodeID and extendedNeighbor.source == source:
                    extendedNeighbor.depth = nodeDepth
                    extendedNeighbor.counter = 0
                    alreadyInList = True
                    break
                    
            if not alreadyInList:#if not already in the list add to and sort list 
                self.extendedNeighborhood.append(ExtendedNeighbor(nodeID, nodeDepth, source, 0))
                self.extendedNeighborhood.sort(key = lambda extendedNeighbor: extendedNeighbor.nodeID, reverse = False)
                self.updateConnectivity()
                
    def updateDeeperNodes(self, nodeID, nodeDepth):
        
        if not self.deeperNodes:
            self.deeperNodes.append(DeeperNode(nodeID, nodeDepth))
            
        else:
            alreadyInList = False
            for deeperNode in self.deeperNodes:
                if deeperNode.nodeID == nodeID:
                    alreadyInList = True
                    break
                
            if not alreadyInList:
                self.deeperNodes.append(DeeperNode(nodeID, nodeDepth))
                
    def updateSwarmMembers(self, nodeID, nodeDepth):
        
        if not self.swarmMembers:#Check if list is empty 
            self.swarmMembers.append(Member(nodeID, nodeDepth))
            self.swarmSize = len(self.swarmMembers)+1
        
        else: #Check if already in list 
            alreadyInList = False
            for member in self.swarmMembers:
                if member.nodeID == nodeID:
                    member.depth = nodeDepth
                    alreadyInList = True
                    break
            
            if not alreadyInList: # if not already in list 
                self.swarmMembers.append(Member(nodeID, nodeDepth))
                
    def partOfneighborhood(self, nodeID):
        
        if self.id == nodeID:
            return True 
        
        for neighbor in self.neighborhood:
            if neighbor.nodeID == nodeID:
                return True
        
        return False
    
        
    def calculateNodeWeight(self):
        
        connectivityWeight = 0.80
        batteryWeight = 0.20
        
        if self.inElection:
            
            if self.electionSize == 0:
                print("test")
        
            connectivity = (self.connectivity/self.electionSize) * connectivityWeight
            battery = (self.batteryLevel/100) * batteryWeight
        
        
        elif self.inSwarm:
            
            if self.swarmSize == 1:
                print("test")
       
            connectivity = (self.connectivity/(self.swarmSize-1)) * connectivityWeight
            battery = (self.batteryLevel/100) * batteryWeight
        
        self.nodeWeight = connectivity + battery
        
    
    def eventHandler(self, event):
        position = event.position
        if self.checkCommunicationRange(position):
            messageType = event.messageType
            messageData = event.messageData
        
            if messageType == 1:
                self.heartbeatMessage(messageData, position)
            
            elif messageType == 2:
                self.electionMessage(messageData, position)
            
            elif messageType == 3:
                self.childMessage(messageData, position)
            
            elif messageType == 4:
                self.ackMessage(messageData)
            
            elif messageType == 5:
                self.leaderMessage(messageData)
            
            elif messageType == 6:
                self.leaderHeartbeat(messageData, position)
            
            elif messageType == 7:
                self.depthDiscoveryMessage(messageData)
            
            elif messageType == 8:
                self.discoveryAckMessage(messageData)
            
            elif messageType == 9:
                self.mergeInvestigationMessage(messageData)
            
            elif messageType == 10:
                self.potentialMergeMessage(messageData)
            
            elif messageType == 11:
                self.mergeRequestMessage(messageData)
            
            elif messageType == 12:
                self.mergeAcceptMessage(messageData)
            
            elif messageType == 13:
                self.changeSwarmMessage(messageData)
                
            elif messageType == 14:
                self.descendantMessage(messageData, position)
                
            elif messageType == 15:
                self.electionSizeMessage(messageData)
                
            elif messageType == 16:
                self.mergeElectionMessage(messageData)
                
            elif messageType == 17:
                self.mergeChildMessage(messageData)
                
            elif messageType == 18:
                self.mergeAckMessage(messageData)
                
            elif messageType == 19:
                self.mergeLeaderMessage(messageData)
                
                
            
    def heartbeatMessage(self, heartbeatMessage, position):
        #|swarmID|electionID|nodeID|nodeDepth|deeperNodes|
        
        swarmID = heartbeatMessage.swarmID
        electionID = heartbeatMessage.electionID
        nodeID = heartbeatMessage.nodeID
        nodeDepth = heartbeatMessage.nodeDepth
        extendedNeighborhood = heartbeatMessage.neighborhood
        
        if self.inSwarm:
            
            if swarmID == self.swarmID: #Check if heartbeat comes from node within swarm
                signalStrength = self.signalStrength(position)
                self.updateNeighborhood(nodeID, nodeDepth, signalStrength)  
                
               
                for extendedNeighbor in extendedNeighborhood:
                    partOfneighborhood = self.partOfneighborhood(extendedNeighbor.nodeID)
                    if not partOfneighborhood:
                        self.updateExtendedNeighborhood(extendedNeighbor.nodeID, extendedNeighbor.depth, nodeID)
                
            elif swarmID != self.swarmID and self.swarmDepth < self.hopCount: #Check if a merge potentially can be done
                
                if not self.doingMerge and self.swarmSynchronized:
                    self.communicationModule.sendMergeInvestigation(self.simulationSteps+1, self.position, self.swarmID, self.swarmSize, self.swarmMaxDepth, self.swarmDepth)
                            
        elif not self.inSwarm: #If not in swarm add to neighborhood of nodes without swarm
            
            if self.inElection: 
                if swarmID == 0 and electionID == self.electionID:
                    signalStrength = self.signalStrength(position)
                    self.updateNeighborhood(nodeID, 0, signalStrength)
                    
                if extendedNeighborhood:
                    for extendedNeighbor in extendedNeighborhood:
                        partOfneighborhood = self.partOfneighborhood(extendedNeighbor.nodeID)
                        if not partOfneighborhood:
                            self.updateExtendedNeighborhood(extendedNeighbor.nodeID, 0, nodeID)
        
            elif swarmID == 0 and electionID == 0:
                signalStrength = self.signalStrength(position)
                self.updateNeighborhood(nodeID, 0, signalStrength)
    
    def electionMessage(self, electionMessage, position):
        #|electionID|NodeID|receivedFrom|HopCount|
        
        electionID = electionMessage.electionID
        nodeID = electionMessage.nodeID
        hopCount = electionMessage.hopCount
        
        #Partake in election if not in swarm and not in another election
        if not self.inElection and not self.inSwarm:
            self.inElection = True
            self.bestCandidate = bestCandidate(self.id, 0, 0)
            self.electionID = electionID
            
            self.parent = nodeID
            self.electionHopCount = hopCount
            signalStrength = self.signalStrength(position)
            self.updateNeighborhood(nodeID, 0, signalStrength)
        
        #Check if part of election but has not send child message 
        elif self.inElection and not self.childSend:
            #If election has higher id partake in this election instead
            if electionID > self.electionID and electionID != self.electionID:
                
                self.parent = nodeID
                self.electionID = electionID
                self.electionHopCount = hopCount
                self.neighborhood = []
                self.extendedNeighborhood = []
                signalStrength = self.signalStrength(position)
                self.updateNeighborhood(nodeID, 0, signalStrength)
                
                if self.isSourceNode:
                    self.isSourceNode = False   
                    
            elif electionID == self.electionID:
                signalStrength = self.signalStrength(position)
                self.updateNeighborhood(nodeID, 0, signalStrength)
                
    def childMessage(self, childMessage, position): 
        #|electionID|nodeID|parentID|
        
        electionID = childMessage.electionID
        nodeID = childMessage.nodeID
        parentID = childMessage.parentID
        
        if electionID == self.electionID:
            if parentID == self.id:
                self.children.append(Child(nodeID, 0, 0, 0))
                self.awaitingAck.append(nodeID)
                self.awaitingDescendants.append(nodeID)
                signalStrength = self.signalStrength(position)
                self.updateNeighborhood(nodeID, 0, signalStrength)

            
    def ackMessage(self, ackMessage):
        #|electionID|nodeID|parentID|bestCandidateID|nodeWeight|averageSignalStrength|
        
        electionID = ackMessage.electionID
        nodeID = ackMessage.nodeID
        parentID = ackMessage.parentID
        bestCandidateID = ackMessage.bestCandidate
        nodeWeight = ackMessage.nodeWeight
        avrSignalStrength = ackMessage.avrSignalStrength
        
        if electionID == self.electionID:
            if parentID == self.id:
                for child in self.children:
                    if child.childID == nodeID:
                        child.bestCandidate = bestCandidateID
                        child.nodeWeight = nodeWeight
                        child.avrSignalStrength = avrSignalStrength
                        break
                    
                for i in self.awaitingAck:
                    if i == nodeID:
                        self.awaitingAck.remove(i)
                        break
                        
                if not self.isSourceNode and not self.awaitingAck:
                    if self.electionSize > 0:
                        self.findBestCandidate()
                        self.communicationModule.sendAckMessage(self.simulationSteps+1, self.position, self.electionID, self.id, self.parent, self.bestCandidate.candidateID, self.bestCandidate.nodeWeight, self.bestCandidate.avrSignalStrength)
                        self.ackSend = True
            
    def leaderMessage(self, leaderMessage):
        #|electionID|sourceNodeID|swarmSize|leaderID|hopCount|
        
        electionID = leaderMessage.electionID
        sourceNodeID = leaderMessage.sourceNodeID
        swarmSize = leaderMessage.swarmSize
        leaderID = leaderMessage.leaderID
        hopCount = leaderMessage.hopCount
        
        if electionID == self.electionID and self.inElection:
            self.inSwarm = True
            self.swarmID = leaderID
            self.swarmSize = swarmSize
            
            
            if leaderID == self.id:
                self.isLeader = True
                self.discoveryStep = self.simulationSteps+2*self.hopCount
                self.resetElection()
            
            else:
                self.leader = Leader(leaderID, 0)
                self.swarmManager.addMember(self.swarmID, self.id)
                self.resetElection()
            
            if hopCount > 0:
                self.communicationModule.sendLeaderMessage(self.simulationSteps+1, self.position, electionID, sourceNodeID, swarmSize, leaderID, hopCount-1)
    
    def leaderHeartbeat(self, leaderHeartbeat, position):
        #|swarmID|leaderID|swarmSize|maxSwarmDepth|timestamp|hopCount|    
        
        swarmID = leaderHeartbeat.swarmID
        leaderID = leaderHeartbeat.leaderID
        swarmSize = leaderHeartbeat.swarmSize
        maxSwarmDepth = leaderHeartbeat.maxSwarmDepth
        timeStamp = leaderHeartbeat.timeStamp
        hopCount = leaderHeartbeat.hopCount
        
        if self.inSwarm and not self.isLeader: 
            
            if swarmID == self.swarmID and leaderID == self.leader.leaderID:#Check if heartbeat was from swarm leader
            
                if timeStamp > self.leaderHbTimestamp: #Ignore relayed heartbeats already heard
                    oldDepth = self.swarmDepth
                    newDepth = self.hopCount - (hopCount-1)  
                    self.leaderHbTimestamp = timeStamp
                    self.leader.counter = 0
                    self.swarmDepth = self.hopCount - (hopCount-1)  
                    self.swarmSize = swarmSize
                    self.swarmMaxDepth = maxSwarmDepth
                    if oldDepth != newDepth:
                        self.swarmManager.updateMember(self.swarmID, self.id, self.swarmDepth)
                    
                    if hopCount == self.hopCount: #If message has not been relayed then leader is in direct neighborhood
                        signalStrength = self.signalStrength(position)
                        self.updateNeighborhood(leaderID, 0, signalStrength)
                        self.communicationModule.sendLeaderHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.leader.leaderID, self.swarmSize, self.swarmMaxDepth, timeStamp, hopCount-1)
                    
                    elif hopCount < self.hopCount and hopCount > 0: #If not in direct neighborhood relay message
                        self.communicationModule.sendLeaderHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.leader.leaderID, self.swarmSize, self.swarmMaxDepth, timeStamp, hopCount-1)
            
            elif swarmID != self.swarmID and not self.doingMerge and self.swarmSynchronized: #If heartbeat if from another swarm and not currently doing a merge
                self.communicationModule.sendMergeInvestigation(self.simulationSteps+1, self.position, self.swarmID, self.swarmSize, self.swarmMaxDepth, self.swarmDepth)
        
        elif self.inSwarm and self.isLeader: #If leader and heartbeat is from another swarm start merge if not already doing merge
            if self.id != swarmID and not self.doingMerge and self.swarmSynchronized:
                self.communicationModule.sendMergeInvestigation(self.simulationSteps+1, self.position, self.swarmID, self.swarmSize, self.swarmMaxDepth, self.swarmDepth)
                
    def depthDiscoveryMessage(self, depthDiscoveryMessage):
        #|swarmID|leaderID|hopCount|
        
        swarmID = depthDiscoveryMessage.swarmID
        leaderID = depthDiscoveryMessage.leaderID
        hopCount = depthDiscoveryMessage.hopCount
        
        
        if self.inSwarm and self.swarmID == swarmID and self.leader.leaderID == leaderID:
            
            if not self.discoverySend:
                
                if hopCount > 0:
                    self.communicationModule.sendDepthDiscoveryMessage(self.simulationSteps+1, self.position, self.swarmID, self.leader.leaderID, hopCount-1)
                    self.discoverySend = True
                    self.discoveryAckSend = False
                    self.discoveryAckStep = self.simulationSteps+(2*hopCount)
                
                else:
                    self.communicationModule.sendDiscoveryAckMessage(self.simulationSteps+1, self.position, self.swarmID, self.id, self.swarmDepth, [])
                    self.swarmSynchronized = True
                    self.resetDepthDiscovery()
                    
    def discoveryAckMessage(self, discoveryAckMessage):
        #|swarmID|nodeID|nodeDepth|deeperNodes|
        
        swarmID = discoveryAckMessage.swarmID
        nodeID = discoveryAckMessage.nodeID
        nodeDepth = discoveryAckMessage.nodeDepth
        deeperNodes = discoveryAckMessage.deeperNodes
        
        if self.inSwarm and self.swarmID == swarmID:
            
            if not self.isLeader:
            
                if self.swarmDepth < nodeDepth:
                    self.deeperNodes.append(DeeperNode(nodeID, nodeDepth))
                    if deeperNodes:
                        for node in deeperNodes:
                            self.updateDeeperNodes(node.nodeID, node.depth)
                    
            else:
                for deeperNode in deeperNodes:
                    self.updateSwarmMembers(deeperNode.nodeID, deeperNode.depth)
                
    def mergeInvestigationMessage(self, mergeInvestigationMessage):
        #|swarmID|swarmSize|maxSwarmDepth|owndepth|
        
        swarmID = mergeInvestigationMessage.swarmID
        swarmSize = mergeInvestigationMessage.swarmSize
        maxSwarmDepth = mergeInvestigationMessage.maxSwarmDepth
        senderDepth = mergeInvestigationMessage.senderDepth
        
        if not self.doingMerge and self.swarmSynchronized:
            
            if swarmID != self.swarmID: #Merge investigation received from another swarm
                canAbsorb = False
                canBeAbsorbed = False
                requiredHops = 0
                
                if self.hopCount >= (senderDepth + maxSwarmDepth + self.swarmDepth): #Check if all nodes in other swarm can be reached by own leader within hopCount
                    self.doingMerge = True
                    canAbsorb = True
                    requiredHops = self.swarmDepth + senderDepth
                        
                if self.hopCount >= (self.swarmMaxDepth + self.swarmDepth + senderDepth): #Check if all nodes in own swarm can be reached by other leader within hopCount
                    self.doingMerge = True
                    canBeAbsorbed = True
                    
                if canAbsorb and canBeAbsorbed: #If both can absorb or be absorbed 
                    self.mergeID = swarmID
                    self.numberOfMerges += 1
                
                    if self.swarmSize < swarmSize: #Smaller swarm prepares to be absorbed awaiting a merge request
                        self.mergeRequestStep = self.simulationSteps+1 + senderDepth*2
                        
                    elif self.swarmSize > swarmSize: #larger swarm prepares to absorb other swarm 
                    
                        if not self.isLeader: #If a node did the merge investigation send the potential towards the leader and await a merge request 
                            self.communicationModule.sendPotentialMerge(self.simulationSteps+1, self.position, self.swarmID, swarmID, requiredHops, self.swarmDepth-1)
                            self.mergeRequestStep = self.simulationSteps + self.swarmDepth*2
                        
                        else: # if leader did the merge investigation send a merge request and await a merge accept 
                            self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, self.swarmID, swarmID, self.id, self.swarmDepth, requiredHops, senderDepth)
                            self.mergeAcceptStep = self.simulationSteps+2 + senderDepth*2
                    
                    elif self.swarmSize == swarmSize:#If swarms are the same size then the swarm with the highest ID absorbs the other 
                        
                        if self.swarmID < swarmID: #if swarm with smaller ID await merge request
                            self.mergeRequestStep = self.simulationSteps+1 + senderDepth*2
                        
                        elif self.swarmID > swarmID: #If swarm with larger ID
                        
                            if not self.isLeader: #If a node did the merge investigation send the potential merge to the leader and await a merge request
                                self.communicationModule.sendPotentialMerge(self.simulationSteps+1, self.position, self.swarmID, swarmID, requiredHops, self.swarmDepth-1)
                                self.mergeRequestStep = self.simulationSteps + self.swarmDepth*2
                            
                            else: #If a leader did the merge investigation send a merge request and await a merge accept
                                self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, self.swarmID, swarmID, self.id, self.swarmDepth, requiredHops, senderDepth)
                                self.mergeAcceptStep = self.simulationSteps+2 + senderDepth*2
                
                elif canAbsorb and not canBeAbsorbed: #If swarm can only absorb and not be absorbed
                    self.mergeID = swarmID
                    self.numberOfMerges += 1
                
                    if not self.isLeader: #If a node did the merge investigation send potential merge and await merge request
                        self.communicationModule.sendPotentialMerge(self.simulationSteps+1, self.position, self.swarmID, swarmID, requiredHops, self.swarmDepth-1)
                        self.mergeRequestStep = self.simulationSteps + self.swarmDepth*2
                    
                    else: #If leader did the merge investigation send merge request and await merge accept
                        self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, self.swarmID, swarmID, self.id, self.swarmDepth, requiredHops, senderDepth)
                        self.mergeAcceptStep = self.simulationSteps+2 + senderDepth*2
                
                elif canBeAbsorbed and not canAbsorb: #iF swarm can only be absorbed and not absorb other swarm set merge ID and await merge request
                    self.mergeID = swarmID
                    self.numberOfMerges += 1
                    self.mergeRequestStep = self.simulationSteps+1 + senderDepth*2         

    def potentialMergeMessage(self, potentialMergeMessage):
        #|SwarmID|potentialMergeSwarmID|requiredHops|hopCount|
        
        swarmID = potentialMergeMessage.swarmID
        potentialMergeSwarmID = potentialMergeMessage.pmSwarmID
        requiredHops = potentialMergeMessage.requiredHops
        hopCount = potentialMergeMessage.hopCount
        
        if not self.isLeader: #If swarm member receives potential merge from other member
            
            if not self.doingMerge and self.swarmSynchronized:
            
                if self.swarmID == swarmID and self.swarmDepth == hopCount: #If hop Count is the same as depth means message came from deeper node 
                    self.doingMerge = True
                    self.mergeID = potentialMergeSwarmID
                    self.numberOfMerges += 1
                    self.mergeRequestStep = self.simulationSteps + self.swarmDepth*2
                    self.communicationModule.sendPotentialMerge(self.simulationSteps+1, self.position, self.swarmID, potentialMergeSwarmID, requiredHops, hopCount-1)
        
        else: #if leader receives potential merge request check if doing other merge
            
            if not self.doingMerge and self.swarmSynchronized: #If not doing another merge
            
                if self.swarmID == swarmID: 
                    self.doingMerge = True 
                    self.mergeID = potentialMergeSwarmID
                    self.numberOfMerges += 1
                    self.mergeAcceptStep = self.simulationSteps+2 + requiredHops*2
                    self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, self.swarmID, potentialMergeSwarmID, self.id, self.swarmDepth, requiredHops, requiredHops)
                    
    def mergeRequestMessage(self, mergeRequestMessage):
        #|senderSwarmID|receiverSwarmID|leaderID|ownDepth|requiredHops|hopCount|
        
        senderSwarmID = mergeRequestMessage.senderSwarmID
        receiverSwarmID = mergeRequestMessage.receiverSwarmID
        leaderID = mergeRequestMessage.leaderID
        relayerDepth = mergeRequestMessage.relayerDepth
        requiredHops = mergeRequestMessage.requiredHops
        hopCount = mergeRequestMessage.hopCount
        
        if not self.isLeader: #If node receives merge request 
            
            if self.doingMerge: #check if already part of a merge
            
                if not self.mergeRequestReceived:
            
                    if self.mergeID == receiverSwarmID and self.swarmID == senderSwarmID: #if part of swarm sending merge request
                    
                        if relayerDepth < self.swarmDepth: #If deeper than node message is received from forward message and await merge accept
                            self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, senderSwarmID, receiverSwarmID, leaderID, self.swarmDepth, requiredHops, hopCount-1)
                            self.mergeRequestReceived = True
                            self.mergeAcceptStep = self.simulationSteps+2 + hopCount*2
                            
                            
                    elif self.swarmID == receiverSwarmID and self.mergeID == senderSwarmID: #If part of swarm awaiting merge request 
                        
                        if self.swarmDepth == hopCount:#check if hop count is the same as own depth
                            self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, senderSwarmID, receiverSwarmID, leaderID, self.swarmDepth, requiredHops, hopCount-1)
                            self.mergeRequestReceived = True
                            self.mergeAcceptStep = self.simulationSteps + self.swarmDepth*2
                            
            elif not self.doingMerge and self.swarmSynchronized: #If not already part of a merge
                
                if self.swarmID == receiverSwarmID:
                    if self.swarmDepth == hopCount:
                        self.communicationModule.sendMergeRequest(self.simulationSteps+1, self.position, senderSwarmID, receiverSwarmID, leaderID, self.swarmDepth, requiredHops, hopCount-1)
                        self.mergeRequestReceived = True
                        self.doingMerge = True
                        self.numberOfMerges += 1
                        self.mergeID = senderSwarmID
                        self.mergeAcceptStep = self.simulationSteps + self.swarmDepth*2
                            
        else:#if a leader receives a merge request
            
            if self.swarmSynchronized:
        
                if not self.doingMerge: #check if already part of a merge 
                
                    if self.swarmID == receiverSwarmID or self.mergeID == senderSwarmID: #Check if the merge reguest matches the merge leader is partaking in. Send merge accept and swarm change message
                        self.communicationModule.sendMergeAccept(self.simulationSteps+1, self.position, self.swarmID, senderSwarmID, self.swarmDepth, requiredHops, self.swarmMembers)
                        self.communicationModule.sendSwarmChange(self.simulationSteps+1, self.position, self.swarmID, senderSwarmID, leaderID, self.swarmMaxDepth)
                        self.swarmManager.addMember(senderSwarmID, self.id)
                        self.swarmDepth = 0
                        self.isLeader = False
                        self.swarmSynchronized = False
                        self.discoverySend = False
                        self.numberOfMerges += 1
                        self.swarmMembers = []
                        self.leader = Leader(leaderID, 0)
                        self.swarmID = senderSwarmID
                        self.resetMerge()
                        
                elif self.doingMerge and self.mergeID == senderSwarmID: #If already doing a merge check if this is the awaited merge request
                        self.communicationModule.sendMergeAccept(self.simulationSteps+1, self.position, self.swarmID, senderSwarmID, self.swarmDepth, requiredHops, self.swarmMembers)
                        self.communicationModule.sendSwarmChange(self.simulationSteps+1, self.position, self.swarmID, senderSwarmID, leaderID, self.swarmMaxDepth)
                        self.swarmManager.addMember(senderSwarmID, self.id)
                        self.swarmDepth = 0
                        self.isLeader = False
                        self.swarmSynchronized = False
                        self.discoverySend = False
                        self.swarmMembers = []
                        self.leader = Leader(leaderID, 0)
                        self.swarmID = senderSwarmID
                        self.resetMerge()
                
    def mergeAcceptMessage(self, mergeAcceptMessage):
        #|senderSwarmID|receiverSwarmID|owndepth|hopCount|members|
        
        senderSwarmID = mergeAcceptMessage.senderSwarmID
        receiverSwarmID = mergeAcceptMessage.receiverSwarmID
        relayerDepth = mergeAcceptMessage.relayerDepth
        hopCount = mergeAcceptMessage.hopCount
        newMembers = mergeAcceptMessage.members
        
        if not self.isLeader: #If node receives merge accept message 
            
            if self.doingMerge:
                
                if self.swarmID == senderSwarmID and self.mergeID == receiverSwarmID:
                
                    if relayerDepth < self.swarmDepth: #If part of swarm sending the merge accept message only forward if message was received from node with smaller depth
                        self.communicationModule.sendMergeAccept(self.simulationSteps+1, self.position, senderSwarmID, receiverSwarmID, self.swarmDepth, hopCount-1, newMembers)
                        self.resetMerge()
                
                elif self.swarmID == receiverSwarmID and self.mergeID == senderSwarmID: #If part of swarm awaiting merge accept message 
                    
                    if self.swarmDepth == hopCount: #Check if own depth matches hop count if so forward merge accept
                        self.communicationModule.sendMergeAccept(self.simulationSteps+1, self.position, senderSwarmID, receiverSwarmID, self.swarmDepth, hopCount-1, newMembers)  
                        self.resetMerge()
       
        else: #If leader receives a merge accept message
            if self.doingMerge:
                if self.swarmID == receiverSwarmID and self.mergeID == senderSwarmID: #Check if merge is the one the leader currently is partaking in 
                    self.swarmSynchronized = False
                    self.mergeElectionStep = self.simulationSteps + self.measurementsPerSec*self.heartbeatinterval
                    self.resetMerge()
                    for member in newMembers:
                        self.updateSwarmMembers(member.nodeID, 0)
                
            
    def changeSwarmMessage(self, changeSwarmMessage):
        #|oldSwarmID|newSwarmID|newLeaderID|hopCount|
        
        oldSwarmID = changeSwarmMessage.oldSwarmID
        newSwarmID = changeSwarmMessage.newSwarmID
        newLeaderID = changeSwarmMessage.newLeaderID
        hopCount = changeSwarmMessage.hopCount
        
        if not self.isLeader:
            
            if self.swarmID == oldSwarmID:
                self.swarmManager.removeMember(oldSwarmID, self.id)
                self.swarmManager.addMember(newSwarmID, self.id)
                self.swarmID = newSwarmID
                self.swarmDepth = 0
                self.leader = Leader(newLeaderID, 0)
                self.swarmSynchronized = False
                self.resetMerge()
                
                if hopCount > 0:
                    self.communicationModule.sendSwarmChange(self.simulationSteps+1, self.position, oldSwarmID, newSwarmID, newLeaderID, hopCount-1)    
                
    def descendantMessage(self, descendantMessage, position):
        
        electionID = descendantMessage.electionID
        nodeID = descendantMessage.nodeID
        parentID = descendantMessage.parentID
        noDescendants = descendantMessage.noDescendants
        
        if self.inElection and electionID == self.electionID:
            if parentID == self.id:
                for child in self.children:
                    if child.childID == nodeID:
                        self.descendants += noDescendants
                        break
                    
                for d in self.awaitingDescendants:
                    if nodeID == d:
                        self.awaitingDescendants.remove(d)
                        break
                    
                if not self.isSourceNode and not self.awaitingDescendants:
                    self.communicationModule.sendDescendants(self.simulationSteps+1, self.position, self.electionID, self.id, self.parent, self.descendants+len(self.children))
                    self.descendantsSend = True
                    
                elif self.isSourceNode and not self.awaitingDescendants:
                    self.electionSize = len(self.children)+self.descendants+1
                    self.communicationModule.sendElectionSize(self.simulationSteps+1, self.position, self.electionID, self.id, self.electionSize, self.neighborhood, self.hopCount)
            
            else:
                signalStrength = self.signalStrength(position)
                self.updateNeighborhood(nodeID, 0, signalStrength)
            
    def electionSizeMessage(self, electionSizeMessage):
        
        electionID = electionSizeMessage.electionID
        nodeID = electionSizeMessage.nodeID
        electionSize = electionSizeMessage.electionSize
        neighbors = electionSizeMessage.neighbors
        hopCount = electionSizeMessage.hopCount
        
        if self.electionID == electionID:
            for neighbor in neighbors:
                partOfneighborhood = self.partOfneighborhood(neighbor.nodeID)
                if not partOfneighborhood:
                    self.updateExtendedNeighborhood(neighbor.nodeID, 0, nodeID)
        
        
        if self.electionSize == 0:
            self.electionSize = electionSize
            
            if hopCount > 0:
                self.communicationModule.sendElectionSize(self.simulationSteps+1, self.position, self.electionID, self.id, self.electionSize, self.neighborhood, hopCount-1)
                self.ackStep = self.simulationSteps+2 + hopCount*2
                
            else:
                self.communicationModule.sendHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.electionID, self.id, 0, self.neighborhood)
                self.ackStep = self.simulationSteps+2
                
    def mergeElectionMessage(self, mergeElectionMessage):
        
        swarmID = mergeElectionMessage.swarmID
        nodeID = mergeElectionMessage.nodeID
        swarmSize = mergeElectionMessage.swarmSize
        neighbors = mergeElectionMessage.neighbors
        hopCount = mergeElectionMessage.hopCount
        
        if not self.isLeader:
        
            if self.swarmID == swarmID:
                for neighbor in neighbors:
                    partOfneighborhood = self.partOfneighborhood(neighbor.nodeID)
                    if not partOfneighborhood:
                        self.updateExtendedNeighborhood(neighbor.nodeID, 0, nodeID)
                
                if not self.doingMergeElection:
                    self.parent = nodeID
                    self.doingMergeElection = True
                    self.swarmSynchronized = False
                    self.mergeChildStep = self.simulationSteps+2
                    
                    self.communicationModule.sendMergeChild(self.simulationSteps+1, self.position, self.swarmID, self.id, self.parent)
                    
                    if hopCount > 0:
                        self.communicationModule.sendMergeElection(self.simulationSteps+1, self.position, self.swarmID, self.id, swarmSize, self.neighborhood, hopCount-1)            
                    
                    else:
                        self.communicationModule.sendHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.electionID, self.id, self.swarmDepth, self.neighborhood)
                        self.mergeAckStep = self.simulationSteps+1
                    
    def mergeChildMessage(self, mergeChildMessage):
        
        swarmID = mergeChildMessage.swarmID
        nodeID = mergeChildMessage.nodeID
        mergeParentID = mergeChildMessage.mergeParentID
        
        if swarmID == self.swarmID:
            if mergeParentID == self.id:
                self.children.append(Child(nodeID, 0, 0, 0))
                self.awaitingMergeAck.append(nodeID)      
        
    def mergeAckMessage(self, mergeAckMessage):
        
        swarmID = mergeAckMessage.swarmID
        nodeID = mergeAckMessage.nodeID
        parentID = mergeAckMessage.mergeParentID
        bestCandidateID = mergeAckMessage.bestCandidateID
        nodeWeight = mergeAckMessage.nodeWeight
        avrSignalStrength = mergeAckMessage.avrSignalStrength
        
        if swarmID == self.swarmID:
            if parentID == self.id:
                for child in self.children:
                    if child.childID == nodeID:
                        child.bestCandidate = bestCandidateID
                        child.nodeWeight = nodeWeight
                        child.avrSignalStrength = avrSignalStrength
                        
                for a in self.awaitingMergeAck:
                    if a == nodeID:
                        self.awaitingMergeAck.remove(a)
           
                if not self.awaitingMergeAck and not self.isLeader:
                    self.findBestCandidate()
                    self.communicationModule.sendMergeAck(self.simulationSteps+1, self.position, self.swarmID, self.id, self.parent, self.bestCandidate.candidateID, self.bestCandidate.nodeWeight, self.bestCandidate.avrSignalStrength)
                    self.mergeAckSend = True
        
    def mergeLeaderMessage(self, mergeLeaderMessage):
        
        swarmID = mergeLeaderMessage.swarmID 
        leaderID = mergeLeaderMessage.leaderID
        hopCount = mergeLeaderMessage.hopCount
        
        if swarmID == self.swarmID:
            oldSwarmID = self.swarmID
            self.resetMergeElection()
            self.swarmManager.removeMember(self.swarmID, self.id)
            self.swarmID = leaderID
            
            if self.id == leaderID:
                self.isLeader = True
                self.leader.leaderID = 0
                self.leader.counter = 0
                self.swarmDepth = 0
                self.swarmSynchronizationStep = self.simulationSteps+1 + hopCount*2
                
            else:
                self.swarmManager.addMember(self.swarmID, self.id)
                self.leader.leaderID = leaderID
                
            if hopCount > 0:
               self.communicationModule.sendMergeLeader(self.simulationSteps+1, self.position, oldSwarmID, leaderID, hopCount-1)
    
    def step(self):
        #Start by sending a heartbeat so all nodes are aware of their neighborhood
        
        self.getInfo()
        
        if self.simulationSteps == 0:
            self.communicationModule.sendHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.electionID, self.id, self.swarmDepth, self.neighborhood)
        
        """Check if node has reached its destination and get a new destination if so. Then call updatePosition"""
        if  (math.sqrt(pow(self.destination[0] - self.position[0], 2) + pow(self.destination[1]-self.position[1], 2)) < 1):
            self.newDestination()
            
        if not self.inSwarm:
            self.timeWithoutLeader += 1
            
        if self.isLeader:
            if self.swarmSize == 1:
                self.timeIsolated += 1
            
            elif self.swarmSize > 1:
                self.timeAsLeader += 1
            
        if self.inElection:
            self.timeInElection += 1
            
        if self.doingMerge:
            self.timeDoingMerge += 1
            
        if self.doingMergeElection:
            self.timeDoingMergeElection += 1
        
        #Check if node is the one to start the election 
        if self.tester:
            self.inElection = True
            self.isSourceNode = True
            self.tester = False
            self.childStep = self.simulationSteps+2
            self.electionID = self.id
            self.bestCandidate = bestCandidate(self.id, 0, 0)
            self.communicationModule.sendElectionMessage(self.simulationSteps+1, self.position, self.electionID, self.id, self.hopCount)
            
            
        #Handle all events which are to occur at the current simulationstep
        if self.eventQueue.events:
            nextEvent = self.eventQueue.getNextEvent()
            
            while(self.simulationSteps == nextEvent.simulationStep and self.eventQueue.events):
                self.eventHandler(nextEvent)
                self.eventQueue.removeEvent(nextEvent)
                
                if self.eventQueue.events:
                    nextEvent = self.eventQueue.getNextEvent()
                    
        if self.inElection:                    
        #Check if node has started a isolated election where no other nodes participate
            if self.isSourceNode:
            
                if self.simulationSteps >= self.childStep and not self.children:
                    self.inSwarm = True
                    self.swarmID = self.id
                    self.swarmSize = 1
                    self.isLeader = True
                    self.swarmSynchronized = True
                    self.resetElection()
                    
            if self.isSourceNode:
                    
                if self.simulationSteps >= self.childStep and not self.awaitingAck:
                
                    self.findBestCandidate()
                    self.inSwarm = True
                    self.swarmSize = len(self.children)+self.descendants+1
                    self.swarmID = self.bestCandidate.candidateID
                    self.communicationModule.sendLeaderMessage(self.simulationSteps+1, self.position, self.electionID, self.id, self.swarmSize, self.bestCandidate.candidateID, self.hopCount)
                    
                    if self.bestCandidate.candidateID == self.id:
                        self.isLeader = True
                        self.discoveryStep = self.simulationSteps+2*self.hopCount
                        self.resetElection()
                    
                    else:
                        self.leader = Leader(self.bestCandidate.candidateID, 0)
                        self.swarmManager.addMember(self.swarmID, self.id)
                        self.resetElection()
            
        #If node has not send shild message to parent yet then send it and relay electionmessage if meant to         
            if not self.isSourceNode and self.inElection:
                
                if not self.childSend:
                    self.communicationModule.sendChildMessage(self.simulationSteps+1, self.position, self.electionID, self.id, self.parent)
                    self.childSend = True
                    self.numberOfLeaderElections += 1
                
                    if self.electionHopCount == 0:#Send descendant messasge immediately if election message is not meant to be relayed
                        self.communicationModule.sendDescendants(self.simulationSteps+1, self.position, self.electionID, self.id, self.parent, self.descendants+len(self.children))        
                        self.descendantsSend = True
                    
                    else:
                        self.communicationModule.sendElectionMessage(self.simulationSteps+1, self.position, self.electionID, self.id, self.electionHopCount-1)
                        self.descendantsStep = self.simulationSteps + self.electionHopCount*2
                        
                elif not self.descendantsSend:
                    
                    if self.simulationSteps >= self.descendantsStep and not self.awaitingDescendants:
                        self.communicationModule.sendDescendants(self.simulationSteps+1, self.position, self.electionID, self.id, self.parent, self.descendants+len(self.children))
                        self.descendantsSend = True
                        
                elif not self.ackSend and self.ackStep != 0:
                    
                    if self.simulationSteps >= self.ackStep and not self.awaitingAck and self.electionSize != 0:
                        self.findBestCandidate()
                        self.communicationModule.sendAckMessage(self.simulationSteps+1, self.position, self.electionID, self.id, self.parent, self.bestCandidate.candidateID, self.bestCandidate.nodeWeight, self.bestCandidate.avrSignalStrength)
                        self.ackSend = True 
            
        #Check if ack has been send and send if node is not missing any acks
    
            
        #Send leader message if node started election and is not waiting for any ack 
                        
        if self.doingMerge:
            
            if self.simulationSteps == self.mergeRequestStep and not self.mergeRequestReceived:
                self.doingMerge = False
            
            if self.simulationSteps == self.mergeAcceptStep:
                self.doingMerge = False
                self.mergeRequestReceived = False
                
        if self.doingMergeElection:
            if self.simulationSteps >= self.mergeChildStep and not self.awaitingMergeAck:
                
                if not self.isLeader:
                    if not self.mergeAckSend:
                        self.findBestCandidate()
                        self.communicationModule.sendMergeAck(self.simulationSteps+1, self.position, self.swarmID, self.id, self.parent, self.bestCandidate.candidateID, self.bestCandidate.nodeWeight, self.bestCandidate.avrSignalStrength)
                        self.mergeAckSend = True
                
                else:
                    
                    if self.children:
                        self.findBestCandidate()
                        self.communicationModule.sendMergeLeader(self.simulationSteps+1, self.position, self.swarmID, self.bestCandidate.candidateID, self.hopCount)
                        self.resetMergeElection()
                        
                        if self.bestCandidate.candidateID != self.id:
                            self.swarmManager.addMember(self.bestCandidate.candidateID, self.id)
                            self.swarmID = self.bestCandidate.candidateID
                            self.leader.leaderID = self.bestCandidate.candidateID
                            self.isLeader = False
                            self.swarmMembers = []
                            self.discoverySend = False
                            self.bestCandidate = bestCandidate(0, 0, 0)
                    else:
                        self.swarmID = self.id
                        self.leader = Leader(0, 0)
                        self.bestCandidate = bestCandidate(0, 0, 0)
                        self.resetMergeElection()
        
        if self.isLeader:
            if self.simulationSteps == self.mergeElectionStep:
                self.communicationModule.sendMergeElection(self.simulationSteps+1, self.position, self.swarmID, self.id, self.swarmSize, self.neighborhood, self.hopCount)
                self.mergeChildStep = self.simulationSteps+2
                self.doingMergeElection = True 
                
            if self.simulationSteps == self.swarmSynchronizationStep:
                self.discoverySend = False
     
            if not self.discoverySend:
                self.communicationModule.sendLeaderHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.id, self.swarmSize, self.swarmMaxDepth, self.simulationSteps, self.hopCount)
                self.communicationModule.sendDepthDiscoveryMessage(self.simulationSteps+1, self.position, self.swarmID, self.id, self.hopCount)
                self.discoverySend = True
                self.swarmSynchronized = True
                
            if self.swarmSize == 1 and not self.swarmSynchronized:
                self.swarmSynchronized = True

            
        if self.inSwarm and not self.isLeader:
            
            if self.simulationSteps == self.discoveryAckStep and not self.discoveryAckSend:
                self.communicationModule.sendDiscoveryAckMessage(self.simulationSteps+1, self.position, self.swarmID, self.id, self.swarmDepth, self.deeperNodes)
                self.discoverySend = False
                self.swarmSynchronized = True
                self.resetDepthDiscovery()
            
        #Sends a heartbeat and updates the neighborhood once every second as 60 simulationsteps are taken each second
        if (self.simulationSteps % (self.measurementsPerSec*self.heartbeatinterval) == 0):
            
            if self.isLeader:
                if self.swarmManager.checkForUpdate(self.swarmID):
                    self.swarmMembers, self.swarmSize, self.swarmMaxDepth = self.swarmManager.getSwarmInformation(self.swarmID)
                self.communicationModule.sendLeaderHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.id, self.swarmSize, self.swarmMaxDepth, self.simulationSteps, self.hopCount)
            else:
                self.communicationModule.sendHeartbeat(self.simulationSteps+1, self.position, self.swarmID, self.electionID, self.id, self.swarmDepth, self.neighborhood)               
                
            self.incrementNeighborhood()
        
        if self.isLeader:
            self.role.append(0.5)
        
        else:
            swarmColor = self.swarmColor()
            self.role.append(swarmColor)
        
        self.updatePosition()
        self.updateBatteryLevel()
        
        
    def isSimulationRunning(self):
        """Check if simulation has run for the set time"""
        if (self.simulationSteps/self.measurementsPerSec) >= self.simulationTime:
            return False
        
        else:
            return True
        
    def findBestCandidate(self):
        #Go through children from election and find best candidate
        self.calculateNodeWeight()
        self.updateAverageSignalStrength()
        self.bestCandidate.nodeWeight = self.nodeWeight
        self.bestCandidate.avrSignalStrength = self.averageSignalStrength
        self.bestCandidate.candidateID = self.id
        
        if self.children:
        
            for child in self.children:
                
                if child.nodeWeight > self.bestCandidate.nodeWeight:    
                    self.bestCandidate.candidateID = child.bestCandidate
                    self.bestCandidate.nodeWeight = child.nodeWeight
                    self.bestCandidate.avrSignalStrength = child.avrSignalStrength
                    
                elif child.nodeWeight == self.bestCandidate.nodeWeight:    
                        if child.avrSignalStrength > self.bestCandidate.avrSignalStrength:
                            self.bestCandidate.candidateID = child.bestCandidate
                            self.bestCandidate.nodeWeight = child.nodeWeight
                            self.bestCandidate.avrSignalStrength = child.avrSignalStrength
                            
                        elif child.avrSignalStrength == self.averageSignalStrength:
                            if child.bestCandidate > self.bestCandidate.candidateID:
                                self.bestCandidate.candidateID = child.bestCandidate
                                self.bestCandidate.nodeWeight = child.nodeWeight
                                self.bestCandidate.avrSignalStrength = child.avrSignalStrength
            
    def getInfo(self):
        information = {
            "id": self.id,
            "inElection": self.inElection,
            "electionID": self.electionID,
            "inSwarm": self.inSwarm,
            "swarmID": self.swarmID,
            "swarmSize": self.swarmSize,
            "swarmDepth": self.swarmDepth,
            "maxSwarmDepth": self.swarmMaxDepth,
            "isLeader": self.isLeader,
            "isSourceNode": self.isSourceNode,
            "doingMerge": self.doingMerge,
            "doingMergeElection": self.doingMergeElection,
            "position": self.position,
            "timeIsolated": self.timeIsolated,
            "timeInElection": self.timeInElection,
            "timeDoingMerge": self.timeDoingMerge,
            "timeDoingMergeElection": self.timeDoingMergeElection,
            "timeToLoseLeader" : self.timeToLoseLeader,
            "energyLevel" : self.batteryLevel
            }
        
        self.info.append(information)
    
    def swarmColor(self):
        #Possible colors for swarms 
        colors = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]
        swarmColor = (self.swarmID % 8) 
        return colors[swarmColor]
 
    def createDataset(self):
        """Creates a data set for the node which can be used for simulation"""
        XPositions = np.array(self.PositionsX)
        YPositions = np.array(self.PositionsY)
        dataset = np.array([XPositions, YPositions])
        return dataset.T
    

            
        