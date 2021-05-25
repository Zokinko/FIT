#  UNIVERSITY: Faculty of Information Technology, Brno University of Technology 
#  FILE: interpret.py
#  DESCRIPTION: IPP project 2, 2021
#  AUTHOR :Tomáš Hrúz <xhruzt00@stud.fit.vutbr.cz>

from __future__ import print_function
from pprint import pprint
import xml.etree.ElementTree as ET
import re
import sys

#global dictionary for instructions
instructionsDictionary = {}
labelDictionary = {}
tempFrame = {}
globalFrame = {}
localFrame = []
isTempFrameSet = False
frameStack = []
callStack = []
valueStack = []
orderCounter = 1
isInputStringFromStdIn = False


#help function
def help():
    print("___________________________________________________________________")
    print("Program nacita XML reprezentaciu programu a tento program s vyuzitim")
    print("vstupu podla parametru prikazovej riadky interpretuje a generuje vystup.")
    print("Vstupna XML reprezentacia je napr. generovana skriptom")
    print("parse.php (ale nie nutne) zo zdrojoveho kodu v IPPcode20.")
    print("Povolene argumenty:") 
    print("-------------------------------------------------------------------")
    print("--help") 
    print("vypise na standardny vystup napovedy skriptu")
    print("-------------------------------------------------------------------") 
    print("--source=file") 
    print("vstupny subor s XML reprezentaciou zdrojoveho kodu")
    print("-------------------------------------------------------------------") 
    print("--input=file") 
    print("subor zo vstupmi pro samotnu interpretaciu zadaneho zdrojoveho kodu")
    print("___________________________________________________________________") 

#load source file
def readFile(arg):
#content behind equals is name of file
        myFile = arg.split("=")  
        if myFile[0] == '--input':
                stdInSource = sys.stdin
                myString = ET.parse(stdInSource)
                return myString
        else:
                try:
                        open(myFile[1], 'r').read()
                        try:
                                #create Tree to easy acces to input
                                myString = ET.parse(myFile[1])
                                return myString
                        except Exception:
                                sys.stderr.write("Wrong XML format\n")
                                sys.exit(31)
                except IOError:
                        sys.stderr.write("File doesn't exist\n")
                        sys.exit(11)

#load input file
def inputFile(arg):
        myFile = arg.split("=")  
        if myFile[0] != '--source':
                try:
                        sys.stdin = open(myFile[1], 'r')
                except IOError:
                        sys.stderr.write("File doesn't exist\n")
                        sys.exit(11)


#checks if content of attributes is correct
def argumentValueChecker(argument):
        if argument.attrib['type'] == 'var':
                if re.match("^(GF|LF|TF)@([a-zA-Z]|-|_|\*|\$|\%|\&|\!|\?)([a-zA-Z0-9]|-|_|\*|\$|\%|\&|\!|\?)*$", argument.text) is None:
                        sys.stderr.write("Argument var has wrong value\n")
                        sys.exit(32)
        elif argument.attrib['type'] == 'int':
                if re.match("^-{0,1}\d*$", argument.text) is None:
                        sys.stderr.write("Argument int has wrong value\n")
                        sys.exit(32)
        elif argument.attrib['type'] == 'string':
                if re.match("^([^\s#\\\\]|\\\\[0-9]{3})+$", argument.text) is None:
                        sys.stderr.write("Argument string has wrong value\n")
                        sys.exit(32)
        elif argument.attrib['type'] == 'bool':
                if re.match("^(true|false)$", argument.text) is None:
                        sys.stderr.write("Argument bool has wrong value\n")
                        sys.exit(32)                
        elif argument.attrib['type'] == 'nil':
                if argument.text != 'nil':
                        sys.stderr.write("Argument nil has wrong value\n")
                        sys.exit(32)
        elif argument.attrib['type'] == 'label':
                if re.match("^([a-zA-Z]|-|_|\*|\$|\%|\&|\!|\?)([a-zA-Z0-9]|-|_|\*|\$|\%|\&|\!|\?)*$", argument.text) is None:
                        sys.stderr.write("Argument label has wrong value\n")
                        sys.exit(32)   
        else:
                sys.stderr.write("Argument has wrong type\n")
                sys.exit(32)                

#checks if dictionary contains instruction with same order
def orderChecker(instructionOrder, instructionDictionary):
        if instructionOrder in instructionsDictionary:
                sys.stderr.write("Instruction with same order already exists in dictionary\n")
                sys.exit(32)
        #save dictionary with content of single instruction and save it to ordered dictionary
        instructionsDictionary[instructionOrder] = instructionDictionary.copy()
        instructionDictionary.clear()

#checks if XML input is correct and loads dictionary with instructions
def xmlChecker(arg):
        #dictionary for single instruction
        instructionDictionary = {}
        #tree to parse
        tree = readFile(arg)
        #root of tree
        root = tree.getroot()

        #check if root is correct
        if root.tag != 'program':
                sys.stderr.write("Wrong XML structure\n")
                sys.exit(32)
        #mandatory attribute
        if root.attrib['language'] != 'IPPcode21':
                sys.stderr.write("Wrong XML structure\n")
                sys.exit(32)
        #optional attributes
        if len(root.attrib) > 3:
                sys.stderr.write("Wrong XML structure\n")
                sys.exit(32)
        if len(root.attrib) == 3:
                if ('name' not in root.attrib) or ('description' not in root.attrib):
                        sys.stderr.write("Wrong XML structure\n")
                        sys.exit(32)  
        if len(root.attrib) == 2:
                if ('name' not in root.attrib):
                        if ('description' not in root.attrib):
                                sys.stderr.write("Wrong XML structure\n")
                                sys.exit(32)  
        
        #Cycle which checks every single instruction and saves it to dictionary
        for child in root:
                #chceck if instruction is really instruction
                if child.tag != 'instruction':
                        sys.stderr.write("Wrong XML structure\n")
                        sys.exit(32)  
                #check missing xml attribute opcode
                if 'opcode' not in child.attrib:
                        sys.stderr.write("Wrong XML structure\n")
                        sys.exit(32) 
                #check missing xml order
                if 'order' not in child.attrib:
                        sys.stderr.write("Wrong XML structure\n")
                        sys.exit(32) 
                #check if instruction order is positive number
                try:
                        val = int(child.attrib['order'])
                        if val < 1:
                                sys.stderr.write("Wrong XML structure\n")
                                sys.exit(32)
                except ValueError:
                        sys.stderr.write("Wrong XML structure\n")
                        sys.exit(32)  

                if child.attrib['opcode'].upper() == 'INT2CHAR' or\
                child.attrib['opcode'].upper() == 'MOVE' or\
                child.attrib['opcode'].upper() == 'TYPE' or\
                child.attrib['opcode'].upper() == 'STRLEN':
                        #number of arguments must be 2
                        if len(child) != 2:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                #saves attributes to variable
                                arg1 = child.findall("arg1")[0]
                                arg2 = child.findall("arg2")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'var':
                                sys.stderr.write("Missing variable\n")
                                sys.exit(32)
                        if arg2.attrib['type'] != 'string' and\
                        arg2.attrib['type'] != 'int' and\
                        arg2.attrib['type'] != 'bool' and\
                        arg2.attrib['type'] != 'nil' and\
                        arg2.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]
                        argumentValueChecker(arg2)
                        instructionDictionary["arg2"] = [arg2.attrib['type'], arg2.text]

                        #check order of instruction and add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)


                elif child.attrib['opcode'].upper() == 'CREATEFRAME' or\
                child.attrib['opcode'].upper() == 'PUSHFRAME' or\
                child.attrib['opcode'].upper() == 'POPFRAME' or\
                child.attrib['opcode'].upper() == 'RETURN' or\
                child.attrib['opcode'].upper() == 'BREAK':
                        #number of arguments must be 0
                        if len(child) != 0:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)


                elif child.attrib['opcode'].upper() == 'DEFVAR' or\
                child.attrib['opcode'].upper() == 'POPS':
                        #number of arguments must be 1
                        if len(child) != 1:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'var':
                                sys.stderr.write("Missing variable\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)


                elif child.attrib['opcode'].upper() == 'CALL' or\
                child.attrib['opcode'].upper() == 'JUMP':
                        #number of arguments must be 1
                        if len(child) != 1:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'label':
                                sys.stderr.write("Missing label\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)
                
                elif child.attrib['opcode'].upper() == 'LABEL':

                        #number of arguments must be 1
                        if len(child) != 1:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                         #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']
                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'label':
                                sys.stderr.write("Missing label\n")
                                sys.exit(32)
                        #checks duplicity of labels in dictionaries
                        #but is checked in interpretation
                        # if arg1.text in labelDictionary:
                        #         sys.stderr.write("Label with same name already exists in dictionary")
                        #         sys.exit(32)                      
                        if child.attrib['order'] in instructionsDictionary:
                                sys.stderr.write("Label with same order already exists in dictionary\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)    

                        #but is checked in interpretation
                        #labelDictionary[arg1.text] = child.attrib['order']
                         #add instruction arguments to dictionary
                        if arg1.text in labelDictionary:
                                sys.stderr.write("Label is already in dictionary\n")
                                sys.exit(52)
                        labelDictionary[arg1.text] = child.attrib['order']

                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]
                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)

                

                elif child.attrib['opcode'].upper() == 'PUSHS' or\
                child.attrib['opcode'].upper() == 'WRITE' or\
                child.attrib['opcode'].upper() == 'EXIT' or\
                child.attrib['opcode'].upper() == 'DPRINT':
                        #number of arguments must be 1
                        if len(child) != 1:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'string' and\
                        arg1.attrib['type'] != 'int' and\
                        arg1.attrib['type'] != 'bool' and\
                        arg1.attrib['type'] != 'nil' and\
                        arg1.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)
                

                elif child.attrib['opcode'].upper() == 'READ':
                        #number of arguments must be 2
                        if len(child) != 2:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                                arg2 = child.findall("arg2")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'var':
                                sys.stderr.write("Missing variable\n")
                                sys.exit(32)
                        if arg2.attrib['type'] != 'string' and\
                        arg2.attrib['type'] != 'int' and\
                        arg2.attrib['type'] != 'bool' and\
                        arg2.attrib['type'] != 'nil':
                                sys.stderr.write("Missing type\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]
                        argumentValueChecker(arg2)
                        instructionDictionary["arg2"] = [arg2.attrib['type'], arg2.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)


                elif child.attrib['opcode'].upper() == 'JUMPIFEQ' or\
                child.attrib['opcode'].upper() == 'JUMPIFNEQ':
                        #number of arguments must be 3
                        if len(child) != 3:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                                arg2 = child.findall("arg2")[0]
                                arg3 = child.findall("arg3")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'label':
                                sys.stderr.write("Missing label\n")
                                sys.exit(32)
                        if arg2.attrib['type'] != 'string' and\
                        arg2.attrib['type'] != 'int' and\
                        arg2.attrib['type'] != 'bool' and\
                        arg2.attrib['type'] != 'nil' and\
                        arg2.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)
                        if arg3.attrib['type'] != 'string' and\
                        arg3.attrib['type'] != 'int' and\
                        arg3.attrib['type'] != 'bool' and\
                        arg3.attrib['type'] != 'nil' and\
                        arg3.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]
                        argumentValueChecker(arg2)
                        instructionDictionary["arg2"] = [arg2.attrib['type'], arg2.text]
                        argumentValueChecker(arg3)
                        instructionDictionary["arg3"] = [arg3.attrib['type'], arg3.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)


                elif child.attrib['opcode'].upper() == 'ADD' or\
                child.attrib['opcode'].upper() == 'SUB' or\
                child.attrib['opcode'].upper() == 'MUL' or\
                child.attrib['opcode'].upper() == 'IDIV' or\
                child.attrib['opcode'].upper() == 'LT' or\
                child.attrib['opcode'].upper() == 'GT' or\
                child.attrib['opcode'].upper() == 'EQ' or\
                child.attrib['opcode'].upper() == 'AND' or\
                child.attrib['opcode'].upper() == 'OR' or\
                child.attrib['opcode'].upper() == 'STRI2INT' or\
                child.attrib['opcode'].upper() == 'GETCHAR' or\
                child.attrib['opcode'].upper() == 'SETCHAR' or\
                child.attrib['opcode'].upper() == 'CONCAT':
                        #number of arguments must be 3
                        if len(child) != 3:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                                arg2 = child.findall("arg2")[0]
                                arg3 = child.findall("arg3")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'var':
                                sys.stderr.write("Missing variable\n")
                                sys.exit(32)
                        if arg2.attrib['type'] != 'string' and\
                        arg2.attrib['type'] != 'int' and\
                        arg2.attrib['type'] != 'bool' and\
                        arg2.attrib['type'] != 'nil' and\
                        arg2.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)
                        if arg3.attrib['type'] != 'string' and\
                        arg3.attrib['type'] != 'int' and\
                        arg3.attrib['type'] != 'bool' and\
                        arg3.attrib['type'] != 'nil' and\
                        arg3.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]
                        argumentValueChecker(arg2)
                        instructionDictionary["arg2"] = [arg2.attrib['type'], arg2.text]
                        argumentValueChecker(arg3)
                        instructionDictionary["arg3"] = [arg3.attrib['type'], arg3.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)

                elif child.attrib['opcode'].upper() == 'NOT':
                 #number of arguments must be 3
                        if len(child) != 2:
                                sys.stderr.write("Wrong number of arguments\n")
                                sys.exit(32)
                        try:
                                arg1 = child.findall("arg1")[0]
                                arg2 = child.findall("arg2")[0]
                        except Exception:
                                sys.stderr.write("Wrong arguments\n")
                                sys.exit(32)

                        #add opcode to dictionary
                        instructionDictionary['opcode'] = child.attrib['opcode']

                        #check if instructions has correct argument types
                        if arg1.attrib['type'] != 'var':
                                sys.stderr.write("Missing variable\n")
                                sys.exit(32)
                        if arg2.attrib['type'] != 'string' and\
                        arg2.attrib['type'] != 'int' and\
                        arg2.attrib['type'] != 'bool' and\
                        arg2.attrib['type'] != 'nil' and\
                        arg2.attrib['type'] != 'var':
                                sys.stderr.write("Missing symbol\n")
                                sys.exit(32)

                        #add instruction arguments to dictionary
                        argumentValueChecker(arg1)                      
                        instructionDictionary["arg1"] = [arg1.attrib['type'], arg1.text]
                        argumentValueChecker(arg2)
                        instructionDictionary["arg2"] = [arg2.attrib['type'], arg2.text]

                        #add instruction dictionary to dictionary of instructions
                        orderChecker(child.attrib['order'], instructionDictionary)
                else:
                        sys.stderr.write("Wrong opcode\n")
                        sys.exit(32)

#argument check--------------------------------------------
argc = len(sys.argv)
if argc <= 1:
        sys.stderr.write("Wrong number of arguments\n")
        sys.exit(10)
elif argc == 2:
        # print("help alebo source/input")
        arg1 = str(sys.argv[1])
        if arg1 == "--help":
                help()
                sys.exit(0)
        elif re.match("^--source=.+", arg1) is not None:
                # print("source zadam a input je zo stdin")
                xmlChecker(arg1)
                inputFile(arg1)
        elif re.match("^--input=.+", arg1) is not None:
                # print("input zadam a source je zo stdin")
                xmlChecker(arg1)
                inputFile(arg1)   
                pass
        else:
                sys.stderr.write("Wrong arguments\n")
                sys.exit(10)
        
elif argc == 3:
        arg1 = str(sys.argv[1])
        arg2 = str(sys.argv[2])
        if re.match("^--source=.+", arg1) is not None:
                if re.match("^--input=.+", arg2) is not None:
                        # print("zadam source aj input")
                        xmlChecker(arg1)
                        inputFile(arg2)
        elif re.match("^--input=.+", arg1) is not None:
                if re.match("^--source=.+", arg2) is not None:
                        # print("zadam input aj source")
                        xmlChecker(arg2)
                        inputFile(arg1)
        else:
                sys.stderr.write("Wrong arguments\n")
                sys.exit(10)
else:
        sys.stderr.write("Too much arguments\n")
        sys.exit(10)
#end of argument check-----------------------------------------------------------

#used to get type and value from variable
def getFrom(varFromFrame):
        # print("getfromframe")
        global localFrame
        global tempFrame
        global globalFrame
        #variables with frame and value part of variable
        splitVariable = varFromFrame.split("@")
        splitFrame = splitVariable[0]
        splitVal = splitVariable[1]

        if splitFrame == "GF":
                if splitVal in globalFrame:
                        typeFromVar = globalFrame[splitVal]["type"]
                        valueFromVar = globalFrame[splitVal]["value"]
                else:
                        sys.stderr.write("Variable is not in GF\n")
                        sys.exit(54)
        elif splitFrame == "LF":
                if splitVal in localFrame[-1]:
                        typeFromVar = localFrame[-1][splitVal]["type"]
                        valueFromVar = localFrame[-1][splitVal]["value"]
                else:
                        sys.stderr.write("Variable not on top of LF\n")
                        sys.exit(54)
        elif splitFrame == "TF":
                if splitVal in tempFrame:
                        typeFromVar = tempFrame[splitVal]["type"]
                        valueFromVar = tempFrame[splitVal]["value"]
                else:
                        sys.stderr.write("Variable is not in TF\n")
                        sys.exit(54)
        
        return [typeFromVar,valueFromVar]

#function used to save type and value to variable
def saveTo(typeFromStack, valueFromStack, varToFrame):
        global localFrame
        global tempFrame
        global globalFrame
        #variables with frame and value part of variable
        splitVariable = varToFrame.split("@")
        splitFrame = splitVariable[0]
        splitVal = splitVariable[1]
        if splitFrame == "GF":
                if splitVal in globalFrame:
                        globalFrame[splitVal]["type"] = typeFromStack
                        globalFrame[splitVal]["value"] = valueFromStack
                else:
                        sys.stderr.write("Variable is not in GF\n")
                        sys.exit(54)
        elif splitFrame == "LF":
                if splitVal in localFrame[-1]:
                        localFrame[-1][splitVal]["type"] = typeFromStack
                        localFrame[-1][splitVal]["value"] = valueFromStack
                else:
                        sys.stderr.write("Variable not on top of LF\n")
                        sys.exit(54)
        elif splitFrame == "TF":
                if splitVal in tempFrame:
                        tempFrame[splitVal]["type"] = typeFromStack
                        tempFrame[splitVal]["value"] = valueFromStack
                else:
                        sys.stderr.write("Variable is not in TF\n")
                        sys.exit(54)


#INSTRUCTION interpretation functions-------------------------------
def ins_CREATEFRAME():
        global isTempFrameSet
        global tempFrame
        # print("createframe")
        #set TF and if has previous value clear it
        isTempFrameSet = True
        tempFrame.clear()

def ins_PUSHFRAME():
        global tempFrame
        global localFrame
        global isTempFrameSet
        if not isTempFrameSet:
                sys.stderr.write("TF not set\n")
                sys.exit(55)

        #add TF to stack
        frameStack.append(tempFrame.copy())
        #set LF to top of the stack
        localFrame = frameStack[-1]
        #clear TF
        tempFrame.clear()
        isTempFrameSet = False    

def ins_POPFRAME():
        global tempFrame
        global localFrame
        global isTempFrameSet
        if not localFrame:
                sys.stderr.write("LF does not exist\n")
                sys.exit(55)

        #set TF to top of the stack and remove it from frameStack        
        tempFrame = frameStack.pop()
        isTempFrameSet = True
        localFrame.pop()

def ins_RETURN():
        global callStack
        global orderCounter
        if not callStack:
                sys.stderr.write("Call stack is empty\n")
                sys.exit(56)
        orderCounter = callStack.pop()

def ins_DEFVAR(argType,argValue):
        global tempFrame
        global localFrame
        global globalFrame
        global isTempFrameSet
        
        #variables with frame and value part of variable
        splitVariable = argValue.split("@")
        splitFrame = splitVariable[0]
        splitVal = splitVariable[1]
        #dictionary for variables
        variableDictionary = {"type": None, "value": None }

        #arrays added to frames contains: Value of variable on index 0, Type of variable on index 0
        if splitFrame == "TF":
                if not isTempFrameSet:
                        sys.stderr.write("TF not set\n")
                        sys.exit(55)
                if splitVal not in tempFrame:
                        tempFrame[splitVal] = variableDictionary
                else:
                        sys.stderr.write("Variable is already in TF\n")
                        sys.exit(52)
        elif splitFrame == "LF":
                if not localFrame:
                        sys.stderr.write("LF does not exist\n")
                        sys.exit(55)
                if splitVal not in localFrame[-1]:
                        localFrame[-1][splitVal] = variableDictionary
                else:
                        sys.stderr.write("Variable already on top of LF\n")
                        sys.exit(52)
        elif splitFrame == "GF":
                if splitVal not in globalFrame:
                        globalFrame[splitVal] = variableDictionary
                else:
                        sys.stderr.write("Variable is already in GF\n")
                        sys.exit(52)

def ins_PUSHS(argumentValue):
        global valueStack
        #if variable get value of variable and its type and value else
        if argumentValue[0] == "var":
                valueStack.append(getFrom(argumentValue[1]))
        else:
                valueStack.append(argumentValue)

def ins_POPS(argType, argValue):
        global valueStack
        if not valueStack:
                sys.stderr.write("Value stack is empty\n")
                sys.exit(56)
        variableFromStack = valueStack.pop()
        #save type and value from stack to variable from argument
        saveTo(variableFromStack[0],variableFromStack[1],argValue)

def ins_MOVE(arg1Type, arg1Val, arg2Type, arg2Val):
        global tempFrame
        global localFrame
        global globalFrame
        #variables with frame and value part of variable
        splitVariable = arg1Val.split("@")
        splitFrame = splitVariable[0]
        splitVal = splitVariable[1]

        if arg2Type == 'int' or arg2Type == 'string' or\
        arg2Type == 'bool' or arg2Type == 'nil':
                saveTo(arg2Type, arg2Val, arg1Val)
        elif arg2Type == 'var':
                typeAndValueFromVar = getFrom(arg2Val)
                saveTo(typeAndValueFromVar[0], typeAndValueFromVar[1], arg1Val)
        else:
                sys.stderr.write("Wrong type of symbol\n")
                sys.exit(53)

def ins_ADD_SUB_MUL_IDIV(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val, insOpcode):

        if arg2Type == 'int':
                valueFromVar2 = arg2Val
                typeFromVar2 = arg2Type
        elif arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                typeFromVar2 = typeAndValueFromVar2[0]
                valueFromVar2 = typeAndValueFromVar2[1]
                if typeFromVar2 != 'int':
                        sys.stderr.write("Symbol must be integer\n")
                        sys.exit(53)
        else:
                sys.stderr.write("Symbol must be integer\n")
                sys.exit(53)

        if arg3Type == 'int':
                valueFromVar3 = arg3Val
                typeFromVar3 = arg3Type
        elif arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                typeFromVar3 = typeAndValueFromVar3[0]
                valueFromVar3 = typeAndValueFromVar3[1]
                if typeFromVar3 != 'int':
                        sys.stderr.write("Symbol must be integer\n")
                        sys.exit(53)
        else:
                sys.stderr.write("Symbol must be integer\n")
                sys.exit(53)
        if insOpcode == 'ADD':
                valueFromVar = int(valueFromVar2) + int(valueFromVar3)
        if insOpcode == 'SUB':
                valueFromVar = int(valueFromVar2) - int(valueFromVar3)
        if insOpcode == 'MUL':
                valueFromVar = int(valueFromVar2) * int(valueFromVar3)
        if insOpcode == 'IDIV':
                if int(valueFromVar3) != 0:
                        valueFromVar = int(valueFromVar2) // int(valueFromVar3)
                else:
                        sys.stderr.write("Division by zero\n")
                        sys.exit(57)
        saveTo('int', valueFromVar, arg1Val)

def ins_LT_GT_EQ(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val, insOpcode):
        #get values and types if its variable
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]

        #int compare
        if arg2Type == 'int' and arg2Type == 'int':
                if insOpcode == 'LT':
                        if int(arg2Val) < int(arg3Val):
                                compareResult = True
                        else:
                                compareResult = False
                elif insOpcode == 'GT':
                        if int(arg2Val) > int(arg3Val):
                                compareResult = True
                        else:
                                compareResult = False
                elif insOpcode == 'EQ':
                        if int(arg2Val) == int(arg3Val):
                                compareResult = True
                        else:
                                compareResult = False
        #string compare
        elif arg2Type == 'string' and arg2Type == 'string':
                if insOpcode == 'LT':
                        if arg2Val < arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
                elif insOpcode == 'GT':
                        if arg2Val > arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
                elif insOpcode == 'EQ':
                        if arg2Val == arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
        #bool compare
        elif arg2Type == 'bool' and arg2Type == 'bool':
                if insOpcode == 'LT':
                        if arg2Val < arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
                elif insOpcode == 'GT':
                        if arg2Val > arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
                elif insOpcode == 'EQ':
                        if arg2Val == arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
        #nil compare
        elif arg2Type == 'nil' and arg2Type == 'nil':
                if insOpcode == 'EQ':
                        if arg2Val == arg3Val:
                                compareResult = True
                        else:
                                compareResult = False
                else:
                        sys.stderr.write("nil can be comapred only by EQ\n")
                        sys.exit(53)
        else:
                sys.stderr.write("Symbols must be same type\n")
                sys.exit(57)
        #save bool value to variable
        saveTo('bool', compareResult,arg1Val)

def ins_AND(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        #get values and types if its variable
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]
        #true if both are true
        if arg2Val == 'true' and arg3Val == 'true':
                saveTo('bool', 'true',arg1Val)
        else: 
                saveTo('bool', 'false',arg1Val)

def ins_OR(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        #get values and types if its variable
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]
        #true if anything is true
        if arg2Val == 'true' or arg3Val == 'true':
                saveTo('bool', 'true',arg1Val)
        else: 
                saveTo('bool', 'false',arg1Val)

def ins_NOT(arg1Type, arg1Val, arg2Type, arg2Val): 
        if arg2Val == 'true':
                reversedResult = 'false'
        elif arg2Val == 'false':
                reversedResult = 'true'
        #save reversed value to variable
        saveTo('bool', reversedResult,arg1Val)

def ins_INT2CHAR(arg1Type, arg1Val, arg2Type, arg2Val):
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg2Type != 'int':
                sys.stderr.write("Symbols must be integer\n")
                sys.exit(53)
        #unicode has big interval of values but not all are defined
        try:
                unicodeChar = chr(int(arg2Val))
        except:
                sys.stderr.write("Not valid unicode value\n")
                sys.exit(58)
        saveTo('string', unicodeChar,arg1Val)

def ins_CONCAT(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        if arg2Type == 'string':
                valueFromVar2 = arg2Val
                typeFromVar2 = arg2Type
        elif arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                typeFromVar2 = typeAndValueFromVar2[0]
                valueFromVar2 = typeAndValueFromVar2[1]
                if typeFromVar2 != 'string':
                        sys.stderr.write("Symbol must be string\n")
                        sys.exit(53)
        else:
                sys.stderr.write("Symbol must be string\n")
                sys.exit(53)

        if arg3Type == 'string':
                valueFromVar3 = arg3Val
                typeFromVar3 = arg3Type
        elif arg2Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                typeFromVar3 = typeAndValueFromVar3[0]
                valueFromVar3 = typeAndValueFromVar3[1]
                if typeFromVar3 != 'string':
                        sys.stderr.write("Symbol must be string\n")
                        sys.exit(53)
        else:
                sys.stderr.write("Symbol must be string\n")
                sys.exit(53)

        concatedString = valueFromVar2 + valueFromVar3
        
        saveTo('string', concatedString, arg1Val)

def ins_STRLEN(arg1Type, arg1Val, arg2Type, arg2Val):
        if arg2Type == 'string':
                valueFromVar2 = arg2Val
                typeFromVar2 = arg2Type
        elif arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                typeFromVar2 = typeAndValueFromVar2[0]
                valueFromVar2 = typeAndValueFromVar2[1]
                if typeFromVar2 != 'string':
                        sys.stderr.write("Symbol must be string\n")
                        sys.exit(53)
        else:
                sys.stderr.write("Symbol must be string\n")
                sys.exit(53)

        lenghtOfString = len(valueFromVar2)      
        saveTo('string', lenghtOfString, arg1Val)

def ins_TYPE(arg1Type, arg1Val, arg2Type, arg2Val):
        #get type of symbol and save it to variable
        if arg2Type == 'string':
                typeOfSymbol = arg2Type
        elif arg2Type == 'int':
                typeOfSymbol = arg2Type
        elif arg2Type == 'bool':
                typeOfSymbol = arg2Type
        elif arg2Type == 'string':
                typeOfSymbol = arg2Type
        elif arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                typeOfSymbol = typeAndValueFromVar2[0]
        else:
                sys.stderr.write("Wrong type of symbol\n")
                sys.exit(53)

        saveTo('string', typeOfSymbol, arg1Val)

def ins_JUMP(arg1Val):
        global orderCounter 
        #check if label exists
        if arg1Val not in labelDictionary:
                sys.stderr.write("Label doesn't exist\n")
                sys.exit(52)
        # minus 1 because order counter is incremented after switch of instructions
        orderCounter = int(labelDictionary[arg1Val]) - 1

def ins_JUMPIFEQ(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        global orderCounter 
        #check if label exists
        if arg1Val not in labelDictionary:
                sys.stderr.write("Label doesn't exist\n")
                sys.exit(52)
        #if variable get type and value
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]    
        if arg2Type == arg3Type:
                if int(arg2Val) == int(arg3Val):
                        # minus 1 because order counter is incremented after switch of instructions
                        orderCounter = int(labelDictionary[arg1Val]) - 1
        elif arg2Type == 'nil' or arg3Type == 'nil':
                orderCounter = int(labelDictionary[arg1Val]) - 1
        else:
                sys.stderr.write("Type of symbols is not the same\n")
                sys.exit(53)

def ins_JUMPIFNEQ(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        global orderCounter
        #check if label exists
        if arg1Val not in labelDictionary:
                sys.stderr.write("Label doesn't exist\n")
                sys.exit(52) 
        #if variable get type and value
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]

        if arg2Type == arg3Type:
                if arg2Val != arg3Val:
                        # minus 1 because order counter is incremented after switch of instructions
                        orderCounter = int(labelDictionary[arg1Val]) - 1
        elif arg2Type == 'nil' or arg3Type == 'nil':
                orderCounter = int(labelDictionary[arg1Val]) - 1
        else:
                sys.stderr.write("Type of symbols is not the same\n")
                sys.exit(53)

def ins_EXIT(arg1Type, arg1Val):
        #if variable get type and value
        if arg1Type == 'var':
                typeAndValueFromVar1 = getFrom(arg1Val)
                arg1Type = typeAndValueFromVar1[0]
                arg1Val = typeAndValueFromVar1[1]
        if arg1Type == 'int':
                arg1Val = int(arg1Val)
                if arg1Val >=0 and arg1Val <= 49:
                        sys.exit(arg1Val)
                else:
                        sys.stderr.write("Exit code must be in interval <0,49>\n")
                        sys.exit(57)
        else:
                sys.stderr.write("Symbol must be type integer\n")
                sys.exit(53)

def ins_GETCHAR(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        #if variable get type and value
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]
        #symbol type checker
        if arg2Type != 'string':
                sys.stderr.write("Symbol must be type string\n")
                sys.exit(53)
        if arg3Type != 'int':
                sys.stderr.write("Symbol must be type integer\n")
                sys.exit(53)
        #get index value of required character
        try:
                character = arg2Val[int(arg3Val)]
        except:
                sys.stderr.write("Index of character out of bounds\n")
                sys.exit(58)
        #save index value to variable
        saveTo('string', character, arg1Val)


def ins_SETCHAR(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        # if its variable store its name
        VariableToChange = arg1Val
        
        #if variable get type and value
        if arg1Type == 'var':
                typeAndValueFromVar1 = getFrom(arg1Val)
                arg1Type = typeAndValueFromVar1[0]
                arg1Val = typeAndValueFromVar1[1]
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]
        #symbol type checker        
        if arg1Type != 'string':
                sys.stderr.write("Symbol must be type string\n")
                sys.exit(53)
        if arg2Type != 'int':
                sys.stderr.write("Symbol must be type integer\n")
                sys.exit(53)
        if arg3Type != 'string':
                sys.stderr.write("Symbol must be type string\n")
                sys.exit(53)
        if arg3Val == "":
                sys.stderr.write("Symbol can not be empty string\n")
                sys.exit(58)
        #change string to list of chars, and change char on required index
        try:
                listFromString = list(arg1Val)
                listFromString[int(arg2Val)] = arg3Val[0]
                arg1Val = "".join(listFromString)
        except:
                sys.stderr.write("Index of character out of bounds\n")
                sys.exit(58)

        #change variable to new version
        saveTo('string', arg1Val, VariableToChange)

def ins_STRI2INT(arg1Type, arg1Val, arg2Type, arg2Val, arg3Type, arg3Val):
        #if variable get type and value
        if arg2Type == 'var':
                typeAndValueFromVar2 = getFrom(arg2Val)
                arg2Type = typeAndValueFromVar2[0]
                arg2Val = typeAndValueFromVar2[1]
        if arg3Type == 'var':
                typeAndValueFromVar3 = getFrom(arg3Val)
                arg3Type = typeAndValueFromVar3[0]
                arg3Val = typeAndValueFromVar3[1]
        #symbol type checker
        if arg2Type != 'string':
                sys.stderr.write("Symbol must be type string\n")
                sys.exit(53)
        if arg3Type != 'int':
                sys.stderr.write("Symbol must be type integer\n")
                sys.exit(53)
        #change string to list of chars, get ordinal value of required char
        try:
                listFromString = list(arg2Val)
                charToOrdinal = listFromString[int(arg3Val)]
                ordinalValue = ord(charToOrdinal)
        except:
                sys.stderr.write("Index of character out of bounds\n")
                sys.exit(58)

        #add ordinal value of char to integer variable
        saveTo('int', ordinalValue, arg1Val)

def ins_CALL(arg1Type, arg1Val):
        global callStack
        global orderCounter
        #add incremented position of instruction counter to call stack
        callStack.append((orderCounter + 1))
        # minus 1 because order counter is incremented after switch of instructions
        orderCounter = int(labelDictionary[arg1Val]) - 1

def ins_WRITE(arg1Type,arg1Val):

        if arg1Type == 'var':
                typeAndValueFromVar1 = getFrom(arg1Val)
                arg1Type = typeAndValueFromVar1[0]
                arg1Val = typeAndValueFromVar1[1]
        if arg1Type == 'nil':
                print("",end='')
        else:
                print(arg1Val,end='')

def ins_READ(arg1Type, arg1Val, arg2Type, arg2Val):
        pass

#end of INSTRUCTION interpretation functions-------------------------------


#interpretation---------------------------------------------
#number of instructions to iterate to
maxOrder = int(list(instructionsDictionary)[-1])
while orderCounter <= maxOrder:
        #except is used if there is missing order number and skips until finds next instruction
        try:
                ins = instructionsDictionary[str(orderCounter)]
        except:
                orderCounter = orderCounter + 1
                continue
        #instruction opcode and order
        insOpcode = ins.get('opcode').upper()
        insOrder = orderCounter
        #arguments of instruciton
        if 'arg1' in ins: 
                insArg1 = ins.get('arg1')
                #instruciton argument type
                insArg1Type = ins.get('arg1')[0]
                #instruciton argument type
                insArg1Val = ins.get('arg1')[1]
                if 'arg2' in ins: 
                        insArg2 = ins.get('arg2')
                        #instruciton argument type
                        insArg2Type = ins.get('arg2')[0]
                        #instruciton argument type
                        insArg2Val = ins.get('arg2')[1]
                        if 'arg3' in ins: 
                                #instruciton argument type
                                insArg3Type = ins.get('arg3')[0]
                                #instruciton argument type
                                insArg3Val = ins.get('arg3')[1]
        #instruction switch
        if insOpcode == 'CREATEFRAME':
                ins_CREATEFRAME()
        elif insOpcode == 'PUSHFRAME':
                ins_PUSHFRAME()
        elif insOpcode == 'POPFRAME':
                ins_POPFRAME()
        elif insOpcode == 'RETURN':
                ins_RETURN()
        elif insOpcode == 'BREAK':
                pass
        elif insOpcode == 'DEFVAR':
                ins_DEFVAR(insArg1Type,insArg1Val)
        elif insOpcode == 'PUSHS':
                ins_PUSHS(insArg1Val)
        elif insOpcode == 'POPS':
                ins_POPS(insArg1Type,insArg1Val)
        elif insOpcode == 'MOVE':
                ins_MOVE(insArg1Type, insArg1Val, insArg2Type, insArg2Val)
        elif insOpcode == 'ADD' or\
        insOpcode == 'SUB' or\
        insOpcode == 'MUL' or\
        insOpcode == 'IDIV':
                ins_ADD_SUB_MUL_IDIV(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val,insOpcode)
        elif insOpcode == 'LT' or\
        insOpcode == 'GT' or\
        insOpcode == 'EQ':
                ins_LT_GT_EQ(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val,insOpcode)
        elif insOpcode == 'AND':
                ins_AND(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val)
        elif insOpcode == 'OR':
                ins_OR(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val)  
        elif insOpcode == 'NOT':
                ins_NOT(insArg1Type, insArg1Val, insArg2Type, insArg2Val)   
        elif insOpcode == 'INT2CHAR':
                ins_INT2CHAR(insArg1Type, insArg1Val, insArg2Type, insArg2Val)  
        elif insOpcode == 'STRI2INT':
                ins_STRI2INT(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val) 
        elif insOpcode == 'CONCAT':
                ins_CONCAT(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val) 
        elif insOpcode == 'STRLEN':
                ins_STRLEN(insArg1Type, insArg1Val, insArg2Type, insArg2Val) 
        elif insOpcode == 'TYPE':
                ins_TYPE(insArg1Type, insArg1Val, insArg2Type, insArg2Val) 
        elif insOpcode == 'LABEL':
                pass
        elif insOpcode == 'JUMP':
                ins_JUMP(insArg1Val) 
        elif insOpcode == 'JUMPIFEQ':
                ins_JUMPIFEQ(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val) 
        elif insOpcode == 'JUMPIFNEQ':
                ins_JUMPIFNEQ(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val)
        elif insOpcode == 'DRPINT':
                pass
        elif insOpcode == 'EXIT':
                ins_EXIT(insArg1Type, insArg1Val)
        elif insOpcode == 'GETCHAR':
                ins_GETCHAR(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val) 
        elif insOpcode == 'SETCHAR':
                ins_SETCHAR(insArg1Type, insArg1Val, insArg2Type, insArg2Val, insArg3Type, insArg3Val) 
        elif insOpcode == 'WRITE':
                ins_WRITE(insArg1Type,insArg1Val)
        elif insOpcode == 'READ':
                ins_READ(insArg1Type, insArg1Val, insArg2Type, insArg2Val)
        elif insOpcode == 'CALL':
                ins_CALL(insArg1Type, insArg1Val)
        else:
                orderCounter = orderCounter + 1

        
        orderCounter = orderCounter + 1
#end of interpretation-----------------------------------------------------------