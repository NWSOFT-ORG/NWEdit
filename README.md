# PyPlusSource

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FZCG-coder%2FPyPlus&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Views&edge_flat=true)](javascript:void(0);)  
The source code of the PyPlus editor.

# The code

The code is a modified(*enhanced*) version of  
[dh7qc/python-text-editor](https://www.github.com/dh7qc/python-text-editor), licensed after the GPL v3.0 license

**The website is at [here](http://zcg-coder.github.io/NWSOFT/PyPlusWeb)**  
**The website may be outdated, so please go to source release to download it.**  
Some code is from pyro written by James Stalings, licensed after the GPL v3.0 License. Thanks him for the source

```
simple elegant text editor built on Python/Tkinter
    by James Stallings, June 2015
    Adapted from:

      Pygments Tkinter example
      copyleft 2014 by Jens Diemer
      licensed under GNU GPL v3
      
    and
    
      'OONO' designed and written by Lee Fallat, 2013-2014.
      Inspired by acme, sam, vi and ohmwriter.
    A sincere thanks to these good people for making their source code available for myself and others
    to learn from. Cheers!
    
    
        Pyro currently does a very minimalist job of text editing via tcl/tk ala tkinter. 
        
        What pyro does now:
        
           colorizes syntax for a variety of text types; to wit:
    
               Python
               PlainText
               Html/Javascript
               Xml
               Html/Php
               Perl6
               Ruby
               Ini/Init
               Apache 'Conf'
               Bash Scripts
               Diffs
               C#
               MySql
           
           writes out its buffer
           converts tabs to 4 spaces
           
           It does this in an austere text editor framework which is essentially a glue layer
           bringing together the tk text widget with the Pygment library for styling displayed
           text. _Editor status line is in the window title.
           
           Pyro comes with one serious warning: it is a user-space editor. It makes no effort
           to monitor state-change events on files and so should not be used in situations
           where it is possible that more than one writer will have access to the file.
           
           
        Pyro's current controls are as follows:
        
           Ctrl+q quits
           Ctrl+w writes out the buffer
           Selection, copy, cut and paste are all per xserver/window manager. Keyboard navigation via
           arrow/control keys, per system READLINE.
           
        Pyro's current commands are:
        
           #(num) move view to line 'num' and highlight it, if possible.
           *(text) find text in file.
           /(delim)(text)(delim)(text) search and replace
        
        Pyro requires Tkinter and Pygment external libraries.
```

Also, from thonny, licensed after the MIT License. And the Hex editor

```
Copyright © 2016-20 Qtrac Ltd. All rights reserved.
This program or module is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. It is provided for educational
purposes and is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.
```

Thanks to overture for the phplint tool, and thanks to people who wrote greate code on Gist and stack overflow.

# Directory Structure
This project is meant to be run prefectly in different OS. Until now, it supports Windows, Mac and Linux.  
To make it run perfectly in these OS, I have to seperate their files, because the original 'cross-compatable' files are finally to big to run on Mac.  
Currently, the only major difference between them is the different menus.  
Windows uses a custom titlebar, so I need to make a custom menubar. But Macs won't run the custom code completely, so I have to use `tk.Menu`.  
But from now on, the differnce will be bigger.  
If you are on:
| OS      | Directory            |
|---------|----------------------|
| Windows | Windows              |
| Mac     | Mac                  |
| Linux   | Windows (soon won’t) |
