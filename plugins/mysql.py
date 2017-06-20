#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os, stat, subprocess, reviverTools

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
    self.keepTime = -1
    if 'keep' in self.instructions:
      self.keepTime = self.instructions['keep']
    self.mysqlDumpCommand = reviverTools.findApp('mysqldump')
    if self.mysqlDumpCommand is None:
      print('Error: Can\'t find dump command mysqldump.')
      return
    self.mysqlServer = instructions['server']
    self.mysqlUser = instructions['user']
    self.mysqlPassword = instructions['password']
    self.mysqlPort = instructions['port']
    if self.initRest():
      return
    self.main()

  # Initialize more variables based on config file. Preparations for main backup function
  def initRest(self):
    self.komprFlag, self.komprString, self.komprString2, self.komprString3 = reviverTools.getCompression(self.globalConf['compression'])
    self.fullPath = reviverTools.genFullPath(self.backupTo, self.backupLabel)
    self.genFile = reviverTools.genFileName('mysql', self.dateOfRun, self.fullPath, self.backupLabel, self.komprString3)
    self.compressionProgram = reviverTools.findApp(self.komprString2[0])
    if self.compressionProgram is None:
      print('Error: Can\t find compression program %s' % self.komprString2[0])
      return 1

  # This function will generate additional temporary MySQL config file.
  def genConfigFile(self):
    insertToFile = ('[mysqldump]\nhost=%s\nuser=%s\npassword=%s' % (self.mysqlServer, self.mysqlUser, self.mysqlPassword)).encode()
    rndFileName = '/tmp/MySQL-%s.cnf' % reviverTools.generateRandomString(20)
    fd = os.open(rndFileName, os.O_RDWR | os.O_CREAT)
    os.chown(fd, 0, 0)
    os.chmod(fd, stat.S_IRUSR | stat.S_IWUSR)
    os.write(fd, insertToFile)
    os.close(fd)
    return rndFileName

 # Main backup function where final backup command is executed 
  def main(self):
    reviverTools.checkTargetDirectoryStructure(self.fullPath)
    print('Making MySQL backup to %s file' % self.genFile)
    tmpConfigFile = self.genConfigFile()
    self.cmdLine1 = [self.mysqlDumpCommand, '--defaults-extra-file=%s' % tmpConfigFile, '-A', '-h', self.mysqlServer, '-P', str(self.mysqlPort), '-u', self.mysqlUser]
    self.cmdLine2 = self.compressionProgram
    f = open(self.genFile, 'wb')

    if self.komprString2 is None:
      self.cmdLine1.append('-r')
      self.cmdLine1.append(self.genFile)
      p1 = subprocess.Popen(self.cmdLine1, stdout=subprocess.PIPE)
      p1.wait()
    else:
      p1 = subprocess.Popen(self.cmdLine1, stdout=subprocess.PIPE)
      p2 = subprocess.Popen(self.cmdLine2, stdin=p1.stdout, stdout=f)
      p1.wait()
      p2.wait()
    f.close()
    os.unlink(tmpConfigFile)

    # Remove old backup files after main backup function
    if self.keepTime > -1:
      reviverTools.cleanOldBackupFiles(self.fullPath, self.dateOfRun, self.keepTime, 'mysql_%s' % (self.backupLabel), self.komprString3, True)
