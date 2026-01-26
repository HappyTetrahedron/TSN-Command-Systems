
#!/usr/bin/env python

# Script to extract entity metadata from a system map

import sys
import os
import faulthandler
faulthandler.enable()
import datetime
import xml.etree.ElementTree as et
import json

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


sector_dimensions = {
    101: {'w':3, 'h':2},
    102: {'w':3, 'h':3},
    103: {'w':4, 'h':2},
    104: {'w':4, 'h':3},
    105: {'w':4, 'h':4},
    106: {'w':5, 'h':3},
    107: {'w':5, 'h':4},
    108: {'w':2, 'h':2},
    109: {'w':1, 'h':2},
    110: {'w':5, 'h':5},
    200: {'w':1, 'h':1},
}

hull_ids = {
    1000: "Station", # DS
    1001: "Civilian Station",
    1002: "Command Post",
    1003: "Industrial Station",
    1004: "Research Station",
    1005: "Station", # Kralien
    1006: "Station", # Arvonian
    1007: "Station", # Torgoth
    1008: "Station", # Skaraan
    1050: "Industrial Station",
    1051: "Denabite Refinery",
    1052: "Weapons Platform",
    1053: "Shipyard",
    1054: "Sensor Buoy",
    1055: "Comms Relay",
    1056: "Bio Base",
    1057: "Gate",
    1100: "Station", # Hjorden
    1250: "Asteroid Base", # Pirate
    1300: "Station", # N'Tani
    1350: "Weapons Platform", # Hegemony
    1351: "Sensor Buoy", # Hegemony
    1352: "Comms Relay", # Hegemony
    1353: "Slingshot Antenna", # Hegemony
    1354: "Slingshot Power Array", # Hegemony
    1355: "Slingshot Platform", # Hegemony
    1356: "Gas Harvester", # Hegemony
    1357: "Logistics Post", # Hegemony
    1358: "Shipyard", # Hegemony
    1359: "Weapons Platform", # Hegemony astrocannon
    1361: "Weapons Platform", # Hegemony defence fort
    1400: "Station", # Free/Ulikai???
    1401: "Station", # Free/Ulikai???
    1402: "Station", # Free/Ulikai???
    1403: "Station", # Free/Ulikai???
    1404: "Station", # Free/Ulikai???
    1405: "Industrial Station", # Free/Ulikai???
    1406: "Research Station", # Free/Ulikai???
    1407: "Industrial Station", # Free/Ulikai?? factory
    1408: "Mining Station", # Free/Ulikai??
    1409: "Shipyard", # Free/Ulikai??
    1410: "Sensor Buoy", # Free/Ulikai??
    1411: "Comms Relay", # Free/Ulikai??
    1412: "Bio Base", # Free/Ulikai??
    7714: "Defense Platform", # Budron platform
}


ROMAN_NUMERALS = [
  "0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV"
]

PLANET_PREFIXES = [
    'PLANET',
    'ARID-PLANET',
    'BLUE-PLANET',
    'RED-PLANET',
    'LAVA-PLANET',
    'SAND-PLANET',
    'GREEN-PLANET',
    'ROCK-PLANET',
    'DEATHSTAR',
    'PULSAR',
    'COMET',
    'MOON',
]

def parse_start(start, system_dict):
    for event in start:
        if event.tag == "set_variable":
            name = event.attrib["name"]
            value = event.attrib["value"]
            match name:
                case "Coordinate X":
                    system_dict["x"] = value
                case "Coordinate Y":
                    system_dict["y"] = value
                case "Alignment":
                    system_dict["alignment"] = value
                case "Width":
                    system_dict["width"] = int(value.split('.')[0])
                case "Height":
                    system_dict["height"] = int(value.split('.')[0])
                case "Skybox":
                    system_dict["skybox"] = int(value.split('.')[0])

def type_from_name(name):
    if name.startswith("DS-"):
        return "Station"
    if name.startswith("SY-"):
        return "Shipyard"
    if name.startswith("WP"):
        return "Weapons Platform"
    if name.startswith("RS-"):
        return "Research Station"
    if name.startswith("BY-"):
        return "Sensor Buoy"
    if name.startswith("CR-"):
        return "Comms Relay"
    if name.startswith("LCR-"):
        return "Comms Relay"
    if name.startswith("I-"):
        return "Industrial Station"
    if name.startswith("B-"):
        return "Marker Buoy"
    if name.startswith("Marker Buoy"):
        return "Marker Buoy"
    if name.endswith(" Prime"):
        return "Planet"
    if name.startswith("M-"):
        return "Mining Station"
    if name.startswith("CP-"):
        return "Command Post"
    if name.startswith("BH"):
        return "Black Hole"
    if name.endswith(" Command"):
        return "Command Post"
    if 'planet' in name.lower():
        return "Planet"
    if name.startswith("PULSAR"):
        return "Pulsar"
    if name.startswith("COMET"):
        return "Comet"
    if 'MOON' in name:
        return "Moon"
    if name.startswith("DEATHSTAR"):
        return "Megastructure"
    return ""

def type_from_hull(hull_id):
    if hull_id in hull_ids:
        return hull_ids[hull_id]
    return "Ship"

def type_from_attribs(attribs):
    if 'type' in attribs:
        t = attribs['type']
        if t == "blackHole":
            return "Black Hole"
        if t == "Anomaly":
            return "Anomaly"
        if t == "monster":
            if 'monsterType' in attribs and attribs['monsterType'] == 8:
                return "Wreck"
            return "Space Fauna"
    return ""

def is_filter_attrib(attribs):
    if 'type' in attribs:
        t = attribs['type']
        if t == "Anomaly":
            return True 
        if t == "monster":
            return True
        if t == "blackHole":
            if attribs["name"].lower() == "blackhole":
                return True
    return False


def process_create_action(action, system_name, sector_id):
    if is_filter_attrib(action.attrib):
        return None
    name = action.attrib["name"]
    if name == "{} {}".format(system_name, ROMAN_NUMERALS[sector_id]):
        return None
    entityData = {
        'name': name,
    }
    t = type_from_attribs(action.attrib)
    if t:
        entityData["type"] = t
    t = type_from_name(name)
    if t:
        entityData["type"] = t
    if 'hullID' in action.attrib:
        hid = int(action.attrib["hullID"].split('.')[0])
        t = type_from_hull(hid)
        entityData["type"] = t
    ps = [p for p in PLANET_PREFIXES if name.startswith(p)]
    if ps:
        entityData['name'] = name.removeprefix(ps[0])
    if name.endswith(" Gate"):
        gate_found = True
        gate_target = name[0:-5]
        gate_target_sector = int(action.attrib["y"].split('.')[0])
        if gate_target_sector != 0:
            entityData["gate_target_sector"] = gate_target_sector
        entityData["type"] = "Gate"
        entityData["gate_target_system"] = gate_target
    return entityData

def process_settext_action(action, original):
    if not original:
        return
    if 'singularity' in action.attrib.get('class', "").lower():
        original["type"] = "Black Hole"
    if 'planet' in action.attrib.get('class', "").lower():
        original["type"] = "Planet"
    if 'planetoid' in action.attrib.get('class', "").lower():
        original["type"] = "Moon"
    if 'moon' in action.attrib.get('class', "").lower():
        original["type"] = "Moon"
    if 'asteroid' in action.attrib.get('class', "").lower():
        original["type"] = "Asteroid"
    if 'newname' in action.attrib:
        original["name"] = action.attrib["newname"]

def process_setspecial_action(action, original, entityList):
    if not original:
        return
    if action.attrib.get('ability', "") == "Cloak":
        del entityList[entityList.index(original)]
    if action.attrib.get('ability', "") == "Stealth":
        del entityList[entityList.index(original)]
    if action.attrib.get('ability', "") == "LowVis":
        del entityList[entityList.index(original)]

def findByName(name, entityList):
    l = [ e for e in entityList if e["name"] == name ]
    if l:
        return l[0]

def parse_event_actions(event, sector, system_name):
    for action in event:
        if action.tag == "create":
            if "name" in action.attrib:
                entity = process_create_action(action, system_name, sector["id"])
                if not entity:
                    continue
                if entity.get("type", "") == "Gate" and "gate_target_sector" not in entity:
                    if "gate_target_sector" in sector:
                        entity["gate_target_sector"] = sector["gate_target_sector"]
                        del sector["gate_target_sector"]
                sector["entities"].append(entity)
        if action.tag == "set_ship_text":
            process_settext_action(action, findByName(action.attrib["name"], sector["entities"]))
        if action.tag == "set_special":
            process_setspecial_action(action, findByName(action.attrib["name"], sector["entities"]), sector["entities"])

def find_skybox(event, system_dict):
    for action in event:
        if action.tag == "set_skybox_index":
            if "index" in action.attrib:
                system_dict["skybox"] = int(action.attrib.get("index"))

def parse_newstyle_event(event, sectors, system_name):
    if not event.attrib.get("name", "").startswith("Sector "):
        eprint("Skipping non-sector event ({})".format(event.attrib.get("name", "no name set")) )
        return
    sector_id = int(event.attrib["name"][7:])
    if sector_id-1 not in sectors:
        sectors[sector_id-1] = {"id": sector_id, "entities": []}
    parse_event_actions(event, sectors[sector_id-1], system_name)


def parse_oldstyle_event(event, old_sector_id, system_dict, sectors):
    sector_id = old_sector_id

    if event.attrib.get("name", "").startswith("Create " + system_dict["name"] + " Sector "):
        rom = event.attrib["name"].split()[-1]
        sector_id = ROMAN_NUMERALS.index(rom)
        if sector_id <= 0:
            eprint("Error: Could not extract sector ID from `{}`".format(event.attrib["name"]))
            sys.exit(1)
        if sector_id-1 not in sectors:
            sectors[sector_id-1] = {"id": sector_id, "entities": []}
        parse_event_actions(event, sectors[sector_id-1], system_dict["name"])
        find_skybox(event, system_dict)
    elif event.attrib.get("name", "").startswith("Create Waypoint"):
        sector_id = int(event.attrib["name"].split('-')[-1])
        if sector_id <= 0:
            eprint("Error: Could not extract sector ID from `{}`".format(event.attrib["name"]))
            sys.exit(1)
        if sector_id-1 not in sectors:
            sectors[sector_id-1] = {"id": sector_id, "entities": []}
        parse_event_actions(event, sectors[sector_id-1], system_dict["name"])
        find_skybox(event, system_dict)
    if event.attrib.get("name", "").startswith("Generate Sector Entities"):
        sector_id = old_sector_id
        if sector_id-1 not in sectors:
            eprint("Error: found sector entities but no sector defined")
            sys.exit(1)
        parse_event_actions(event, sectors[sector_id-1], system_dict["name"])
    if event.attrib.get("name", "").startswith("Settings"):
        sector_id = old_sector_id
        if sector_id-1 not in sectors:
            eprint("Error: found sector entities but no sector defined")
            sys.exit(1)
        parse_event_actions(event, sectors[sector_id-1], system_dict["name"])
    if event.attrib.get("name", "").endswith(" System") or event.attrib.get("name", "") == system_dict["name"]:
        for action in event:
            if action.tag == "set_variable":
                if action.attrib.get("name", "") == "Sector":
                    value = action.attrib["value"]
                    dimension_key = int(value.split('.')[0])
                    if dimension_key not in sector_dimensions:
                        eprint("Error: Unknown sector dimension key {}".format(dimension_key))
                        sys.exit(1)
                    system_dict["width"] = sector_dimensions[dimension_key]['w']
                    system_dict["height"] = sector_dimensions[dimension_key]['h']
    if event.attrib.get("name", "").startswith("Jump Initiated"):
        for action in event:
            if action.tag == "set_variable":
                if action.attrib.get("name", "") == "Sector":
                    value = action.attrib["value"]
                    if value != "targetSector":
                        target_sector = int(value.split('.')[0])
                        if sector_id-1 not in sectors:
                            eprint("ERROR: gate found but sector not defined: {}.".format(sector_id))
                            sys.exit(1)
                        sectors[sector_id-1]["gate_target_sector"] = target_sector
    if event.attrib.get("name", "").startswith("Custom Planet Data"):
        for action in event:
            if action.tag == "set_ship_text":
                if action.attrib.get("name", "") == "Planet":
                    value = action.attrib["newname"]
                    e = [ e for e in sectors[sector_id-1]["entities"] if e["name"] == "Planet" ][0]
                    e["name"] = value.title()
                    e["type"] = "Planet"
    return sector_id


def parse_file(file, style):
    filename = os.path.basename(file)
    system_name = filename.split('.')[0]

    xml_tree = et.parse(file)
    root = xml_tree.getroot()

    system_dict = {
    "name": system_name,
    "sectors": [],
    }

    sectors = {}
    current_sector = 0

    if style == "new":
        for child in root:
            if child.tag == "start":
                parse_start(child, system_dict)
            if child.tag == "event":
                parse_newstyle_event(child, sectors, system_dict["name"])

    if style == "old":
        sec = 0
        for child in root:
            if child.tag == "start":
                parse_start(child, system_dict)
            if child.tag == "event":
                sec = parse_oldstyle_event(child, sec, system_dict, sectors)
    
    for sector in sectors.values():
        sector["entities"] = [e for e in sector["entities"] if 'type' in e]


    w = system_dict.get("width", 0)
    h = system_dict.get("height", 0)
    if w == 0 or h == 0:
        eprint("Error: System dimensions not set.")
        sys.exit(1)
    for i in range(w*h):
        if i not in sectors:
            eprint("Error: Sector {} not defined".format(i+1))
            sys.exit(1)
        system_dict["sectors"].append(sectors[i])


    return system_dict

if __name__ == "__main__":
    file = sys.argv[1]

    style = "new"
    if len(sys.argv) > 2 and sys.argv[2].lower() == "old":
        eprint("Using old style map parser")
        style = "old"

    if not file.endswith('.xml'):
        eprint("Invalid file type")
        sys.exit(1)

    result = parse_file(file, style)
    json.dump(result, sys.stdout, indent=4)
    print()
