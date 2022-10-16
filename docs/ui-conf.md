# File-wide Configuration
These settings affect how PyPlus displays its UI.\
The json files are located in the `Config/` directory in the source.\
Because PyPlus loads these settings on start, you need to restart PyPlus (PyPlus > Restart) to see the changes.
## ***WARNING: ADVANCED SETTINGS***
***THESE SETTINGS ARE FOR ADVANCED USERS. CORRUPTION WILL CAUSE SERIOUS UNRECOVERABLE DAMAGE! IT IS RECOMMENDED TO KEEP A BACKUP OF THEM BEFORE EDITING.***
## Menu
PyPlus supports menu customization since commit [71f080b](https://github.com/ZCG-coder/PyPlus/commit/71f080b).\
The defaults are in `menu.json`. The configuration is in a recursive format, which gets processed recursively as well. Therefore, the more layers the menu has, the longer it takes to render it.\
Example:
```jsonc
{
    "main": {
        "[Parent]@A": {
            "Item": [
                null, // Icon
                null, // Accelerator
                "Class(obj.master)", // Command
                "src.Components.class -> Class", // Imports
                false // Disable when no files open
            ]
        }
    }
}
```
### Which menu?
Currently, PyPlus supports two menus: the PyPlus application menu and the start screen menu.\
The `main` word in the above example means this menu will be created for the PyPlus application.
### Which platform?
Platform markers are used to specify the platform to display the menu.\
Supported markers are:
- `W, !W` for Windows and all except Windows
- `M, !A` for macOS and all except macOS
- `L, !L` for Linux and all except Linux
- `A` for all platforms
E.g, display the Application menu on macOS only:
```jsonc
{
    "main": {
        "[PyPlus]@M": {
            "Item": [
                null, // Icon
                null, // Accelerator
                "Class(obj.master)", // Command
                "src.Components.class -> Class", // Imports
                false // Disable when no files open
            ]
        }
    }
}
```
### Accelerator
An accelerator is a marker to show the shortcut of a command, PyPlus also creates bindings with this option.\
An accelerator accepted by PyPlus is either a bare accelerator (just a key), or a CTRL-key (Command-key on Macs) binding.
#### Bare accelerator
**Keep in mind that macOS highlights the menu if a command is selected with a shortcut. If bare accelerator is used, it might be a bit annoying when the key is commonly-used, e.g., alphanumeric keys**\
To specify a bare accelerator, start the accelerator with a `` ` ``
```jsonc
{
    "[Parent]@A": {
        "Item": [
            null, // Icon
            "`a", // Accelerator: a
            "Class(obj.master)", // Command
            "src.Components.class -> Class", // Imports
            false // Disable when no files open
        ]
    }
}
```
#### CTRL-key accelerator
```jsonc
{
    "[Parent]@A": {
        "Item": [
            null, // Icon
            "a", // Accelerator: CTRL/Command + a
            "Class(obj.master)", // Command
            "src.Components.class -> Class", // Imports
            false // Disable when no files open
        ]
    }
}
```
### Command and imports
Use this option to map a command to a specific menu item.\
The `obj` can be used to reference the editor class.
```jsonc
{
    "[Parent]@A": {
        "Item": [
            null, // Icon
            "a", // Accelerator: CTRL/Command + a
            "Class(obj.master)", // Command
            "src.Components.class -> Class", // Imports
            false // Disable when no files open
        ]
    }
}
```
Imports from the PyPlus library is also allowed. Use the `->` operator to separate the module name and the object name.
## Start dialog links
This modifies the links displayed in the start dialog. The defaults are in `start.json`\
```jsonc
{
    "Title": [
        "icon",
        "command()"
    ]
}
```
This adds the link called "Title", and runs `command()` when clicked.
