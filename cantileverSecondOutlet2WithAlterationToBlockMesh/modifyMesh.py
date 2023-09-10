#! /user/bin/env python

import fnmatch, sys

argument = sys.argv
print ("Length of the beam should be %s" % argument[1])
print ("Deflection of the beam should be %s" % argument[2])
print ("Start position of outlet 2 should be %s" % argument[3])
print ("Start position of outlet 1 should be %s" % argument[4])

Aout1 = round(1 / (float(argument[5]) + 1) * float(argument[5]), 2)
Aout1 = 0.05 * round(Aout1/0.05) # round to the closest 0.05
Aout2 = round(1 / (float(argument[5]) + 1), 2)
Aout2 = 0.05 * round(Aout2/0.05) # round to the closest 0.05
print ("area of outlet 1 should be %.2f" % Aout1)
print ("area of outlet 2 should be %.2f" % Aout2)

var2changeCantLength = ("cantLength %s;" % argument[1])
identifierCantLength = "cantLength"
var2changeCantDeflect = ("cantDeflect %s;" % argument[2])
identifierCantDeflect = "cantDeflect"
var2changeOutlet2 = ("HO2Start %s;" % argument[3])
identifierOutlet2 = "HO2Start"
var2changeOutlet1 = ("WO1Start %s;" % argument[4])
identifierOutlet1 = "WO1Start"
var2changeLenOutlet1 = ("WO1 %.2f;" % Aout1)
identifierLenOutlet1 = "WO1"
var2changeLenOutlet2 = ("HO2 %.2f;" % Aout2)
identifierLenOutlet2 = "HO2"

# Read file
file = open('system/blockMeshDict', 'r')
fileLines = file.read()
fileLines = fileLines.splitlines()

for lineNum,var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join([identifierCantLength,'*'])): break

for lineNumDeflect,var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join([identifierCantDeflect,'*'])): break

for lineNumOut2,var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join([identifierOutlet2,'*'])): break

for lineNumOut1,var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join([identifierOutlet1,'*'])): break

for lineNumLenOut1,var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join([identifierLenOutlet1,'*'])): break

for lineNumLenOut2,var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join([identifierLenOutlet2,'*'])): break

file.close()

file = open("system/blockMeshDict", "w")
for ln, data in enumerate(fileLines):
    if ln == lineNum:
        lineToWrite = ''.join([var2changeCantLength, '\n'])
    elif ln == lineNumDeflect:
        lineToWrite = ''.join([var2changeCantDeflect, '\n'])
    elif ln == lineNumOut2:
        lineToWrite = ''.join([var2changeOutlet2, '\n'])
    elif ln == lineNumOut1:
        lineToWrite = ''.join([var2changeOutlet1, '\n'])
    elif ln == lineNumLenOut1:
        lineToWrite = ''.join([var2changeLenOutlet1, '\n'])
    elif ln == lineNumLenOut2:
        lineToWrite = ''.join([var2changeLenOutlet2, '\n'])
    else:
        lineToWrite = ''.join([data, '\n'])

    file.write(lineToWrite)

file.close()
