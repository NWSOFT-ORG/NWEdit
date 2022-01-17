from src.modules import (tk, ttk, ttkthemes, os, subprocess, lexers, Path)
from src.functions import (is_dark_color, run_in_terminal, open_system_shell)
from src.Dialog.commondialog import (get_theme, ErrorInfoDialog)
from src.Dialog.search import Search
from src.Widgets.console import Console
from src.constants import (WINDOWS, logger, APPDIR, LINT_BATCH, RUN_BATCH)
from src.highlighter import (recolorize, create_tags)


class CodeFunctions:
    def __init__(self, master, tabs, nb):
        self.nb = nb
        self.tabs = tabs
        self.master = master

        self.style = ttkthemes.ThemedStyle()
        self.style.set_theme(get_theme())
        self.bg = self.style.lookup("TLabel", "background")
        self.fg = self.style.lookup("TLabel", "foreground")
        if is_dark_color(self.bg):
            self.lint_icon = tk.PhotoImage(file="Images/lint-light.gif")
            self.search_icon = tk.PhotoImage(file="Images/search-light.gif")
            self.pyterm_icon = tk.PhotoImage(file="Images/py-term-light.gif")
            self.term_icon = tk.PhotoImage(file="Images/term-light.gif")
            self.format_icon = tk.PhotoImage(file="Images/format-light.gif")
        else:
            self.lint_icon = tk.PhotoImage(file="Images/lint.gif")
            self.search_icon = tk.PhotoImage(file="Images/search.gif")
            self.pyterm_icon = tk.PhotoImage(file="Images/py-term.gif")
            self.term_icon = tk.PhotoImage(file="Images/term.gif")
            self.format_icon = tk.PhotoImage(file="Images/format.gif")
        self.run_icon = tk.PhotoImage(file="Images/run-16px.gif")

    def create_menu(self, master):
        codemenu = tk.Menu(master)
        codemenu.add_command(
            label="Run",
            command=self.run,
            image=self.run_icon,
            compound='left'
        )
        codemenu.add_command(
            label="Lint",
            command=self.lint_source,
            image=self.lint_icon,
            compound='left'
        )
        codemenu.add_command(
            label="Auto-format",
            command=self.autopep,
            image=self.format_icon,
            compound='left'
        )
        codemenu.add_command(
            label="Open System Shell",
            command=self.system_shell,
            image=self.term_icon,
            compound='left'
        )
        codemenu.add_command(
            label="Python Shell",
            command=self.python_shell,
            image=self.pyterm_icon,
            compound='left'
        )
        codemenu.add_command(
            label="Find and replace",
            command=self.search,
            image=self.search_icon,
            compound='left'
        )
        return codemenu
    
    def search(self, _=None) -> None:
        Search(self.master, self.tabs[self.nb.get_tab()].textbox)

    def run(self, _=None) -> None:
        """Runs the file
        Steps:
        1) Writes run code into the batch file.
        2) Linux only: uses chmod to make the sh execuable
        3) Runs the run file"""
        try:
            if WINDOWS:  # Windows
                with open(APPDIR + "/run.bat", "w") as f:
                    f.write(
                        (
                            RUN_BATCH.format(
                                dir=APPDIR,
                                file=self.tabs[self.nb.get_tab()].file_dir,
                                cmd=self.tabs[self.nb.get_tab()].textbox.cmd,
                            )
                        )
                    )
                run_in_terminal("run.bat && del run.bat && exit", cwd=APPDIR)
            else:  # Others
                with open(APPDIR + "/run.sh", "w") as f:
                    f.write(
                        (
                            RUN_BATCH.format(
                                dir=APPDIR,
                                file=self.tabs[self.nb.get_tab()].file_dir,
                                cmd=self.tabs[self.nb.get_tab()].textbox.cmd,
                                script_dir=Path(
                                    self.tabs[self.nb.get_tab()].file_dir
                                ).parent,
                            )
                        )
                    )
                run_in_terminal("chmod 700 run.sh && ./run.sh && rm run.sh", cwd=APPDIR)
        except Exception:
            ErrorInfoDialog(self.master, "This language is not supported.")

    @staticmethod
    def system_shell() -> None:
        open_system_shell()

    def python_shell(self) -> None:
        curr_tab = self.tabs[self.nb.get_tab()].textbox.panedwin
        shell_frame = ttk.Frame(curr_tab)
        main_window = Console(shell_frame, None, shell_frame.destroy)
        main_window.text.lexer = lexers.get_lexer_by_name("pycon")
        main_window.text.focus_set()
        create_tags(main_window.text)
        recolorize(main_window.text)
        main_window.text.bind(
            "<KeyRelease>", lambda _=None: recolorize(main_window.text)
        )
        main_window.pack(fill="both", expand=1)
        shell_frame.pack(fill='both', expand=1)
        curr_tab.add(shell_frame)

    def lint_source(self) -> None:
        if not self.tabs:
            return
        try:
            if self.tabs[self.nb.get_tab()].textbox.lint_cmd:
                currdir = self.tabs[self.nb.get_tab()].file_dir
                if WINDOWS:
                    with open("lint.bat", "w") as f:
                        f.write(
                            LINT_BATCH.format(
                                cmd=self.tabs[self.nb.get_tab()].textbox.lint_cmd
                            )
                        )
                    subprocess.call(f'lint.bat "{currdir}"', shell=True)
                    os.remove("lint.bat")
                else:
                    with open("lint.sh", "w") as f:
                        f.write(
                            LINT_BATCH.format(
                                cmd=self.tabs[self.nb.get_tab()].textbox.lint_cmd
                            )
                        )
                    subprocess.call(
                        f'chmod 700 lint.sh && ./lint.sh "{currdir}"', shell=True
                    )
                    os.remove("lint.sh")
                self.open_file("results.txt")
                os.remove("results.txt")
        except Exception:
            ErrorInfoDialog(self.master, "This language is not supported")
            return

    def autopep(self) -> None:
        """Auto Pretty-Format the document"""
        try:
            currtext = self.tabs[self.nb.get_tab()].textbox
            currdir = self.tabs[self.nb.get_tab()].file_dir
            if currtext.format_command:
                subprocess.Popen(
                    f'{currtext.format_command} "{currdir}" > {os.devnull}', shell=True
                )  # Throw the autopep8 results into the bit bin.(/dev/null)
            else:
                ErrorInfoDialog(self.master, "Language not supported.")
                return
            self.reload()
        except Exception:
            logger.exception("Error when formatting:")
