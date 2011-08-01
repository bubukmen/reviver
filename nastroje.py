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
		if den != 0 and denMesice != 01: vysledek = 0 #denní přírůstková
		if den == 0 and denMesice != 01: vysledek = 1 #týdenní přírůstková
		if denMesice == 01: vysledek = 2 #měsíční
	return vysledek

def nazevSouboru(dnes, typ, cesta, suffix):
	vysledek = ""
	den, denMesice, tyden, mesic, rok = vratDatumHodnoty(dnes)
	if typ == 3: vysledek = cesta + "/vynucena_" + str(denMesice) + "_" + str(mesic) + "_" + str(rok) + suffix
	if typ == 2: vysledek = cesta + "/" + mesicCesky(mesic) + "_" + str(rok) + suffix
	if typ == 1: vysledek = cesta + "/tyden_" + str(tyden) + suffix
	if typ == 0: vysledek = cesta + "/" + denCesky(den) + suffix

	return vysledek

def mesicCesky(mesic):
	if mesic == 1: vysledek = "leden"
	if mesic == 2: vysledek = "unor"
	if mesic == 3: vysledek = "brezen"
	if mesic == 4: vysledek = "duben"
	if mesic == 5: vysledek = "kveten"
	if mesic == 6: vysledek = "cerven"
	if mesic == 7: vysledek = "cervenec"
	if mesic == 8: vysledek = "srpen"
	if mesic == 9: vysledek = "zari"
	if mesic == 10: vysledek = "rijen"
	if mesic == 11: vysledek = "listopad"
	if mesic == 12: vysledek = "prosinec"
	return vysledek

def denCesky(den):
	if den == 0: vysledek = "nedele"
	if den == 1: vysledek = "pondeli"
	if den == 2: vysledek = "utery"
	if den == 3: vysledek = "streda"
	if den == 4: vysledek = "ctvrtek"
	if den == 5: vysledek = "patek"
	if den == 6: vysledek = "sobota"
	return vysledek

def komprese(typ):
	if typ == 'lzma':
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
		print "Neznámá hodnota \"" + typ + "\". Komprese bude vypnuta."
		komprFlag = ""
		komprString = ".tar"
		komprString2 = " > "
		komprString3 = ".sql"

	return komprFlag, komprString, komprString2, komprString3
