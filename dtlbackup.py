#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
from dobackup import *

def napoveda():
	print '''

Dtlbackup je aplikace pro zálohování linuxových strojů firmy Datalite:

Použití: dtlbackup [parametry]

Parametry:

-h			Vyvolá tuto nápovědu
-c [SOUBOR]		Použije jiný konfigurační soubor než /etc/dtlbackup/dtlbackup.conf

	'''

def rozcestnik():
	for i in range(len(sys.argv)):
		if sys.argv[i] == "-h":
			napoveda()
			sys.exit()

		elif sys.argv[i] == "-c":
			if os.getuid() == 0:
				if os.access(sys.argv[i+1], 4):
					try:
						bkp = bkpcontrol(sys.argv[i+1])
					except IndexError:
						print "Nebyl zadán parametr konfiguračního souboru"
						sys.exit()
				else:
					print "Nelze nalézt soubor " + sys.argv[i+1]
			else:
				print "Zálohovací program se musí spouštět pod uživatelem root!"

if len(sys.argv) == 1:
	if os.getuid() == 0:
		if os.access('/etc/dtlbackup/dtlbackup.conf', 4):
			bpk = bkpcontrol('/etc/dtlbackup/dtlbackup.conf')
		else:
			print "Nelze nalézt soubor /etc/dtlbackup/dtlbackup.conf"
	else:
		print "Zálohovací program se musí spouštět pod uživatelem root!"

else:
	rozcestnik()

