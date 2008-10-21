# -*- coding: utf-8 -*-

from random import randrange

class generovani:

    def vygeneruj(self, pocet_pismen):
        slovo, a, generovani = "", 0, 0

        while a < pocet_pismen:
            generovani = randrange(48,122,1)
            if (generovani >= 48 and generovani <= 57) or (generovani >= 65 and generovani <= 90) or (generovani >= 97 and generovani <= 122):
                slovo = slovo + chr(generovani)
                a = a + 1
        return slovo

