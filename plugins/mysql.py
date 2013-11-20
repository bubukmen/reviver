# -*- coding: utf-8 -*-

import os,configparser,reviverTools

class action:
	def __init__ (self, configFile, vynucena, denSpusteni):
		cnfP = configparser.ConfigParser()
		cnfP.read(configFile)
		backupTo = cnfP.get('global', 'backupTo')
		mysqlDumpCommand = cnfP.get('mysql', 'mysqlDumpCommand')
		mysqlServer = cnfP.get('mysql', 'mysqlServer')
		mysqlUser = cnfP.get('mysql', 'mysqlUser')
		mysqlPassword = cnfP.get('mysql', 'mysqlPassword')
		mysqlPort = cnfP.get('mysql', 'mysqlPort')

		komprFlag, komprString, komprString2, komprString3 = reviverTools.komprese(cnfP.get('global', 'compression'))
		soubor = reviverTools.nazevSouboru('mysql', denSpusteni, backupTo, komprString3)
		backupString = mysqlDumpCommand + ' -A -P ' + mysqlPort + ' -u ' + mysqlUser + ' --password=\"' + mysqlPassword + '\"' + komprString2 + soubor
		print('Making MySQL backup to ' + soubor + ' file')
		os.system(backupString)
