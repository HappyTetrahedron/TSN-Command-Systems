#!/usr/bin/env python

# Quick script to render the sandbox locally; used for development

import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader
import datetime

env = {
    "extensions": [
        "S21",
        "VerdantFleet",
    ],
    "systems": [
        "Waypoint 52",
        "Vrae",
        "Khoros",
        "Jhohara",
        "Volantis",
        "Acantha",
        "Erebus",
    ],
    "ordnance": {
        "ship1": {
            "torpedo": 10,
            "pshock": 10,
        },
        "ship2": {
            "torpedo": 10,
            "emp": 0,
            "nuke": -1,
        },
    },
    "cargo": {
        "ship1": {
            "marines": 5
        }
    },
    "modules": {
        "ship1": [
            "ClusterMine",
            "Decoy",
            "ShieldEnhancer",
            "KamikazeMine",
        ]
    }
}

template_env = Environment(loader=FileSystemLoader('.'))
template_env.lstrip_blocks = True
template_env.trim_blocks = True
template_env.add_extension('jinja2.ext.do')
TMPL_FNAME = 'main.xml'
OUT_FNAME = '../MISS_TSN-Command.xml'

context = {
    "data": env,
    "version": "local",
    "time": datetime.datetime.now().isoformat()
}

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(TMPL_FNAME).render(g=context))
