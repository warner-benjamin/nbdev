# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_processors.ipynb.

# %% auto 0
__all__ = ['strip_ansi', 'meta_', 'show_meta', 'insert_warning', 'remove_', 'hide_line', 'filter_stream_', 'clean_magics',
           'bash_identify', 'rm_header_dash', 'rm_export', 'clean_show_doc']

# %% ../nbs/07_processors.ipynb 3
from .read import *
from .imports import *
from .process import *

from fastcore.imports import *
from fastcore.xtras import *

# %% ../nbs/07_processors.ipynb 6
_re_ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(cell):
    "Strip Ansi Characters."
    for outp in cell.get('outputs', []):
        if outp.get('name')=='stdout': outp['text'] = [_re_ansi_escape.sub('', o) for o in outp.text]

# %% ../nbs/07_processors.ipynb 9
def meta_(nbp, cell, key, *args):
    "Add arbitrary metadata to a cell"
    cell.metadata[key] = args

# %% ../nbs/07_processors.ipynb 10
def show_meta(cell):
    "Show cell metadata"
    if cell.metadata: print(cell.metadata)

# %% ../nbs/07_processors.ipynb 15
def insert_warning(nb):
    "Insert Autogenerated Warning Into Notebook after the first cell."
    content = "<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->"
    nb.cells.insert(1, AttrDict(cell_type='markdown', metadata={}, source=content))

# %% ../nbs/07_processors.ipynb 18
def remove_(nbp, cell, *args):
    for arg in args:
        if arg=='input': cell['source'] = ''
        elif arg=='output': del(cell['outputs'])
        elif arg=='cell': del(cell['source'])
        else: raise NameError(arg)

# %% ../nbs/07_processors.ipynb 20
_re_hideline = re.compile(r'#\|\s*hide_line\s*$', re.MULTILINE)
def hide_line(cell):
    "Hide lines of code in code cells with the directive `hide_line` at the end of a line of code"
    if cell.cell_type == 'code' and _re_hideline.search(cell.source):
        cell.source = '\n'.join([c for c in cell.source.splitlines() if not _re_hideline.search(c)])

# %% ../nbs/07_processors.ipynb 22
def filter_stream_(nbp, cell, *words):
    "Remove output lines containing any of `words` in `cell` stream output"
    if not words: return
    for outp in cell.get('outputs', []):
        if outp.output_type == 'stream':
            outp['text'] = [l for l in outp.text if not re.search('|'.join(words), l)]

# %% ../nbs/07_processors.ipynb 24
_magics_pattern = re.compile(r'^\s*(%%|%).*', re.MULTILINE)

def clean_magics(cell):
    "A preprocessor to remove cell magic commands"
    if cell.cell_type == 'code': cell.source = _magics_pattern.sub('', cell.source).strip()

# %% ../nbs/07_processors.ipynb 26
_bash_pattern = re.compile('^\s*!', flags=re.MULTILINE)

def bash_identify(cell):
    "A preprocessor to identify bash commands and mark them appropriately"
    if cell.cell_type == 'code' and _bash_pattern.search(cell.source):
        cell.metadata.magics_language = 'bash'
        cell['source'] = _bash_pattern.sub('', cell.source).strip()

# %% ../nbs/07_processors.ipynb 29
_re_hdr_dash = re.compile(r'^#+\s+.*\s+-\s*$', re.MULTILINE)

def rm_header_dash(cell):
    "Remove headings that end with a dash -"
    src = cell.source.strip()
    if cell.cell_type == 'markdown' and src.startswith('#') and src.endswith(' -'): del(cell['source'])

# %% ../nbs/07_processors.ipynb 31
def rm_export(cell):
    "Remove cells that are exported or hidden"
    if any(o in cell.directives_ for o in ('export','exporti','hide','default_exp')): del(cell['source'])

# %% ../nbs/07_processors.ipynb 33
_re_showdoc = re.compile(r'^ShowDoc', re.MULTILINE)
def _is_showdoc(cell): return cell['cell_type'] == 'code' and _re_showdoc.search(cell.source)

def clean_show_doc(cell):
    "Remove ShowDoc input cells"
    if not _is_showdoc(cell): return
    cell.source = ''
