#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import sys, os, stat, subprocess, reviverTools
try:
  import pymssql
except ImportError as err:
  print('Error while loading %s\nYou probably need to install this module.' % (err.name))
  sys.exit(1)

class action:

  # Constructor where all variables are set and moved inside the class
  def __init__ (self, globalConf, instructions, forced, dateOfRun, log):
    self.globalConf = globalConf
    self.instructions = instructions
    self.forced = forced
    self.dateOfRun = dateOfRun
    self.log = log
    self.backupTo = self.globalConf['backupTo']
    self.backupLabel = self.instructions['backupLabel']
    self.localBackupDir = reviverTools.sanitizePath(self.instructions['localBackupDir'])
    self.keepTime = -1
    if 'keep' in self.instructions:
      self.keepTime = self.instructions['keep']
    if 'server' in self.instructions:
      self.mssqlServer = self.instructions['server']
    else:
      self.mssqlServer = '127.0.0.1'
    self.mssqlUser = self.instructions['user']
    self.mssqlPassword = self.instructions['password']
    if 'port' in self.instructions:
      self.mssqlPort = self.instructions['port']
    else:
      self.mssqlPort = 1433
    if 'databases' in self.instructions:
      self.mssqlDatabaseList = self.instructions['databases']
    else:
      self.mssqlDatabaseList = self.findAllDatabases()
    if 'mountPoint' in self.instructions:
      self.mountPoint = reviverTools.sanitizePath(self.instructions['mountPoint'])
    else:
      self.mountPoint = None
    self.transformDatabaseList()
    self.tarCommand = reviverTools.findApp('tar')
    if self.initRest():
      return
    self.main()

  # Initialize more variables based on config file. Preparations for main backup function
  def initRest(self):
    self.comprFlag, self.comprString, self.comprString2, self.comprString3 = reviverTools.getCompression(self.globalConf['compression'])
    self.fullPath = reviverTools.genFullPath(self.backupTo, self.backupLabel)
    self.genFile = reviverTools.genFileName('mssql', self.dateOfRun, self.fullPath, self.backupLabel, '.tar')
    self.genFinalFile = reviverTools.genFileName('mssql', self.dateOfRun, self.fullPath, self.backupLabel, self.comprString)
    self.compressionProgram = reviverTools.findApp(self.comprString2[0])
    if self.compressionProgram is None:
      print('Error: Can\'t find compression program %s' % self.comprString2[0])
      return 1

  #Function to generate Tar command
  def genBackupString(self, dbFileName, append=True):
    transform1 = 's/}_[0-9a-f]*.bak$/.bak/'
    transform2 = 's/^{/%s\\//' % self.backupLabel
    return [
      self.tarCommand,
      '--transform',
      transform1,
      '--transform',
      transform2,
      '-C',
      '%s/' % self.mountPoint if 'mountPoint' in self.instructions else '%s/' % self.localBackupDir,
      '-vrf' if append else '-vcf',
      self.genFile,
      dbFileName
      ]

  #Function cleaning old temporary MSSQL BAK files
  def cleanDbBakFile(self, dbFileName):
    fileDir = self.mountPoint if 'mountPoint' in self.instructions else self.localBackupDir
    try:
      os.unlink('%s/%s' % (fileDir, dbFileName))
    except Exception as e:
      print('Error while removing db BAK file: %s' % str(e))

  def findAllDatabases(self):
    print('Acquiring all MSSQL databases to backup...')
    retVal = None
    with pymssql.connect(server=self.mssqlServer, user=self.mssqlUser, password=self.mssqlPassword, database="master", port=self.mssqlPort) as conn:
      with conn.cursor() as cursor:
        cursor.execute('select name from master.sys.databases where name != %s', 'tempdb')
        retVal = [i[0] for i in cursor.fetchall()]
    return retVal
  
  #Function creating list of pair Database name and Unique ID
  def transformDatabaseList(self):
    self.mssqlDatabaseList = [{'dbName': i, 'dbUniqueId': reviverTools.genUniqueId()} for i in self.mssqlDatabaseList]

  #Function to safely mount or unmount remote filesystem
  def remoteMount(self, unmount=False):
    if 'mountPoint' not in self.instructions:
      return
    if not self.mountPoint:
      return
    mountStatus = reviverTools.testIfMounted(self.mountPoint)
    if (not unmount and mountStatus) or (unmount and not mountStatus):
      return
    if not unmount:
      mntCommand = reviverTools.findApp('mount')
    else:
      mntCommand = reviverTools.findApp('umount')
    commandLine = [mntCommand, self.mountPoint]
    try:
      subprocess.run(commandLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as err:
      print('Mount command failed: %s' % err.stderr)
      raise

  #FFunction to test if final Tar filename already exists. If yes, function will rename this file with unique ID suffix for safety reasons
  def sanitizeAlreadyExistingFile(self, targetFile):
    if os.access(targetFile, os.F_OK):
      fileSuffix = reviverTools.genUniqueId(5)
      print('File %s aready exists. For safety reasons file will be renamed to %s' % (targetFile, '%s_%s' % (targetFile, fileSuffix)))
      os.rename(targetFile, '%s_%s' % (targetFile, fileSuffix))

  # Main backup function where final backup command is executed
  def main(self):
    reviverTools.checkTargetDirectoryStructure(self.fullPath)
    try:
      self.remoteMount()
    except subprocess.CalledProcessError:
      return
    print('Making MSSQL backup to %s file' % self.genFinalFile)
    try:
      with pymssql.connect(server=self.mssqlServer, user=self.mssqlUser, password=self.mssqlPassword, database="master", port=self.mssqlPort, autocommit=True) as conn:
        with conn.cursor() as cursor:
          firstRunLoop = False
          for i in self.mssqlDatabaseList:
            print('Processing database %s' % i['dbName'])
            tempFile = '%s%s{%s}_%s.bak' % (self.localBackupDir, reviverTools.guessPathSeparator(self.localBackupDir), i['dbName'], i['dbUniqueId'])
            cursor.execute('backup database [%s] ' % i['dbName'] + 'to disk = %s with no_compression, format', tempFile)
            if not firstRunLoop:
              firstRunLoop = True
              backupString = self.genBackupString('{%s}_%s.bak' % (i['dbName'], i['dbUniqueId']), append=False)
            else:
              backupString = self.genBackupString('{%s}_%s.bak' % (i['dbName'], i['dbUniqueId']))
            try:
              subprocess.run(backupString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
            except subprocess.CalledProcessError as err:
              print('Backup command %s failed' % (err.stderr))
              self.cleanDbBakFile('{%s}_%s.bak' % (i['dbName'], i['dbUniqueId']))
              return
            self.cleanDbBakFile('{%s}_%s.bak' % (i['dbName'], i['dbUniqueId']))
    except pymssql.OperationalError as err:
      print('MSSQL backup failed with error: %s' % (err))
      return
    self.remoteMount(unmount=True)
    if self.comprString2:
      self.sanitizeAlreadyExistingFile(self.genFinalFile)
      compressCmdLine = [self.compressionProgram, self.genFile]
      try:
        subprocess.run(compressCmdLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
      except subprocess.CalledProcessError as err:
        print('Compression command failed: %s' % err.stderr)
        return

    # Remove old backup files after main backup function
    if self.keepTime > -1:
      reviverTools.cleanOldBackupFiles(self.fullPath, self.dateOfRun, self.keepTime, 'mssql_%s' % (self.backupLabel), self.comprString, True)
        