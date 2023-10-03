import sys
from simulator import *

class main:
    def main():
        if len(sys.argv) != 2:
            print("error: usage: python main.py <machine-code file>")
            exit(1)

    machineCodeFile = sys.argv[1]
    
    simulator = Simulator()
    simulator.loadMachineCode(machineCodeFile)
    simulator.executeTask()
    simulator.saveOutputToFile()
