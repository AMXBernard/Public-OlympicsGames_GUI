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


import re
#import os,locale
#import os.path as op
import tkinter as tk
import tkinter.scrolledtext as tkText
import tkinter.font as tkFont

from configs import *
from gui_tools import Window_StateBar
from itertools import chain


class Patterns():
    """ Classe définissant le pattern qui permet de créer et classer à partir d'un fichier texte
        un très léger système d'aide simple à utiliser.
    """
    @property
    def whole_paragraph(self) -> str:
        return r'-([\d.]*?)__([\s\S]*?):([\s\S]*?)EOP'


class Paragraphe():
    """ Classe définissant la structure d'un paragraphe du système d'aide """
    def __init__(self, paragraph:tuple):
        if isinstance(paragraph,tuple) and len(paragraph)==5:
            self.numero = f"{paragraph[0]}"
            self.title = f"{paragraph[1]} :"
            self.text = paragraph[2].strip('\n')
            self.span = paragraph[3],paragraph[4]
        else:
            raise ValueError("Bad tuple format, must be a 5 tuple (number,title,text,span1,span2)") 
    
    def __str__(self) -> str:
        return f"Chapitre {self.numero} : {self.title}\n{self.text}\n"

class Paragraphes():
    """ Classe qui lit un fichier texte pré-formaté et crée un dictionnaire dans lequel on
        retrouve tous les paragraphes extraits du fichier texte.
        Propriétés:
            all_paragraph : construit et renvoi le dictionnaire complet des objets 'Paragraphe'
        Méthodes (publiques):
            get_paragraph(number): renvoi la valeur de la clé 'number' qui est un objet
            de la classe 'Paragraphe'   
    """
    def __init__(self, filename:str=None):
        self.__pattern = Patterns()
        self.__handler_file:os.TextIOWrapper
        self.__wholeTextParagraph:dict =({})
        # - Lecture fichier d'aide et création du dictionnaire des chapitres --
        if op.isfile(filename):
            self.__handler_file = open(filename, mode="rt", encoding="utf-8")
            self.__readText(self.__handler_file)
        #else:
        #    raise FileExistsError(f"File '{filename}' does not exist!")
            
    @property
    def all_paragraph(self) -> dict:
        return self.__wholeTextParagraph
    @all_paragraph.setter
    def all_paragraph(self, paragraph:tuple):
        self.__wholeTextParagraph.update({f"{paragraph[0]}":Paragraphe(paragraph)})

    def __find_whole_paragraph(self, wholetext:str) -> list:
        return list(re.finditer(self.__pattern.whole_paragraph,wholetext,flags=re.MULTILINE | re.DOTALL))    
        
    def __readText(self, handlerfile):
        paragraphs = self.__find_whole_paragraph(handlerfile.read())
        for paragraph in paragraphs:
            self.all_paragraph = tuple(chain.from_iterable((paragraph.groups(), paragraph.span())))
        handlerfile.close()
    
    def get_paragraph(self, number:str) -> Paragraphe:
        return self.all_paragraph.get(number, Paragraphe((number,"Bad number","No paragraph text",0,0)))
        
    def __str__(self) -> str:
        return '\n'.join([f"{item[0]}, {item[1].title}{item[1].text}\n" for item in list(self.all_paragraph.items())])    
        
    
class Help_System(tk.Toplevel):
    
    def __init__(self, master:tk.Tk, options:App_Options, *args, **kwargs):
        
        self.__master = master
        self.__options = options
        self.__helpText:tkText.ScrolledText
        self.paragraphes = Paragraphes(op.join(os.getcwd(),options.datapath,options.helpfilename))
        # ------- Création de la liste des rubriques 'titre' de l'aide --------
        titles_list = list(filter(lambda p:p.numero.find('.')!=-1, self.paragraphes.all_paragraph.values()))
        self.__vlstTitles = tk.StringVar(value=list(map(lambda t:t.title.split(' :')[0], titles_list)))
        #print(f"Help titles list: {self.__vlstTitles.get()}")
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3, 'bg':'LightSteelBlue1', 'relief':'ridge', 'padx':2, 'pady':2}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, name="!help_Window", *args, **kwargs)
        # ---------------------------------------------------------------------
        self.lblFont = tkFont.Font(family='Courier New', size=13, weight='bold', slant='italic')
        self.txtFont = tkFont.Font(family='Consolas', size=12, weight='normal', slant='italic')
        self.btnFont = tkFont.Font(family='Sans', size=11, weight='normal', slant='italic')
        # ---------------------------------------------------------------------
        self.title(f" Aide GBRecord v2.5 ")
        self.protocol("WM_DELETE_WINDOW", self.Quit)    
        self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        self.grid_columnconfigure(list(range(0,2)), weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.bind("<Escape>", self.Quit)
        self.minsize(640, 280)
        self.grid_anchor("nw")
        self.cree_widgets()
        self.withdraw()
        
    def cree_widgets(self):
        self.title_bar = Window_StateBar(self,"",0,0,0,cspan=10,txtfont=self.lblFont,sticky="nsew",
                                                                       defMessage=" Rubrique ",bg='azure2',pady=3)
        self.__helpList = tk.Listbox(self,bg='LightCyan',bd=2,font=('Consolas 10 bold italic'),width=35,
                              activestyle="dotbox",height=20,selectmode="extended",listvariable=self.__vlstTitles)
        self.__helpList.grid(column=0, row=1, columnspan=2, sticky="nsew")
        self.__helpText = tkText.ScrolledText(self, bg='ivory', bd=2, relief="sunken",
                                                        font=self.txtFont, wrap="word", width=100, height=20)
        self.__helpText.tag_configure("number", font=('Consolas 14 bold italic'), lmargin1=10, spacing1=2,
                                                   spacing3=3, relief="sunken", border=2, background="azure2")
        self.__helpText.tag_configure("header", font=('Consolas 10 bold italic'), background="azure1",
                                                  lmargin2=10, spacing1=5, spacing3=5, border=3, relief="ridge")
        self.__helpText.tag_configure("texte", background="ivory", spacing1=5, lmargin2=10, rmargin=10)
        self.__helpText.tag_configure("title", font=self.lblFont, background="DarkOliveGreen1")
        self.__helpText.grid(column=2, row=1, columnspan=8, sticky="nsew")
        self.state_bar = Window_StateBar(self,"",0,0,2,cspan=10,pady=3,txtfont=self.btnFont,sticky="nsew",
                                    defMessage=" Aide info : Touche 'Echap' pour fermer la fenètre.", defTime=5)
        self.bind("<<ListboxSelect>>", self.on_paragraph_select)
    
    def on_paragraph_select(self, event):
        selection = event.widget.curselection() 
        if selection:
            data = f"{event.widget.get(selection[0])} :"
            number = list(filter(lambda p:p.title==data, self.paragraphes.all_paragraph.values()))[0].numero
            index = self.__helpText.search(f"{number}", "1.0", tk.END)
            self.__helpText.see(index=index)
    
    def show_paragraph(self, number:str):
        paragraph = self.paragraphes.get_paragraph(number)
        if paragraph.numero.find('.') != -1:
            self.__helpText.insert(tk.END, paragraph.numero+' - ', (f"paragraph_{number}", "number"))
            self.__helpText.mark_set("end_number", f"{tk.END} -1c")
            linT,colT = self.__helpText.index("end_number").split('.')
            # -----------------------------------------------------------------
            self.__helpText.insert(tk.END, ' '+paragraph.title, f"paragraph_{number}")
            # -----------------------------------------------------------------
            self.__helpText.mark_set("deb_txt", f"{tk.END}"); deb_txt = self.__helpText.index('deb_txt')
            self.__helpText.insert(tk.END, f"{paragraph.text}\n", f"paragraph_{number}")
            self.__helpText.mark_set('end_txt', f"{tk.END}+1c"); end_txt = self.__helpText.index('end_txt')
            # -----------------------------------------------------------------
            self.__helpText.tag_add("title", f"{linT}.{colT}", f"{int(linT)+1}.0")
            self.__helpText.tag_add("texte", deb_txt, end_txt)
            self.__helpText.insert(tk.END, '\n')
            self.wm_deiconify()
        else:
            self.title_bar.update_vltexte(f" Aide de GBRecord GUI v2.5 - {paragraph.numero} / {paragraph.title}",1)
            if not paragraph.text.isspace():
                self.__helpText.insert("1.0",f"\t{paragraph.text.strip()}\n","header")
    
    def show_whole_help(self):
        [self.show_paragraph(number) for number in self.paragraphes.all_paragraph]
        self.title_bar.update_vltexte(f" Aide de OlympicGamse GUI v1 alpha ",1)
        self.__helpText.configure(state='disabled')
            
    def show_strait_help(self):
        self.title_bar.update_vltexte(f" Aide de OlympicGamse GUI v1 alpha ",1)
        self.__helpText.insert('end', self.paragraphes.__str__()+'\n')
        self.__helpText.configure(state='disabled')
        self.wm_deiconify()
    
    def delete_text(self):
        self.__helpText.configure(state='normal')
        self.__helpText.delete("1.0",'end')        
    
    def readonly(self):
        self.__helpText.configure(state='disabled')
        
    def Quit(self, event=None):
        self.delete_text()
        self.withdraw() 
        
if __name__ == "__main__":
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")
    # -------------------------------------------------------------------------
    root = tk.Tk()
    
    config = Saveload_CFG()
    if config.cfg_load():
        helper = Help_System(root, config.options)
        #helper.show_paragraph("1.1")
        helper.show_whole_help()
        #helper.show_strait_help()
        root.mainloop()
    else:
        print(f"Fichier d'aide '{config.options.helpfilename}' introuvable")
