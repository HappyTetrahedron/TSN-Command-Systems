
#!/usr/bin/env python

# Script to turn a minimal system data XML into a proper system module

import sys
import os
import faulthandler
faulthandler.enable()
from jinja2 import Environment, FileSystemLoader
import datetime
import xml.etree.ElementTree as et

file = sys.argv[1]

if not file.endswith('.xml'):
    print("Invalid file type")
    sys.exit(1)

filename = os.path.basename(file)
system_name = filename.split('.')[0]

system_dict = {
   "name": system_name,
   "sectors": [],
}
sectors = {}

xml_tree = et.parse(file)
root = xml_tree.getroot()

def parse_start(start):
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


def parse_event(event):
    if not event.attrib.get("name", "").startswith("Sector "):
        print("Skipping non-sector event ({})".format(event.attrib.get("name", "no name set")) )
        return
    sector_id = int(event.attrib["name"][7:])
    sector_dict = {
        "createdEntities": [],
    }

    w = system_dict.get("width", 0)
    h = system_dict.get("height", 0)
    if w == 0 or h == 0:
        print("Error: System dimensions not set. Make sure you set the system dimension variables in the Start section, and make sure the Start section comes first.")
        sys.exit(1)

    transitions = []

    isTop = sector_id <= w
    isBottom = sector_id > (w*h) - w
    isLeft = sector_id % w == 1 or w == 1
    isRight = sector_id % w == 0

    if not isTop:
        transitions.append("Grid A")
    if not isBottom:
        transitions.append("Grid E")
    if not isLeft:
        transitions.append("Grid 1")
    if not isRight:
        transitions.append("Grid 5")

    if not isTop and not isLeft:
        transitions.append("Corner A1")
    if not isTop and not isRight:
        transitions.append("Corner A5")
    if not isBottom and not isLeft:
        transitions.append("Corner E1")
    if not isBottom and not isRight:
        transitions.append("Corner E5")
    sector_dict["transitions"] = transitions

    terrainLines = []
    sectorLines = []
    gate_found = False
    gate_target = ""
    gate_target_sector = 0

    for action in event:
        if action.tag == "create":
            if "name" in action.attrib:
                name = action.attrib["name"]
                if action.attrib.get("type", "") in ["enemy", "neutral"]:
                    action.attrib["sideValue"] = "sectorSide"
                sector_dict["createdEntities"].append(name)
                sectorLines.append(et.tostring(action, encoding="unicode"))
                if name.endswith(" Gate"):
                    if gate_found:
                        print("Error: Can't have multiple gates in a sector. Sorry.")
                        sys.exit(1)
                    gate_found = True
                    gate_target = name[0:-5]
                    gate_target_sector = int(action.attrib["y"].split('.')[0])
                    if gate_target_sector == 0:
                        print("Error: No target sector configured for {}. Configure a target sector by adjusting the gate object's Y coordinate to the target sector's number. (I know, it's a hack.)".format(name))
                        sys.exit(1)
            else:
                terrainLines.append(et.tostring(action, encoding="unicode"))
        else:
            sectorLines.append(et.tostring(action, encoding="unicode"))


    sector_dict["statements"] = "\n".join(sectorLines)
    sector_dict["terrainStatements"] = "\n".join(terrainLines)
    if gate_found:
        sector_dict["gateTarget"] = {
            "system": gate_target,
            "sector": gate_target_sector,
        }


    sectors[sector_id-1] = sector_dict

for child in root:
    if child.tag == "start":
        parse_start(child)
    if child.tag == "event":
        parse_event(child)

w = system_dict.get("width", 0)
h = system_dict.get("height", 0)
if w == 0 or h == 0:
    print("Error: System dimensions not set. Make sure you set the system dimension variables in the Start section, and make sure the Start section comes first.")
    sys.exit(1)
for i in range(w*h):
    if i not in sectors:
        print("Error: Sector {} not defined".format(i+1))
        sys.exit(1)
    system_dict["sectors"].append(sectors[i])

# Render jinja
template_env = Environment(loader=FileSystemLoader('..'))
template_env.lstrip_blocks = True
template_env.trim_blocks = True
template_env.add_extension('jinja2.ext.do')

TMPL_FNAME = 'NewSystems/SystemTemplate.jinja'
TMPL_FOLDER = 'NewSystems/'
OUT_FNAME = '../Systems (Generated)/{}.xml'.format(system_name)

template_to_use = TMPL_FNAME
if os.path.exists("{}.jinja".format(system_name)):
    template_to_use = "{}{}.jinja".format(TMPL_FOLDER, system_name)

jinja_context = {
    "system": system_dict,
    "version": "local",
    "time": datetime.datetime.now(datetime.UTC).isoformat()
}

with open(OUT_FNAME, 'w') as f:
    f.write(template_env.get_template(template_to_use).render(g=jinja_context))
