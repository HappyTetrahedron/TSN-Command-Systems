
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
    

def parse_newstyle_event(event, sectors, system_name):
    if not event.attrib.get("name", "").startswith("Sector "):
        eprint("Skipping non-sector event ({})".format(event.attrib.get("name", "no name set")) )
        return
    sector_id = int(event.attrib["name"][7:])
    if sector_id-1 not in sectors:
        sectors[sector_id-1] = {"id": sector_id, "entities": []}
    parse_event_actions(event, sectors[sector_id-1], system_name)

folder = {}

def parse_event(event):
    data = {}
    statements = []
    for action in event:
        if action.tag == "if_gm_button":
            text = action.attrib["text"]
            data["name"] = text.split('\\', 1)[1]
        elif action.tag == "set_variable":
            name = action.attrib["name"]
            value = action.attrib["value"].split(".")[0]
            if name == "Auto AI Type":
                data["autoAI"] = value
            elif name == "Name Assign":
                if value == "1":
                    data["nameassign"] = True
            else:
                statements.append(et.tostring(action, encoding="unicode"))
        else:
            statements.append(et.tostring(action, encoding="unicode"))

    data["statements"] = statements
    return data

def print_event(event):
    if 'name' not in event:
        print("<!-- INVALID EVENT -->")
        print()
        return
    args = [
        "factions." + folder[0],
        '"' + event["name"] + '"',
    ]
    print('{% call spawnWreck(' + ", ".join(args) + ') %}')
    for s in event["statements"]:
        print("  " + s.strip())
    print('{% endcall %}')
    print()


def parse_file(file, style):
    filename = os.path.basename(file)
    system_name = filename.split('.')[0]

    xml_tree = et.parse(file)
    root = xml_tree.getroot()

    for child in root:
        if child.tag == "folder_arme":
            if child.attrib["name"].endswith(" Wrecks"):
                folder[0] = child.attrib["name"].removesuffix(" Wrecks")
        if child.tag == "event":
            data = parse_event(child)
            print_event(data)
    

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
    print()
