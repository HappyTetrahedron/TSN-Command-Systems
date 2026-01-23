
#!/usr/bin/env python

# Script to extract entity metadata from a system map

import sys
import os
import faulthandler
faulthandler.enable()
import datetime
import xml.etree.ElementTree as et
import json
import collect_map_metadata as cmm

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

ROMAN_NUMERALS = [
  "0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV"
]

def create_start(metadata, out):
    start = et.SubElement(out, "start")
    cx = et.SubElement(start, "set_variable")
    cx.set("name", "Coordinate X")
    cx.set("value", metadata["x"])
    cy = et.SubElement(start, "set_variable")
    cy.set("name", "Coordinate Y")
    cy.set("value", metadata["y"])
    w = et.SubElement(start, "set_variable")
    w.set("name", "Width")
    w.set("value", str(metadata["width"]))
    h = et.SubElement(start, "set_variable")
    h.set("name", "Height")
    h.set("value", str(metadata["height"]))
    a = et.SubElement(start, "set_variable")
    a.set("name", "Alignment")
    a.set("value", metadata["alignment"])
    s = et.SubElement(start, "set_variable")
    s.set("name", "Skybox")
    s.set("value", str(metadata["skybox"]))

def getPlanetName(sector_id, metadata):
    sector = metadata["sectors"][sector_id-1]
    for e in sector["entities"]:
        if e["type"] == "Planet":
            return e["name"]
    eprint("Could not find planet in sector {}".format(sector_id))
    sys.exit(1)

def getGateTarget(sector_id, metadata):
    sector = metadata["sectors"][sector_id-1]
    for e in sector["entities"]:
        if e["type"] == "Gate":
            if "gate_target_sector" not in e:
                eprint("WARNING: unconnected gate: {}".format(e["name"]))
                return 1
            return e["gate_target_sector"]
    eprint("Could not find gate in sector {}".format(sector_id))
    sys.exit(1)

TYPICALTAGS = [
    "create",
    "set_ship_text",
    "set_object_property",
    "set_relative_position",
    "clear_ai",
    "add_ai",
    "set_special",
]
IGNORETAGS = [
    "set_variable",
    "set_timer",
    "set_skybox_index",
]
TYPICALVARS = [
    "SYS System",
    "SYS",
    "Sector",
    "Sector Entities",
    "MissionCode",
    "ExitorRetreat",
    "Infiltrators",
    "Grid 5 Transition Enabled",
    "Grid 1 Transition Enabled",
    "Grid E Transition Enabled",
    "Grid A Transition Enabled",
    "Corner A1 Transition Enabled",
    "Corner A5 Transition Enabled",
    "Corner E1 Transition Enabled",
    "Corner E5 Transition Enabled",
    "Entry Random",
    "Sector Type",
    "USFPTraffic1",
    "USFPTraffic2",
    "CustomPlanet",
]
TYPICALTIMERS = [
    "Entry Random",
    "Transition",
]
def should_ignore(action):
    if action.tag.startswith("if"):
        return True
    if action.tag in IGNORETAGS:
        return True
    if action.tag == "set_object_property":
        if "Gate" in action.get("name"):
            return True
    return False

def convert_event_actions(event, sector, sector_id, metadata):
    system_name = metadata["name"]
    for action in event:
        if action.tag == "create":
            if "name" in action.attrib:
                if action.get("name").endswith("Gate"):
                    action.set("y", "{}.0".format(getGateTarget(sector_id, metadata)))
                if action.get("name") == "Planet":
                    action.set("name", "PLANET{}".format(getPlanetName(sector_id, metadata)))
            if action.get("type", "") == "genericMesh":
                if "angle" in action.attrib:
                    action.attrib.pop("angle")
        
        if not should_ignore(action):
            if action.tag not in TYPICALTAGS:
                eprint("WARNING: Encountered unusual tag {}".format(action.tag))
            sector.append(action)
        else:
            if action.tag == "set_variable" and action.get("name").replace(metadata["name"], 'SYS') not in TYPICALVARS:
                eprint("WARNING: Ignoring untypical variable {}".format(action.get("name")))
            if action.tag == "set_timer" and action.get("name").replace(metadata["name"], 'SYS') not in TYPICALVARS:
                eprint("WARNING: Ignoring untypical timer {}".format(action.get("name")))

def convert_event(event, metadata, old_sector_id, out, sectormap):
    sector_id = old_sector_id

    if event.attrib.get("name", "").startswith("Create " + metadata["name"] + " Sector "):
        rom = event.attrib["name"].split()[-1]
        sector_id = ROMAN_NUMERALS.index(rom)
        if sector_id <= 0:
            eprint("Error: Could not extract sector ID from `{}`".format(event.attrib["name"]))
            sys.exit(1)
        if sector_id not in sectormap:
            s = et.SubElement(out, "event")
            sectormap[sector_id] = s
            s.set("name", "Sector {}".format(sector_id))
        convert_event_actions(event, sectormap[sector_id], sector_id, metadata)
    elif event.attrib.get("name", "").startswith("Create Waypoint"):
        sector_id = int(event.attrib["name"].split('-')[-1])
        if sector_id <= 0:
            eprint("Error: Could not extract sector ID from `{}`".format(event.attrib["name"]))
            sys.exit(1)
        if sector_id not in sectormap:
            s = et.SubElement(out, "event")
            sectormap[sector_id] = s
            s.set("name", "Sector {}".format(sector_id))
        convert_event_actions(event, sectormap[sector_id], sector_id, metadata)
    if event.attrib.get("name", "").startswith("Generate Sector Entities"):
        sector_id = old_sector_id
        if sector_id not in sectormap:
            eprint("Error: found sector entities but no sector defined")
            sys.exit(1)
        convert_event_actions(event, sectormap[sector_id], sector_id, metadata)
    if event.attrib.get("name", "").startswith("Settings"):
        sector_id = old_sector_id
        if sector_id not in sectormap:
            eprint("Error: found sector entities but no sector defined")
            sys.exit(1)
        convert_event_actions(event, sectormap[sector_id], sector_id, metadata)
    if event.attrib.get("name", "").startswith("Custom Planet Data"):
        sector_id = old_sector_id
        if sector_id not in sectormap:
            eprint("Error: found planet but no sector defined")
            sys.exit(1)
        for action in event:
            if action.tag == "set_ship_text":
                if action.attrib.get("name", "") == "Planet":
                    action.set("name", "PLANET{}".format(getPlanetName(sector_id, metadata)))
                    action.attrib.pop("newname")
                    sectormap[sector_id].append(action)
    return sector_id


def convert(file):
    filename = os.path.basename(file)
    metadata = cmm.parse_file(file, "old")

    system_name = filename.split('.')[0]

    out = et.Element('mission_data')
    out.set("version", "1.0")

    xml_tree = et.parse(file)
    root = xml_tree.getroot()

    current_sector = 0

    create_start(metadata, out)

    sectormap = {}

    sec = 0
    for child in root:
        if child.tag == "event":
            pass
            sec = convert_event(child, metadata, sec, out, sectormap)

    return out

if __name__ == "__main__":
    file = sys.argv[1]

    if not file.endswith('.xml'):
        eprint("Invalid file type")
        sys.exit(1)

    out = convert(file)

    basename = os.path.basename(file)
    tree = et.ElementTree(out)
    et.indent(tree, '  ')
    tree.write(basename)
