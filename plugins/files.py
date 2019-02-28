#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import subprocess, reviverTools

class action:

  # Constructor where all variables are set and moved inside the class
  def __init__ (self, globalConf, instructions, forced, dateOfRun, log):
    self.globalConf = globalConf
    self.instructions = instructions
    self.forced = forced
    self.dateOfRun = dateOfRun
    self.log = log
    self.backupTo = globalConf['backupTo']
    self.compressionType = instructions['compression'] if 'compression' in instructions else globalConf['compression']
    self.backupLabel = self.instructions['backupLabel']
    self.sourceList = self.instructions['sources']
    self.keepTime = -1
    if 'keep' in self.instructions:
      self.keepTime = self.instructions['keep']
    self.excludeCommands = [None]
    if 'exclude' in self.instructions:
      if self.instructions['exclude'] is not None:
        self.excludeCommands = ['--exclude=%s' % i for i in self.instructions['exclude']]
    self.tarBinary = reviverTools.findApp('tar')
    if self.tarBinary is None:
      print('No tar command found. Backup of files will exit.')
      return
    self.initRest()
    self.main()

  # Initialize more variables based on config file. Preparations for main backup function
  def initRest(self):
    self.komprFlag, self.komprString, self.komprString2, self.komprString3 = reviverTools.getCompression(self.compressionType)
    self.bkpType = reviverTools.getBackupType(self.dateOfRun, self.forced)
    if self.bkpType == 0:
      self.outputText = 'daily incremental'
      self.tarCommand = '--after-date=yesterday'
    if self.bkpType == 1:
      self.outputText = 'weekly incremental'
      self.tarCommand = '--after-date=-1week'
    if self.bkpType == 2:
      self.outputText = 'complete full'
      self.tarCommand = None
    if self.bkpType == 3:
      self.outputText = 'forced complete full'
      self.tarCommand = None
    self.fullPath = reviverTools.genFullPath(self.backupTo, self.backupLabel)
    self.genFile = reviverTools.genFileName('files', self.dateOfRun, self.fullPath, self.backupLabel, self.komprString, self.bkpType)
    tmpBackupString = [self.tarBinary] + self.excludeCommands + [self.tarCommand, '-hc%sf' % (self.komprFlag), self.genFile] + self.sourceList
    self.backupString = [i for i in tmpBackupString if i is not None]

  # Main backup function where final backup command is executed
  def main(self):
    reviverTools.checkTargetDirectoryStructure(self.fullPath)
    print('Making %s backup of files... (%s)' % (self.outputText, ', '.join(self.sourceList)))
    try:
      subprocess.run(self.backupString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as err:
      print('Backup command failed with error:\n%s' % (err.stderr))
      return

    # Remove old backup files after main backup function
    if self.keepTime > -1:
      reviverTools.cleanOldBackupFiles(self.fullPath, self.dateOfRun, self.keepTime, 'files_%s' % (self.backupLabel), self.komprString)
      
