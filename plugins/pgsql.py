# -*- coding: utf-8 -*-

import os,ConfigParser,nastroje

class action:
	def __init__ (self, configFile, vynucena, denSpusteni):
		cnfP = ConfigParser.ConfigParser()
		cnfP.read(configFile)
		backupTo = cnfP.get('global', 'backupTo')
		pgDumpCommand = cnfP.get('pgsql', 'pgDumpCommand')
		pgServer = cnfP.get('pgsql', 'pgServer')
		pgpassFile = cnfP.get('pgsql', 'pgpassFile')
		pgUser = cnfP.get('pgsql', 'pgUser')
		pgPort = cnfP.get('pgsql', 'pgPort')

		komprFlag, komprString, komprString2, komprString3 = nastroje.komprese(cnfP.get('global', 'compression'))
		backupString = "PGPASSFILE=\"" + pgpassFile + "\" " + pgDumpCommand + " -p " + pgPort + " -U " + pgUser + komprString2 + backupTo + "/pgsql" + komprString3
		print "Zálohuji databázi Postgresql do souboru " + backupTo + "/pgsql" + komprString3
		os.system(backupString)
		
