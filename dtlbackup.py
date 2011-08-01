#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys,os,getopt,ConfigParser,nastroje
from datetime import datetime
#from dobackup import *
#from logovani import *

def napoveda():
	print '''
Dtlbackup je aplikace pro zálohování linuxových strojů firmy Datalite
Použití: dtlbackup [parametry]
Parametry:

-h, --help                        Vyvolá tuto nápovědu
-c <soubor>, --config <soubor>    Použije jiný konfigurační soubor než /etc/dtlbackup/dtlbackup.conf
-F, --force                       Spustí vynucenou kompletní zálohu
-D, --daemon                      Spustí se na pozadí jako démon
	'''
	sys.exit(0)

def demonizuj():
	try:
		if os.fork() > 0:
			os._exit(0)
	except OSError, error:
		print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
		os._exit(1)

	os.chdir('/')
	os.setsid()
	os.umask(0)

	try:
		pid = os.fork()
		if pid > 0:
			#print 'Daemon PID %d' % pid
			os._exit(0)
	except OSError, error:
		print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
		os_exit(1)

def importTridy(name):
	mod = __import__(name)
	components = name.split('.')
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod

def main():

	vynucena = 'N'
	demon = 'N'
	configFile = '/etc/dtlbackup/dtlbackup.conf'

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hc:FD", ["help", "config=", "force", "daemon"])
	except getopt.error, msg:
		#print msg
		napoveda()
	for o, a in opts:
		if o in ("-h", "--help"):
			napoveda()
		elif o in ("-c", "--config"):
			configFile = a
		elif o in ("-F", "--force"):
			vynucena = 'Y'
		elif o in ("-D", "--daemon"):
			demon = 'Y'

	if demon == 'Y':
		demonizuj()

	if os.getuid() == 0:
		if os.access(configFile, os.F_OK):
			if os.access(configFile, os.R_OK):
				cnfP = ConfigParser.ConfigParser()
				try:
					cnfP.read(configFile)
				except ConfigParser.MissingSectionHeaderError:
					print "Chyba, nelze pokračovat - Konfigurační soubor " + configFile + " obsahuje chyby!"
					sys.exit(1)
				if cnfP.has_section('global') == False:
					print "Chyba, nelze pokračovat - V konfiguračním souboru " + configFile  + " chybí sekce global!"
					sys.exit(1)
				#komprFlag, komprString, komprStringOther = nastroje.komprese(cnfP.get('global', 'compression'))
				dnesniDatum = datetime.today();
				if cnfP.has_option('global', 'remoteFileSystem'):
					rmtFS = cnfP.get('global', 'remoteFileSystem')
					tmpTrida = importTridy('plugins.' + rmtFS)
					tmpTrida.action(configFile, 'connect')
				for i in cnfP.sections():
					if i != 'global':
						tmpTrida = importTridy('plugins.' + i)
						tmpTrida.action(configFile, vynucena, dnesniDatum)
						#tmPlugin = __import__('plugins.' + i)
						#tmpTrida = tmPlugin.action()
				if cnfP.has_option('global', 'remoteFileSystem'):
					tmpTrida.action(configFile, 'disconnect')
			else:
				print "Soubor " + configFile + " nemá práva pro čtení."
				sys.exit(1)
		else:
			print "Nelze nalézt konfigurační soubor " + configFile
			sys.exit(1)
	else:
		print "Zálohovací program se musí spustit pod uživatelem root!"
		sys.exit(1)

if __name__ == "__main__":
	sys.exit(main())


