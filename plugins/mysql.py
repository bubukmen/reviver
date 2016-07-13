#!/usr/bin/env python
import os, reviverTools

class action:
  def __init__ (self, globalConf, instructions, forced, dayOfRun):
    backupTo = globalConf['backupTo']
    backupLabel = instructions['backupLabel']
    mysqlDumpCommand = instructions['dumpCommand']
    mysqlServer = instructions['server']
    mysqlUser = instructions['user']
    mysqlPassword = instructions['password']
    mysqlPort = instructions['port']

    komprFlag, komprString, komprString2, komprString3 = reviverTools.getCompression(globalConf['compression'])
    fullPath = reviverTools.genFullPath(backupTo, backupLabel)
    genFile = reviverTools.genFileName('mysql', dayOfRun, fullPath, backupLabel, komprString3)
    backupString = mysqlDumpCommand + ' -A -h ' + mysqlServer + ' -P ' + str(mysqlPort) + ' -u ' + mysqlUser + ' --password=\"' + mysqlPassword + '\"' + komprString2 + genFile
    print('Making MySQL backup to ' + genFile + ' file')
    reviverTools.checkTargetDirectoryStructure(fullPath)
    os.system(backupString)
