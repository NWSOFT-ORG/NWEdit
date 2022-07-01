from src.constants import APPDIR, LINT_BATCH, RUN_BATCH, WINDOWS, logger
from src.Dialog.codelistdialog import CodeListDialog
from src.Dialog.commondialog import ErrorInfoDialog
from src.Dialog.search import Search
from src.highlighter import create_tags, recolorize
from src.modules import Path, lexers, os, subprocess, tk, ttk
from src.Utils.functions import open_shell, shell_command
from src.Utils.images import get_image
from src.Widgets.console import Console
from src.Widgets.customenotebook import ClosableNotebook


class CodeFunctions:
    def __init__(
        self,
        master: tk.Misc,
        tabs: dict,
        nb: ClosableNotebook,
        bottomframe: ttk.Notebook,
    ) -> None:
        self.nb = nb
        self.tabs = tabs
        self.master = master
        self.bottomframe = bottomframe

        self.style = ttk.Style(master)
        self.bg = self.style.lookup("TLabel", "background")
        self.fg = self.style.lookup("TLabel", "foreground")

    def code_struct(self) -> None:
        text = self.tabs[self.nb.get_tab].textbox
        CodeListDialog(self.bottomframe, text)

    def search(self, _=None) -> None:
        bottomframe = self.bottomframe
        Search(bottomframe, self.tabs[self.nb.get_tab].textbox)

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
                                file=self.tabs[self.nb.get_tab].file_dir,
                                cmd=self.tabs[self.nb.get_tab].textbox.cmd,
                            )
                        )
                    )
                shell_command("run.bat && del run.bat && exit", cwd=APPDIR)
            else:  # Others
                with open(APPDIR + "/run.sh", "w") as f:
                    f.write(
                        (
                            RUN_BATCH.format(
                                dir=APPDIR,
                                file=self.tabs[self.nb.get_tab].file_dir,
                                cmd=self.tabs[self.nb.get_tab].textbox.cmd,
                                script_dir=Path(
                                    self.tabs[self.nb.get_tab].file_dir
                                ).parent,
                            )
                        )
                    )
                shell_command("chmod 700 run.sh && ./run.sh && rm run.sh", cwd=APPDIR)
        except Exception as e:
            ErrorInfoDialog(self.master, "This language is not supported.")

    @staticmethod
    def system_shell() -> None:
        open_shell()

    def python_shell(self) -> None:
        curr_tab = self.bottomframe
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
        shell_frame.pack(fill="both", expand=1)
        curr_tab.add(shell_frame, text="Python Shell")

    def lint_source(self) -> None:
        if not self.tabs:
            return
        try:
            if self.tabs[self.nb.get_tab].textbox.lint_cmd:
                currdir = self.tabs[self.nb.get_tab].file_dir
                if WINDOWS:
                    with open("lint.bat", "w") as f:
                        f.write(
                            LINT_BATCH.format(
                                cmd=self.tabs[self.nb.get_tab].textbox.lint_cmd
                            )
                        )
                    subprocess.call(f'lint.bat "{currdir}"', shell=True)
                    os.remove("lint.bat")
                else:
                    with open("lint.sh", "w") as f:
                        f.write(
                            LINT_BATCH.format(
                                cmd=self.tabs[self.nb.get_tab].textbox.lint_cmd
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
            currtext = self.tabs[self.nb.get_tab].textbox
            currdir = self.tabs[self.nb.get_tab].file_dir
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
