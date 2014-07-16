#!/usr/bin/env python
import os,configparser,reviverTools

class action:
	def __init__ (self, configFile, vynucena, denSpusteni):
		cnfP = configparser.ConfigParser()
		cnfP.read(configFile)
		backupTo = cnfP.get('global', 'backupTo')
		pgDumpCommand = cnfP.get('pgsql', 'pgDumpCommand')
		pgServer = cnfP.get('pgsql', 'pgServer')
		pgpassFile = cnfP.get('pgsql', 'pgpassFile')
		pgUser = cnfP.get('pgsql', 'pgUser')
		pgPort = cnfP.get('pgsql', 'pgPort')

		komprFlag, komprString, komprString2, komprString3 = reviverTools.komprese(cnfP.get('global', 'compression'))
		soubor = reviverTools.nazevSouboru('pgsql', denSpusteni, backupTo, komprString3)
		backupString = "PGPASSFILE=\"" + pgpassFile + "\" " + pgDumpCommand + " -p " + pgPort + " -U " + pgUser + komprString2 + soubor
		print("Making Postgresql backup to " + soubor + ' file')
		os.system(backupString)
		
