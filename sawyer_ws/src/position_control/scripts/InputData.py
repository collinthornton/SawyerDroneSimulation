#!/usr/bin/env python

class InputData:
    def __init__(self):
        self.use_file = "Sam"

        if self.use_file == "Sam":
            self.f = open("/home/cthornton/git/SawyerDroneSimulation/Collin_Quad/Trials/TrialTwoSigma0.5/Quad_Data_Hover_Crosswinds.txt", "r")
        
        elif self.use_file == "Hao":
            self.f = open("/home/cthornton/git/SawyerDroneSimulation/Collin_Quad/Trials/quadcopter_hover_wind.csv", "r")

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
            rpy_rates = [0,0,0]
            

            if self.use_file == "Sam":
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
                
                i=0
                for i in range(0,3):
                    index = line.find(",", prevIndex)
                    rpy_rates[i] = float(line[prevIndex:index])
                    prevIndex = index+1
            


            elif self.use_file == "Hao":
                for i in range(0,3):
                    index = line.fine(",", prevIndex)
                    pos[i] = float(line[prevIndex:index])
                    prevIndex = index+1
            
                i = 0
                for i in range(0,3):
                    index = line.find(",", prevIndex)
                    vel[i] = float(line[prevIndex:index])
                    prevIndex = index+1            

                i = 0
                for i in range(0,3):
                    index = line.find(",", prevIndex)
                    rpy[i] = float(line[prevIndex:index])
                    prevIndex = index+1

                i=0
                for i in range(0,3):
                    index = line.find(",", prevIndex)
                    rpy_rates[i] = float(line[prevIndex:index])
                    prevIndex = index+1                    
                    

            state = [vel, accel, pos, rpy, rpy_rates]
            
            #print(state)
            #input("hi")
            path.append(state)

        self.f.close()

        return(path)

parser = InputData()
parser.inputMatrix()