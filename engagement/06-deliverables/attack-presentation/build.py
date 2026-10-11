#!/usr/bin/env python3
"""Rebuild the single-file presentation from src/."""
import os
here = os.path.dirname(os.path.abspath(__file__))
tmpl   = open(os.path.join(here,'src','template.html'), encoding='utf-8').read()
slides = open(os.path.join(here,'src','slides.js'),     encoding='utf-8').read()
notes  = open(os.path.join(here,'src','notes.js'),      encoding='utf-8').read()
out    = tmpl.replace('/*__SLIDES__*/', slides + "\n\n" + notes)
path   = os.path.join(here,'Narayana-Security-Attack-Presentation.html')
open(path,'w',encoding='utf-8').write(out)
print("built:", path, os.path.getsize(path), "bytes")
