from flask import Flask
from flask import Blueprint
from flask import current_app
from flask import request
from flask import stream_template
from flask import g
import os

app = Blueprint('app', __name__)

MAIN_TMPL='main.xml'

def sanitize(filename):
    return filename.replace('.', '').lstrip('/')

@app.route("/render", methods = ['POST'])
def render():
    data = request.json
    g.data = data
    print(g.data)

    return stream_template(MAIN_TMPL)


def create_app(datadir):
    myapp = Flask(__name__, template_folder=datadir)
    myapp.jinja_env.lstrip_blocks = True
    myapp.jinja_env.trim_blocks = True
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
