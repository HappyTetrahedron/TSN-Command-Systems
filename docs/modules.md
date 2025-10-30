# Modules
Modules are a way to customize the individual ships in the TSN Sandbox.
Modules always add functionality to ships.
A ship can have multiple modules active, and the same module can be active on multiple ships.

Module files are rendered with jinja, and are instantiated multiple times if the module is active for multiple ships.
The result of the rendered jinja is a number of Artemis `event` blocks.

The module jinja must include a macro called `render(ship, util)`.
This macro is called when the module is activated for a ship.
The parameters are:
- `ship`: A dictionary containing information about the ship for which the module should be rendered. The dictionary will be one of the items of the `shipConfigs` list defined in `XML Files/Utils.xml`.
. `util`: A reference to the `XML Files/ModuleUtils` jinja file, which provides access to various helper functions.

Always keep in mind that your module may be invoked multiple times, for different ships.
You need to make sure that the module being used on one ship does not interfere with the module on another ship (unless you specifically want that behaviour).

The recommended practice is to include `ship.id` somewhere in all variable names and timers defined by your module.


## Modules 101

### Integrating with the Comms menu
Many modules make themselves available to the player by way of the Comms menu, where new buttons can be added.

The Comms menu works a lot like the GM menu, whose function is explained somewhat in [Extensions](extensions.md).
However, the module utils provide a bunch of helper functions to interface with this menu.

#### Simple case: Comms buttons that are permanently visible
If your module is simple enough, it may be accomodated by a number of Comms buttons that are always available.

These are easily created with the `util.registerPermanentModuleButtons` macro.

```
{# Fireworks module - spawn fireworks whenever the button is pressed. #}

{% macro render(ship, util) %}

  {# The following command adds a button "Spawn Fireworks" to the Ship Modules submenu for Comms. #}
  {# It's possible to add multiple buttons by providing more button names in the list. #}
  {# The third parameter is a unique identifier of this group of buttons. #}
  {{ util.registerPermanentModuleButtons(ship, ["Spawn Fireworks"], "Fireworks") }}

  {# The following call creates an event that is executed every time the Comms officer presses the indicated button. #}
  {% call util.onModuleButtonPressed("Spawn Fireworks", ship) %}
    <create type="enemy" x="0.0" y="0.0" z="0.0" name="D{{ ship.id }}" hullID="1058" sideValue="2" fleetnumber="-1" />
    <set_object_property name="D{{ ship.id }}" shieldStateFront="0" />
    <set_object_property name="D{{ ship.id }}" shieldStateBack="0" />
    <set_relative_position name2="D{{ ship.id }}" distance="2000" angle="0" player_slot1="{{ ship.slot }}" />
    <get_object_property property="positionX" name="D{{ ship.id }}" variable="Module_Fireworks_{{ ship.id }}_X" />
    <get_object_property property="positionY" name="D{{ ship.id }}" variable="Module_Fireworks_{{ ship.id }}_Y" />
    <get_object_property property="positionZ" name="D{{ ship.id }}" variable="Module_Fireworks_{{ ship.id }}_Z" />
    <create count="1" type="mines" startX="Module_Fireworks_{{ ship.id }}_X" startY="Module_Fireworks_{{ ship.id }}_Y" startZ="Module_Fireworks_{{ ship.id }}_Z" radius="1" />
  {% endcall %}

{% endmacro %}
```


#### More complex cases
Let's look at an example:

```
{# Decoy module - add a deployable drone defense / decoy buoy to a ship. #}

{% macro render(ship, util) %}

  {# Menu Lifecycle #}
  {% call() util.createConditionalModuleButtons(ship, moduleName + "Decoy") %}
    {{ util.ifCommsMenuState(ship, 3) }}
    <if_not_exists name="Decoy {{ ship.id }}" />
    <if_variable name="Module_Decoy_{{ ship.id }}_Used" comparator="NOT" value="1.0" />
    {{ util.sendCommsButton("Deploy Decoy", ship) }}
  {% endcall %}

  {% call() util.destroyConditionalModuleButtons(ship, moduleName + "Decoy") %}
    {{ util.ifCommsMenuState(ship, 3, "NOT") }}
    {{ util.clearCommsButton("Deploy Decoy", ship) }}
  {% endcall %}

  {% call util.destroyConditionalModuleButtons(ship, moduleName + "Decoy") %}
    <if_exists name="Decoy {{ ship.id }}" />
    {{ util.clearCommsButton("Deploy Decoy", ship) }}
  {% endcall %}

  {% call util.destroyConditionalModuleButtons(ship, moduleName + "Decoy") %}
    <if_variable name="Module_Decoy_{{ ship.id }}_Used" comparator="EQUALS" value="1.0" />
    {{ util.clearCommsButton("Deploy Decoy", ship) }}
  {% endcall %}

  {# ... Logic for spawning the decoy is omitted ... #}
{% endmacro %}
```

The first call to `util.createConditionalModuleButtons` creates the menu.
This event has three conditions.

- `util.ifCommsMenuState(ship, 3)` is a utility that generates a single condition. It checks whether the comms menu variable on this ship is set to 3 (which corresponds to the `Modules` submenu in Comms).
- `if_not_exists name="Decoy {{ ship.id }}"` checks whether an object of a specific name exists. The logic of this module is such that only one decoy can be active at a time, so if there already is one, we don't show the button to create another.
- `if_variable name="Module_Decoy_{{ ship.id }}_Used"` checks whether the decoy has been used already on this ship. If the decoy was used, we don't show the button to create a new one.

The only action inside this event is `util.sendCommsButton("Deploy Decoy", ship)`. This macro generates a single action that will send a comms button with the indicated text to the indicated ship.


We have a single event to show our menu if the conditions are right.
This is followed by three separate events that hide the menu again if the conditions are no longer right.
Conditions are conjunctive in Artemis, meaning that an event is run only if *all* of its conditions are true.
But we want to hide the event as soon as *either* condition is no longer true.
This is only possible by making three separate events, each with one of the three conditions.