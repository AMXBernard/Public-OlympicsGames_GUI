# -- encode utf-8 --
"""
helptools v1.0, bibliothèque du projet de librairie d'aide applicatif simple mêlant texte,
annotations et images. Fournit les objets, classes pour l'aide intégré à l'application. 
Copyright (C) 2026  Bernard AMOUROUX

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

GPL3 License - PyHELP (c) 2026 Bernard AMOUROUX

This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""
__author__ = "Bernard AMOUROUX"
__date__ = "$Date: 2026/08/01 07:00 $"
__copyright__ = "Copyright (c) 2026 Bernard AMOUROUX"
__license__ = "GPL 3"

import re
import locale
import os, sys

import tkinter as tk
import os.path as osp
import tkinter.scrolledtext as tkText

from configs import Saveload_CFG,App_Options
from dataclasses import dataclass
from PIL import Image,ImageTk
from tkinter.font import Font
from itertools import chain
from math import nan

DEBUG:bool = True


@dataclass
class Help_Options():
    
    hlpPath: str
    fileName: str
    imgPath: str = "helpfiles"
    hlpTitle:str = "Aide de l'Application"

        
class Help_StateBar(tk.Frame):
    """ Classe créant une barre d'état configurable qui permet l'affichege d'un message
        d'état pendant une durée déterminée, indéterminée ou immédiate.
        Méthodes de la classe:
            update_vltexte : 
                msg  : message à afficher
                wait : temps d'affichge du message. défaut 10s
            tips: wait à 1 pour que le message s'affiche en permanence. 
            message :
                getter : extrait le message en cours.
                setter : définit le message par défaut
            tips: pour que le message par défaut soit affiché imméditement, exécuter 'update_vltexte("",0)'                              
    """
    def __init__(self, master, col=0, row=0, cspan=1, sticky="nsew",
                          defMessage:str=' Info : ', defTime:int=10, txtfont=None, *args, **kwargs):
        """
        Attributs du constructeur:
            master     : Fenètre appelant, objet tkinter.Tk()
            col, row   : colone et ligne pour le placement dans la grille de la fenètre principale
            rspan, cspan, sticky : paramètres d'extension des lignes et colones dans la grille
            defMessage : message défaut qui s'affiche dès la tempo message terminée.
            defTime    : durée d'affichage des message par défaut 
            txtfont    : police de caractères pour l'affichage des messages
        """
        self.__waitnbr:int = None
        self.__defaultTime = defTime
        self.__defaultMsg = defMessage
        self.__vl_texte = tk.StringVar()

        tab_options:dict = {'bd':1, 'bg':'tan2', 'relief':'groove'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        lblfont = ("Consolas",11 ,'bold','italic') if not txtfont else txtfont
        
        self.grid(column=col,row=row,columnspan=cspan,padx=2,pady=2,sticky=sticky)
        
        tk.Label(self,bd=0,bg=self.cget('bg'),anchor="sw",height=1,font=lblfont,textvariable=self.__vl_texte).grid()
        self.update_vltexte(defMessage, 0)

    def __raz_vltexte__(self):
        """ methode privée de mise au message par défaut """
        self.__vl_texte.set(self.__defaultMsg)
        self.__waitnbr = None
    
    def update_vltexte(self, msg:str, wait=10):
        """ méthode de chargement d'un nouveau message pour affichage le temps désiré """
        if self.__waitnbr != None:
            self.after_cancel(self.__waitnbr)
        if wait == 0:
            self.__raz_vltexte__()
        elif wait > 1:
            self.__waitnbr = self.after(self.__defaultTime if wait==None else (wait*1000) , self.__raz_vltexte__)
        if msg: self.__vl_texte.set(msg)            
        super().update_idletasks()

    @property
    def message(self) -> str:
        return self.__vl_texte.get().rstrip()
    @message.setter
    def message(self, message:str):
        self.__defaultMsg = message


class Patterns():
    """ Classe définissant les pattern qui permettent de rechercher et numéroter 
        les paragraphes, mettre en évidence du texte, charger des images, mettre
        de la couleur; soit un très léger système d'aide simple à mettre en oeuvre et utiliser.
    """
    @property
    def whole_paragraph(self) -> str:
        return r'-([\d.]*?)__([\s\S]*?):([\s\S]*?)EOP-'
    
    @property
    def items_title(self) -> str:
        return r"[\s]{1}('[\w /_\'\-]+?'[\s]*?:)+?"
    
    @property
    def item_words(self) -> str:
        return r'[\s]{1}(\"[\w\s/_\'\.:=+?!#\*\-]+?\")[\s|,|.]{1}'
    
    @property
    def txt_italic(self) -> str:
        return r'##TxtItalic:[\d]{1,3}##'
    
    @property
    def txt_bold(self) -> str:
        return r'##TxtBold:[\d]{1,3}##'
    
    @property
    def imageInText(self) -> str:
        return r"##Image[\d]{1,3}:[\s\S]+?.png##"
    
    @property
    def colorText(self) -> str:
        """ Définition de la couleur et du nombre de caractères à colorer """
        return r'##Couleur:[#0-9a-zA-Z ]+?:[\d]{1,3}##'
    
    @property
    def changeFont(self) -> str:
        """ Capture :        family,         size,        weight,        slant """
        return r'##Font:([\s0-9a-zA-Z]+?):([0-9]{1,2}):(bold|normal):(roman|italic)##'
    
    @property
    def commentText(self) -> str:
        return r'//\*[\s\S]*?\*//'


class Paragraphe():
    
    @classmethod
    def Null_Paragraph(cls, number:float=nan) -> "Paragraphe":
        return Paragraphe((number," Index de paragraphe invalide","",0,0,[],[],[],[],[],[]))
    
    """ Classe définissant la structure d'un paragraphe du système d'aide """
    def __init__(self, paragraph:tuple):
        if isinstance(paragraph,(tuple,list)) and len(paragraph)==11:
            self.numero:float = float(paragraph[0])
            self.isTitle:bool = f"{self.numero}".find('.0') != -1
            self.title = f"{paragraph[1]} :"
            self.text = paragraph[2].strip('\n')
            self.span_text   = paragraph[3],paragraph[4]
            self.span_imgs   = paragraph[5]   # spanlist des images à encapsuler dans le texte
            self.span_evds   = paragraph[6]   # spanlist des mises en evidences de texte 'xxxxx' suivi de ':' 
            self.span_words  = paragraph[7]   # spanlist des mises en evidences des mots "xxxxx" entre double quotes
            self.span_colors = paragraph[8]   # spanlist des mises en couleur des mots, parties de texte.
            self.span_italic = paragraph[9]   # spanlist des mots mis en gras -> slant ='italic'  
            self.span_bold   = paragraph[10]  # spanlist des mots mis en gras -> weight='bold'  
        else:
            raise ValueError("Bad tuple format, must be a 11 tuple (number,title,text,span_text1,span_text2,[span_imgs],[span_evds],[span_words],[span_colors],[span_italic],[span_bold])") 
    
    def __eq__(self, other:"Paragraphe") -> bool:
        return self.numero == other.numero and self.span == other.span
      
    def __hash__(self) -> int:
        return hash((self.numero, self.span, self.text))
    
    def __str__(self) -> str:
        return f"Chapitre {self.numero} : {self.title}{self.text if not self.isTitle else ' -> TITLE'}\tspan: {self.span}"

class Paragraphes():
    """ Classe qui lit un fichier texte pré-formaté et crée un dictionnaire dans lequel on
        retrouve tous les paragraphes extraits du fichier texte.
        Propriétés:
            all_paragraph : construit et renvoi le dictionnaire complet des objets 'Paragraphe'
        Méthodes (publiques):
            get_paragraph(number): renvoi la valeur de la clé 'number' qui est un objet
            de la classe 'Paragraphe'. 'number' est de type float.
    """
    def __init__(self, filename:str=None):
        self.__pattern = Patterns()
        self.__handler_file:os.TextIOWrapper
        self.__wholeTextParagraph:dict =({})
        self.defaultFontText:tuple = ()    # -> (Family,size,weight,slant)
        # - Lecture fichier d'aide et création du dictionnaire des chapitres --
        if osp.isfile(filename):
            self.__handler_file = open(filename, mode="rt", encoding="utf-8")
            self.__readText(self.__handler_file)
        else:
            raise FileExistsError(f"File '{filename}' does not exist!")
            
    @property
    def all_paragraph(self) -> dict:
        return self.__wholeTextParagraph
    @all_paragraph.setter
    def all_paragraph(self, paragraph:tuple):
        self.__wholeTextParagraph.update({paragraph[0]:Paragraphe(paragraph)})

    def __find_whole_paragraph(self, wholetext:str) -> list:
        return list(re.finditer(self.__pattern.whole_paragraph,wholetext,flags=re.MULTILINE | re.DOTALL))
        
    def __readText(self, handlerfile):
        # --- Recherche des commentaires pour suppression dans le texte lu ----
        comments = re.compile(self.__pattern.commentText, flags=0)
        paragraphs = self.__find_whole_paragraph(wholetext=comments.sub("",handlerfile.read()))
        # ---------------------------------------------------------------------
        defaultFont = re.findall(self.__pattern.changeFont,paragraphs[0].group(),flags=0)
        if defaultFont : self.defaultFontText = defaultFont[0]
        for paragraph in paragraphs[1 if defaultFont else 0:]:
            # -- Recherche des descripteurs de couleurs "##(Couleur:([0-9a-zA-Z ]+?)##" --
            span_imgs = list(re.finditer(self.__pattern.imageInText, paragraph.group(), flags=re.IGNORECASE))
            # -- Recherche des descripteurs d'images "##ImageXX:fname.PNG##" --
            span_imgs   = list(re.finditer(self.__pattern.imageInText, paragraph.group(), flags=re.IGNORECASE))
            # ---- Recherche des mises en evidence de texte "'xxxxx'   :" -----
            span_evds   = list(re.finditer(self.__pattern.items_title, paragraph.group(), flags=0))
            # ------- Recherche des mises en evidence de texte "xxxxx" --------
            span_words  = list(re.finditer(self.__pattern.item_words, paragraph.group(), flags=0))
            # -------- Recherche des couleurs "##Couleur:xxxxxx:nn##" ---------
            span_colors = list(re.finditer(self.__pattern.colorText, paragraph.group(), flags=re.IGNORECASE))
            # ---------- Recherche des couleurs "##TxtItalic:nn##" ------------
            span_italic = list(re.finditer(self.__pattern.txt_italic, paragraph.group(), flags=re.IGNORECASE))
            # ----------- Recherche des couleurs "##TxtBold:nn##" -------------
            span_bold = list(re.finditer(self.__pattern.txt_bold, paragraph.group(), flags=re.IGNORECASE))
            # ---------- Création du dictionnaire des Paragraphes() -----------
            self.all_paragraph = tuple(chain.from_iterable((paragraph.groups(), paragraph.span(),
                                                                [span_imgs,] if span_imgs else (0,), 
                                                                    [span_evds,] if span_evds else (0,), 
                                                                        [span_words,] if span_words else (0,),
                                                                            [span_colors,] if span_colors else ("",),
                                                                                [span_italic] if span_italic else (0,),
                                                                                    [span_bold] if span_bold else (0,)   )))
            # -----------------------------------------------------------------
            if not DEBUG:   # - FOR TEST DEBUG ONLY - # 
                numero = list(self.all_paragraph.keys())[-1]; print(f"\n - Chapitre {numero}:")
                [print(f"\t{key:<10}: {value if key != 'text' else value.lstrip()}") for key,value in self.all_paragraph[numero].__dict__.items()]
            # -----------------------------------------------------------------
        self.__handler_file.close()
    
    def get_paragraph(self, number:float) -> Paragraphe:
        return self.all_paragraph.get(number, Paragraphe((number,"Bad number","No paragraph text",0,0,[0,],[0,],[0,],["",],[0,],[0,])))
    
    def __str__(self) -> str:
        return '\n'.join([f"{item.__str__()}" for item in list(self.all_paragraph.values())])    


class Help_System(tk.Toplevel):
    
    def __init__(self, master:tk.Tk, options:Help_Options, *args, **kwargs):
        
        #self.__pattern = Patterns()
        self.__help_images:dict = ({})
        self.__helpText:tkText.ScrolledText
        self.options:Help_Options = options
        self.__maxsize = master.wm_maxsize()
        # -------- Affichage des attributs de la Classe Help_Options() --------
        if DEBUG: 
            print("Help_Option Attributes:")
            [print(f"\t{key:<10}: {value}") for key,value in self.options.__dict__.items()]
        # ---------------------------------------------------------------------    
        helpfileName:str = osp.join(os.getcwd(),options.hlpPath,options.fileName)
        self.paragraphes = Paragraphes(helpfileName)
        # --------- Extraction de la police de caractère à utiliser -----------
        df = self.paragraphes.defaultFontText
        if DEBUG: print(f"Paragraphes.defaultTextFont: {df}")
        # ------- Création de la liste des rubriques 'titre' de l'aide --------
        self.Titles_List = list(filter(lambda p:not p.isTitle, self.paragraphes.all_paragraph.values()))
        self.__vlstTitles = tk.StringVar(value=list(map(lambda t:t.title.split(' :')[0], self.Titles_List)))
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3, 'bg':'LightSteelBlue1', 'relief':'ridge', 'padx':0, 'pady':0}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, name="!help_Window", *args, **kwargs)
        # -------- police par défaut pour tout le texte / tag "texte" ---------
        if self.paragraphes.defaultFontText:    # != "Family":
            self.txtFont = Font(family=df[0],size=df[1],weight=df[2],slant=df[3])
        else:
            self.txtFont = Font(family='Consolas', size=10, weight='normal', slant='roman')    
        # ---------------- police des divers labels et boutons ----------------
        self.lblFont = Font(family='Courier New', size=14, weight='bold', slant='italic')
        self.btnFont = Font(family='Sans', size=11, weight='normal', slant='italic')
        # ---------------------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.Quit)    
        #self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        self.grid_columnconfigure(list(range(10)), weight=1)
        self.grid_rowconfigure(list(range(1,9)), weight=1)
        #self.bind('<Configure>', self.__getSize)
        self.bind("<Escape>", self.Quit)
        self.title(options.hlpTitle)
        self.minsize(640, 280)
        self.grid_anchor("center")
        self.cree_widgets()
        self.withdraw()
        
    def cree_widgets(self):
        self.boldFont = self.txtFont.copy(); self.boldFont.configure(weight='bold')
        self.evdsFont = self.txtFont.copy(); self.evdsFont.configure(family='Consolas',size=14,weight='bold',slant='italic')
        self.italicFont = self.txtFont.copy(); self.italicFont.configure(slant='italic')
        self.title_bar = Help_StateBar(self,0,0,cspan=10,txtfont=self.lblFont,defMessage=" Rubrique ",bg='azure2')
        self.__helpList = tk.Listbox(self,bg='LightCyan',bd=2,font=('Consolas 10 bold italic'),
                                        activestyle="dotbox",selectmode="extended",listvariable=self.__vlstTitles)
        self.__helpList.configure(width=self.__listboxWidth(self.Titles_List),height=len(self.Titles_List))
        self.__helpList.grid(column=0, row=1, columnspan=2, rowspan=8, sticky="nsew")
        self.__helpText = tkText.ScrolledText(self,bg='ivory',bd=2,relief="sunken",wrap="word") #,font=self.txtFont,wrap="word")
        # ------- Création des Tag_texte pour mise en évidence du texte -------
        self.__helpText.tag_configure("title_nbr", font=('Consolas 14 bold italic'), lmargin1=2, spacing1=2,
                                                   spacing3=2, relief="flat", border=0, background="orange")
        self.__helpText.tag_configure("number", font=('Consolas 14 bold italic'), lmargin1=10, spacing1=2,
                                                   spacing3=3, relief="sunken", border=2, background="azure2")
        self.__helpText.tag_configure("texte", background="ivory",font=self.txtFont,wrap="word",spacing1=5,lmargin2=5,rmargin=10)
        self.__helpText.tag_configure("title", font=self.lblFont, background="DarkOliveGreen1")
        self.__helpText.tag_configure("txtitle", font= ('Courier\\ New 13 bold italic'))
        self.__helpText.tag_configure("txtevds", font= ('Consolas 14 bold italic'))
        self.__helpText.tag_configure("txtitalic", font=self.italicFont)
        self.__helpText.tag_configure("txtbold", font=self.boldFont)
        self.__helpText.tag_configure("image", elide= True)
        # ---------------------------------------------------------------------
        self.__helpText.grid(column=2, row=1, columnspan=8, rowspan=8, sticky="nsew")
        message = " Info : F1 pour l'aide complet, Ctrl-F1 pour l'aide contextuel, 'Echap' ferme la fenètre."
        self.state_bar = Help_StateBar(self,0,10,cspan=10,bd=3,bg='wheat',pady=2,defTime=5,defMessage=message)
        self.bind("<<ListboxSelect>>", self.on_paragraph_select)
        # ------------ Taille de la fenetre de l'aide par défaut --------------
        self.geometry("1170x532") if self.__maxsize[0] > 1170 else self.geometry(f"{self.__maxsize[0]-50}x532")


    def __getSize(self, event:tk.Event=None):
        #print(f"App.size: {self.__maxsize[0]}")
        pass

    def __listboxWidth(self, titlelist:list) -> int:
        return max(map(lambda t:len(t.title.split(' :')[0]), titlelist)) + 2

    def __preload_help_Image(self, fname:str) -> Image.Image:
        filename = osp.join(os.getcwd(),self.options.hlpPath,self.options.imgPath,fname)
        if osp.isfile(filename):
            image = Image.open(fp=filename, mode='r', formats=('PNG',)).convert("RGBA")
            image.thumbnail((800,800), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image=image, master=self)
        return None

    def on_paragraph_select(self, event):
        selection = event.widget.curselection() 
        if selection:
            # ------- Recherche du numéro du paragraphe par son 'Titre' -------
            data = f"{event.widget.get(selection[0])} :"
            number = list(filter(lambda p:p.title==data, self.paragraphes.all_paragraph.values()))[0].numero
            # -- Recherche de l'index relatif du paragraphe par son tag texte -
            index = int(f"{self.__helpText.tag_ranges(f'paragraph_{number}')[0]}".split('.')[0])
            # -- Placement du paragraphe relativement au 1/4 haut de l'écran --
            self.__helpText.yview_pickplace(index-3)
    
    def show_paragraph(self, number:float, state="normal"):
        paragraph = self.paragraphes.get_paragraph(number)
        if paragraph.isTitle:
            self.__helpText.insert(tk.END, f"{int(paragraph.numero)}"+' - '+paragraph.title+'\n', (f"paragraph_{number}", "title_nbr"))
        else:
            self.__helpText.insert(tk.END, f"{paragraph.numero}"+' - '+paragraph.title, f"paragraph_{number}")
        linT,colT = self.__helpText.index(f"{tk.END}-1c").split('.')
        # ---------------------------------------------------------------------
        if not paragraph.text.isspace():
            # --- Insertion du texte dans le widget Tkinter.ScrolledText() ----
            self.__helpText.mark_set("deb_txt", "end-1c"); deb_txt = self.__helpText.index('deb_txt')
            self.__helpText.insert(deb_txt, f"{paragraph.text}\n", (f"paragraph_{number}", "texte"))
            # -------- Insertion des tags de mise en evidence de texte --------
            if paragraph.span_evds:
                spans = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]),
                                               self.__getIdx__(deb_txt,sp.span()[1])), paragraph.span_evds))
                [self.__helpText.tag_add("txtevds", span[0], span[1]) for span in spans]
                if DEBUG: print(f"tagged_evidence: {spans}")         
            # -------- Insertion des tags de mise en evidence des mots --------
            if paragraph.span_words:
                spans = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), 
                                               self.__getIdx__(deb_txt,sp.span()[1])), paragraph.span_words))
                [self.__helpText.tag_add("txtitle", span[0], span[1]) for span in spans]
                if DEBUG: print(f"tagged_words: {spans}")         
            
            # ------- Insertion des tags de mise en italique du texte  --------
            if paragraph.span_italic:
                italics = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1]),
                                                      sp.group().replace('##','').split(':')[1]), paragraph.span_italic))
                for span in italics:
                    nbr = span[2]
                    self.__helpText.tag_add("image", span[0], span[1])
                    self.__helpText.tag_add("txtitalic",span[1],f"{span[1]}+{nbr}c")
                if DEBUG: print(f"tagged_italic: {italics}")         
            # --------- Insertion des tags de mise en gras du texte -----------
            if paragraph.span_bold:
                bolds = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1]),
                                                          sp.group().replace('##','').split(':')[1]), paragraph.span_bold))
                for span in bolds:
                    nbr = span[2]
                    self.__helpText.tag_add("image", span[0], span[1])
                    self.__helpText.tag_add("txtbold",span[1],f"{span[1]}+{nbr}c")
                if DEBUG: print(f"tagged_bold: {bolds}")         
            # -------- Insertion des tags de mise en couleur des mots ---------
            if paragraph.span_colors:
                colors = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1]),
                                                      tuple(sp.group().replace('##','').split(':')[1:])), paragraph.span_colors))
                for span in colors:  # -- pattern de la forme : ##Couleur:xxxxxx:nnn##
                    #color, nbr = f"Color={span[2][0]}", span[2][1]
                    color, nbr = span[2][0], span[2][1]
                    #tags = self.__helpText.tag_names(f"{span[1]}+{int(nbr)//2}c"); print(f"tags names avant: {tags}")
                    self.__helpText.tag_add("image", span[0], span[1])
                    #self.__helpText.tag_configure(color,background=color.split('=')[1])
                    self.__helpText.tag_configure(color,background=color)
                    self.__helpText.tag_add(color,span[1],f"{span[1]}+{nbr}c")
                    #tags = self.__helpText.tag_names(f"{span[1]}+{int(nbr)//2}c"); print(f"tags names apres: {tags}")
                if DEBUG: print(f"tagged_colors: {colors}")         
            # -------- Insertion des tags des illustrations de l'aide ---------
            if paragraph.span_imgs:
                imgs = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1]),
                                                                       sp.group().split(':')[1][:-2]), paragraph.span_imgs[::-1]))
                [self.__helpText.tag_add("image", img[0], img[1]) for img in imgs]
                # ---- Affichage des images sur les emplacements des tags -----
                [self.__create_taggedImage__(img[0], img[2]) for img in imgs]
                if DEBUG: print(f"tagged_images: {imgs}")         
            # -----------------------------------------------------------------
            self.__helpText.tag_add("title", f"{linT}.0", f"{linT}.end+1c")
            self.__helpList.selection_set('active')
            if state != "normal":
                self.__helpList.configure(state=state)
                self.readonly(state=state)
        self.wm_deiconify()
    
    def __create_taggedImage__(self, pos, image):
        if self.__help_images.get(image, -1) == -1:
            self.__help_images[image] = self.__preload_help_Image(image)
        self.__helpText.image_create(pos,image=self.__help_images[image],align="top",name=image)
                    
    def __getIdx__(self, end:str, span:int) -> str:
        return self.__helpText.index(f"{end.split('.')[0]}.0+{span+1}c")
    
    def show_whole_help(self):
        self.delete_text()
        self.__helpList.configure(state="normal")
        [self.show_paragraph(number) for number in self.paragraphes.all_paragraph]
        self.title_bar.update_vltexte(f"  Aide de OlympicGames GUI v2.5 ",1)
        self.__helpText.configure(state='disabled')
            
    def show_strait_help(self):
        self.title_bar.update_vltexte(f"  Aide de OlympicGames GUI v2.5 ",1)
        self.__helpText.insert('end', self.paragraphes.__str__()+'\n')
        self.__helpText.configure(state='disabled')
        self.__helpList.config(state="disabled")
        self.wm_deiconify()
    
    def delete_text(self):
        self.__helpText.configure(state='normal')
        self.__helpText.delete("1.0",'end')        
    
    def readonly(self, state='disabled'):
        self.__helpText.configure(state=state)
        
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
        options = config.options
        Help_options = Help_Options(hlpPath=osp.basename(options.datapath),fileName=options.helpfilename)
        helper = Help_System(root, Help_options)
        helper.show_whole_help()
        
    #print(helper.paragraphes.__str__())
    #print(helper.paragraphes.get_paragraph("1"))
    #print(helper.paragraphes.get_paragraph("2.1"))
    #[print(item.__str__()) for key,item in helper.paragraphes.all_paragraph.items()]
    
    #helper.show_paragraph("3.2", state="disabled")
    #helper.readonly(state='normal')
    #root.after(2000,helper.show_paragraph,"1.5","disabled")
    #helper.show_strait_help()
    
    root.mainloop()
    root.quit()