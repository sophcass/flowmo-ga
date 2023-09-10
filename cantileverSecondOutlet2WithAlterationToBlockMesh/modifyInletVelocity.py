#! /user/bin/env python

import fnmatch, sys

argument = sys.argv
print("New inlet velocity is %s" % argument[1])

var2change = ("        value           uniform (0 %s 0);" % argument[1])
identifier = "value"

#Read file
file = open('0/U', 'r')
fileLines = file.read()
fileLines = fileLines.splitlines()

for lineNum, var in enumerate(fileLines):
    if fnmatch.fnmatch(str(var),''.join(['*',identifier,'*'])): break

file.close()

file = open("0/U", "w")
for ln, data in enumerate(fileLines):
    if ln == lineNum:
        lineToWrite = ''.join([var2change, '\n'])
    else:
        lineToWrite = ''.join([data, '\n'])
    file.write(lineToWrite)

file.close()
