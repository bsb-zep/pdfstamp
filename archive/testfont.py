#!/usr/bin/env python
from itertools import chain
import sys
from decimal import Decimal

from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

ttf = TTFont(sys.argv[1], 0, verbose=0, allowVID=0,
                ignoreDecompileErrors=True,
                fontNumber=-1)

chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
for ch in chars:
	print (str(ch[0])+",")
# Use this for just checking if the font contains the codepoint given as
# second argument:
char = int(sys.argv[2], 0)
#print(Unicode[char])
#print(char in (x[0] for x in chars))
l = "sadfdsaf#"
l = list(l)
#for char in l:
#	print (ord(char))
ttf.close()
