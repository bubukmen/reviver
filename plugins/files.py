# -*- coding: utf-8 -*-

import os,ConfigParser,nastroje

class action:
	def __init__ (self, configFile, vynucena, denSpusteni):
		cnfP = ConfigParser.ConfigParser()
		cnfP.read(configFile)
		backupTo = cnfP.get('global', 'backupTo')
		sourceList = cnfP.get('files', 'sourceList')
		excludeCommand = ''
		if cnfP.has_option('files', 'excludeList'):
			excludeList = cnfP.get('files', 'excludeList')
			excludeCommand = '-X ' + excludeList + ' '

		komprFlag, komprString, komprString2, komprString3 = nastroje.komprese(cnfP.get('global', 'compression'))
		typZal = nastroje.typZalohy(denSpusteni, vynucena)
		includeList = self.sourceFiles(sourceList)
		if typZal == 0:
			textZalohovani = 'denní přírůstkovou'
			tarCommand = '--after-date=yesterday'
		if typZal == 1:
			textZalohovani = 'týdenní přírůstkovou'
			tarCommand = '--after-date=-1week'
		if typZal == 2:
			textZalohovani = 'kompletní měsíční'
			tarCommand = ''
		if typZal == 3:
			textZalohovani = 'vynucenou kompletní'
			tarCommand = ''
		soubor = nastroje.nazevSouboru(denSpusteni, typZal, backupTo, komprString)
		print "Provádím " + textZalohovani + " zálohu souborů... (" + soubor + ")"
		backupString = 'tar ' + excludeCommand + tarCommand + ' -hc' + komprFlag + 'f ' + soubor + includeList
		os.system(backupString)

	def sourceFiles(self, sourceList):
		includeList = ""
		soubor = open(sourceList, 'r')
		for i in soubor:
			includeList = includeList + " " + i.strip('\n')
		return includeList

