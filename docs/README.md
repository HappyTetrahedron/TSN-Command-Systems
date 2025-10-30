# Documentation

This folder contains the documentation for the TSN Command Systems codebase (such as it is).
The documentation is meant to help you contribute to the Command Systems by designing your own maps and modules.

We're still working on this, so if you find something undocumented, feel free to create an issue.

## About Artemis Scripting

To work on the TSN Command Systems and Sandbox, it's very helpful to be at least passingly familiar with [Artemis Mission Scripting](http://artemiswiki.pbworks.com/w/page/51088806/Mission%20Scripting).

Here's the basic rundown: An Artemis script is a single XML file containing a single `mission_data` element.
The `mission_data` element has a bunch of children; including exactly one `start` element and a number of `event` elements.
Both of these, in turn, have children - many tags are available, and they are broadly categorized into *conditions* and *actions*.

The `start` element has no conditions, only actions. These actions are ran once when the mission starts.

Each `event` element can have any number of conditions and actions.

Every game tick, Artemis goes through the entire list of `event`s and checks their condition.
If an event has all of its conditions true, then all of its actions are executed in order.

This happens *every single game tick*.
Meaning that if your event has conditions that are always true, then its actions are executed *every tick*.
This is *usually* not what you want, and your event should therefore change something that makes its own conditions no longer true.

Actions can include changing variables, setting timers and spawning stuff.
Conditions can include checking variables, checking whether timers have run out, and checking whether stuff exists.

All variables are global, and all events are checked and executed sequentially.
Order matters too: say we have one event A with no conditions that sets variable X to 1, and after it comes event B with a condition that variable X must be 1.
Within the same tick, event A happens first, which sets X=1, and then when B's conditions are checked they wind up being true and B is executed as well. 
If the events were reversed, B would be checked first, X would not yet be 1, and therefore only A is executed within the same tick.

## Structure of the TSN Command Systems and Sandbox

The TSN Command Systems is, in essence, a collection of jinja files.
When rendered, these jinja files produce a valid Artemis script XML.

The core of the Sandbox is included in the files directly under `XML Files`.
`main.xml` is the main jinja template being rendered; it includes other files as required.

The files directly in `XML Files` are currently organized a bit haphazardly; I am in the middle of splitting individual features into separate files.
The structure currently changes often and is therefore not documented in further detail.

The TSN Sandbox is designed with modularity in mind.
It is possible to include or exclude certain parts as required, to avoid the final Artemis script being so big as to crash the game.

The parts that can be excluded are divided into [Maps](maps.md), [Modules](modules.md) and [Extensions](extensions.md). 
Whenever you build the Sandbox, you must decide which of these to include.

The core Sandbox, comprised of the files directly under `XML Files`, is always included.

The file `XML Files/render.py` builds the Sandbox from the jinja templates.
You can check that file for an example of the parameters that must be provided to the jinja templates.