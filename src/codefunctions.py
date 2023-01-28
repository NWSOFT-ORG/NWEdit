import os
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import pygments.lexers
from pygments import lexers

from src.Components.commondialog import ErrorInfoDialog
from src.Components.console import Console
from src.Components.tktext import EnhancedText
from src.constants import (events, LINT_BATCH, logger, WINDOWS)
from src.highlighter import create_tags, recolorize
from src.Utils.functions import open_shell


class CodeFunctions:
    def __init__(
        self,
        master: tk.Misc,
        text: EnhancedText,
        bottomframe: ttk.Notebook,
    ) -> None:
        self.text = text
        self.master = master
        self.bottomframe = bottomframe

    def system_shell(self) -> None:
        terminal = open_shell(self.bottomframe)
        self.bottomframe.add(terminal, text="System Shell")
        lexer = pygments.lexers.get_lexer_by_name("Bash")
        create_tags(terminal)
        recolorize(terminal, lexer)
        terminal.bind(
            "<KeyRelease>", lambda _=None: recolorize(terminal, lexer)
        )

    def python_shell(self) -> None:
        curr_tab = self.bottomframe
        shell_frame = ttk.Frame(curr_tab)
        console = Console(shell_frame, None, shell_frame.destroy)
        lexer = lexers.get_lexer_by_name("pycon")
        console.text.focus_set()
        create_tags(console.text)
        recolorize(console.text, lexer)
        console.text.bind(
            "<KeyRelease>", lambda _=None: recolorize(console.text, lexer)
        )
        console.pack(fill="both", expand=1)
        shell_frame.pack(fill="both", expand=1)
        curr_tab.add(shell_frame, text="Python Shell")

    def lint_source(self) -> None:
        # noinspection PyBroadException
        try:
            if controller := self.text.controller:
                if controller.textbox.lint_cmd:
                    currdir = controller.file_dir
                    if WINDOWS:
                        bat_path = Path(currdir, "lint.bat").resolve()
                        with bat_path.open("w") as f:
                            f.write(
                                LINT_BATCH.format(
                                    cmd=controller.textbox.lint_cmd
                                )
                            )
                        subprocess.call(f'lint.bat "{currdir}"', shell=True)
                        bat_path.unlink()  # Remove the lint.bat file
                    else:
                        sh_path = Path(currdir, "lint.sh").resolve()
                        with sh_path.open("w") as f:
                            f.write(
                                LINT_BATCH.format(
                                    cmd=controller.textbox.lint_cmd
                                )
                            )
                        subprocess.call(
                            f'chmod 700 lint.sh && ./lint.sh "{currdir}"', shell=True
                        )
                        sh_path.unlink()  # Remove the lint.sh file
                    events.emit("editor.open_file", file="results.txt", askhex=False)
                    Path(currdir, "results.txt").unlink()  # Remove the results.txt file
        except Exception:
            logger.exception("Cannot lint the file:")
            ErrorInfoDialog(self.master, "This language is not supported")
            return

    def autopep(self) -> None:
        """Auto Pretty-Format the document"""
        try:
            if controller := self.text.controller:
                currtext = controller.textbox
                currdir = controller.file_dir
                if currtext.format_command:
                    subprocess.Popen(
                        f'{currtext.format_command} "{currdir}" > {os.devnull}', shell=True
                    )  # Throw the autopep8 results into the bit bin.(/dev/null)
                else:
                    ErrorInfoDialog(self.master, "Language not supported.")
                    return
                events.emit("editor.reload")
        except Exception:
            logger.exception("Error when formatting:")
