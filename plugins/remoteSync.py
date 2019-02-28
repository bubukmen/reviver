#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os, subprocess, reviverTools

class action:

  # Constructor where all variables are set and moved inside the class
  def __init__ (self, globalInstructions, instructions, log):
    backupTo = globalInstructions['backupTo']
    remoteLabel = instructions['remoteLabel']
    mountPoint = instructions['mountPoint']
    remoteDir = instructions['remoteDir']

    #Mount remote mount point
    print('Mounting %s' % (remoteLabel))
    try:
      subprocess.run(['mount', mountPoint], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as err:
      print('Remote synchronization will skip because we can\'t mount %s mountpoint.\n%s' % (mountPoint, err.stderr))
      return
   
    reviverTools.checkTargetDirectoryStructure('%s/%s' % (mountPoint, remoteDir))

    #Synchronize remote and local directory with rsync application
    try:
      subprocess.run(['rsync', '-a', '--delete', reviverTools.rsyncSanitizeDir(backupTo), reviverTools.rsyncSanitizeDir('%s/%s' % (mountPoint, remoteDir))], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as err:
      print('Error while running synchronization command.\n%s' % (err.stderr))

    #Unmount remote mount point
    print('Unmounting %s' % (remoteLabel))
    try:
      subprocess.run(['umount', mountPoint], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as err:
      print('Error. Can\'t unmount %s. Please unmount drive manually.\n%s' % (mountPoint, err.stderr))
      return
