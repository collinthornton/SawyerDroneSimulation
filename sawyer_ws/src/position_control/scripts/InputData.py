#!/usr/bin/env python3

class InputData:
    def __init__(self):
        self.f = open("../../../../Collin_Quad/Trials/Trial_One/Trial_One.txt", "r")

    def inputMatrix(self):
        vel = [0,0,0]
        accel = [0,0,0]
        pos = [0,0,0]
        rpy = [0,0,0]

        state = [vel, accel, pos, rpy]
        path = []

        lines = self.f.readlines()
        for line in lines:
            index = prevIndex = 0
            for i in range(0,3):
                index = line.find(",", prevIndex)
                vel[i] = float(line[prevIndex:index])
                prevIndex = index+1

            for i in range(0,3):
                index = line.find(",", prevIndex)
                accel[i] = float(line[prevIndex:index])
                prevIndex = index+1

            for i in range(0,3):
                index = line.find(",", prevIndex)
                pos[i] = float(line[prevIndex:index])
                prevIndex = index+1

            for i in range(0,3):
                index = line.find(",", prevIndex)
                rpy[i] = float(line[prevIndex:index])
                prevIndex = index+1

            state = [vel, accel, pos, rpy]
            path.append(state)


        self.f.close()

        #print(path)
        return(path)

parser = InputData()
parser.inputMatrix()