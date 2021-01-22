# PyPlusSource

The source code of the PyPlus editor.

# The code

The code is a modified(*enhanced*) version of  
[dh7qc/python-text-editor](https://www.github.com/dh7qc/python-text-editor).

**The website is at [here](http://zcg-coder.github.io/PyPlusWeb)**  
**The website may be outdated, so please go to source release to download it.**  
Some of the code is from pyro written by James Stalings. Thanks him for the source  
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
           text. Editor status line is in the window title.
           
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
