from src.modules import ttk
import ast
import traceback


class CodeListDialog(ttk.Frame):
    def __init__(self, parent=None, text=None, file=None):
        super().__init__(parent)
        self.file = file
        self.text = text

        self.state_label = ttk.Label(self, text='')
        self.state_label.pack(anchor='nw', fill='x')
        self.tree = ttk.Treeview(self, show='tree')
        self.tree.bind('<Double-1>', self.double_click)
        self.tree.pack(fill='both', expand=1)

        self.show_items()
        self.pack(fill='both', expand=1)
        parent.forget(parent.panes()[0])
        parent.insert('0', self)
    
    def show_items(self):
        filename = self.file
        with open(filename) as f:
            try:
                node = ast.parse(f.read())
            except Exception:
                self.state_label.configure(text=f'Error: Cannot parse docoment.\n {traceback.format_exc()}',
                                           foreground='red')
                return

        functions = [_obj for _obj in node.body if isinstance(_obj, ast.FunctionDef)]
        classes = [_obj for _obj in node.body if isinstance(_obj, ast.ClassDef)]
        defined_vars = [_obj for _obj in node.body if isinstance(_obj, ast.Assign)]


        for function in functions:
            self.show_info("", function, 'func')

        for class_ in classes:
            parent = self.show_info("", class_, 'class')
            methods = [_obj for _obj in class_.body if isinstance(_obj, ast.FunctionDef)]
            defined_vars = [_obj.targets for _obj in class_.body if isinstance(_obj, ast.Assign)]
            for method in methods:
                self.show_info(parent, method, 'func')
            
            for var in defined_vars:
                self.show_var(parent, var)
        
        for var in defined_vars:
            self.show_var("", var)
    
    def show_info(self, parent, _obj, _type=''):
        return self.tree.insert(parent,
                                "end", text=f"{_obj.name} [{_obj.lineno}:{_obj.col_offset}]",
                                tags=[_type])
    
    def show_var(self, parent,  _obj):
        for item in _obj.targets:
            self.tree.insert(parent, 'end',
                             text=f'{item.id} [{item.lineno}:{item.col_offset}]')
    
    def double_click(self, _=None):
        try:
            item = self.tree.focus()
            text = self.tree.item(item, 'text')
            index = text.split(' ')[-1][1:-1]
            line = index.split(':')[0]
            col = index.split(':')[1]
            self.text.mark_set('insert', f"{line}.{col}")
            self.text.see('insert')
            self.text.focus_set()

        except IndexError:  # Click on empty places
            pass