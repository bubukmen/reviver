# -*- coding: utf-8 -*-

import os,configparser,reviverTools

class action:
	def __init__ (self, configFile, vynucena, denSpusteni):
		cnfP = configparser.ConfigParser()
		cnfP.read(configFile)
		backupTo = cnfP.get('global', 'backupTo')
		sourceList = cnfP.get('files', 'sourceList')
		excludeCommand = ''
		if cnfP.has_option('files', 'excludeList'):
			excludeList = cnfP.get('files', 'excludeList')
			excludeCommand = '-X ' + excludeList + ' '

		komprFlag, komprString, komprString2, komprString3 = reviverTools.komprese(cnfP.get('global', 'compression'))
		typZal = reviverTools.typZalohy(denSpusteni, vynucena)
		includeList = self.sourceFiles(sourceList)
		if typZal == 0:
			textZalohovani = 'daily incremental'
			tarCommand = '--after-date=yesterday'
		if typZal == 1:
			textZalohovani = 'weekly incremental'
			tarCommand = '--after-date=-1week'
		if typZal == 2:
			textZalohovani = 'complete full'
			tarCommand = ''
		if typZal == 3:
			textZalohovani = 'forced complete full'
			tarCommand = ''
		soubor = reviverTools.nazevSouboru('files', denSpusteni, backupTo, komprString, typ=typZal)
		print('Making ' + textZalohovani + ' backup of files... (' + soubor + ')')
		backupString = 'tar ' + excludeCommand + tarCommand + ' -hc' + komprFlag + 'f ' + soubor + includeList
		os.system(backupString)

	def sourceFiles(self, sourceList):
		includeList = ''
		soubor = open(sourceList, 'r')
		for i in soubor:
			includeList = includeList + ' ' + i.strip('\n')
		return includeList

