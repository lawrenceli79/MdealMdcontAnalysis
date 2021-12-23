#!/usr/bin/env python3
# Created By  : Lawrence Li
# Created Date: 2021/12/23
# version ='1.0'
#
# This is for anken:  患者カルテが開けない（UAE発生）[#992708]
# MDEA.DBF(pid=15848,cvt=77760) has bad MDCONT(s) content.
# This script will fix wrong 0xfd???? to correct sequence.
# mdeal.txt assumes 21 MDCONT fields with MDCONT FieldLen=96 

import sys
import os
import re
import time

if(len(sys.argv) < 2):
    print ("Usage:")
    print ("    py {} <mdeal.txt> ".format(os.path.basename(__file__)))
    sys.exit()

strInFile = sys.argv[1]

# Put all MDCONT(s) to allMDcont[]
allMDcont = []
with open(strInFile) as fInFile:
    for line in fInFile:
        fields = line.split()
        for i in range(0, 21): # Assume 21 MDCONT fields
            field = fields[i]
            allMDcont.append(field)

# Set correct 0xfd???? sequence in allMDcont
for i,mdcont in enumerate(allMDcont):
    headerFD = mdcont[2:4]
    headerSeq = mdcont[4:8]
    content = mdcont[8:]
    if (headerFD=="00" and headerSeq=="0000"):
        pass
    else:
        if (headerFD=="fd"):
            i_1 = (i>>8) & 0xFF
            i_0 = i & 0xFF
            mdcontFixed = "0xfd{:02x}{:02x}{}".format(i_0, i_1, content)
            allMDcont[i] = mdcontFixed
        else:
            assert False, "Oh no! This assertion failed!"

# Values for output
pid=15848
#cvt=77760
addtm="0x51e3123700"
dbh=0
updtm="0x51e3123700"
fmt="0x00"
cnttm="0x0000000000"
cvt = 77832

# Output allMDcont
mdconts = allMDcont
seq = 0
jNextStart = 0
while True:
    jStart = jNextStart
    jNextStart = jStart+21
    jEnd = min(jNextStart, len(mdconts))

    strMdconts = "" # concat of all mdcont fields
    for k in range(jStart, jEnd):
        strMdconts = strMdconts + " " + mdconts[k]
    for k in range(jEnd, jNextStart): # For remaining fields, do padding
        strMdconts = strMdconts + " 0x" + '00'*96  # Assume FieldLen=96, padd '00' 
    
    # Assume following fields sequence
    lineOut = "{mdconts:>4096} {midnum:>9} {mvisit:>9} {mseq:>6} {addtime:>12} {dbhndl:>6} {updtime:>12} {mdatafmt:>4} {cntntupt:>12}".format(
        mdconts=strMdconts, midnum=pid, mvisit=cvt, mseq=seq, addtime=addtm, dbhndl=dbh, updtime=updtm, mdatafmt=fmt, cntntupt=cnttm )
    print(lineOut)
    seq += 1
    if(jNextStart >= len(mdconts)):
        break
