# TSN Command Systems - Tetra's Fork

TSN Command Systems is a script that generates the TSN Sandbox.

The TSN Sandbox is a mission script to be used in Artemis that enables fully Game Master-moderated missions.

*This fork is maintained by Tetra. If you have questions about this fork, feel free to create an issue. If you have questions about the TSN Sandbox or Command Systems in general, I recommend you direct them to the TSN RP community.*
 
## Requirements
The current version of TSN Command Systems and the TSN Sandbox require Artemis 2.8.1 with the TSN Mod installed.
For the TSN Mod, see [here](https://github.com/tsnrp/mod).

## Usage
The easiest way to get the Sandbox script is to download it from https://cic.tetrahedron.ch/ - that website runs the code from this repo and can generate mission scripts on the fly.

Select your options, download the script, and then drop it into the `dat\missions` folder of your Artems installation.
**Important**: The name of the folder within `dat\missions` has to exactly correspond to the file name of the mission XML file (minus the file extension)─in this case, `MISS_TSN-Command`.
The final folder structure should look as follows:
```
[Artemis install directory]
├── dat
│   ├── missions
│   │   ├── MISS_TSN-Command
│   │   │   ├── MISS_TSN-Command.xml
```

To use the generated sandbox, first launch Artemis and start a server. Select a Custom Script, and then select the `TSN-Command` script.
Note that to use the sandbox, it is required for one of the clients to use the Game Master console.

[Slightly outdated, but still helpful video explaining how to use the TSN Sandbox](https://www.youtube.com/watch?v=pFmg2e8LOYs)

## Running locally
To generate the XML files of the TSN sandbox, you can run the `XML Files/render.py` script contained in this repository.
It will compile the sandbox with hardcoded options.
Change the options by directly editing the script.
You will need the python-jinja2 package as a dependency.

The mission script can also be generated via API.
The API server is in the `render_server` directory - it is a simple Python flask app.

A fully interactive frontend for this API can be found [here](https://github.com/HappyTetrahedron/cic-webapp).