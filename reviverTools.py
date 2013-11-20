# -*- coding: utf-8 -*-

from random import randrange
from datetime import datetime

def randomPasswordGenerator(self, pocet_pismen):
	slovo, a, generovani = "", 0, 0
	while a < pocet_pismen:
		generovani = randrange(48,122,1)
		if (generovani >= 48 and generovani <= 57) or (generovani >= 65 and generovani <= 90) or (generovani >= 97 and generovani <= 122):
			slovo = slovo + chr(generovani)
			a = a + 1
	return slovo

def vratDatumHodnoty(dnes):
	den = int(dnes.strftime('%w'))
	denMesice = int(dnes.strftime('%d'))
	tyden = int(dnes.strftime('%W'))
	mesic = int(dnes.strftime('%m'))
	rok = int(dnes.strftime('%Y'))
	return den, denMesice, tyden, mesic, rok


def typZalohy(dnes, vynucena):
	den, denMesice, tyden, mesic, rok = vratDatumHodnoty(dnes)
	if vynucena == 'Y':
		vysledek = 3 #vynucená záloha
	else:
		if den != 0 and denMesice != 1: vysledek = 0 #denní přírůstková
		if den == 0 and denMesice != 1: vysledek = 1 #týdenní přírůstková
		if denMesice == 1: vysledek = 2 #měsíční
	return vysledek

def nazevSouboru(prefix, dnes, cesta, suffix, typ=0):
	vysledek = ''
	den, denMesice, tyden, mesic, rok = vratDatumHodnoty(dnes)
	if typ == 3: vysledek = cesta + '/' + prefix + '_' + dnes.strftime('%Y-%m-%d') + '-forced' + suffix
	if typ == 2: vysledek = cesta + '/' + prefix + '_' + dnes.strftime('%Y-%m-%d') + '-monthly' + suffix
	if typ == 1: vysledek = cesta + '/' + prefix + '_' + dnes.strftime('%Y-%m-%d') + '-weekly' + suffix
	if typ == 0: vysledek = cesta + '/' + prefix + '_' + dnes.strftime('%Y-%m-%d') + '-daily' + suffix
	return vysledek

def komprese(typ):
	if typ == 'xz':
		komprFlag = "J"
		komprString = ".tar.xz"
		komprString2 = " | xz > "
		komprString3 = ".xz"
	elif typ == 'bzip':
		komprFlag = "j"
		komprString = ".tar.bz2"
		komprString2 = " | bzip2 > "
		komprString3 = ".bz2"
	elif typ == 'gzip':
		komprFlag = "z"
		komprString = ".tar.gz"
		komprString2 = " | gzip > "
		komprString3 = ".gz"
	elif typ == 'none':
		komprFlag = ""
		komprString = ".tar"
		komprString2 = " > "
		komprString3 = ".sql"
	else:
		print("Neznámá hodnota \"" + typ + "\". Komprese bude vypnuta.")
		komprFlag = ""
		komprString = ".tar"
		komprString2 = " > "
		komprString3 = ".sql"

	return komprFlag, komprString, komprString2, komprString3
