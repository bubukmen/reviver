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
    self.compressionType = instructions['compression'] if 'compression' in instructions else globalConf['compression']
    self.keepTime = -1
    if 'keep' in self.instructions:
      self.keepTime = self.instructions['keep']
    self.svnDumpCommand = reviverTools.findApp('svnadmin')
    if self.svnDumpCommand is None:
      print('Error: Can\'t find dump command svnadmin.')
      return
    self.svnPath = instructions['svnPath']
    if self.initRest():
      return
    self.main()

  # Initialize more variables based on config file. Preparations for main backup function
  def initRest(self):
    self.compressionParams = reviverTools.getCompression(self.compressionType, oldSyntax=False)
    self.fullPath = reviverTools.genFullPath(self.backupTo, self.backupLabel)
    self.genFile = reviverTools.genFileName('svn', self.dateOfRun, self.fullPath, self.backupLabel, '.svndump%s' % self.compressionParams['customSuffix'])
    if self.compressionParams['compressionProgram']:
      self.compressionProgram = reviverTools.findApp(self.compressionParams['compressionProgram'])
    else:
      self.compressionProgram = self.compressionParams['compressionProgram']

  def main(self):
    reviverTools.checkTargetDirectoryStructure(self.fullPath)
    print('Making SVN backup to %s file' % self.genFile)
    self.cmdLine1 = [self.svnDumpCommand, 'dump', '-q', self.svnPath]
    self.cmdLine2 = self.compressionProgram
    with open(self.genFile, 'wb') as f:

      if self.compressionParams['compressionProgram'] is None:
        p1 = subprocess.Popen(self.cmdLine1, stdout=f)
        p1.wait()
      else:
        p1 = subprocess.Popen(self.cmdLine1, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(self.cmdLine2, stdin=p1.stdout, stdout=f)
        p1.wait()
        p2.wait()

    # Remove old backup files after main backup function
    if self.keepTime > -1:
      reviverTools.cleanOldBackupFiles(self.fullPath, self.dateOfRun, self.keepTime, 'svn_%s' % (self.backupLabel), '.svndump%s' % self.compressionParams['customSuffix'], True)