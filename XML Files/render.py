#!/usr/bin/env python
import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('.'))
TMPL_FNAME = 'S21.xml.tmpl'
OUT_FNAME = 'XML Files/S21.xml'
# TMPL_FNAME = "ShieldSharing.xml.tmpl"
# OUT_FNAME = "ShieldSharing.xml"

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(TMPL_FNAME).render())
