# -*- coding: utf-8 -*-

import ConfigParser,sys,os,generate
from datetime import datetime

class bkpcontrol:

	def __init__(self, konfigurak, vynucena):
		self.vynucena = vynucena
		print "Používám konfigurační soubor " + konfigurak
		self.config = ConfigParser.ConfigParser()
		try:
			self.config.read(konfigurak)
		except ConfigParser.MissingSectionHeaderError:
			print "Chyba, nelze pokračovat - Konfigurační soubor " + konfigurak + " obsahuje chyby!"
			sys.exit()

		if self.config.has_section('global') == False:
			print "Chyba, nelze pokračovat - V konfiguračním souboru " + konfigurak  + " chybí sekce global!"
			sys.exit()
		self.gen = generate.generovani()
		self.komprese()
		self.typZalohy()
		self.includeFiles()

		self.doglobal()
		if self.config.has_section('mysql'): self.domysql()
		if self.config.has_section('pgsql'): self.dopgsql()

	def doglobal(self):
		print self.aktualniDatumCas() + "Provádím " + self.chrTypZalohy  + " zálohu dat do souboru " + self.globalBkpFile
		backupString =  "tar " + self.globalCommand + " -hc" + self.komprFlag + "f " + self.globalBkpFile + self.includeList
		os.system(backupString)
		print self.aktualniDatumCas() + "Dokončeno"

	def domysql(self):
		nazevSouboru = self.config.get('global','backupTo') + "/mysql-" + self.denCesky(self.den) + self.komprString
		print self.aktualniDatumCas() + "Provádím zálohu databáze MySQL do souboru " + nazevSouboru
		mysqlPrikaz = self.config.get('mysql','mysqlDumpCommand') + " -A -h " + self.config.get('mysql','mysqlServer') + " -u " + self.config.get('mysql','mysqlUser') + " --password=\"" + self.config.get('mysql','mysqlPassword') + "\"" + self.pridejKompresi() + nazevSouboru
		os.system(mysqlPrikaz)
		print self.aktualniDatumCas() + "Dokončeno"

	def dopgsql(self):
		nazevSouboru = self.config.get('global','backupTo') + "/pgsql-" + self.denCesky(self.den) + self.komprString
		print self.aktualniDatumCas() + "Provádím zálohu databáze PostgreSQL do souboru " + nazevSouboru
		tmpSoubor = self.config.get('pgsql','pgTmpDir') + "/" + self.gen.vygeneruj(10) + ".psqlbackup"
		pgsqlPrikaz = self.config.get('pgsql','pgDumpCommand') + " -h " + self.config.get('pgsql','pgServer') + " -o" + self.pridejKompresi() + tmpSoubor
		pgsqlPrikaz = "su " + self.config.get('pgsql','suUser') + " -c \"" + pgsqlPrikaz + "\""
		os.system(pgsqlPrikaz)
		os.rename(tmpSoubor, nazevSouboru)
		os.chown(nazevSouboru, 0, 0)
		print self.aktualniDatumCas() + "Dokončeno"

	def typZalohy(self):
		self.dnes = datetime.today()
		self.den = int(self.dnes.strftime('%w'))
		self.denMesice = int(self.dnes.strftime('%d'))
		self.tyden = int(self.dnes.strftime('%W'))
		self.mesic = int(self.dnes.strftime('%m'))
		self.rok = int(self.dnes.strftime('%Y'))

		if self.den != 0 and self.denMesice != 01 and self.vynucena != "Y":
			self.numTypZalohy = 0
			self.chrTypZalohy = "denní přírůstkovou"
			self.globalCommand = "--after-date=yesterday"
			self.globalBkpFile = self.config.get('global','backupTo') + "/data-" + self.denCesky(self.den) + self.komprString
		
		if self.den == 0 and self.denMesice != 01 and self.vynucena != "Y":
			self.numTypZalohy = 1
			self.chrTypZalohy = "týdenní přírůstkovou"
			self.globalCommand = "--after-date=-1week"
			self.globalBkpFile = self.config.get('global','backupTo') + "/data-tyden-" + str(self.tyden) + self.komprString

		if self.denMesice == 01 and self.vynucena != "Y":
			self.numTypZalohy = 2
			self.chrTypZalohy = "kompletní měsíční"
			self.globalCommand = ""
			self.globalBkpFile = self.config.get('global','backupTo') + "/data-mesic-" + str(self.mesic) + "-" + str(self.rok) + self.komprString

		if self.vynucena == "Y":
			self.numTypZalohy = 3
			self.chrTypZalohy = "vynucenou kompletní"
			self.globalCommand = ""
			self.globalBkpFile = self.config.get('global','backupTo') + "/data-vynucena-" + self.dnes.strftime('%d-%m-%Y') + self.komprString

	def denCesky(self,den):
		if den == 0: pom = "nedele"
		if den == 1: pom = "pondeli"
		if den == 2: pom = "utery"
		if den == 3: pom = "streda"
		if den == 4: pom = "ctvrtek"
		if den == 5: pom = "patek"
		if den == 6: pom = "sobota"
		return pom
	
	def komprese(self):
		typ = self.config.get('global','compression')
		if typ == 'bzip':
			self.komprimovat = 2
			self.komprFlag = "j"
			self.komprString = ".tar.bz2"
		elif typ == 'gzip':
			self.komprimovat = 1
			self.komprFlag = "z"
			self.komprString = ".tar.gz"
		elif typ == 'none':
			self.komprimovat = 0
			self.komprFlag = ""
			self.komprString = ".tar"
		else:
			print "Volba compression obsahuje neplatný parametr - komprese bude vypnuta"
			self.komprimovat = 0
			self.komprFlag = ""
			self.komprString = ".tar"
	
	def includeFiles(self):
		self.includeList = ""
		soubor = open(self.config.get('files','sourceList'), 'r')
		for i in soubor:
			self.includeList = self.includeList + " " + i.strip('\n')

	def pridejKompresi(self):
		if self.komprimovat == 2:
			vratka = " | bzip2 > "
		elif self.komprimovat == 1:
			vratka = " | gzip > "
		else:
			vratka = " > "
		return vratka

	def aktualniDatumCas(self):
		return datetime.now().strftime('[%d.%m.%Y %H:%M:%S] - ')

