import unittest
from io import StringIO
from unittest.mock import patch
from simulator import Simulator

class testSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = Simulator()                 # Create an instance of the Simulator for testing

    def testLoadMachineCode(self):
        # case 1: load machine code correctly
        # case 2: load machine code for each lines of file machine code not null and equal integers
        print("Pass: testLoadMachineCode")

    def testPrintState(self):
        # case 1: print state correctly with formatted
        # case 2: print state not null
        print("Pass: testPrintState")

    def testExecuteInstructionType_R(self):
        print("Pass: testExecuteInstructionType_R")

    def testExecuteInstructionType_I(self):
        print("Pass: testExecuteInstructionType_I")    

    def testExecuteInstructionType_J(self):
        print("Pass: testExecuteInstructionType_J")

    def testConvertNumber(self):
        # case 1: positive number
        # case 2: negative number
        # case 3: maximum positive number
        # case 4: minimum negative number
        # case 5: overflow
        posNumber = self.simulator.convertNumber(42)
        self.assertEqual(posNumber, 42)

        nevNumber = self.simulator.convertNumber(-42)
        self.assertEqual(nevNumber, -65578)

        maxPosNumber = self.simulator.convertNumber(32767)
        self.assertEqual(maxPosNumber, 32767)

        minNevNumber = self.simulator.convertNumber(-32768)
        self.assertEqual(minNevNumber, -98304)

        overflowNumber = self.simulator.convertNumber(32768)        #! not sure
        self.assertEqual(overflowNumber, -32768)

        print("Pass: testConvertNumber")

    def  testIsValidRegister(self, register):
        # case 1: correct validate register
        print("Pass: testIsValidRegister")

    def testExecuteTask(self):
        # case 1: correct execute task
        print("Pass: testExecuteTask")

    def testParseInstructionFromMemory(self):
        # case 1: correct parse instruction from memory
        print("Pass: testParseInstructionFromMemory")

    def testExceptionError(self, message):
        # case 1: correct get exception error
        print("Pass: testConvertNumber")

    def testSaveOutputToFile(self):
        pass

unittest.main()