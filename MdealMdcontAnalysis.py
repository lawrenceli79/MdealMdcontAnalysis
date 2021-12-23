import sys
import os
import re

if(len(sys.argv) < 2):
    print ("Usage:")
    print ("    py {} <mdeal.txt> ".format(os.path.basename(__file__)))
    sys.exit()

strInFile = sys.argv[1]

with open(strInFile) as fInFile:
    for line in fInFile:
        mdheaders = []
        fields = line.split()
        for i in range(0, 21):
            field = fields[i]
            header = field[2:6]
            mdheaders.append(header)
        allmdheaders = ','.join(mdheaders)
        midnum = fields[21]
        mvisit = fields[22]
        mseq = fields[23]
        lineOut = "{},{},{},{}".format(midnum, mvisit, mseq, allmdheaders)
        print(lineOut)




        