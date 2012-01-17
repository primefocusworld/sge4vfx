#Houdini Plugins

The Houdini plugin is currently very basic.  It doesn't use SOHO and requires IFDs to be generated before it's run.  It also works for geometry nodes and when used as such, will request a resource from GridEngine.

If 'Use non-GUI lics only' is checked then it'll request a complex called 'hbatch'
If 'Use non-GUI lics only' is not checked then it'll requests a complex called 'anyhou'

There are a lot of todos for this one but here are a couple I can think of right now:

* Have a checkbox that does the IFD gen on submission or on the farm
* Allow multiple level dependencies
* Improve license handling (how??)
