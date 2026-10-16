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
from gui_tools import My_LabelFrame,ScrolledListbox,Win_MessageBox

import tkinter as tk        
import tkinter.font as tkFont


class Linux_InitPrinters():


    def __init__(self, master=None):

        self.master = master
        self.list_prt = list()

        self.conn = cups.Connection()        
        self.dico_printers = self.conn.getPrinters()
        self.default_printer = self.conn.getDefault()
        self.active_printer = self.default_printer
        # ----------- Création du dictionnaires de toutes les imprimantes du système -----------
        for key in self.dico_printers.keys():
            values = self.dico_printers.get(key)
            name_prt = key
            name_model = values['printer-make-and-model']
            name_uri = values['device-uri']
            prt_string = f"{name_prt[:36]:<36} {name_model[:64]:<64} {name_uri[:30]:<30}"
            self.list_prt.append(prt_string)

    def print_file(self, fname=None):
        pass


class ShowPrinters(tk.Toplevel):

    def __init__(self, master=None, parent=None, printers:dict=({}), *args, **kwargs):

        self.master = master
        self.parent = parent
        self.listPrinters = list(printers.keys())

        self.vselected = tk.StringVar(None,'','!vselected')
        self.vactive = tk.StringVar(value=parent.active_printer,name='!vactive')
        self.vdefault = tk.StringVar(value=parent.default_printer,name='!vdefault')
        self.vprtlist = tk.StringVar(None,['Liste des imprimantes du système',],'!vprtlist')
        
        self.C_ACTIVE,self.C_DEFAULT,self.C_NORMAL = 'thistle2','light goldenrod','ivory1'

        tab_options:dict = {'bd':3,'bg':'wheat','relief':'ridge','name':'!showPrinters_Win'}
        for key in list(tab_options.keys()):            # -- On remplace les options définies par défaut de l'objet bouton.
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)

        super().__init__(master, *args, **kwargs)
        # --------------------------------------------------------------------------------------
        self.tle_font = tkFont.Font(family='Courier New', size=14, weight='bold', slant='italic')
        self.lbx_font = tkFont.Font(family='Courier', size=11, weight='bold', slant='roman')
        self.lbl_font = tkFont.Font(family='Verdana', size=11, weight='normal', slant='italic')
        # --------------------------------------------------------------------------------------
        self.title("Fenêtre de choix de l'imprimante à utiliser")
        self.minsize(int(master.winfo_width()*0.8), int(master.winfo_height()*0.4))
        self.columnconfigure(list(range(8)), weight=1)
        self.rowconfigure(list(range(1,5)), weight=1)
        self.resizable(width= True, height= False)
        # -------- Interception de la fermeture de la fenetre à la croix (rouge) système -------      
        self.protocol('WM_DELETE_WINDOW', self.Quit)    
        # --------------------------------------------------------------------------------------
        self.event_add("<<SelectedPrinter>>","<Double-Button-1>","<Return>")
        # --------------------------------------------------------------------------------------
        self.cree_widgets()

    def cree_widgets(self):
        nprt="Nom de l'Imprimante"; pprt='Classe - Driver - Serveur'; jprt='Socket'
        lboxTitle = f"{nprt:^30}{pprt:^160}{jprt:^30}"
        lframe = My_LabelFrame(self,bg='khaki',font=self.tle_font,cspan=8,row=0,pad=(2,2,0,0),
                                 rspan=6,text=' Liste des imprimantes du Système ',sticky='nsew')
        tk.Label(lframe,bg='khaki',font=('Courier\ New 12 bold italic underline'),
            text='Imprimante par défaut :').grid(column=0,row=0,columnspan=2,pady=5,sticky='new')
        frame1 = My_LabelFrame(lframe, col=2,row=0,bg="orange",pad=(2,5,0,0),sticky="new",
                                                        cspan=6,name='!frame1_defaultprinter')
        tk.Label(frame1,textvariable=self.vdefault,bg='ivory1',anchor="center",
                           font=self.lbl_font).grid(column=0,row=0,columnspan=6,sticky='new')
        # --------------------------------------------------------------------------------------        
        self.vprtlist.set(self.parent.list_prt)
        self.my_LboxPrt = ScrolledListbox(lframe,self.vprtlist,row=1,cspan=8,rspan=4,fbg='#FDEFDD',
                        ftext=lboxTitle,pad=(2,2,2,2),ffont=('Ubuntu 12 italic'),name='!my_listboxPrt',
                        vbar=False,bg='ivory1',selectforeground='black',selectbackground='tan')
        self.bind_class(self.my_LboxPrt, "<<SelectedPrinter>>", self._selectActive)
        # --------------------------------------------------------------------------------------        
        frame2 = My_LabelFrame(lframe, col=0,row=5,bg="#F6FCD5",pad=(2,5,0,0),
                                                          cspan=8,name='!frame2_Zone3boutons',sticky="new")
        tk.Button(frame2,text="Définir par défaut",bg='navajo white',highlightbackground='chocolate1',
                font=self.lbl_font,width=16,command=self._selectDefault).grid(column=0,row=0,sticky='nw')
        tk.Button(frame2,text="Définir Active",bg='navajo white',activebackground='chocolate1',width=16,
                         font=self.lbl_font, command=self._selectActive).grid(column=3,row=0,sticky='n')
        tk.Button(frame2,text="Quitter",bg='navajo white',activebackground='red',width=16,state="active",
                                   font=self.lbl_font, command=self.Quit).grid(column=6,row=0,sticky='ne')
        # ----- Mise à jour des couleurs de l'imprimante par défaut et l'imprimante active -----
        for svar, color in [(self.vactive,self.C_ACTIVE), (self.vdefault,self.C_DEFAULT)]:
            [self.my_LboxPrt.itemconfig(i,background=color) for i,item in enumerate(self.listPrinters) if svar.get() in item]
        self.focus_force()
        
    def __colorDefault(self):
        idx = [idx for idx,item in enumerate(self.listPrinters) if self.vdefault.get() in item][0]
        [self.my_LboxPrt.itemconfig(i,background=self.C_DEFAULT) if i==idx \
                             else self.my_LboxPrt.itemconfig(i,background=self.C_NORMAL) \
             for i in range(self.my_LboxPrt.size()) if self.my_LboxPrt.itemcget(i,'background') != self.C_ACTIVE]

    def _selectDefault(self):
        self.parent.default_printer = self.listPrinters[self.my_LboxPrt.curselection()[0]]
        self.parent.conn.setDefault(self.parent.default_printer)
        self.vdefault.set(self.parent.default_printer)
        self.__colorDefault()

    def _selectActive(self, event=None):
        self.parent.active_printer = self.listPrinters[self.my_LboxPrt.curselection()[0]]
        self.vactive.set(self.parent.active_printer)
        self.__colorActivate()
        
    def __colorActivate(self):
        idx = [idx for idx,item in enumerate(self.listPrinters) if self.vactive.get() in item][0]
        [self.my_LboxPrt.itemconfig(i,background=self.C_ACTIVE) \
           if i==idx and self.my_LboxPrt.itemcget(i,'background')!=self.C_DEFAULT \
                             else self.my_LboxPrt.itemconfig(i,background=self.C_NORMAL) \
               for i in range(self.my_LboxPrt.size()) if self.my_LboxPrt.itemcget(i,'background')!=self.C_DEFAULT]
        self.my_LboxPrt.activate(idx)
        
    def Quit(self):
        self.destroy()


if __name__ == "__main__":
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")

    root = tk.Tk()
    options:App_Options = None
    root.msgbox = Win_MessageBox(root)

    root.app_parameters = Saveload_CFG()
    Wpd = Linux_InitPrinters(root)
    if root.app_parameters.cfg_load():
        options = root.app_parameters.options
        options.createEvtAthFile = False
    else:
        print(f"Options not loaded. End of program")
        exit(2) 

    ShowPrinters(root,Wpd,Wpd.dico_printers).lift()
    
    root.mainloop()

    #print(f" ---> Dictionnaire lu dans CUPS :\n{Wpd.dico_printers}\n ---> Liste créée :\n")
    print(f"\n ---> Default printer: {Wpd.default_printer}\n")
    [print(item) for item in Wpd.list_prt]
    

    
