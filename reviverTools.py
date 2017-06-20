# vim: set fileencoding=utf-8 :

import os, re, shutil
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import randint

def generateRandomString(letterCount=10, advPass=False):
  retVal, a = '', 0
  if advPass:
    letterList = list('!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
  else:
    letterList = list('23456789ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
  while a < letterCount:
    retVal += letterList[randint(0, len(letterList) - 1)] 
    a += 1
  return retVal

def getDateTimeValues(dnes):
  day = int(dnes.strftime('%w'))
  dayOfMonth = int(dnes.strftime('%d'))
  week = int(dnes.strftime('%W'))
  month = int(dnes.strftime('%m'))
  year = int(dnes.strftime('%Y'))
  return day, dayOfMonth, week, month, year


def getBackupType(dateOfRun, forced):
  day, dayOfMonth, week, month, year = getDateTimeValues(dateOfRun)
  if forced:
    output = 3 #forced backup
  else:
    if day != 0 and dayOfMonth != 1:output = 0 #daily incremental
    if day == 0 and dayOfMonth != 1: output = 1 #weekly incremental
    if dayOfMonth == 1: output = 2 #monthly
  return output

def genFullPath(backupTo, backupLabel):
  return '%s/%s' % (backupTo, backupLabel)

def genFileName(prefix, dateOfRun, fullPath, backupLabel, suffix, bkpType=0):
  output = ''
  strDate = dateOfRun.strftime('%Y-%m-%d')
  if bkpType == 0: output = '%s/%s_%s_%s-daily%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  if bkpType == 1: output = '%s/%s_%s_%s-weekly%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  if bkpType == 2: output = '%s/%s_%s_%s-monthly%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  if bkpType == 3: output = '%s/%s_%s_%s-forced%s' % (fullPath, prefix, backupLabel, strDate, suffix)
  return output

def getCompression(bkpType):
  if bkpType == 'xz':
    komprFlag = 'J'
    komprString = '.tar.xz'
    komprString2 = ['xz']
    komprString3 = '.sql.xz'
  elif bkpType == 'bzip':
    komprFlag = 'j'
    komprString = '.tar.bz2'
    komprString2 = ['bzip2']
    komprString3 = '.sql.bz2'
  elif bkpType == 'gzip':
    komprFlag = 'z'
    komprString = '.tar.gz'
    komprString2 = ['gzip']
    komprString3 = '.sql.gz'
  elif bkpType == 'none':
    komprFlag = ''
    komprString = '.tar'
    komprString2 = None
    komprString3 = '.sql'
  else:
    print('Unknown value"%s". Compression turned off' % (bkpType))
    komprFlag = ''
    komprString = '.tar'
    komprString2 = None
    komprString3 = '.sql'

  return komprFlag, komprString, komprString2, komprString3

def checkTargetDirectoryStructure(fullPath):
  if not os.path.isdir(fullPath):
    print('Creating directory %s' % (fullPath))
    os.makedirs(fullPath)

def rsyncSanitizeDir(dirName):
  output = dirName
  if dirName[-1] is not '/':
    output = '%s/' % (dirName)
  return output

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

def findApp(appName):
  return shutil.which(appName)
