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
    if 'keep' in self.instructions:
      self.keepTime = self.instructions['keep']
    self.backupTo = self.globalConf['backupTo']
    self.compressionType = instructions['compression'] if 'compression' in instructions else globalConf['compression']
    self.backupLabel = self.instructions['backupLabel']
    self.pgDumpCommand = reviverTools.findApp('pg_dumpall')
    if self.pgDumpCommand is None:
      print('Error: Can\'t find dump command pg_dumpall.')
      return
    self.pgServer = self.instructions['server']
    self.pgUser = self.instructions['user']
    self.pgPassword = self.instructions['password']
    self.pgPort = self.instructions['port']
    if self.initRest():
      return
    self.main()

  # Initialize more variables based on config file. Preparations for main backup function
  def initRest(self):
    self.komprFlag, self.komprString, self.komprString2, self.komprString3 = reviverTools.getCompression(self.compressionType)
    self.fullPath = reviverTools.genFullPath(self.backupTo, self.backupLabel)
    self.genFile = reviverTools.genFileName('pgsql', self.dateOfRun, self.fullPath, self.backupLabel, self.komprString3)
    self.compressionProgram = reviverTools.findApp(self.komprString2[0])
    if self.compressionProgram is None:
      print('Error: Can\t find compression program %s' % self.komprString2[0])
      return 1

  def genConfigFile(self):
    insertToFile = ('%s:%s:*:%s:%s' % (self.pgServer, self.pgPort, self.pgUser, self.pgPassword)).encode()
    rndFileName = '/tmp/PGSQL-%s.conf' % reviverTools.genUniqueId()
    fd = os.open(rndFileName, os.O_RDWR | os.O_CREAT)
    os.chown(fd, 0, 0)
    os.chmod(fd, stat.S_IRUSR | stat.S_IWUSR)
    os.write(fd, insertToFile)
    os.close(fd)
    return rndFileName

  def main(self):
    reviverTools.checkTargetDirectoryStructure(self.fullPath)
    print('Making PostgreSQL backup to %s file' % self.genFile)
    tmpConfigFile = self.genConfigFile()
    tmpEnv = os.environ.copy()
    tmpEnv['PGPASSFILE'] = tmpConfigFile
    self.cmdLine1 = [self.pgDumpCommand, '-h', self.pgServer, '-p', str(self.pgPort), '-U', self.pgUser]
    self.cmdLine2 = self.compressionProgram
    f = open(self.genFile, 'wb')

    if self.komprString2 is None:
      self.cmdLine1.append('-f')
      self.cmdLine1.append(self.genFile)
      p1 = subprocess.Popen(self.cmdLine1, stdout=subprocess.PIPE, env=tmpEnv)
      p1.wait()
    else:
      p1 = subprocess.Popen(self.cmdLine1, stdout=subprocess.PIPE, env=tmpEnv)
      p2 = subprocess.Popen(self.cmdLine2, stdin=p1.stdout, stdout=f)
      p1.wait()
      p2.wait()
    f.close()
    os.unlink(tmpConfigFile)

    # Remove old backup files after main backup function
    if self.keepTime > -1:
      reviverTools.cleanOldBackupFiles(self.fullPath, self.dateOfRun, self.keepTime, 'pgsql_%s' % (self.backupLabel), self.komprString3, True)
