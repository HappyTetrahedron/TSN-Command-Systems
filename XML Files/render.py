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

def textwidth(text):
    w = 0
    for c in text:
        if c.isupper():
            w += 9
        elif c.isdigit():
            w += 8
        elif c.isalpha():
            w += 7
        elif c.isspace():
            w += 2
        else:
            w += 4
    return w

env = {
    "difficulty": 7,
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
template_env.filters.update(textwidth=textwidth)
TMPL_FNAME = 'main.xml'
OUT_FNAME = '../MISS_TSN-Command.xml'

context = {
    "data": env,
    "version": "local",
    "time": datetime.datetime.now().isoformat()
}

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(TMPL_FNAME).render(g=context))
