#!/usr/bin/env python
import os, reviverTools

class action:
	def __init__ (self, globalConf, instructions, forced, dayOfRun):
		backupTo = globalConf['backupTo']
		backupLabel = instructions['backupLabel']
		pgDumpCommand = instructions['dumpCommand']
		pgServer = instructions['server']
		pgpassFile = instructions['pgpassFile']
		pgUser = instructions['user']
		pgPort = instructions['port']

		komprFlag, komprString, komprString2, komprString3 = reviverTools.getCompression(globalConf['compression'])
		fullPath = reviverTools.genFullPath(backupTo, backupLabel)
		genFile = reviverTools.genFileName('pgsql', dayOfRun, fullPath, backupLabel, komprString3)
		backupString = "PGPASSFILE=\"" + pgpassFile + "\" " + pgDumpCommand + " -p " + str(pgPort) + " -U " + pgUser + komprString2 + genFile
		print("Making Postgresql backup to " + genFile + ' file')
		reviverTools.checkTargetDirectoryStructure(fullPath)
		os.system(backupString)
		
