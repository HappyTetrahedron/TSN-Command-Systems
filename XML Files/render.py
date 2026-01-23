#!/usr/bin/env python

# Quick script to render the sandbox locally; used for development

import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader
import datetime
import sys
import os

# ugly but idgaf
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'render_server'))
import jinja_functions as jf

env = {
    "difficulty": 10,
    "extensions": [
        "TokenSystem",
        "HazardPainter",
        "NebulaEffects",
        "FuelStatusDisplay",
        "ForceShipNames",
        "VerdantFleet",
    ],
    "maps": [
        "Atlantis",
        "Arietis",
        "Helios",
        "Tibur",
    ],
    "ordnance": {
        "ship1": {
            "torpedo": -1,
            "pshock": -1,
        },
        "ship2": {
            "torpedo": -1,
            "emp": -1,
            "nuke": -1,
        },
    },
    "cargo": {
        "ship1": {
            "marines": 3
        }
    },
    "modules": {
        "ship1": [
            "KamikazeMine",
            "Decoy",
            "Fireworks",
        ],
    }
}

template_env = Environment(loader=FileSystemLoader('.'))
template_env.lstrip_blocks = True
template_env.trim_blocks = True
template_env.autoescape = True
template_env.add_extension('jinja2.ext.do')

jf.register(template_env)
TMPL_FNAME = 'main.xml'
OUT_FNAME = '../MISS_TSN-Command.xml'

context = {
    "data": env,
    "version": "local",
    "time": datetime.datetime.now().isoformat()
}


with open(OUT_FNAME, 'w') as f:
    jf.clear_all_state()
    f.write(template_env.get_template(TMPL_FNAME).render(g=context))
