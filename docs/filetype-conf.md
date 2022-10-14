# File-wide Configuration
These settings affect how PyPlus edits files.\
The json files are located in the `Config/` directory in the source.\
Because PyPlus loads these settings on start, you need to restart PyPlus (PyPlus > Restart) to see the changes.
## 2.1 File type handling
PyPlus supports code highlighting for a variety of file types. The defaults are already specified in the `lexer-settings.json` file.\
To override for a file type, simply specify the config like this:
```jsonc
{
    "extens": "Lexer",
}
```
This will make PyPlus use the [lexer](https://pygments.org/docs/lexers/) 'Lexer' to highlight files ending with 'extens'.\
The key is the file extension, and the value is the lexer name ('short name' in Pygments docs).\
E.g:
```jsonc
{
    "py": "Python",
}
```
So that PyPlus will highlight `.py` files with a [Python lexer](https://pygments.org/docs/lexers/#pygments.lexers.python.PythonLexer).
### Note
For every file that is not included in the list, PyPlus automatically uses [TextLexer](https://pygments.org/docs/lexers/#pygments.lexers.special.TextLexer), which doesn't highlight anything.
## 2.2 Comment markers
PyPlus supports wrapping code with comment markers. The defaults are already specified in the `comment-markers.json` file.\
The key is the file extension, and the value is the comment marker (in `string`).\
To override for a file type, simply specify the config like this:
```jsonc
{
    "extens": "marker0 marker1",
}
```
This will make PyPlus surround every file with the extension 'extens' with `marker0` and `marker1`.
## 2.3 Run commands and linter
PyPlus supports running and linting. Currently, it determines the command by file type.\
To override for a file type, do this:
```jsonc
{
    "extens": "command"
}
```
This will make PyPlus run/lint file with `command file-name` for files with extension 'extens'.
### Note
We're now adding project-wide run configuration. See issue [#13](https://github.com/ZCG-coder/PyPlus/issues/13) for details.
## 2.4 Icons
PyPlus added icons support in commit [1c31fb3](https://github.com/ZCG-coder/PyPlus/commit/1c31fb3).\
To configure how PyPlus displays the icons, specify config like this in `file-icons.json`:
```jsonc
{
    "extens": "icon-name"
}
```
where 'icon-name' is the name of the icon, i.e., the icon's file name excluding the '.svg' extension. E.g. the file name is 'python.svg', then the name is 'python'.
### Note
Icons are listed in the `src/Images/file-icons/` directory.
## 2.5 "New file" dialog
PyPlus added a "New File" dialog in commit [df70af4](https://github.com/ZCG-coder/PyPlus/commit/df70af4).\
The dialog helps creating files of type, and the user can choose a file extension. The defaults are already in `file-extens.json`.
### To add a type
```jsonc
{
    "Name": [
        "extens1", "extens2"
    ]
}
```
Where 'Name' is the type of the files with extens, and the extensions for the type are specified with a list.
### To add an extension
1. Find the key for the extension. E.g., 'Python' for extension 'py'.
2. Add the extension to the list under the key.
