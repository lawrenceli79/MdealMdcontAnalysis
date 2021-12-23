#!/usr/bin/env python3
# Created By  : Lawrence Li
# Created Date: 2021/12/23
# version ='1.0'
#
# This is for anken:  患者カルテが開けない（UAE発生）[#992708]
# MDEA.DBF(pid=15848,cvt=77760) has bad MDCONT(s) content.
# Maybe many mvisit(s) mdeal content are packed into single cvt=77760.
# This script will try to split them to multiple cvisit(s) according to "0xfd0000" start
# mdeal.txt assumes 21 MDCONT fields with MDCONT FieldLen=96 

import sys
import os
import re
import time
from datetime import datetime
from datetime import timedelta

def MakeCvisit(year:int, month:int, day:int)->int:
    cvisit=(year-85)*12+month-1
    cvisit<<=8
    cvisit+=day<<3
    return cvisit

def GetCvisitOfDateShift(dt:datetime, nDays:int)->int:
    dt2 = dt + timedelta(days=nDays)
    cvisit = MakeCvisit(dt2.year-1900, dt2.month, dt2.day)
    return cvisit


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

# Split allMDcont[] to splitMDconts[][] according to "0xfd00" start
splitMDconts = []
mdconts = []
for i,mdcont in enumerate(allMDcont):
    header = mdcont[2:8] # skip beginning "0x" and get "fd??"
    if (header=="000000"):
        pass
    else:
        if (header=="fd0000"):
            if (len(mdconts)>0):
                splitMDconts.append(mdconts)
                mdconts = []
        mdconts.append(mdcont)
splitMDconts.append(mdconts)
mdconts = []

# Values for output
pid=15848
#cvt=77760
addtm="0x51e3123700"
dbh=0
updtm="0x51e3123700"
fmt="0x00"
cnttm="0x0000000000"
dtStartDate = datetime(year=2010, month=5, day=1)

# Output splitMDconts
for i,mdconts in enumerate(splitMDconts):
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
        cvt = GetCvisitOfDateShift(dtStartDate, i)
        
        # Assume following fields sequence
        lineOut = "{mdconts:>4096} {midnum:>9} {mvisit:>9} {mseq:>6} {addtime:>12} {dbhndl:>6} {updtime:>12} {mdatafmt:>4} {cntntupt:>12}".format(
            mdconts=strMdconts, midnum=pid, mvisit=cvt, mseq=seq, addtime=addtm, dbhndl=dbh, updtime=updtm, mdatafmt=fmt, cntntupt=cnttm )
        print(lineOut)
        seq += 1
        if(jNextStart >= len(mdconts)):
            break
