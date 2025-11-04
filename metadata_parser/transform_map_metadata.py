# This script collects metadata about the maps and transforms them into the asinine format used by navcon/Stellar Cartography.
import collect_map_metadata as cmm
import sys
import glob
import os

XMLFOLDER = sys.argv[1]
OLD = "Legacy Maps"
NEW = "Maps"
NAVCONFOLDER = sys.argv[2]

old_systems = glob.glob('{}/{}/*.xml'.format(XMLFOLDER, OLD))
new_systems = glob.glob('{}/{}/*.xml'.format(XMLFOLDER, NEW))

TYPEMAP = {
    'Station': 'S',
    'Deep Space Station': 'DS',
    'Civilian Station': 'V',
    'Command Post': 'C',
    'Research Station': 'R',
    'Industrial Station': 'I',
    'Mining Station': 'M',
    'Denabite Refinery': 'F',
    'Weapons Platform': 'W',
    'Defense Platform': 'DP',
    'Shipyard': 'Y',
    'Sensor Buoy': 'SB',
    'Comms Relay': 'CR',
    'Bio Base': 'S',
    'Gate': 'G',
    'Asteroid Base': 'S',
    'Slingshot Antenna': 'SLS',
    'Slingshot Power Array': 'SLS',
    'Slingshot Platform': 'SLS',
    'Gas Harvester': 'I',
    'Logistics Post': 'V',
    'Planet': 'P',
    'Pulsar': 'PUL',
    'Moon': 'P',
    'Megastructure': 'MEG',
    'Black Hole': 'H',
    'Marker Buoy': 'MK',
    'Ship': 'SHIP',
}
UNKNOWN_TYPE = "UNK"

def sanitize_sysname(name):
    return name.replace('\'', '')


def write_entities(sys):
    n = sanitize_sysname(sys['name'])
    sysdir = '{}/{}'.format(NAVCONFOLDER, n)
    if not os.path.isdir(sysdir):
        print("No output directory for {}, skipping!".format(n))
        return
    outfile = '{}/entities.txt'.format(sysdir)
    with open(outfile, 'w') as out:
        for sector in sys["sectors"]:
            si = sector["id"]
            for entity in sector["entities"]:
                etype = UNKNOWN_TYPE
                t = entity.get("type", "")
                if t in TYPEMAP:
                    etype = TYPEMAP[t]
                out.write("{},{},{}\n".format(entity["name"], etype, si))

def write_sectorfile(sys):
    n = sanitize_sysname(sys['name'])
    sysdir = '{}/{}'.format(NAVCONFOLDER, n)
    if not os.path.isdir(sysdir):
        print("No output directory for {}, skipping!".format(n))
        return
    outfile = '{}/sector.txt'.format(sysdir)
    with open(outfile, 'w') as out:
        line = "IGNORED,{},{}\n".format(sys["width"], sys["height"])
        out.write(line)

for sys in old_systems:
    print("Parsing {}".format(sys))
    sys = cmm.parse_file(sys, "old")
    write_sectorfile(sys)
    write_entities(sys)

for sys in new_systems:
    print("Parsing {}".format(sys))
    sys = cmm.parse_file(sys, "new")
    write_sectorfile(sys)
    write_entities(sys)
