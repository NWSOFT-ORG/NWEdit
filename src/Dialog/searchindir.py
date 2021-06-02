from src.Dialog.commondialog import get_theme
from src.functions import darken_color
from src.modules import tk, ttk, ttkthemes
from src.Dialog.search import finditer_withlineno, find_all
import re


class Search:
	def __init__(self, master: tk.Misc, path: str):
		self.master = master
		self.path = path
		self.result = None
		self._style = ttkthemes.ThemedStyle()
		self._style.set_theme(get_theme())
		bg = self._style.lookup("TLabel", "background")
		fg = self._style.lookup("TLabel", "foreground")

		self.search_frame = ttk.Frame(self.text.frame)
		
		# Tkinter Variables
		self.case = tk.BooleanVar()
		self.regex = tk.BooleanVar()
		self.fullword = tk.BooleanVar()

		self.search_frame.pack(anchor="nw", side="bottom")
		ttk.Label(self.search_frame, text="Search: ").pack(side="left",
		                                                   anchor="nw",
		                                                   fill="y")
		self.content = tk.Entry(
		    self.search_frame,
		    background=darken_color(bg, 30, 30, 30),
		    foreground=fg,
		    insertbackground=fg,
		    highlightthickness=0,
		)
		self.content.pack(side="left", fill="both")

		ttk.Label(self.search_frame, text="Replacement: ").pack(side="left",
		                                                        anchor="nw",
		                                                        fill="y")
		self.repl = tk.Entry(
		    self.search_frame,
		    background=darken_color(bg, 30, 30, 30),
		    foreground=fg,
		    insertbackground=fg,
		    highlightthickness=0,
		)
		self.repl.pack(side="left", fill="both")

		self.repl_button = ttk.Button(self.search_frame, text="Replace all")
		self.repl_button.pack(side="left")

        # Checkboxes
		self.case_yn = ttk.Checkbutton(self.search_frame,
		                               text="Case Sensitive",
		                               variable=self.case)
		self.case_yn.pack(side="left")

		self.reg_yn = ttk.Checkbutton(self.search_frame,
		                               text="RegExp",
		                               variable=self.regex)
		self.reg_yn.pack(side="left")

		self.fullw_yn = ttk.Checkbutton(self.search_frame,
		                               text="Full Word",
		                               variable=self.fullword)
		self.fullw_yn.pack(side="left")
		
		for x in (self.case, self.regex, self.fullword):
		    x.trace_add('write', self.find)

		self.repl_button.config(command=self.replace)
		self.content.bind("<KeyRelease>", self.find)
		ttk.Button(self.search_frame, text="x",
		           command=self._exit).pack(side="right")
		
		self.content.insert('end', 'e')
		self.find()

	def re_search(self, pat, text, nocase=False, full_word=False, regex=False):
		if nocase and full_word:
			res = [(x[0], x[1]) for x in finditer_withlineno(
				r"\b" + re.escape(string1) +
				r"\b", string2, (re.IGNORECASE, re.MULTILINE))]
		elif full_word:
			res = [(x[0], x[1]) for x in finditer_withlineno(
				r"\b" + re.escape(string1) + r"\b", string2, re.MULTILINE)]
		elif nocase and regex:
			res = [(x[0], x[1]) for x in finditer_withlineno(
				string1, string2, (re.IGNORECASE, re.MULTILINE))]
		elif regex:
			res = [(x[0], x[1]) for x in finditer_withlineno(
				string1, string2, re.MULTILINE)]
		if nocase:
		    res = [(x[0], x[1]) for x in find_all(pat, text, case=False)]
		else:
			res = [(x[0], x[1]) for x in find_all(pat, text)]
		return res

	def find(self, *_):
		path = self.path
		# FIXME: add something

	def replace(self):
		pass

	def _exit(self):
		self.search_frame.pack_forget()
