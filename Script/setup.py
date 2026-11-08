#!/usr/bin/python3
# coding: utf-8
# commande à taper en ligne de commande après la sauvegarde de ce fichier:
# python setup.py build
import os,sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
#-----------------------------------------------------------------------------
# Linux: Définir les chemins vers Tcl/Tk sans environnement particulier
#tcl_dir = '/usr/share/tcltk/tcl8.6'
#tk_dir = '/usr/share/tcltk/tk8.6'
# -----------------------------------------------------------------------------
# Linux: Définir les chemins vers Tcl/Tk avec un environnement Conda
CONDA_PREFIX = os.environ.get('CONDA_PREFIX', sys.prefix)
tcl_dir = os.path.join(CONDA_PREFIX,'lib','tcl8.6')
tk_dir = os.path.join(CONDA_PREFIX,'lib','tk8.6')
# -----------------------------------------------------------------------------
# Ajouter les variables d'environnement dans l'exécutable
os.environ['TCL_LIBRARY'] = tcl_dir
os.environ['TK_LIBRARY'] = tk_dir

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
                         "packages":['tkinter','athlete','country','hlptools','gui_tools','handle_csv',
                                          'tokyotweats','linuxprt','medailles','resultats','sport','configs'],
                         "include_files":[(tcl_dir,'lib/tcl8.6'),(tk_dir,'lib/tk8.6'),"../Data","../Image",
                                          "../OlympicData","../README.md","../LICENSE","../CasDEtude-JO.pdf"],
                         "excludes": ["PyQt6","PySide6","setup.py",
                                        'OlympicsGames_GUI.code-workspace','olympic_games_GUI.py',]
                     }

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Projet OlympicGames GUIv2.5",
    version = "2.5.0",
    description = "Interface graphique pour interroger les bases des JO en local.",
    options = {"build_exe": build_exe_options},
    executables = [Executable(  script = "olympic_games_GUI.py",
                                icon = "../Image/olympicgames_ico.gif",
                                copyright = "(c) AMOUROUX Bernard 10/2026",
                                shortcut_name = "../OlympicGames-GUI_v2",
                                shortcut_dir = "/usr/share/applications",
                                target_name = "OlympicGamesGUI-v2",
                                base = base)]
      )
