#!/usr/bin/env python

class InputData:
    def __init__(self):
        self.f = open("/home/cthornton/git/SawyerDroneSimulation/Collin_Quad/Trials/Trial_One/Trial_One.txt", "r")

    def inputMatrix(self):
        path = []

        lines = self.f.readlines()
        index = prevIndex = 0

        for line in lines:
            i = 0
            vel = [0,0,0]
            accel = [0,0,0]
            pos = [0,0,0]
            rpy = [0,0,0]
            
            for i in range(0,3):
                index = line.find(",", prevIndex)
                vel[i] = float(line[prevIndex:index])
                prevIndex = index+1
            
            i = 0
            for i in range(0,3):
                index = line.find(",", prevIndex)
                accel[i] = float(line[prevIndex:index])
                prevIndex = index+1

            i = 0
            for i in range(0,3):
                index = line.find(",", prevIndex)
                pos[i] = float(line[prevIndex:index])
                prevIndex = index+1

            i = 0
            for i in range(0,3):
                index = line.find(",", prevIndex)
                rpy[i] = float(line[prevIndex:index])
                prevIndex = index+1

            state = [vel, accel, pos, rpy]
            path.append(state)

        self.f.close()

        return(path)

parser = InputData()
parser.inputMatrix()