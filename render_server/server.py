from flask import Flask
from flask import Blueprint
from flask import current_app
from flask import request
from flask import stream_template
from flask import g
import os
import datetime

app = Blueprint('app', __name__)

MAIN_TMPL='main.xml'

SCRIPT_FOLDER="Extensions"
SYSTEM_FOLDER="Generated Maps"
MODULE_FOLDER="Modules"

VERSION_FILE="../.version"

XML_EXT = ".xml"

def sanitize(filename):
    return filename.replace('.', '').lstrip('/')

@app.route("/render", methods = ['POST'])
def render():
    data = request.json
    g.data = data
    g.version = current_app.config['version']
    g.time = datetime.datetime.now().isoformat()

    return stream_template(MAIN_TMPL)

@app.route("/version")
def get_version():
    return current_app.config['version']

@app.route("/maps")
def get_star_systems():
    mypath = current_app.config['datadir']
    scripts_path = os.path.join(mypath, SYSTEM_FOLDER)
    found = []
    files = [f for f in os.listdir(scripts_path) if f.endswith(XML_EXT) and os.path.isfile(os.path.join(scripts_path, f))]
    for file in files:
        metaParsed = False
        data = {
            "name": os.path.splitext(file)[0]
        }
        print("Parsing " + file)
        with open(os.path.join(scripts_path, file)) as content:
            l = "\n"
            while not metaParsed:
                l = content.readline()
                if l.strip().startswith('{#'):
                    metaParsed = True
                    s = l.strip('{#-}').strip()
                    for kv in s.split():
                        parts = kv.split('=')
                        if len(parts) == 2:
                            data[parts[0]] = parts[1]
                
        found.append(data)
    return found

@app.route("/extensions")
def get_systems():
    mypath = current_app.config['datadir']
    scripts_path = os.path.join(mypath, SCRIPT_FOLDER)
    found = []
    files = [f for f in os.listdir(scripts_path) if f.endswith(XML_EXT) and os.path.isfile(os.path.join(scripts_path, f))]
    for file in files:
        metaParsed = False
        data = {
            "name": os.path.splitext(file)[0]
        }
        print("Parsing " + file)
        with open(os.path.join(scripts_path, file)) as content:
            l = "\n"
            c = 0
            while c < 6 and not metaParsed:
                l = content.readline()
                c += 1
                if l.strip().startswith('{#') and l.strip().endswith('#}'):
                    metaParsed = True
                    s = l.strip().strip('{#-}').strip()
                    data["comment"] = s
        found.append(data)
    return found

@app.route("/modules")
def get_modules():
    mypath = current_app.config['datadir']
    scripts_path = os.path.join(mypath, MODULE_FOLDER)
    found = []
    files = [f for f in os.listdir(scripts_path) if f.endswith(XML_EXT) and os.path.isfile(os.path.join(scripts_path, f))]
    for file in files:
        metaParsed = False
        data = {
            "name": os.path.splitext(file)[0]
        }
        print("Parsing " + file)
        with open(os.path.join(scripts_path, file)) as content:
            l = "\n"
            c = 0
            while c < 6 and not metaParsed:
                l = content.readline()
                c += 1
                if l.strip().startswith('{#') and l.strip().endswith('#}'):
                    metaParsed = True
                    s = l.strip().strip('{#-}').strip()
                    data["comment"] = s
        found.append(data)
    return found

@app.route("/ship_configs")
def get_config_options():
    return {
        "ordnance": {
            "friendly_name": "Ordnance",
            "type": "property-dict",
            "options": [
                {
                    "name": "torpedo",
                    "friendly_name": "Torp count",
                    "type": "integer",
                },
                {
                    "name": "nuke",
                    "friendly_name": "Nuke count",
                    "type": "integer",
                },
                {
                    "name": "mine",
                    "friendly_name": "Mine count",
                    "type": "integer",
                },
                {
                    "name": "emp",
                    "friendly_name": "EMP count",
                    "type": "integer",
                },
                {
                    "name": "pshock",
                    "friendly_name": "P-Shock count",
                    "type": "integer",
                },
                {
                    "name": "probe",
                    "friendly_name": "Probe count",
                    "type": "integer",
                },
                {
                    "name": "tag",
                    "friendly_name": "Tag count",
                    "type": "integer",
                },
                {
                    "name": "beacon",
                    "friendly_name": "Beacon count",
                    "type": "integer",
                },
            ]
        },
        "cargo": {
            "friendly_name": "Shuttle cargo",
            "type": "property-dict",
            "options": [
                {
                    "name": "marines",
                    "friendly_name": "Marine teams",
                    "type": "integer",
                },
                {
                    "name": "engineers",
                    "friendly_name": "Engineer teams",
                    "type": "integer",
                },
                {
                    "name": "medics",
                    "friendly_name": "Medic teams",
                    "type": "integer",
                },
                {
                    "name": "cargos",
                    "friendly_name": "Cargo units",
                    "type": "integer",
                },
                {
                    "name": "commsrelays",
                    "friendly_name": "Comms Relays",
                    "type": "integer",
                },
                {
                    "name": "sensorbuoys",
                    "friendly_name": "Sensor BOIS",
                    "type": "integer",
                },
            ]
        },
        "modules": {
            "friendly_name": "Ship modules",
            "type": "multi-select",
            "options": [
                {
                    "name": "ClusterMine",
                    "friendly_name": "Cluster mines",
                },
                {
                    "name": "Decoy",
                    "friendly_name": "Decoy buoys",
                },
                {
                    "name": "ShieldEnhancer",
                    "friendly_name": "Shield enhancers",
                },
                {
                    "name": "KamikazeMine",
                    "friendly_name": "Kamikaze Bombs",
                },
            ]
        }
    }


def create_app(datadir):
    myapp = Flask(__name__, template_folder=datadir)

    myapp.config['version'] = "unknown"
    if os.path.isfile(os.path.join(datadir, VERSION_FILE)):
        with open(os.path.join(datadir, VERSION_FILE)) as vfile:
            version = vfile.readline()
            myapp.config['version'] = version.strip()

    myapp.config['datadir'] = datadir
    myapp.jinja_env.lstrip_blocks = True
    myapp.jinja_env.trim_blocks = True
    myapp.jinja_env.add_extension('jinja2.ext.do')
    myapp.register_blueprint(app)

    return myapp

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-d', '--data-directory', dest='ddir', type='string',
                      help="Path of XML file directory")
    parser.add_option('-H', '--host', dest='host', type='string', default="0.0.0.0",
                      help="Host at which to serve requests")
    parser.add_option('-p', '--port', dest='port', type='string', default="2245",
                      help="Port at which to serve requests")
    (opts, args) = parser.parse_args()
    myapp = create_app(opts.ddir)
    myapp.run(opts.host, opts.port)
