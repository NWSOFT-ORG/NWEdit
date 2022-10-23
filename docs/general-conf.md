# Customization of NWEdit
NWEdit is designed to be customisable through [JSON](https://json.org/).\
The json files are located in the `Config/` directory in the source.\
Because NWEdit loads these settings on start, you need to restart NWEdit (NWEdit > Restart) to see the changes.
## 1. General Settings
### 1.1 Themes and color schemes
NWEdit supports theming through [ttkthemes](https://ttkthemes.readthedocs.io), and color schemes from [Pygments](https://pygments.org)\
Explore themes [here](https://ttkthemes.readthedocs.io/en/latest/themes.html) and color schemes [here](https://pygments.org/styles/)\
Configuration (Menu > NWEdit > Preferences > General Settings):
```jsonc
{
    "ttk_theme": "black", // Any ttk theme
    "pygments_theme": "monokai", // Any Pygments theme
}
```
### 1.2 Fonts and options
Tkinter, the framework which NWEdit written in, supports font customization.\
You can use any system-installed font, or 'TkFixedFont' for a built-in fixed-width font.\
Configuration (Menu > NWEdit > Preferences > General Settings):
```jsonc
{
    // Font face
    "font": "Menlo",
    // Size of font
    "font_size": 13,
}
```
Tk also supports font options too.\
| Option | Available value |
| ------ | --------------- |
| `weight` | `"normal"`, `"bold"`... |
| `slant` | `"normal"`, `"roman" `|
| `underline` | `true`, `false` |
| `overstrike` | `true`, `false` |
```jsonc
{
    "font_options": {
        "weight": "normal",
        "slant": "roman",
        "underline": false,
        "overstrike": false,
    },
}
```
### 1.3 Others
#### Line Height
Adds spacing between lines.\
Configuration:
```jsonc
{
    "line_height": 1.3, // Decimals accepted
}
```
#### Tab width
Configures how tabs render and how long soft tabs are.\
E.g. When set to `8`, every tab takes 8 spaces and each soft tab is 8 chars in length\
Configuration:
```jsonc
{
    "tab_width": 4,
}
```
#### Block cursor
Changes how cursor renders. If set to `true`, the text cursor takes up the space of one char, else, it will become a thin line.\
Configuration:
```jsonc
{
    // Shows the cursor as a block
    "block_cursor": true,
}
```

