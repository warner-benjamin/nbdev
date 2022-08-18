# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/13_quarto.ipynb.

# %% ../nbs/13_quarto.ipynb 2
from __future__ import annotations
import warnings

from .config import *
from .doclinks import *

from fastcore.utils import *
from fastcore.script import call_parse
from fastcore.shutil import rmtree,move

from os import system
import subprocess,sys,shutil,ast

# %% auto 0
__all__ = ['BASE_QUARTO_URL', 'install_quarto', 'install', 'nbdev_sidebar', 'nbdev_readme', 'refresh_quarto_yml', 'nbdev_quarto',
           'preview', 'deploy']

# %% ../nbs/13_quarto.ipynb 5
_def_file_re = '\.(?:ipynb|qmd|html)$'

def _sprun(cmd):
    try: subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as cpe: sys.exit(cpe.returncode)

# %% ../nbs/13_quarto.ipynb 6
BASE_QUARTO_URL='https://www.quarto.org/download/latest/'

def _install_linux():
    system(f'curl -LO {BASE_QUARTO_URL}quarto-linux-amd64.deb')
    system('sudo dpkg -i *64.deb && rm *64.deb')
    
def _install_mac():
    system(f'curl -LO {BASE_QUARTO_URL}quarto-macos.pkg')
    system('sudo installer -pkg quarto-macos.pkg -target /')

@call_parse
def install_quarto():
    "Install latest Quarto on macOS or Linux, prints instructions for Windows"
    if sys.platform not in ('darwin','linux'):
        return print('Please visit https://quarto.org/docs/get-started/ to install quarto')
    print("Installing or upgrading quarto -- this requires root access.")
    system('sudo touch .installing')
    try:
        installing = Path('.installing')
        if not installing.exists(): return print("Cancelled. Please download and install Quarto from quarto.org.")
        if 'darwin' in sys.platform: _install_mac()
        elif 'linux' in sys.platform: _install_linux()
    finally: system('sudo rm -f .installing')

# %% ../nbs/13_quarto.ipynb 7
@call_parse
def install():
    "Install Quarto and the current library"
    install_quarto.__wrapped__()
    d = get_config().path('lib_path')
    if (d/'__init__.py').exists(): system(f'pip install -e "{d.parent}[dev]"')

# %% ../nbs/13_quarto.ipynb 8
def _doc_paths(path:str=None, doc_path:str=None):
    cfg = get_config()
    cfg_path = cfg.config_path
    path = cfg.path('nbs_path') if not path else Path(path)
    doc_path = cfg.path('doc_path') if not doc_path else Path(doc_path)
    tmp_doc_path = path/f"{cfg['doc_path']}"
    return cfg,cfg_path,path,doc_path,tmp_doc_path

# %% ../nbs/13_quarto.ipynb 9
def _f(a,b): return Path(a),b
def _pre(p,b=True): return '    ' * (len(p.parts)) + ('- ' if b else '  ')
def _sort(a):
    x,y = a
    if y.startswith('index.'): return x,'00'
    return a

# %% ../nbs/13_quarto.ipynb 10
@call_parse
def nbdev_sidebar(
    path:str=None, # Path to notebooks
    symlinks:bool=False, # Follow symlinks?
    file_glob:str=None, # Only include files matching glob
    file_re:str=_def_file_re, # Only include files matching regex
    folder_re:str=None, # Only enter folders matching regex
    skip_file_glob:str=None, # Skip files matching glob
    skip_file_re:str='^[_.]', # Skip files matching regex
    skip_folder_re:str='(?:^[_.]|^www$)', # Skip folders matching regex
    printit:bool=False,  # Print YAML for debugging
    force:bool=False,  # Create sidebar even if settings.ini custom_sidebar=False
    returnit:bool=False  # Return list of files found
):
    "Create sidebar.yml"
    if not force and str2bool(get_config().custom_sidebar): return
    path = get_config().path('nbs_path') if not path else Path(path)
    files = nbglob(path, func=_f, symlinks=symlinks, file_re=file_re, folder_re=folder_re, file_glob=file_glob,
                   skip_file_glob=skip_file_glob, skip_file_re=skip_file_re, skip_folder_re=skip_folder_re).sorted(key=_sort)
    lastd,res = Path(),[]
    for d,name in files:
        d = d.relative_to(path)
        if d != lastd:
            res.append(_pre(d.parent) + f'section: {d.name}')
            res.append(_pre(d.parent, False) + 'contents:')
            lastd = d
        res.append(f'{_pre(d)}{d.joinpath(name)}')

    yml_path = path/'sidebar.yml'
    yml = "website:\n  sidebar:\n    contents:\n"
    yml += '\n'.join(f'      {o}' for o in res)
    if printit: return print(yml)
    yml_path.write_text(yml)
    if returnit: return files

# %% ../nbs/13_quarto.ipynb 12
def _render_readme(path):
    idx_path = path/get_config().readme_nb
    if not idx_path.exists(): return

    yml_path = path/'sidebar.yml'
    moved=False
    if yml_path.exists():
        # move out of the way to avoid rendering whole website
        yml_path.rename(path/'sidebar.yml.bak')
        moved=True
    try:
        _sprun(f'cd "{path}" && quarto render "{idx_path}" -o README.md -t gfm --no-execute')
    finally:
        if moved: (path/'sidebar.yml.bak').rename(yml_path)

# %% ../nbs/13_quarto.ipynb 13
@call_parse
def nbdev_readme(
    path:str=None, # Path to notebooks
    doc_path:str=None): # Path to output docs
    "Render README.md from index.ipynb"
    cfg,cfg_path,path,doc_path,tmp_doc_path = _doc_paths(path, doc_path)
    _render_readme(path)
    if (tmp_doc_path/'README.md').exists():
        _rdm = cfg_path/'README.md'
        if _rdm.exists(): _rdm.unlink() # py37 doesn't have arg missing_ok so have to check first
        move(str(tmp_doc_path/'README.md'), cfg_path) # README.md is temporarily in nbs/_docs

# %% ../nbs/13_quarto.ipynb 14
def _ensure_quarto():
    if shutil.which('quarto'): return
    print("Quarto is not installed. We will download and install it for you.")
    install.__wrapped__()

# %% ../nbs/13_quarto.ipynb 15
_quarto_yml="""ipynb-filters: [nbdev_filter]

project:
  type: website
  output-dir: {doc_path}
  preview:
    port: 3000
    browser: false

format:
  html:
    theme: cosmo
    css: styles.css
    toc: true
    toc-depth: 4

website:
  title: "{title}"
  site-url: "{doc_host}{doc_baseurl}"
  description: "{description}"
  twitter-card: true
  open-graph: true
  reader-mode: true
  repo-branch: {branch}
  repo-url: "{git_url}"
  repo-actions: [issue]
  navbar:
    background: primary
    search: true
    right:
      - icon: github
        href: "{git_url}"
  sidebar:
    style: "floating"

metadata-files: 
  - sidebar.yml
  - custom.yml
"""

# %% ../nbs/13_quarto.ipynb 16
def refresh_quarto_yml():
    "Generate `_quarto.yml` from `settings.ini`."
    cfg = get_config()
    p = cfg.path('nbs_path')/'_quarto.yml'
    vals = {k:cfg.get(k) for k in ['doc_path', 'title', 'description', 'branch', 'git_url', 'doc_host', 'doc_baseurl']}
    # Do not build _quarto_yml if custom_quarto_yml is set to True
    if str2bool(get_config().custom_quarto_yml): return
    if 'title' not in vals: vals['title'] = vals['lib_name']
    yml=_quarto_yml.format(**vals)
    p.write_text(yml)

# %% ../nbs/13_quarto.ipynb 17
def _is_qpy(path:Path):
    "Is `path` a py script starting with frontmatter?"
    path = Path(path)
    if not path.suffix=='.py': return
    try: p = ast.parse(path.read_text())
    except: return
    if not p.body: return
    a = p.body[0]
    if isinstance(a, ast.Expr) and isinstance(a.value, ast.Constant):
        v = a.value.value.strip().splitlines()
        return v[0]=='---' and v[-1]=='---'

# %% ../nbs/13_quarto.ipynb 18
def _exec_py(fname):
    "Exec a python script and warn on error"
    try: subprocess.check_output('python ' + fname, shell=True)
    except subprocess.CalledProcessError as cpe: warn(str(cpe))

# %% ../nbs/13_quarto.ipynb 19
@call_parse
def nbdev_quarto(
    path:str=None, # Path to notebooks
    doc_path:str=None, # Path to output docs
    symlinks:bool=False, # Follow symlinks?
    file_re:str=_def_file_re, # Only include files matching regex
    folder_re:str=None, # Only enter folders matching regex
    skip_file_glob:str=None, # Skip files matching glob
    skip_file_re:str=None, # Skip files matching regex
    preview:bool=False, # Preview the site instead of building it
    port:int=3000 # The port on which to run preview
):
    "Create Quarto docs and README.md"
    _ensure_quarto()
    cfg,cfg_path,path,doc_path,tmp_doc_path = _doc_paths(path, doc_path)
    refresh_quarto_yml()
    nbdev_sidebar.__wrapped__(path, symlinks=symlinks, file_re=file_re, folder_re=folder_re,
                              skip_file_glob=skip_file_glob, skip_file_re=skip_file_re)
    pys = globtastic(path, file_glob='*.py', symlinks=symlinks, folder_re=folder_re, skip_folder_re='^[_.]',
                     skip_file_glob=skip_file_glob, skip_file_re=skip_file_re).filter(_is_qpy)
    for py in pys: _exec_py(py)
    if preview: os.system(f'cd "{path}" && quarto preview --port {port}')
    else: _sprun(f'cd "{path}" && quarto render')
    if not preview:
        nbdev_readme.__wrapped__(path, doc_path)
        if tmp_doc_path.parent != cfg_path: # move docs folder to root of repo if it doesn't exist there
            rmtree(doc_path, ignore_errors=True)
            move(tmp_doc_path, cfg_path)

# %% ../nbs/13_quarto.ipynb 20
@call_parse
def preview(
    path:str=None, # Path to notebooks
    doc_path:str=None, # Path to output docs
    symlinks:bool=False, # Follow symlinks?
    file_re:str=_def_file_re, # Only include files matching regex
    folder_re:str=None, # Only enter folders matching regex
    skip_file_glob:str=None, # Skip files matching glob
    skip_file_re:str=None, # Skip files matching regex
    port:int=3000 # The port on which to run preview
):
    "Preview docs locally"
    nbdev_quarto.__wrapped__(path, doc_path=doc_path, symlinks=symlinks, file_re=file_re, folder_re=folder_re,
                             skip_file_glob=skip_file_glob, skip_file_re=skip_file_re, preview=True, port=port)

# %% ../nbs/13_quarto.ipynb 21
@call_parse
def deploy(
    path:str=None, # Path to notebooks
    doc_path:str=None, # Path to output docs
    skip_build:bool=False,  # Don't build docs first
    symlinks:bool=False, # Follow symlinks?
    file_re:str=_def_file_re, # Only include files matching regex
    folder_re:str=None, # Only enter folders matching regex
    skip_file_glob:str=None, # Skip files matching glob
    skip_file_re:str=None, # Skip files matching regex
):
    "Deploy docs to GitHub Pages"
    if not skip_build:
        nbdev_quarto.__wrapped__(path, doc_path=doc_path, symlinks=symlinks, file_re=file_re, folder_re=folder_re,
                                 skip_file_glob=skip_file_glob, skip_file_re=skip_file_re)
    try: from ghp_import import ghp_import
    except: return warnings.warn('Please install ghp-import with `pip install ghp-import`')
    ghp_import(get_config().path('doc_path'), push=True, stderr=True, no_history=True)
