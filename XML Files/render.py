#!/usr/bin/env python
import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader

env = {
    "scripts": [
        "NebulaEffects"
    ],
    "systems": [
        "Acantha",
        "Ashia"
    ],
    "cargo": {
        "ship1": {
            "marines": 5
        }
    }
}

template_env = Environment(loader=FileSystemLoader('.'))
template_env.lstrip_blocks = True
template_env.trim_blocks = True
TMPL_FNAME = 'main.xml'
OUT_FNAME = '../MISS_TSN-Command.xml'

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(TMPL_FNAME).render(g={"data": env, "version": "local"}))
