# -*- coding: utf-8 -*-

import os,ConfigParser,nastroje

class action:
	def __init__ (self, configFile, vynucena, denSpusteni):
		cnfP = ConfigParser.ConfigParser()
		cnfP.read(configFile)
		backupTo = cnfP.get('global', 'backupTo')
		mysqlDumpCommand = cnfP.get('mysql', 'mysqlDumpCommand')
		mysqlServer = cnfP.get('mysql', 'mysqlServer')
		mysqlUser = cnfP.get('mysql', 'mysqlUser')
		mysqlPassword = cnfP.get('mysql', 'mysqlPassword')
		mysqlPort = cnfP.get('mysql', 'mysqlPort')

		komprFlag, komprString, komprString2, komprString3 = nastroje.komprese(cnfP.get('global', 'compression'))
		backupString = mysqlDumpCommand + " -A -P " + mysqlPort + " -u " + mysqlUser + " --password=\"" + mysqlPassword + "\"" + komprString2 + backupTo + "/mysql" + komprString3
		print "Zálohuji databázi MySQL do souboru " + backupTo + "/mysql" + komprString3
		os.system(backupString)
		
