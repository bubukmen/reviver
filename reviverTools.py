# vim: set fileencoding=utf-8 :

import os, re, shutil
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import randint
from base64 import b64encode

#Function to generate unique ID
def genUniqueId(size=24, b64=False):
  retVal = bytes()
  for i in range(0, size):
    retVal += bytes([randint(0, 255)])
  if b64:
    retVal = b64encode(retVal)
  else:
    retVal = retVal.hex()
  return retVal

#Helper function returning tuple with date repesentation in numbers
def getDateTimeValues(dnes):
  day = int(dnes.strftime('%w'))
  dayOfMonth = int(dnes.strftime('%d'))
  week = int(dnes.strftime('%W'))
  month = int(dnes.strftime('%m'))
  year = int(dnes.strftime('%Y'))
  return day, dayOfMonth, week, month, year

#Helper function returning backup type in number representation
def getBackupType(dateOfRun, forced):
  day, dayOfMonth, week, month, year = getDateTimeValues(dateOfRun)
  if forced:
    output = 3 #forced backup
  else:
    if day != 0 and dayOfMonth != 1:output = 0 #daily incremental
    if day == 0 and dayOfMonth != 1: output = 1 #weekly incremental
    if dayOfMonth == 1: output = 2 #monthly
  return output

#Helper funtction returning full backup path
def genFullPath(backupTo, backupLabel):
  return '%s/%s' % (backupTo, backupLabel)

#Helper function returning final backup name
def genFileName(prefix, dateOfRun, fullPath, backupLabel, suffix, bkpType=0):
  output = ''
  strDate = dateOfRun.strftime('%Y-%m-%d')
  if bkpType == 0: output = '%s/%s_%s_%s-daily%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  if bkpType == 1: output = '%s/%s_%s_%s-weekly%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  if bkpType == 2: output = '%s/%s_%s_%s-monthly%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  if bkpType == 3: output = '%s/%s_%s_%s-forced%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  return output

#This function is returning tuple with possible filename suffixes
def getCompression(bkpType, oldSyntax=True):
  trueBkpType = bkpType.lower() if type(bkpType) == str else bkpType
  if oldSyntax:
    switcher = {
      'xz': ('J', '.tar.xz', ['xz'], '.sql.xz'),
      'bzip': ('j', '.tar.bz2', ['bzip2'], '.sql.bz2'),
      'gzip': ('z', '.tar.gz', ['gzip'], '.sql.gz'),
      'none': ('', '.tar', None, '.sql'),
      b'\x00': ('', '.tar', None, '.sql')
    }
  else:
    switcher = {
      'xz': {
        'compressionFlag': 'J',
        'tarSuffix': '.tar.xz',
        'compressionProgram': 'xz',
        'customSuffix': '.xz'
      },
      'bzip': {
        'compressionFlag': 'j',
        'tarSuffix': '.tar.bz2',
        'compressionProgram': 'bzip2',
        'customSuffix': '.bz2'
      },
      'gzip': {
        'compressionFlag': 'z',
        'tarSuffix': '.tar.gz',
        'compressionProgram': 'gzip',
        'customSuffix': '.gz'
      },
      'none': {
        'compressionFlag': '',
        'tarSuffix': '.tar',
        'compressionProgram': None,
        'customSuffix': ''
      },
      b'\x00': {
        'compressionFlag': '',
        'tarSuffix': '.tar',
        'compressionProgram': None,
        'customSuffix': ''
      }
    }
  if trueBkpType not in switcher:
    print('Unknown value "%s". Compression will be turned off' % (bkpType))
  return switcher.get(trueBkpType, switcher.get(b'\x00'))

#This function automatically create backup destination directory structure
def checkTargetDirectoryStructure(fullPath):
  if not os.path.isdir(fullPath):
    print('Creating directory %s' % (fullPath))
    os.makedirs(fullPath)

#This function is adding slash to the end of configuration directive
def rsyncSanitizeDir(dirName):
  output = dirName
  if dirName[-1] != '/':
    output = '%s/' % (dirName)
  return output

#This function is removing (back)slashes from the end of configuration directive
def sanitizePath(pathStr):
  retVal = pathStr
  if pathStr[-1] == '\\' or pathStr[-1] == '/':
    retVal = pathStr[:-1]
  return retVal

#This function is platform independent and recognize path separator type.
def guessPathSeparator(pathStr):
  rxpCompile = re.compile(r'^.*(?P<rxpSeparator>[\\/]).*$')
  rxp = re.match(rxpCompile, pathStr)
  return rxp.groups('rxpSeparator')[0]

#This function is seeking and removing old backups based on keep directive in configuration
def cleanOldBackupFiles(fullPath, dateOfRun, keepTime, filePrefix, bkpString, dbTypeBackup=False):
  print('Cleaning old backup files in %s:' % (fullPath))
  fnRegexp = re.compile(r'^%s_(?P<rxpDate>[-0-9]*)-(daily|weekly|monthly|forced)%s$' % (filePrefix, bkpString))
  if not dbTypeBackup:
    dateBack = dateOfRun - relativedelta(months=keepTime)
    dateBack = dateBack.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
  else:
    dateBack = dateOfRun - relativedelta(days=keepTime)
    dateBack = dateBack.replace(hour=0, minute=0, second=0, microsecond=0)
  for fileName in os.listdir(fullPath):
    rxp = re.match(fnRegexp, fileName)
    if not rxp:
      continue
    fileDate = datetime.strptime(rxp.group('rxpDate'), '%Y-%m-%d')
    if fileDate < dateBack:
      print('Removing file: %s' % (fileName))
      os.unlink('%s/%s' % (fullPath, fileName))
    
  print('Cleaning in %s complete' % (fullPath))

#Function shortcut to find app binary path
def findApp(appName):
  return shutil.which(appName)

#This function is testing if mount is already mounted or not
def testIfMounted(mountPath):
  retVal = False
  with open('/proc/mounts', 'r') as f:
    for line in f:
      if mountPath in line:
        retVal = True
  return retVal