#!/usr/bin/env python
import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('.'))
TMPL_FNAME = 'CureTags.xml.tmpl'
OUT_FNAME = 'CureTags.xml'
# TMPL_FNAME = "ShieldSharing.xml.tmpl"
# OUT_FNAME = "ShieldSharing.xml"

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(TMPL_FNAME).render())
