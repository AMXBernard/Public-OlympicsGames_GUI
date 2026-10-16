#!/usr/bin/python3.9
# -- encode utf-8 --
"""
OlympicGames v1 alpha - Une étude Python POO sur la gestion des fichiers
CSV des résultats des JO de 1896 à nos jours en mode graphique (TKinter)
avec quelques méthodes de recherche d'évènements, villes, pays, atlètes etc ...
Copyright (C) 2025  Bernard AMOUROUX

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

OlympicGames v1 alpha (C) 2025  Bernard AMOUROUX
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""

__author__ = "Bernard AMOUROUX"
__date__ = "$Date: 2026/02/15 07:00 $"
__copyright__ = "Copyright (c) 2026 Bernard AMOUROUX"
__license__ = "GPL 3"



from configs import *

import tkinter as tk
import tkinter.font as tkFont

from PIL import Image,ImageTk
from hlptools import Help_System
from handle_csv import Handle_CSV,GUI_EditionGame
from gui_tools import Win_MessageBox,PopupMenu,Window_StateBar,Parameters
from linuxprt import Linux_InitPrinters



class Application(tk.Tk):
    
    def __init__(self):

        tk.Tk.__init__(self, className="Application")
        print(f" OlympicGames GUI written with Python 3.9 - Tkinter(),Tcl" \
                    f"v{self.tk.exprstring('$tcl_version')} / {locale.getlocale()}", end=" - ")
        
        self.app_parameters = Saveload_CFG()
        if self.app_parameters.cfg_load():
            self.app_options = self.app_parameters.options
            self.__fullscreen = self.app_options.fullscreen
            backfname = op.join(os.getcwd(),self.app_options.imagepath,self.app_options.backfilename)
            backImage = Image.open(fp=backfname, mode='r')
            width, height = self.app_options.app_size
        else:
            exit(f"Erreur de lecture fichier configuration '{self.app_parameters.options.paramfilename}'")
        #print(f"\nself.app_options: {self.app_options}")    
        # ---------------------------------------------------------------------
        self.MessageBox = Win_MessageBox(self)
        self.Printers = Linux_InitPrinters(self)
        self.help_handler = Help_System(self, self.app_options)
        self.handle_csv = Handle_CSV(self, self.app_options)
        # ---------------------------------------------------------------------
        self.waitnbr = None
        self.time_vltexte = 10000
        self.vl_texte = tk.StringVar(self,' Info : ','!vl_texte')
        # ---------------------------------------------------------------------
        self.menuFont = tkFont.Font(self, family='Serif', size=11, weight='normal', slant='italic')
        self.labelFont = tkFont.Font(self, family='Courier New', size=10, weight='bold', slant='roman')
        # ---------------------------------------------------------------------
        self.protocol('WM_DELETE_WINDOW',self.Quit)
        # ---------------------------------------------------------------------
        self.MAX_WIDTH, self.MAX_HEIGHT = self.maxsize()
        print(f"screen: {self.MAX_WIDTH}, {self.MAX_HEIGHT}")
        self.app_size = (self.MAX_WIDTH-offset_W,self.MAX_HEIGHT-offset_H) \
                                            if self.app_options.app_size==(0,0) else (width, height)
        self.wm_geometry(f"{self.app_size[0]}x{self.app_size[1]}+{(self.MAX_WIDTH-self.app_size[0])//2}+{(self.MAX_HEIGHT-self.app_size[1])//2}")
        # ---------------------------------------------------------------------
        self.backImage = ImageTk.PhotoImage(backImage.resize((int(self.MAX_WIDTH),
                                                int(self.MAX_HEIGHT)), Image.Resampling.LANCZOS), master=self)
        #print(f"app_size: {self.app_options.app_size} -/- self.backImage size: {self.backImage.width()} x {self.backImage.height()}")
        # ---------------------------------------------------------------------
        self.__fullscreen:bool = self.app_options.fullscreen
        self.attributes("-fullscreen", self.__fullscreen)
        # ------------- Création virtual-Event menu contextuel ----------------
        self.event_add("<<PopupMenu>>","<Control-M>","<Control-m>","<Button-3>")
        # ----------------------- EDT main poup menu --------------------------
        commandsList = [(" Paramètres de OGG","Ctrl-M",self.parameters),
                        ("separator","",None),
                        (" Mode plein écran on/off","F11",self.__toggle_fullscreen),
                        ("separator","",None),
                        (" A propos de OGG","",self.fenetre_a_propos),
                        (" Aide de OGG","F1",self.__whole_help),
                        ("separator","",None),
                        (" Quitter OGG "," Alt-F4 ",self.Quit)]
        self.OGGmainMenu = PopupMenu(self, " OlympicGames-GUI  PopupMenu,",commandsList, nosel=[])
        self.bind_class(self, "<<PopupMenu>>", self.OGGmainMenu.show_Menu_Popup)
        # ---------------------------------------------------------------------
        self.columnconfigure(list(range(5)),minsize=80,weight=0)
        self.columnconfigure(list(range(5,20)), weight=1)
        self.rowconfigure(list(range(0, 19)), weight=1)
        self.bind("<Configure>",self.update_idletasks)
        self.bind("<Escape>", self.__exit_fullscreen)
        self.bind("<F11>",self.__toggle_fullscreen)
        self.bind("<F1>",self.__whole_help)
        self.grid_anchor('center')
        self.minsize(1024, 768)
        # ---------------------------------------------------------------------
        self.menu_principal()
        self.creer_widgets()
        self.update()

    def menu_principal(self):
        self.menu=tk.Menu(self, font=self.menuFont)
        self.config(menu=self.menu,pady=5)
        # ---------------------------------------------------------------------
        self.filemenu = tk.Menu(self.menu, tearoff = 0, font=self.menuFont)
        self.menu.add_cascade(label = "Fichier", menu = self.filemenu)
        # ---------------------------------------------------------------------        
        self.loadfiles = tk.Menu(self.filemenu, tearoff = 0, font=self.menuFont)        
        self.filemenu.add_cascade(label=' Charger fichier CSV', menu= self.loadfiles)
        self.loadfiles.add_command(label = " Données des Athlete (BIO)",underline=9,command=lambda mode="Bio":self.load_OGG_File(mode))
        self.loadfiles.add_command(label = " Résultats des épreuves par Athlète",underline=9,command=lambda mode="Spt":self.load_OGG_File(mode))
        self.loadfiles.add_command(label = " Données Epreuves par athlète",underline=9,command=lambda mode="Evt":self.load_OGG_File(mode))
        self.loadfiles.add_separator()
        self.loadfiles.add_command(label = " Données des Olympiades ",underline=13,command=lambda mode="Oly":self.load_OGG_File(mode))
        self.loadfiles.add_command(label = " Médailles par Olympiade",underline=15,command=lambda mode="Mdl":self.load_OGG_File(mode))
        self.loadfiles.add_command(label = " Pays participants/Organisateurs",underline=19,command=lambda mode="Noc":self.load_OGG_File(mode))
        self.loadfiles.add_command(label = " Résultats par Sport/Epreuve",underline=15,command=lambda mode="Res":self.load_OGG_File(mode))
        # ---------------------------------------------------------------------        
        self.filemenu.add_separator()
        self.filemenu.add_command(label = " Paramètres OGG ",underline = 1,command = self.parameters)
        self.filemenu.add_separator()
        self.filemenu.add_command(label = " Quitter",command = self.Quit)
        # ---------------------------------------------------------------------
        self.athlete = tk.Menu(self.menu, tearoff = 0, font=self.menuFont)
        self.menu.add_cascade(label = "Athlètes", menu = self.athlete, state="normal")
        self.athlete.add_command(label = " Afficher tous les athlètes",command=lambda search="global":self.search_athletes(search))
        self.athlete.add_separator()
        self.athlete.add_command(label = " Chercher un athlète par son Nom",command=lambda search="nom":self.search_athletes(search))
        self.athlete.add_command(label = " Chercher un athlète par son Id",command=lambda search="Id":self.search_athletes(search))
        self.athlete.add_separator()
        self.athlete.add_command(label = " Chercher les athlètes d'une Olympiade",command=lambda search="olympiade":self.search_athletes(search))
        self.athlete.add_command(label = " Chercher les athlètes d'un Pays",command=lambda search="pays":self.search_athletes(search))
        self.athlete.add_separator()
        self.athlete.add_command(label = " Recherche multi-critères d'athlètes",command=lambda search="multi":self.search_athletes(search))
        # ---------------------------------------------------------------------
        self.olympic = tk.Menu(self.menu, tearoff = 0, font=self.menuFont)
        self.menu.add_cascade(label = "Olympiades", menu = self.olympic, state="normal")
        self.olympic.add_command(label = " Afficher tous les Sports/épreuves ",command=self.olympic_results)
        self.olympic.add_separator()
        # ---------------------------------------------------------------------
        self.helpmenu = tk.Menu(self.menu, tearoff = 0, font=self.menuFont)
        self.menu.add_cascade(label = "Aide", menu = self.helpmenu)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label = " Aide global", command = self.__whole_help)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label = "À propos", command = self.fenetre_a_propos)
        self.update()

    def creer_widgets(self):
        # ----- Création du tk.Canvas() pour affichage de l'image de fond -----
        self.background = tk.Canvas(self, bd=3, relief='ridge', bg='light blue', name="!backgroundCanvas")
        self.back_image = self.background.create_image(0,0, image=self.backImage, 
                                                    state="normal",anchor="center",tags='img_background')
        self.background.grid(columnspan=20, rowspan=19, sticky='nsew')
        # ----------------- Création des listes evenements JO -----------------
        edition_game:EditionGame = GUI_EditionGame(self, self.handle_csv.edition,col=0,row=0,bg="",cspan=20,rspan=19,pad=(10,10,0,0))
        # ---------- Création de la barre d'état avec message d'info ----------
        msg = """ Info : [Clic Gauche] pour sélection une Olympiade et visualiser ses infos - [Clic Droit] Menu contextuel (application)"""
        self.barre_Etat = Window_StateBar(self,"",0,col=0,row=20,cspan=19,bg='tan',pady=5,defMessage=msg,sticky="nsew")    
        # ------------- Création Bouton Quitter sur barre d'état --------------
        tk.Button(self,bg="#EBB34B",text="Quitter",command=self.Quit).grid(row=20,column=19,padx=2,pady=2,sticky="nsew")
        # ----------------- Affichage fenètre 'A propos' ----------------------
        if self.app_options.splashscreen: self.fenetre_a_propos()

    def search_athletes(self, search:SEARCHTYPE="global"):
        from handle_csv import GUI_SearchAthlete
        searchAthlete = GUI_SearchAthlete(self, self.handle_csv, searchtype=search)
        
    def olympic_results(self, mode:CMODETYPE="Ath"):
        from handle_csv import GUI_SearchSportEvt
        searchSportEvent = GUI_SearchSportEvt(self, self.handle_csv, mode=mode)
        
    def load_OGG_File(self, mode:CMODETYPE):
        self.handle_csv.load_OGG_File(mode=mode)
    
    def parameters(self):
        options = Parameters(self, self.app_options).go()
        if options != None: 
            self.app_options = options

    def __whole_help(self, event:tk.Event=None):
        self.help_handler.show_whole_help()
            
    def __toggle_fullscreen(self, event:tk.Event=None):
        self.__fullscreen = not self.__fullscreen
        self.attributes("-fullscreen",self.__fullscreen)
    
    def __exit_fullscreen(self, event:tk.Event=None):
        self.__fullscreen = False
        self.attributes("-fullscreen", self.__fullscreen)

    def _save_CFG(self):
        self.app_parameters.options = self.app_options
        if self.app_parameters.cfg_backup():
            self.barre_Etat.update_vltexte(" Info : Sauvegarde de la configuration.")
            print(" ---> Config sauvée OK")
        else:
            self.barre_Etat.update_vltexte(" Info : ERREUR - Configuration non sauvegardée")
            print(" ---> Config NON sauvée")
    
    def update_idletasks(self, event:tk.Event=None) -> None:
        width, height = self.geometry().split('+')[0].split('x')
        self.app_options.app_size = (int(width), int(height))
        try:
            self.nametowidget(".!backgroundCanvas")
            if event and event.widget == self.background:
                self.background.coords(self.back_image, event.width//2, event.height//2)
        except KeyError:
            super().update_idletasks()
    
    def fenetre_a_propos(self):
        """ Fenêtre-message à propos.
            Indique le nom de l'auteurs ainsi que la licence.
        """
        message = "OlympicGames v1 Beta"+"\n\nCopyright (C) 2026\nBernard Amouroux\n" \
        "\nDonnées : https://www.kaggle.com/datasets/josephcheng123456/olympic-historical-dataset-from-olympediaorg\n" \
        "http://www.olympedia.org/\n" \
        "\n\nConnaissances : Université de Toulouse - Master BBS\nBioinformatique et Biologie des Systèmes\n" \
        "https://www.univ-tlse3.fr/decouvrir-nos-diplomes/\nmaster-mention-bio-informatique\n" \
        "\nLicense : GPL Version 3, 29 June 2007"
        self.MessageBox.textfont('Times 15 normal roman')
        self.MessageBox.boxtitle('À propos')
        self.MessageBox.message = message
    
    def do_nothing(self):
        self.barre_Etat.update_vltexte(msg=" Info : Partie de l'application en cours de développement...")
    
    def Quit(self):
        #print(f"Save CFG on quit: {self.app_options.saveCFGonquit}")
        # --------------- Sauvegarde des paramètres de OlympicGames -----------
        if self.app_options.saveCFGonquit:
            self._save_CFG()
            self.after(500)
        # ---------------------------------------------------------------------
        self.quit()

if __name__ == "__main__":
    
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except Exception as msg:
        print(f"Locale message: {msg}")        
        
    app = Application()
    app.title("OlympicGames GUI utility V1")
    icon = tk.PhotoImage(master=app, file=op.join(IMAGE_PATH,'olympicgames_ico.gif'))
    app.wm_iconphoto(True, icon)
    app.mainloop()
