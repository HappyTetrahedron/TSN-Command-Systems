# Extensions
Extensions are the most versatile method for adding functionality to the TSN Sandbox.
An extension contains arbitrary XML that is loaded into the final mission script unchanged.
Oftentimes, extensions add new tools for the Game Master console, but they can do a number of other things.

The extension files are rendered with jinja, so it is possible (but not required) to use jinja in them.
The result of the rendered jinja should be a partial XML file which contains a number of Artemis `event` blocks.

In particular, the extension file may not contain a `start` block, and the surrounding `mission_data` tag must be removed.
If you created your extension using the [Artemis Mission Editor](http://artemiswiki.pbworks.com/w/page/53389687/Mission%20Editor), you must manually remove these two things from the finished file.

You are encouraged to include a jinja comment at the top of your extension file, which explains briefly what this extension does:

```
{# HazardPainter extension - GM tool to dynamically generate rings or lines of mines/nebulae/asteroids. #}
```

## Extensions 101

### Integrating with the GM Menu

A common thing extensions do is add new buttons to the GM Menu.
To make sure your button properly follows the lifecycle of the menu, it's important you understand said lifecycle first.

The GM menu uses a number of variables to manage its state.
One set of variables indicates which menu *should* currently be displayed.
A different set of variables indicates which menu currently *is* displayed.
The events in the GM menu watch for discrepancies between these variables, and take action accordingly.

*If the Spawn menu should be shown, but it is currently not being shown, then we should create the Spawn menu and update the variables to say the Spawn menu is now shown.*

If you add new buttons to the GM menu, it is recommended you follow the same principle.
You can look at the variables of the GM menu to find out whether your buttons should be shown.
You should then create your own variable to track whether your buttons *are* shown.
Whenever your variable differs from the appropriate menu variable, you should take action to either construct or delete your buttons.

The main variable for the *should-be* state of the GM menu is called `GM_Menu_Selector`.
It is set to a number, and different numbers correspond to different GM menus.
For example, the Spawn menu is number 2.

#### Example
Let's say your extension adds new TSN ships to the Sandbox, and you want to add buttons to the GM menu to spawn these ships.

First, think about when your buttons should show.

Naturally, ship spawn buttons should show up in the Spawn menu.
In scripting terms, this means the variable `GM_Menu_Selector` should be `2`.

But that's not all: the Spawn menu has a submenu.
You can select one of several factions, and then you get spawn buttons for that faction.
Since you're adding TSN ships, you want your buttons to show in the TSN submenu.
The submenu is governed by the variable `GM_SpawnMenu_Selector`, and when the TSN faction is selected, its value is `1`.

So, in summary, our menu should only show when `GM_Menu_Selector` is `2` and `GM_SpawnMenu_Selector` is `1`.

We can now make use of a utility macro to generate events with the appropriate conditions:

```
{% import 'Utils.xml' as util %}

{% call() util.createConditionalMenu("VerdantSpawn", {
    "GM_Menu_Selector": "2",
    "GM_SpawnMenu_Selector": "1",
}) %}
    <set_gm_button text="TSN Ships\+Verdant" />
    <set_gm_button text="TSN Fleets\+VerdantFleet" />
    <set_gm_button text="TSN Fleets\+VerdantForm" />
    <set_gm_button text="TSN Ships\+WhispersofFreedom" />
{% endcall %}
```

The macro `util.createConditionalMenu` generates an event that executes only once if a certain set of conditions are true.

The first parameter is the name of the menu. It must be unique.

The second parameter is a dictionary of conditions.
The keys are the variable names, and the values are what values the variables must have for this event to run.

The body of the call includes code to set up all the buttons you need.

The macro automatically creates a new variable to track whether this menu is currently being shown, so you don't need to do that by hand.

This is only half of the deal, though - we must also clean up our menu.
For this, we create a corresponding menu destruction event, again with a macro:

```
{% call() util.destroyConditionalMenu("VerdantSpawn", {
    "GM_Menu_Selector": "2",
    "GM_SpawnMenu_Selector": "1",
}) %}
    <clear_gm_button text="TSN Ships\+Verdant" />
    <clear_gm_button text="TSN Fleets\+VerdantFleet" />
    <clear_gm_button text="TSN Fleets\+VerdantForm" />
    <clear_gm_button text="TSN Ships\+WhispersofFreedom" />
{% endcall %}
```

The macro `util.destroyConditionalMenu` generates an event that executes only once if a certain set of conditions are *not* true.

The first parameter is the name of the menu. It must be the same as in the corresponding `createConditionalMenu` call.

The second parameter is a dictionary of conditions.
It should look the same as in the corresponding `createConditionalMenu` event.

The body of the call includes code to delete all the buttons you previously created.

There you go, now you have buttons that show up in the TSN spawn menu.
You can have a look at `XML Files/GM Menus.xml` to find out what all the variables are to track GM menu state.

By convention, some variables in the system start with an underscore `_`.
As a rule, those variables should never be changed by extensions.
The file which owns these variables assumes that they are never changed externally, and doing so will very likely break things.