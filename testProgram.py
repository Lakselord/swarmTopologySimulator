# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 15:04:21 2022

@author: frederik
"""

import random
from nodeWeightVersion import Node
from animatedScatter import AnimatedScatter
from mobilityModel import checkInput
from mobilityModel import animationData
from swarmManager import swarmManager
import matplotlib.pyplot as plt
import json

if __name__ == '__main__':
    
    #Get input parameters
    NumberOfNodes = checkInput("Enter number of nodes in the simulation:")
    MaxSpeed = checkInput("Enter maximum speed in m/s:")
    HopCount = checkInput("Enter hop count:")
    WorkSpaceSize = checkInput("Enter side length of square mission space in meter:")
    SimulationTime = checkInput("Enter simulation time in seconds:")
    SimulationSpeed = checkInput("Enter simulation speed:")
    
    #Create multiple nodes 
    Nodes = list()
    swarmManager = swarmManager(NumberOfNodes)
    
    
    for i in range(NumberOfNodes):
        Nodes.append(Node((0, 0), MaxSpeed, HopCount, WorkSpaceSize, i+1, SimulationTime, swarmManager))
    
    
    #Updates the node list in each communication module to caontain all nodes except the node possessing the communication module
    for i in Nodes:
        i.communicationModule.updateNodelist(Nodes, i.id)
        i.tester = True  
    
    #Make the nodes take next step unitl simulation time has elapsed
    print('Generating simulation data...')
    while (Nodes[0].isSimulationRunning()):
        for i in Nodes:
            i.step()

    #Create the simulation data'
    AnimationData, Roles = animationData(Nodes)
    print('Simulation data ready \n')
      
    totalNumberOfMessages = 0
    totalTimeWithoutLeader = 0
    totalNumberOfElectionParticipations = 0
    totalNumberOfMergeParticipations = 0
    totalTimeIsolated = 0
    totalTopologyChangesDuringElection = 0
    totalTimeWaitingForLeaderLoss = 0
    totalTimeAsleader = 0
    totalTimeInElection = 0
    
    for i in Nodes:
        totalNumberOfMessages += i.communicationModule.messagesSend
        totalTimeWithoutLeader += i.timeWithoutLeader
        totalNumberOfElectionParticipations += i.numberOfLeaderElections
        totalNumberOfMergeParticipations += i.numberOfMerges
        totalTimeIsolated += i.timeIsolated
        totalTopologyChangesDuringElection += i.topologyChangesDuringElection
        totalTimeWaitingForLeaderLoss += i.timeToLoseLeader
        totalTimeAsleader += i.timeAsLeader
        totalTimeInElection += i.timeInElection
        
    totalNodeTime = SimulationTime*60*NumberOfNodes
    
    AverageNumberOfMessagesPerSec = round((totalNumberOfMessages/NumberOfNodes)/SimulationTime, 2)
    AverageTimeWithLeader = round(((totalNodeTime-totalTimeWithoutLeader)/totalNodeTime)*100, 2)
    AverageNumberOfMergesPerMin = round(totalNumberOfMergeParticipations/(SimulationTime*NumberOfNodes),4)
    AverageNumberOfElectionsPerMin = round(totalNumberOfElectionParticipations/(SimulationTime*NumberOfNodes),4)
    AverageTimeIsolated = round((totalTimeIsolated/totalNodeTime)*100, 2)
    AverageTimeWaintingForLeaderLoss =  round((totalTimeWaitingForLeaderLoss/NumberOfNodes)/(SimulationTime*60)*100, 2)
    AveragePercentageOfTimeAsLeader = round((totalTimeAsleader/NumberOfNodes)/(SimulationTime*60)*100, 2)
    AveragePercentageOfTimeInElection = round((totalTimeInElection/NumberOfNodes)/(SimulationTime*60)*100, 2) 
    AveragePercentageOfTimeNotInSwarm = round(100-AverageTimeWithLeader, 2)
    AverageMultiNodeSwarmMember = round((100-AverageTimeIsolated) - AveragePercentageOfTimeAsLeader, 2)
    
    print("Statistics for the simulation:")
    print("Average % of time isolated alone in swarm: " + str(AverageTimeIsolated) + "%")
    print("Average % of time being part of a swarm: " + str(AverageTimeWithLeader) + "%")
    print("Average % of time as leader leader for multi node swarm: " + str(AveragePercentageOfTimeAsLeader) + "%")
    print("Average % of time as member of multi node swarm: " + str(AverageMultiNodeSwarmMember - AverageTimeWaintingForLeaderLoss) + "%")
    print("Average % of time not in swarm: " + str(AveragePercentageOfTimeNotInSwarm) + "%")
    print("Average % of time spend in election: " + str(AveragePercentageOfTimeInElection) + "%")
    print("Average % of time waiting for leader loss: " + str(AverageTimeWaintingForLeaderLoss) + "%")
    print("Average number of messages send each second: " + str(AverageNumberOfMessagesPerSec))
    print("Average number of elections participated in per minute: " + str(AverageNumberOfElectionsPerMin))
    print("Average number of merges participated in per minute: " + str(AverageNumberOfMergesPerMin))
    print("Number of topology changes during elections " + str(totalTopologyChangesDuringElection))
    
    
    #Create animation and set axis labels
    
    animationData(Nodes)
    a = AnimatedScatter(len(Nodes), WorkSpaceSize, len(Nodes[0].PositionsX), AnimationData, Roles, SimulationSpeed)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()
    
    data = []
    swarmIDs =[]
    nodesNotinSwarm = []
    numberOfSwarms = []
    batteryLevels = []
    
    # for i in range(SimulationTime*60):
    for i in range(SimulationTime*60):
        temp = []
        for node in Nodes:
            temp.append(node.info[i])
            
        wrapper = {
            "Time step": i,
            "Data": temp
            }
        
        data.append(wrapper)
        
    for step in data:
        a = step['Data']
        for b in a:
            swarmIDs.append(b['swarmID'])
            
    for i in range(72000):
        timestep = swarmIDs[0:20]
        del swarmIDs[:20]
        timestep.sort()
        swarmCount = 0
        lastSwarmID = 0
        for i in timestep:
            if i > lastSwarmID:
                lastSwarmID = i
                swarmCount += 1
                
        numberOfSwarms.append(swarmCount)
    
    totalSwarms = 0
    
    for n in numberOfSwarms:
        totalSwarms = totalSwarms + n
        
    laststep = data[71999]['Data']
    
    for i in laststep:
        batteryLevels.append(i['energyLevel'])
        
    averageNumberOfSwarms = round(totalSwarms/(SimulationTime*60), 2)
    tempPercentage = AverageTimeWithLeader/100
    averageSwarmSize = round(((tempPercentage*NumberOfNodes)/averageNumberOfSwarms), 2)
    minBatteryLevel = round(min(batteryLevels),2)
    maxBatteryLevel = round(max(batteryLevels),2)
    averageBatteryLevel = round(sum(batteryLevels)/len(batteryLevels),2)
    
    
    print("Average number of swarms through out simulation: " + str(averageNumberOfSwarms))
    print("Average swarm size: " + str(averageSwarmSize))
    print("Minimum energy level: " + str(minBatteryLevel) + "%")
    print("Maximum energy level: " + str(maxBatteryLevel) + "%")
    print("Average energy level: " + str(averageBatteryLevel) + "%")
    
    
    # with open ('HBLeaderLoss.json', 'w') as json_file:
    #     json.dump(data, json_file)
        