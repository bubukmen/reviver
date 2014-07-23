# -*- coding: utf-8 -*-

import os
from random import randrange
from datetime import datetime

def randomPasswordGenerator(self, pocet_pismen):
	output, a, generation = "", 0, 0
	while a < letterCount:
		generation = randrange(48,122,1)
		if (generation >= 48 and generation <= 57) or (generation >= 65 and generartion <= 90) or (generation >= 97 and generation <= 122):
			output += chr(generation)
			a += 1
	return output

def getDateTimeValues(dnes):
	day = int(dnes.strftime('%w'))
	dayOfMonth = int(dnes.strftime('%d'))
	week = int(dnes.strftime('%W'))
	month = int(dnes.strftime('%m'))
	year = int(dnes.strftime('%Y'))
	return day, dayOfMonth, week, month, year


def getBackupType(dateOfRun, forced):
	day, dayOfMonth, week, month, year = getDateTimeValues(dateOfRun)
	if forced == 'Y':
		output = 3 #forced backup
	else:
		if day != 0 and dayOfMonth != 1:output = 0 #daily incremental
		if day == 0 and dayOfMonth != 1: output = 1 #weekly incremental
		if dayOfMonth == 1: output = 2 #monthly
	return output

def genFullPath(backupTo, backupLabel):
	return backupTo + '/' + backupLabel

def genFileName(prefix, dateOfRun, fullPath, backupLabel, suffix, bkpType=0):
	output = ''
	if bkpType == 3: output = fullPath + '/' + prefix + '_' + backupLabel + '_' + dateOfRun.strftime('%Y-%m-%d') + '-forced' + suffix
	if bkpType == 2: output = fullPath + '/' + prefix + '_' + backupLabel + '_' + dateOfRun.strftime('%Y-%m-%d') + '-monthly' + suffix
	if bkpType == 1: output = fullPath + '/' + prefix + '_' + backupLabel + '_' + dateOfRun.strftime('%Y-%m-%d') + '-weekly' + suffix
	if bkpType == 0: output = fullPath + '/' + prefix + '_' + backupLabel + '_' + dateOfRun.strftime('%Y-%m-%d') + '-daily' + suffix
	return output

def getCompression(bkpType):
	if bkpType == 'xz':
		komprFlag = "J"
		komprString = ".tar.xz"
		komprString2 = " | xz > "
		komprString3 = ".xz"
	elif bkpType == 'bzip':
		komprFlag = "j"
		komprString = ".tar.bz2"
		komprString2 = " | bzip2 > "
		komprString3 = ".bz2"
	elif bkpType == 'gzip':
		komprFlag = "z"
		komprString = ".tar.gz"
		komprString2 = " | gzip > "
		komprString3 = ".gz"
	elif bkpType == 'none':
		komprFlag = ""
		komprString = ".tar"
		komprString2 = " > "
		komprString3 = ".sql"
	else:
		print("Unknown value \"" + bpkType + "\". Compression turned off.")
		komprFlag = ""
		komprString = ".tar"
		komprString2 = " > "
		komprString3 = ".sql"

	return komprFlag, komprString, komprString2, komprString3

def checkTargetDirectoryStructure(fullPath):
	if not os.path.isdir(fullPath):
		print('Creating directory ' + fullPath)
		os.makedirs(fullPath)
