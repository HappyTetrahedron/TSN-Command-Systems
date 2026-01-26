import random
random.seed(2245)
from math import sin, cos, tan

track_dict = {}

def track(key, value, dedup_key=None):
    if not dedup_key:
      if isinstance(value, str):
        dedup_key = value
      else:
        raise ValueError("Complex types require a dedup key")
    if key in track_dict:
        track_dict[key][dedup_key] = value
    else:
        track_dict[key] = {dedup_key: value}

def retrieve(key):
    return list(track_dict.get(key, {}).values())

def raise_helper(str):
    raise ValueError(str)

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

def clear_all_state():
  keys = list(track_dict.keys())
  for key in keys:
    del track_dict[key]

def stripspace(text):
    return ''.join(text.split())


def register(jinja_env):
  jinja_env.globals.update(
    track=track,
    retrieve=retrieve,
    panic=raise_helper,
    randint=random.randint,
    sin=sin,
    cos=cos,
    tan=tan,
    )
  jinja_env.filters.update(textwidth=textwidth, stripspace=stripspace)