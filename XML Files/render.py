#!/usr/bin/env python

# Quick script to render the sandbox locally; used for development

import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader
import datetime

track_dict = {}

def track(key, value):
    if key in track_dict:
        track_dict[key].append(value)
    else:
        track_dict[key] = [value]

def retrieve(key):
    return track_dict.get(key, [])

env = {
    "extensions": [
        "TokenSystem",
        "VerdantFleet",
        "NebulaEffects",
    ],
    "maps": [
        "Acantha",
        "Ibroan",
        "Erowis",
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
            "Decoy",
            "KamikazeMine",
        ],
    }
}

template_env = Environment(loader=FileSystemLoader('.'))
template_env.lstrip_blocks = True
template_env.trim_blocks = True
template_env.autoescape = True
template_env.add_extension('jinja2.ext.do')
template_env.globals.update(track=track, retrieve=retrieve)
TMPL_FNAME = 'main.xml'
OUT_FNAME = '../MISS_TSN-Command.xml'

context = {
    "data": env,
    "version": "local",
    "time": datetime.datetime.now().isoformat()
}

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(TMPL_FNAME).render(g=context))
