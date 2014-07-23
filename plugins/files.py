#!/usr/bin/env python
import os, reviverTools

class action:
	def __init__ (self, globalConf, instructions, forced, dateOfRun):
		backupTo = globalConf['backupTo']
		backupLabel = instructions['backupLabel']
		sourceList = instructions['sources']
		excludeCommand = ''
		if 'exclude' in instructions:
			if instructions['exclude'] is not None:
				excludeList = instructions['exclude']
				excludeCommand = self.genExcludeCommand(excludeList)

		komprFlag, komprString, komprString2, komprString3 = reviverTools.getCompression(globalConf['compression'])
		bkpType = reviverTools.getBackupType(dateOfRun, forced)
		includeList = self.genSourceCommand(sourceList)
		if bkpType == 0:
			outputText = 'daily incremental'
			tarCommand = '--after-date=yesterday'
		if bkpType == 1:
			outputText = 'weekly incremental'
			tarCommand = '--after-date=-1week'
		if bkpType == 2:
			outputText = 'complete full'
			tarCommand = ''
		if bkpType == 3:
			outputText = 'forced complete full'
			tarCommand = ''
		fullPath = reviverTools.genFullPath(backupTo, backupLabel)
		genFile = reviverTools.genFileName('files', dateOfRun, fullPath, backupLabel, komprString, bkpType)
		print('Making ' + outputText + ' backup of files... (' + genFile + ')')
		backupString = 'tar ' + excludeCommand + tarCommand + ' -hc' + komprFlag + 'f ' + genFile + includeList
		reviverTools.checkTargetDirectoryStructure(fullPath)
		os.system(backupString)

	def genSourceCommand(self, sourceList):
		output = ''
		for i in sourceList:
			output += ' ' + i
		return output

	def genExcludeCommand(self, excludeList):
		output = ''
		for i in excludeList:
			output += '--exclude=' + i + ' '
		return output
