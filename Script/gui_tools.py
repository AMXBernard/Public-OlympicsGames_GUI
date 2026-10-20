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

OlympicGames v1 Beta (C) 2026  Bernard AMOUROUX
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""
import re
import tkinter as tk

from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename,asksaveasfilename
from tkinter.scrolledtext import ScrolledText
from configs import *

class My_LabelFrame(tk.LabelFrame):

    def __init__(self,master,col=0,row=0,cspan=1,rspan=1,pad=(0,0,0,0),sticky='nsew', *args, **kwargs):

        tab_options:dict = {'bg':'ivory', 'bd':3, 'relief':'groove', 'labelanchor':'n'}
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)

        super().__init__(master,*args,**kwargs)        

        self.grid(column=col, row=row, columnspan=cspan, rowspan=rspan,
                                  padx=pad[0], pady=pad[1], ipadx=pad[2], ipady=pad[3], sticky=sticky)
        self.columnconfigure(list(range(cspan)), weight=1)
        self.rowconfigure(list(range(rspan)), weight=1)

    def name(self):
        return f"{self.master}."+self._name
        
        
class Window_StateBar(tk.Frame):
    
    def __init__(self, master, message:str, waitime:int, col=0, row=0, cspan=1, sticky="nsew", textWidth:int=1,
                        defMessage:str=' Info : ', defTime:int=10, txtfont=None, *args, **kwargs):
        
        self.__master = master
        self.__width = textWidth
        self.__message = f"{message:^{self.__width}}"
        self.__waitnbr:int = None
        self.__defaultTime = defTime
        self.__defaultMsg = f"{defMessage:<{self.__width}}"
        self.__vl_texte = tk.StringVar()
        self.__wait = waitime

        tab_options:dict = {'bd':1, 'bg':'tan2', 'relief':'groove'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        lblfont = ("Courier New",10 ,'bold','italic') if not txtfont else txtfont
        
        self.grid(column=col,row=row,columnspan=cspan,padx=2,pady=2,sticky=sticky)
        
        tk.Label(self,bd=0,bg=self.cget('bg'),anchor="sw",height=1,font=lblfont,textvariable=self.__vl_texte).grid()
        self.update_vltexte(defMessage if message=="" else message, waitime)

    def __raz_vltexte__(self):
        self.__vl_texte.set(self.__defaultMsg)
        self.__waitnbr = None
    
    def update_vltexte(self, msg:str, wait=10):
        if self.__waitnbr != None:
            self.after_cancel(self.__waitnbr)
        if wait == 0:
            self.__raz_vltexte__()
        elif wait > 1:
            self.__waitnbr = self.after(self.__defaultTime if wait==None else (wait*1000) , self.__raz_vltexte__)
            self.__vl_texte.set(f"{msg:<{self.__width}}")
        super().update_idletasks()

    @property
    def message(self) -> str:
        return self.__vl_texte.get().rstrip()
    @message.setter
    def message(self, message:str):
        self.__defaultMsg = message


class Win_MessageBox(tk.Toplevel):
    
    def __init__(self,master:tk.Tk,message:str=None,nobtn=False,msgtext=('Consolas 11 bold italic'), *args, **kwargs):
        
        self.__master = master
        self.__name__ = 'win_messagebox'
        self.__vmessage = tk.StringVar(value=message)
        
        tab_options:dict = {'bd':3, 'bg':'wheat', 'relief':'ridge', 'pady':5}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        self.protocol("WM_DELETE_WINDOW", self.Quit)
        self.wm_attributes("-topmost", 1)                     # - Fenetre popup toujours au premier plan
        self.resizable(False, False)
        self.grid_anchor('center')
        
        self.messageBox = tk.Message(self,bg='wheat',width=450,aspect=100,justify=tk.CENTER,
                                                        font=msgtext,textvariable=self.__vmessage)
        self.messageBox.grid(column=0,row=0,padx=20,pady=10,sticky="nsew")
        self.button = tk.Button(self,width = 8,bg='tan',text='Ok',command=self.Quit)
        self.button.configure(state='active' if not nobtn else 'disabled')
        self.button.grid(column=0,row=1,sticky="n")
        self.button.bind('<Return>', self.Quit)
        self.withdraw()
    
    @property
    def message(self)->str:
        return self.__vmessage.get()
    @message.setter
    def message(self, message):
        self.__vmessage.set(message)
        if not self.winfo_ismapped():
            self.deiconify()
            self.grab_set()
            self.lift()
        self.update()
    
    def message_update(self, message:str=""):
        self.__vmessage.set(message)
        self.update()        
    
    def textfont(self, msgtext:str):
        self.messageBox.configure(font=msgtext)
        
    def boxtitle(self, title:str):
        self.title(title)
        
    def noButton(self, nobtn:bool=True):
        self.button.configure(state='active' if not nobtn else 'disabled')
        if self.button.cget('state') == 'active':
            self.after(1000, self.Quit)
    
    def Quit(self, event=None):
        self.boxtitle(" Message ")
        self.grab_release()
        self.withdraw()    
   
   
class ScrolledListbox(tk.Listbox):
    """ Initialisation de la nouvelle Listbox avec ascenseur horizontal/vertical si nécessaire
        Nouvelles variables :
            master  : Objet appelant
            fxxxx   : option de la frame principale dont le texte.
            data    : Liste à afficher dans la listbox. Doit être un tk.StringVar
            vbar    : affichage forcé de l'ascenseur vertical à droite de la zone de liste.
            hbar    : affichage forcé de l'ascenseur horizontal au bas de la zone de liste.
            vsel    : marquage de la selection lorsque perte du focus par la listbox
            swidth  : épaisseur des ascenseurs en pts.
    """ 
    def __init__(self,master,data:tk.StringVar,col=0,row=0,cspan=3,rspan=2,name=None,
                            frelief='ridge',ftext=None,fbg=None,fbd=None,ffont=None,sticky='nsew',
                                pad=(0,0,0,0),swidth=12,vbar=True,hbar:bool=False,vsel=False,*args,**kwargs):

        self.__master = master
        self.__marked_Selected:list=([])
        
        lbx_font = tk.font.Font(family='Courier New', size=12, weight='bold', slant='roman')
        
        tab_options:dict = { 'bg':'ivory',          'listvariable':data,        'bd':3,              
                             'font':lbx_font,       'selectmode':'tk.SINGLE',   'activestyle':'dotbox',
                             'relief':'flat',       'selectborderwidth':1,      'selectbackground':'grey75',
                             'selectmode':'browse', 'highlightcolor':'tan',     'highlightbackground':'orange',
                             'name':name
                            }
        for key in tab_options:
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        
        self.__frame = My_LabelFrame(master,col=col,row=row,cspan=cspan,rspan=rspan,bg=fbg,bd=fbd,
                                        font=ffont,relief=frelief,text=ftext,pad=pad,sticky=sticky)
        
        super().__init__(self.__frame, *args, **kwargs)
        self.grid(column=0,row=0,columnspan=cspan,rowspan=rspan,
                                  padx=pad[0],pady=pad[1],ipadx=pad[2],ipady=pad[3],sticky=sticky)
        if vsel: 
            self.bind("<Enter>", self.unmark_selected)
            self.bind("<Leave>", self.mark_selected)
        # ---------------------- Mise en forme de la listbox à afficher --------------------------
        versb = tk.Scrollbar(self.__frame,orient=tk.VERTICAL,width=swidth,bg=self.cget('selectbackground'))
        horsb = tk.Scrollbar(self.__frame,orient=tk.HORIZONTAL,width=swidth,bg=self.cget('selectbackground'))
        if vbar: versb.grid(column=max(1,cspan-1),row=0,rowspan=rspan,pady=pad[1],ipady=pad[3],sticky='nse')
        if hbar: horsb.grid(row=max(2,rspan),column=0,columnspan=cspan,padx=pad[0],ipadx=pad[2],sticky='sew')
        self.columnconfigure(list(range(cspan)), weight=1)
        self.rowconfigure(list(range(rspan+1)), weight=1)
        self['xscrollcommand']=horsb.set
        self['yscrollcommand']=versb.set
        horsb['command']=self.xview
        versb['command']=self.yview
        self.select_set(0)
        self.activate(0)      
                  
    @property
    def marked_Selected(self) -> list:
        return self.__marked_Selected
    @marked_Selected.setter
    def marked_Selected(self, selected:list):
        self.__marked_Selected = selected
    
    def fconfigure(self, **options):
        """ configuration de la frame de la ScrolledListbox 
            options : dictionnaire de paramètres ({option1=valeur, option2=valeur ...etc...})
        """
        self.__frame.configure(**options)
    
    def getMultiSelectItems(self):
        """ Renvoi les index et les libellés des sélections de la listbox """
        if len(self.curselection()) > 1:
            idx = list(map(lambda x:int(x), self.curselection()))
            return list(zip(idx, map(lambda idx: self.get(idx), idx)))
        elif self.curselection():
            return [(int(self.curselection()[0]),self.get(self.curselection()[0]))]
        else:
            return None
        
    def getSelectItem(self):
        """ Renvoi l'index et le libellé de la premiere sélection de la listbox """
        idx = self.index('active') if not self.curselection() else self.curselection()[0]
        return int(idx), self.get(idx)
    
    def mark_selected(self, event):
        self.marked_Selected = list([idx for idx in self.curselection() if idx <= self.size()])
        [self.itemconfigure(idx, bg='orange') for idx in self.marked_Selected]
        [self.selection_set(idx) for idx in self.marked_Selected]
        
    def unmark_selected(self, event):
        if self.marked_Selected:
            if self.marked_Selected[-1] < self.size():
                [self.itemconfigure(idx, bg=self.cget('bg')) for idx in self.marked_Selected]
                [self.selection_set(idx) for idx in self.marked_Selected]
            self.marked_Selected.clear()
            
    @property
    def ftext(self) -> str:
        return self.__frame.cget('text')
    @ftext.setter
    def ftext(self, texte):
        self.__frame.configure(text = texte)

    def name(self) -> str:
        return self._name
    
    def destroy(self):
        self.unmark_selected(None)
        

class PopupMenu(tk.Menu):
    """ Classe Menu popup paramétrable.
        Les parametres du contructeur sont:
            'master': widget appelant dont le parent est un tk.Toplevel()
            'title' : titre du popup menu mis en surbrillance continue.
            Les 2 paramètres suivants indiquent les actions du menu.
            'commandsList': tuple de la forme (label_cmd:str, accel_cmd:str, commande:list[callable])
            'nosel' : list[int] liste des indices des rubrique dont l'état sera 'disabled'
        Les méthodes de la classe sont:
            show_Menu_popup(): affiche le menu popup à l'endroit du clic droit souris.
            nomenupopup(NoSel)    : prend en paramètre une liste contenant les numéros des rubriques à dévalider.
        La propriété 'NoSel' getter/setter sert de paramètre à la méthode 'nomenupopup()'.
    """
    def __init__(self, master:tk.Tk, title:str, commandsList:tuple=None, nosel:list=None):
        
        self.__master = master
        self.__commandList = commandsList
        self.__title = title.split(',')
        self.__NoSel = nosel
        
        super().__init__(master,tearoff=0,font=('Arial 12 bold italic'),postcommand=lambda :self.nomenupopup(self.__NoSel))
            
    def show_Menu_Popup(self, event:tk.Event):
        #self.__NoSel = [8] if self.__no_print() else []
        # ---------------------------------------------------------------------
        self.delete(0, 'end')   # -- reset de la liste des commandes ajoutées -
        if len(self.__title) == 1: self.__title = (self.__title, " ")
        self.add_command(label=self.__title[0],accelerator=self.__title[1],background='orange',activebackground='orange')
        self.configure(background="ivory", activebackground='tan',borderwidth=2,relief="solid")
        self.add_separator()
        self.add_Popup_Commands(commands=self.__commandList)
        self.nomenupopup(self.NoSel)
        # ---------------------------------------------------------------------
        try:
            self.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Erreur interne : {e}")
            self.grab_release()
    
    @property
    def NoSel(self) -> list:
        return self.__NoSel
    @NoSel.setter
    def NoSel(self, nosel:list):
        self.__NoSel = nosel
             
    def nomenupopup(self,nosel:list):                
        [self.entryconfigure(i, state = 'disabled') for i in nosel]

    def add_Popup_Commands(self, commands:tuple):
        for command in commands:
            if command[0] == "separator":
                self.add_separator()
            else:
                self.add_command(label=command[0],accelerator=command[1],command=command[2])   

    #def __no_print(self) -> bool:
    #    file1 = op.join(getcwd(),self.__master.app_options.exportpath,"Semaine_Q1.png")
    #    file2 = op.join(getcwd(),self.__master.app_options.exportpath,"Semaine_Q2.png")
    #    return not op.exists(file1) or not op.exists(file2)
    

class Win_popup(tk.Toplevel):
    """ Affichage d'une fenetre popup toujours au premier plan avec boutons système
        Intègre un Tkinter.ScrolledText() pour l'affichage de texte.
        Paramètres:
            'master': handle pouvant contenir/afficher la fenètre Toplevel
            'message': texte à afficher dans la zone tk.Text() de la fenètre
            'title': titre de la fenètre. S'affiche dans la barre système
        Méthodes:
            'get(index1, index2)'              : renvoi le texte compris entre index1 et index2, par défaut tout le texte 
            'insert(index, texte, *tags)'      : intégrer du texte dans le widget ScrolledText()
            'tag_add(tag_name, index1, *args)' : ajoute un tag 'tag_name' à partir de index1 et args est "index2" ou une liste d'indexes
            'tag_configure(tag_name, **kwargs)': configure un tag dans le widget ScrolledText()
            'readonly()'                       : place le status du widget ScrolledText en mode 'readonly'  
        Renvoi l'ID de la fenètre topLevel crée.  
    """
    def __init__(self, master=None, message=tk.StringVar, title:str="", *args, **kwargs):
        
        self.__master = master
        self.__message = message.get() if isinstance(message,tk.StringVar) else None
        
        self.menu_Font = tk.font.Font(family='Arial',size=12,weight='normal',slant='roman')
        self.txt_font = tk.font.Font(family='Courier New',size=12,weight='bold',slant='italic')    
        #self.max_size = master.bbox()[2], master.bbox()[3]  # - taille en pts de la fenetre principale
        
        tab_options:dict = {'bd':1, 'bg':'orange', 'relief':'flat'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        # ---------------------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.Quit)
        # ---------------------------------------------------------------------
        self.grid_columnconfigure(list(range(10)), weight=1)    # - Pour redimensionner la hauteur de la fenetre
        self.grid_rowconfigure(list(range(10)), weight=1)       
        self.minsize(width=640,height=480)
        self.resizable(True, True)                              # - Fenetre non redimensionnable en totalité.
        if title: self.title(title)                             # - Titre de la fenètre.
        # ---------------------------------------------------------------------       
        self.__creeWidgets()
        self.update()
    
    def __creeWidgets(self):
        # ----- construction frame pour zone texte et ascenseur vertical ------
        frame1 = My_LabelFrame(self, col=0, row=0, cspan=10, rspan=10, bg='tan2', sticky="nsew", pad=(2,2,2,2))
        frame1.grid_columnconfigure(list(range(10)), weight=1)   # - Pour redimensionner la hauteur de la frame
        frame1.grid_rowconfigure(list(range(10)), weight=1)      # - Pour redimensionner la hauteur de la frame
        # ----------------- widget tk.Text de la fenètre popup ----------------
        self.scrtxt = ScrolledText(frame1,bg='ivory',font=self.txt_font,wrap='word',relief='flat',bd=2,exportselection=True)
        self.scrtxt.grid(column=0,row=0,columnspan=10,rowspan=10,sticky="nsew")
        # - configuration des tags pour mise en évidence des termes sélectionnés 
        self.scrtxt.tag_configure("name",background="wheat",font=('Courier\ New 18 bold italic'))
        self.scrtxt.tag_configure("titre",font=('Helvetica 14 bold italic'),justify="center")
        self.scrtxt.tag_configure("event", background="#FCFBD0",relief='sunken',border=2,spacing1=3,spacing2=3,spacing3=0)
        self.scrtxt.tag_configure("description", background="#CAFAB7",spacing1=5,spacing3=5)
        self.scrtxt.tag_configure("special", background="#C8F6FC",spacing1=5,spacing3=5)  
        self.scrtxt.tag_configure("events", background="#FDFCA5",spacing1=5,spacing3=5)
        self.scrtxt.tag_configure("texteTitre", font=('Consolas 12 bold italic')) 
        self.scrtxt.tag_configure("texte", font=('Consolas 11 bold italic')) 
        self.scrtxt.tag_configure("trait",overstrike=True,justify="center")    
        self.scrtxt.tag_configure("souligne", underline = True)
        self.scrtxt.tag_configure("centre", justify="center")
        if self.__message: self.insert("1.0",self.__message)
        self.scrtxt.config(state='disabled',cursor="arrow")
        self.lift(self.__master)
            
    def get(self, index1='0.0', index2=tk.END) -> str:
        return self.scrtxt.get(index1, index2)

    def tag_configure(self, tagname:str, **kwargs):
        self.scrtxt.tag_configure(tagname, kwargs)

    def tag_add(self, tagname, index1, *args):
        self.scrtxt.tag_add(tagname, index1, args)

    def insert(self, index:str, message:str, *tags):
        self.scrtxt.configure(state="normal")            
        self.scrtxt.insert(index, message, tags)
        self.scrtxt.configure(state="disabled")            
    
    def delete(self, index1:str, index2:str=None):
        self.scrtxt.configure(state="normal")
        self.scrtxt.delete(index1=index1, index2=index2)          
        self.scrtxt.configure(state="disabled")                    
        
    def name(self) -> str:
        return f"{self.__master}."+self._name
        
    def Quit(self, event=None):
        self.destroy()


class Resultat_InfoWindow(Win_popup):
    
    def __init__(self, master, result:list, *args, **kwargs):
        
        self.__master = master
        self.__result:list = result if isinstance(result, list) else None
        
        if not self.__result: 
            return 'break'
        
        fr = result[0]
        title = f"Fenêtre d'information des Olympiade Modernes"
        super().__init__(master, None, title=title, name="!win_ResultPopup", *args, **kwargs)
        self.wm_attributes("-topmost", 1)                   # - Fenetre popup toujours au premier plan
        self.minsize(width=1024,height=768)
        
        self.insert("1.0",f"Listes des résultats Olympiade : {fr.edition} (Ed.{fr.edition_id})\n", "name","centre")
        self.insert(tk.END,"\n",)
        for resultat in self.__result:
            self.insert(tk.END, f"{resultat.sport} ({resultat.event}) - Id: {resultat.result_id}\n","centre","texteTitre","event")
            if resultat.result_date or resultat.result_location:
                self.insert(tk.END, f"La performance s'est déroulée le {resultat.result_date} au {resultat.result_location}\n","centre","event")
                self.insert(tk.END, "\n")
            if not any([s==resultat.result_format for s in ["na","NA","-/- ",""]]):
                self.insert(tk.END, f"Format de l'épreuve :\n","centre","events")
                self.insert(tk.END, f"\t{resultat.result_format}\n")
                self.insert(tk.END, "\n")
            if not any([s==resultat.result_detail for s in ["na","NA","-/- ",""]]):
                self.insert(tk.END, f"Informations, détails liés à l'épreuve\n","centre","special")
                self.insert(tk.END, f"{self.__details_format(resultat.result_detail)}\n","texte")
                self.insert(tk.END, "\n")
            if not any([s==resultat.result_description for s in ["na","NA","-/- ",""]]):
                self.insert(tk.END, f"Performances, informations liés à l'épreuve :\n","centre","description")
                self.insert(tk.END, f"\t{resultat.result_description}\n","texte")
            self.insert(tk.END, f"{' ':^40}\n", "trait")
        self.lift()
    
    def __details_format(self, raw_result:str) -> str:
        """
            "Course Length: 7,623 mHeight Differential: 47 mMaximum Climb: 31 mShooting 1: Prone at 2.5 km, 50 m rangeShooting 2: Standing at 5.5 km, 50 m rangeTotal Climbing: 241 m"
            "Inrun Distance: 62 mInrun Gradient: 27°Kicker #1: 4.00 m - 55° - 2.10 mKicker #2: 6.80 m - 66° - 3.50 mKicker #3: 6.80 m - 66° - 3.50 mKicker #4: 8.00 m - 70° - 4.15 mKicker
            #5: 8.00 m - 70° - 4.15 mKicker #6: 8.00 m - 71° - 4.15 mLanding Distance: 39 mLanding Gradient: 36.5°Start Elevation: ?Table Distance: 22 mTable Gradient: 0°Vertical Drop: ?,"
            "Course Length: ?Height Differential: ?Maximum Climb: ?Shooting 1: Prone at 6 km, 200 m range / Prone at 6.1Km, 200.1 m rangeShooting 2: Prone at 10.4 km, 250 m rangeShooting 3: 
            Prone at 11.8 km, 150 m rangeShooting 4: Standing at 17.1 km, 100 m rangeTotal Climbing: ?"
        """
        pattern = re.compile(r'([A-Z][a-zA-Z0-9 #]*:.*?)(?=[A-Z][a-zA-Z0-9 #]*:|$)')
        parts = [m.group(1).strip() for m in pattern.finditer(raw_result)]
        if not parts:
            return f"\t{raw_result}\n"
        else:
            idx,text = 0, "\t"
            if len(max(parts, key=lambda p:len(p))) < 50:
                if len(parts)%2 != 0: parts.append(f"{TIRET:^30}")
                while idx < len(parts) -1:
                    text += f"{parts[idx]:<50}{parts[idx+1]}\n\t"
                    idx += 2 if idx < len(parts) else 1
                    if idx == len(parts)-1: text += parts[-1]
            else:
                text += "\n\t".join(parts)
            return text    
    
    @property
    def result(self) -> list:
        return self.__result
    @result.setter
    def result(self, results:list):
        self.__result.extend(results)
        

class Athlete_InfoWindow(Win_popup):
    
    INDEX:int = 0
    
    def __init__(self, master, athlete=None, *args, **kwargs):
        
        self.__master = master
        self.__athlete = athlete
        
        if athlete:
            title = f"Fenêtre d'information - Athlète {self.__athlete.name} ({self.__athlete.athlete_id})"
        else:
            title = "Fenêtre d'information"
        super().__init__(master, None, title=title, name="!athlete_InfoWindow", *args, **kwargs)
        self.insert_athlete(self.__athlete, clear=True)
        self.bind("<Button-1>", self.__get_TextTag)
        self.minsize(width=1024, height=768)
        self.wm_attributes("-topmost", 1)                           # - Fenetre popup toujours au premier plan

        if not self.__athlete or self.__athlete.athlete_id == 0:    # - Fenetre initialisée mais cachée
            self.withdraw()
    
    @property
    def athlete(self):
        return self.__athlete
    @athlete.setter
    def athlete(self, athlete):
        self.insert_athlete(athlete, clear=True)
    
    def __get_TextTag(self, event:tk.Event=None):
        # ---------------------------------------------------------------------
        from resultats import Resultat
        # ---------------------------------------------------------------------        
        if event and isinstance(event.widget, ScrolledText):
            w:ScrolledText = event.widget
            index = w.index(f"@{event.x},{event.y}")
            found = list(filter(lambda tag:"line" in tag, w.tag_names(index)))
            if found:
                index1, index2 =  w.tag_ranges(*found)
                dumResult = w.get(index1, index2)
                # '1908 Summer Olympics in London, Swimming (100 metres Freestyle, Men),  \n' 
                # '1908 Summer Olympics in London, Boxing (Middleweight, Men - (Medal:Silver)),  \n'
                found = re.search(r'\d{4}[\s\S]+?ics', dumResult)
                edition = found.group() if found else "All editions"     
                found = re.search(r', ([\s\S]+?) \(', dumResult)
                sport = found.groups()[0] if found else "All sports"
                found = re.search(r' \(([\s\S]+?)(?=(?: - |\)))', dumResult)
                events = found.groups()[0] if found else "All events"
                resultat = Resultat.get_Olympics_Results_Details("obj", edition=edition,sport=sport,event=events)
                if resultat: Resultat_InfoWindow(self.__master, resultat)
                
    def insert_athlete(self, athlete, clear:bool=False):
        # -------------------------------------------------
        from athlete import AthleteEvents
        # -------------------------------------------------
        if athlete and athlete.athlete_id != 0:
            ath:Athlete = athlete
            if clear : 
                self.delete("1.0", tk.END)
            else:
                self.insert(tk.END, f"\n")
                
            self.title(f"Fenêtre d'information - Athlète {ath.name} ({ath.athlete_id})")
            self.insert(tk.END, f"{ath.name} ({ath.sex[0] if ath.sex else ''}) - Id: {ath.athlete_id}\n", "name","centre")
            self.insert(tk.END, f"\n{'Né' if ath.sex=='Male' else 'Née'} le {ath.naissance} ","texteTitre")
            self.insert(tk.END, f"{'en' if (ath.country.pays[-1]=='e' or ath.country.noc[-1]=='E') else 'au'} {ath.country.pays} ({ath.country.noc})\n","texteTitre")
            self.insert(tk.END, f"Corpulence : {ath.height if ath.height != 'nan' else '-/- '}cm pour {ath.weight}Kg\n","texteTitre")
            if not any([s==ath.description for s in ["na","NA","-/- ",""]]):
                self.insert(tk.END, f"{' ':^40}\n", "trait",)
                self.insert(tk.END, f"Performances/informations sur l'athlète sélectionné(e)\n", "centre","description")
                self.insert(tk.END, f"\t{ath.description}\n","texte")
            if not any([s==ath.special for s in ["na","NA","-/- ",""]]):
                self.insert(tk.END, f"{' ':^40}\n", "trait",)
                self.insert(tk.END, f"Evènements/informations liés à l'athlète sélectionné(e)\n", "centre","special")
                self.insert(tk.END, f"{self.__special_format(ath.special)}","texte")
            events = AthleteEvents.get_Olympics_Events_List("obj",select=None,athlete_id=ath.athlete_id)
            if events:
                self.insert(tk.END, f"{' ':^40}\n", "trait")
                self.insert(tk.END, f"Evènements auquels a participé l'athlète sélectionné(e)\n", "centre","events")
                [self.insert(tk.END, f"{event.edition} in {event.city}, {event.__repr__()}\n", "event","texte", \
                                          f"line{idx + Athlete_InfoWindow.INDEX}") for idx,event in enumerate(events)]   # if event.event != "No event"]
                Athlete_InfoWindow.INDEX += len(ath.events)
            self.deiconify()
    
    def __special_format(self, raw_special) -> str:
        """ Extraction des Evènements sportifs et épreuves associées 
            regex: "Listed in Olympians Who (Won a Medal at|Died in|Participated in|Set a) ((?:the|World)[^()]*?(?:\([^)]+|[^\d)]+\))?) \(([^)]+(?:\)[^A-Za-z0-9;]*;[^)]+)*[)(, :–\-\w\/]+)"
                   "Listed in Olympians Who (Won a Medal at|Died in|Participated in|Set a|Acted in) ((?:the|World|Movies)[^()]*?(?:\([^)]+|[^\d)]+\))?) \(([^)]+(?:\)[^A-Za-z0-9;]*;[^)]+)*[)(,\S]+)(?:\)|.\))"
        """
        pattern = re.compile(
            r"Listed in Olympians Who (Won a Medal at|Died in|Participated in|Set a|Acted in) ((?:the|World|Movies)[^()]*?(?:\([^)]+|[^\d)]+\))?) \(([^)]+(?:\)[^A-Za-z0-9;]*;[^)]+)*[)(,\S]+)(?:\)|.\))",
            flags=re.UNICODE | re.DOTALL | re.MULTILINE
            )
        results = []
        last_end = 0
        for m in pattern.finditer(raw_special):
            # Texte hors pattern avant ce match
            if m.start() > last_end:
                hors_pattern = raw_special[last_end:m.start()].strip()
                if hors_pattern:
                    results.append({'autre': hors_pattern})
            evenement = f"\n{m.group(1)} {m.group(2)} :"
            # On récupère la suite éventuelle d'épreuves après la parenthèse si elle est suivie d'un ';'
            epreuves_str = m.group(len(m.groups()))
            end = m.end()
            #print(f"groups(): {m.groups()}\nevenement: {evenement.lstrip()}\nepreuves_str: {epreuves_str} ---> end: {end}\n--------------------------------------")
            # Ajout des épreuves suivantes si ';' suit la parenthèse
            while end < len(raw_special) and raw_special[end] == ';':
                next_match = re.match(r';\s*([^;]+)', raw_special[end:])
                if next_match:
                    epreuves_str += ';' + next_match.group(1)
                    end += next_match.end()
                else:
                    break
            #print(f"epreuves_str+: {epreuves_str} ---> end: {end}\n--------------------------------------")
            epreuves = [e.strip() for e in epreuves_str.split(';')]
            results.append({'evenement': evenement, 'epreuves': epreuves})
            last_end = end
        # Reste du texte après le dernier match
        if last_end < len(raw_special):
            hors_pattern = raw_special[last_end:].strip()
            if hors_pattern and len(hors_pattern) > 1:
                results.append({'autre': hors_pattern})
                #print(f"hors pattern: {hors_pattern}")
        # Formatage pour affichage
        text = ""
        for r in results:
            if 'evenement' in r:
                # On vérifie si l'évènement se termine par une parenthèse contenant un mot seul
                match_alias = re.match(r"^(.*?)(\([^)]+\))$", r['evenement'].strip())
                if match_alias:
                    # Affiche l'évènement et l'alias sur la même ligne
                    text += f"r{match_alias.group(1).strip()} r{match_alias.group(2)}\n"
                else:
                    text += f"{r['evenement']}\n"
                for e in r['epreuves']:
                    motif = re.match(r"^(\d+[–-]\d+[–-]\d+)\s+(.*)", e)
                    if motif:  # -- On place le motif à la fin, entre parenthèses --
                        e = motif.group(2).strip() + f" ({motif.group(1).strip()})"
                    text += f"\t{e}\n"
            else:
                text += f"\t{r['autre']}\n"
        return text
    
    def Quit(self):
        Athlete_InfoWindow.INDEX = 0
        self.withdraw()    
            

class Parameters(tk.Toplevel):
    
    #CMODE = Literal["Sys","Oly","Img","Cfg","Bck","Hlp","Bio","Mdl","Res","Evt"]
    #cmode_List = get_args(CMODE)
            
    def __init__(self, master, app_options:App_Options, *args, **kwargs):
        
        self.__master = master
        self.__options = App_Options()
        if isinstance(app_options, App_Options): self.__options = app_options
        
        self.volympFolder = tk.StringVar(value=self.__options.olympicpath)              #
        self.vsystemFolder = tk.StringVar(value=self.__options.datapath)                #
        self.vimageFolder = tk.StringVar(value=self.__options.imagepath)                #
        self.volyfoldLbl = tk.StringVar(value=f"...{self.volympFolder.get()[-46:]}")
        #----------------------------------------------------------------------
        self.vconfigFile = tk.StringVar(value=self.__options.paramfilename)             #
        self.vbackground = tk.StringVar(value = self.__options.backfilename)            #
        self.vhelpFile = tk.StringVar(value=self.__options.helpfilename)                #
        #----------------------------------------------------------------------
        self.volympicsFile = tk.StringVar(value=self.__options.edition_file)            #
        self.volyresultsFile = tk.StringVar(value=self.__options.result_file)           #
        self.vcountryFile = tk.StringVar(value=self.__options.country_file)             #
        self.vathletebioFile = tk.StringVar(value=self.__options.athlete_file)          #
        self.vathletsportFile = tk.StringVar(value=self.__options.sport_file)           #
        self.vmedalTallyFile = tk.StringVar(value=self.__options.medal_file)            #
        self.veventsFile = tk.StringVar(value=self.__options.athevent_file)
        #----------------------------------------------------------------------
        self.vsearchCases = tk.IntVar(value=int(self.__options.search_options.cases))   #
        self.vsearchWhole = tk.IntVar(value=int(self.__options.search_options.whole))   #
        self.vsearchExact = tk.IntVar(value=int(self.__options.search_options.exact))   #
        self.vsearchPatrom = tk.IntVar(value=int(self.__options.search_options.patronym))#
        self.vsearchScale = tk.IntVar(value=(self.__options.search_options.scaleId))    #
        self.vradioScale = tk.DoubleVar(value=self.witchScale(self.vsearchScale.get()))
        self.vhomonynId = tk.IntVar(value=int(self.__options.search_options.multiId))   #
        self.vregexp = tk.IntVar(value=int(self.__options.search_options.regexp))       #
        self.vregexval = tk.StringVar(value="r'\sAdam*?'")
        #----------------------------------------------------------------------
        My_Datetime.Long = self.__options.datelong
        self.vdatelong = tk.IntVar(value=int(self.__options.datelong))                  #
        self.vfullscreen = tk.IntVar(value=int(self.__options.fullscreen))              #
        self.vsplashscreen = tk.IntVar(value=int(self.__options.splashscreen))          #
        self.vsaveonquit = tk.IntVar(value=int(self.__options.saveCFGonquit))           #
        self.vcreatevtath = tk.IntVar(value=int(self.__options.createEvtAthFile))
        #----------------------------------------------------------------------
        self.vseparatorCSV = tk.StringVar(value=self.__options.csvseparator)            #
        #----------------------------------------------------------------------
        self.vdefprinter = tk.StringVar(value=self.__options.default_printer)           #
        self.vfontfamily = tk.StringVar(value=self.__options.policy_family)             #
        self.vlinelength = tk.IntVar(value=self.__options.length_line)                  #
        self.vshowlinlen = tk.StringVar(value=f"({self.vlinelength.get()})")
        
        tab_options:dict = {'bd':2, 'bg':'ivory2', 'relief':'flat', 'name':'!app_Parameters'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        self.protocol("WM_DELETE_WINDOW", self.Quit)
        self.wm_attributes("-topmost", 1)                       # - Fenetre popup toujours au premier plan
        
        self.minsize(int(self.__options.app_size[0]*2/3), int(self.__options.app_size[1]*4/7))
        #print(f"app_size: {self.__options.app_size} ---> paramwin_size: {self.minsize()} " )
        self.title("Paramètres Olympics Games GUI v2.0 - (c) AMOUROUX Bernard 2026")
        self.resizable(False, False)
        self.grid_anchor('nw')
        self.cree_widgets()

    def cree_widgets(self):
        # ---------------------------------------------------------------------
        from tkinter.font import Font
        from tkinter.ttk import Combobox
        from country import EditionGame
        # ---------------------------------------------------------------------
        self.ttlfont = Font(self, family="Courier New", size=18, weight="bold", slant="italic")
        self.lblfont = Font(self, family="Consolas", size=10, weight="bold", slant="italic")
        self.frmfont = Font(self, family="Consolas", size=9, weight="bold", slant="italic")
        self.btnfont = Font(self, family="Helvetica", size=11, weight="bold", slant="italic")
        # ---------------------------------------------------------------------
        text = f"{EditionGame.FirstEdition}-{EditionGame.LastEdition}"
        tk.Label(self,text=f"Paramètres de OlympicsGames-GUI - Editions {text}",bd=3,relief="groove",
                    bg=self.cget('background'),font=self.ttlfont).grid(column=0,row=0,columnspan=20,sticky="nsew")
        # ---------------------------------------------------------------------
        frame0 = tk.Frame(self, bg="ivory", bd=3, relief="groove", name="!frame0Params")
        frame0.grid(column=0,row=1,columnspan=20,rowspan=13,ipadx=2,ipady=2,sticky="nsew")
        # ---------------------------------------------------------------------
        title = " Dossiers de l'application OG-GUI v2.0 "
        lframeFolders = My_LabelFrame(frame0,bg="#DDF3CA",bd=2,relief="ridge",col=0,row=0,cspan=10,
                                   font=self.frmfont,text=title,rspan=4,pad=(2,0,0,0),name="!labelframeFolders")
        tk.Label(lframeFolders,bg=lframeFolders.cget('bg'),text=" Dossier fichiers système:",
                                                 font=self.lblfont).grid(column=0,row=0,columnspan=3,sticky="w")
        sysentry = tk.Entry(lframeFolders,bg="ivory",textvariable=self.vsystemFolder,font=self.lblfont,width=40)
        sysentry.grid(column=3,row=0,columnspan=5,padx=5,sticky="w"); sysentry.xview("end")
        tk.Button(lframeFolders,bg="wheat",command=lambda: self.__chooseFolder(self.vsystemFolder,"Sys"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=0,columnspan=2,padx=2,sticky="nsew")
        tk.Label(lframeFolders,bg=lframeFolders.cget('bg'),text=" Dossier fichiers 'CSV'  :",
                                                 font=self.lblfont).grid(column=0,row=1,columnspan=3,sticky="w")
        olyentry = tk.Entry(lframeFolders,bg="ivory",textvariable=self.volympFolder,font=self.lblfont, width=40)
        olyentry.grid(column=3,row=1,columnspan=5,padx=5,sticky="w"); olyentry.xview("end")
        tk.Button(lframeFolders,bg="wheat",command=lambda: self.__chooseFolder(self.volympFolder,"Oly"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=1,columnspan=2,padx=2,sticky="nsew")
        tk.Label(lframeFolders,bg=lframeFolders.cget('bg'),text=" Dossier fichiers images :",
                                                 font=self.lblfont).grid(column=0,row=2,columnspan=3,sticky="w")
        imgentry = tk.Entry(lframeFolders,bg="ivory",textvariable=self.vimageFolder,font=self.lblfont, width=40)
        imgentry.grid(column=3,row=2,columnspan=5,padx=5,sticky="w"); imgentry.xview("end")
        tk.Button(lframeFolders,bg="wheat",command=lambda: self.__chooseFolder(self.vimageFolder,"Img"), 
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=2,columnspan=2,padx=2,sticky="nsew")
        # ---------------------------------------------------------------------
        title = " Fichiers de l'application OG-GUI v2.0 "
        lframeFiles = My_LabelFrame(frame0,bg="#DBF8C2",bd=2,relief="ridge",col=10,row=0,cspan=10,
                                   font=self.frmfont,text=title,rspan=4,pad=(2,0,0,0),name="!labelframeFiles")
        title = f" : Sauver la configuration en quittant (fichier '{self.vconfigFile.get()}')"
        lsaveonQuit = My_LabelFrame(lframeFiles,col=0,row=0,cspan=10,pad=(2,0,2,0),bg="#EBFDDD",bd=2)
        tk.Checkbutton(lsaveonQuit,bg=lsaveonQuit.cget('bg'),text=title,font=self.lblfont,
              variable=self.vsaveonquit,bd=0).grid(column=0,row=0,columnspan=10,padx=3,sticky="nsew")
        tk.Label(lframeFiles,bg=lframeFiles.cget('bg'),text=" Image d'arrière plan    :",
                                                 font=self.lblfont).grid(column=0,row=1,columnspan=3,sticky="w")
        backentry = tk.Entry(lframeFiles,bg="ivory",textvariable=self.vbackground,font=self.lblfont,width=32)
        backentry.grid(column=3,row=1,columnspan=5,padx=5,sticky="w"); backentry.xview("end")
        tk.Button(lframeFiles,bg="wheat",command=lambda: self.__chooseFile(self.vbackground,"Bck"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=1,columnspan=2,padx=2,sticky="nsew")
        tk.Label(lframeFiles,bg=lframeFiles.cget('bg'),text=" Fichier d'Aide OG-GUI   :",
                                                 font=self.lblfont).grid(column=0,row=2,columnspan=3,sticky="w")
        helpentry = tk.Entry(lframeFiles,bg="ivory",textvariable=self.vhelpFile,font=self.lblfont,width=32)
        helpentry.grid(column=3,row=2,columnspan=5,padx=5,sticky="w"); helpentry.xview("end")
        tk.Button(lframeFiles,bg="wheat",command=lambda: self.__chooseFile(self.vhelpFile,"Hlp"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=2,columnspan=2,padx=2,sticky="nsew")
        # ---------------------------------------------------------------------
        title = f" Fichiers de données au format 'CSV' des Olympiades de {EditionGame.FirstEdition}-{EditionGame.LastEdition}"
        lframeEdition = My_LabelFrame(frame0,bg="#DCF8ED",bd=2,relief="ridge",col=0,row=4,cspan=20,
                                   font=self.frmfont,text=title,rspan=5,pad=(2,2,0,0),name="!labelframeEditions")
        title= "Ces fichiers sont téléchargeables sur : https://www.kaggle.com/datasets/josephcheng123456/olympic-historical-dataset-from-olympediaorg"
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=title,
                            font=self.lblfont).grid(column=0,row=0,columnspan=20,pady=5,sticky="nsew")
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=" Fichier des Olympiades    :",
                                                 font=self.lblfont).grid(column=0,row=1,columnspan=4,sticky="w")
        olympicentry = tk.Entry(lframeEdition,bg="ivory",textvariable=self.volympicsFile,font=self.lblfont,width=32)
        olympicentry.grid(column=4,row=1,columnspan=4,padx=5,sticky="w")
        tk.Button(lframeEdition,bg="wheat",command=lambda: self.__chooseOlyfile(self.volympicsFile,"Oly"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=1,columnspan=2,padx=2,sticky="w")
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=" Fichiers des épreuves olympiques:",
                                                 font=self.lblfont).grid(column=10,row=1,columnspan=4,sticky="w")
        resultentry = tk.Entry(lframeEdition,bg="ivory",textvariable=self.volyresultsFile,font=self.lblfont,width=32)
        resultentry.grid(column=14,row=1,columnspan=4,padx=5,sticky="w")
        tk.Button(lframeEdition,bg="wheat",command=lambda: self.__chooseOlyfile(self.volyresultsFile,"Res"),
                      text=" Choisir ",font=self.btnfont).grid(column=18,row=1,columnspan=2,padx=2,sticky="w")
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=" Fichier des athlètes (BIO):",
                                                 font=self.lblfont).grid(column=0,row=2,columnspan=4,sticky="w")
        athbioentry = tk.Entry(lframeEdition,bg="ivory",textvariable=self.vathletebioFile,font=self.lblfont,width=32)
        athbioentry.grid(column=4,row=2,columnspan=4,padx=5,sticky="w")
        tk.Button(lframeEdition,bg="wheat",command=lambda: self.__chooseOlyfile(self.vathletebioFile,"Bio"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=2,columnspan=2,padx=2,sticky="w")
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=" Fichier des athlètes par sport  :",
                                                 font=self.lblfont).grid(column=10,row=2,columnspan=4,sticky="w")
        athsptentry = tk.Entry(lframeEdition,bg="ivory",textvariable=self.vathletsportFile,font=self.lblfont,width=32)
        athsptentry.grid(column=14,row=2,columnspan=4,padx=5,sticky="w")
        tk.Button(lframeEdition,bg="wheat",command=lambda: self.__chooseOlyfile(self.vathletsportFile,"Spt"),
                      text=" Choisir ",font=self.btnfont).grid(column=18,row=2,columnspan=2,padx=2,sticky="w")
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=" Fichier des médailles/pays:",
                                                 font=self.lblfont).grid(column=0,row=3,columnspan=4,sticky="w")
        medalentry = tk.Entry(lframeEdition,bg="ivory",textvariable=self.vmedalTallyFile,font=self.lblfont,width=32)
        medalentry.grid(column=4,row=3,columnspan=4,padx=5,sticky="w")
        tk.Button(lframeEdition,bg="wheat",command=lambda: self.__chooseOlyfile(self.vmedalTallyFile,"Mdl"),
                      text=" Choisir ",font=self.btnfont).grid(column=8,row=3,columnspan=2,padx=2,sticky="w")
        tk.Label(lframeEdition,bg=lframeEdition.cget('bg'),text=" Fichier des pays participants   :",
                                                 font=self.lblfont).grid(column=10,row=3,columnspan=4,sticky="w")
        countryentry = tk.Entry(lframeEdition,bg="ivory",textvariable=self.vcountryFile,font=self.lblfont,width=32)
        countryentry.grid(column=14,row=3,columnspan=4,padx=5,sticky="w")
        tk.Button(lframeEdition,bg="wheat",command=lambda: self.__chooseOlyfile(self.vcountryFile,"Noc"),
                      text=" Choisir ",font=self.btnfont).grid(column=18,row=3,columnspan=2,padx=2,sticky="w")
        lframeEvents = My_LabelFrame(lframeEdition,bg="#D8FCF1",bd=2,relief="ridge",col=0,
                                                      row=4,cspan=20,pad=(3,0,0,0),name="!labelframeEvents")
        
        tk.Checkbutton(lframeEvents,text=" Créer le fichier de données des épreuves :",font=self.lblfont,
                            bg=lframeEvents.cget('bg'),variable=self.vcreatevtath,command=self.__createEB_State,
                                        onvalue=True,offvalue=False,bd=0).grid(column=0,row=0,columnspan=10,sticky="w")
        self.eventsentry = tk.Entry(lframeEvents,bg="ivory",textvariable=self.veventsFile,font=self.lblfont,width=32)
        self.eventsentry.grid(column=10,row=0,columnspan=4,padx=5,sticky="ew")
        self.eventsbtn = tk.Button(lframeEvents,command=lambda: self.__chooseOlyfile(self.veventsFile,"Evt"),
                                                                  bg="wheat",text=" Choisir/Créer ",font=self.btnfont)
        self.eventsbtn.grid(column=14,row=0,columnspan=2,padx=2,sticky="w")
        #tk.Label(lframeEvents,bg=lframeEvents.cget('bg'),text=f"dans le dossier '...{self.volympFolder.get()[-30:]}'",
        #                   textvariable=self.volyfoldLbl,font=self.lblfont).grid(column=16,row=0,columnspan=4,sticky="w")
        tk.Label(lframeEvents,bg=lframeEvents.cget('bg'),textvariable=self.volyfoldLbl,
                                        font=self.lblfont).grid(column=16,row=0,columnspan=4,sticky="w")
        
        # ---------------------------------------------------------------------
        title = f" Options pour les recherches d'Athlètes, de Sports, d'épreuves, etc ... "
        lframeSearch = My_LabelFrame(frame0,bg="#F8E9DA",bd=2,relief="ridge",col=0,row=9,cspan=20,
                                   rspan=3,font=self.frmfont,text=title,pad=(2,2,0,0),name="!labelframeSearch")
        title = " Options syntaxiques "
        lframeCheckbtn = My_LabelFrame(lframeSearch,bg="#F8E9DA",bd=2,relief="groove",col=0,row=0,cspan=12,rspan=2,
                font=self.frmfont,text=title,pad=(1,2,2,2),name="!labelframeSearchBtn",sticky="nsew")
        tk.Checkbutton(lframeCheckbtn,bg=lframeCheckbtn.cget('bg'),text=" : Sensible à la casse",font=self.lblfont,
                    variable=self.vsearchCases,bd=0).grid(column=0,row=0,columnspan=3,padx=5,pady=3,rowspan=1,sticky="w")
        tk.Checkbutton(lframeCheckbtn,bg=lframeCheckbtn.cget('bg'),bd=0,text=" : Mot entier",font=self.lblfont,
                    variable=self.vsearchWhole).grid(column=4,row=0,columnspan=3,padx=5,pady=3,rowspan=1,sticky="w")
        tk.Checkbutton(lframeCheckbtn,bg=lframeCheckbtn.cget('bg'),bd=0,text=" : Mot exact",font=self.lblfont,
                    variable=self.vsearchExact).grid(column=8,row=0,columnspan=2,padx=5,pady=3,rowspan=1,sticky="w")
        tk.Checkbutton(lframeCheckbtn,bg=lframeCheckbtn.cget('bg'),bd=0,text=" : Patronyme",font=self.lblfont,
                    variable=self.vsearchPatrom).grid(column=11,row=0,columnspan=2,padx=5,pady=3,rowspan=1,sticky="w")
        tk.Checkbutton(lframeCheckbtn,bg=lframeCheckbtn.cget('bg'),text=" : utiliser une RegEx =",font=self.lblfont,bd=0,
                 variable=self.vregexp,command=self.__activentry).grid(column=0,row=1,columnspan=4,padx=5,pady=3,sticky="w")
        self.regexEntry = tk.Entry(lframeCheckbtn,bg='ivory',textvariable=self.vregexval,state="disabled",font=self.frmfont)
        self.regexEntry.grid(column=4,row=1,columnspan=2,pady=3,ipady=1,sticky="w")
        tk.Checkbutton(lframeCheckbtn,bg=lframeCheckbtn.cget('bg'),text=" : Rechercher les Homonymes",bd=0,
                 font=self.lblfont,variable=self.vhomonynId).grid(column=8,row=1,columnspan=4,padx=5,pady=3,sticky="w")
        title = " Fenètre d'amplitude de recherche d'Athlète ID "
        lframeScale = My_LabelFrame(lframeSearch,bg="#F8E9DA",bd=2,relief="groove",col=12,row=0,
                        font=self.frmfont,text=title,rspan=2,cspan=8,pad=(1,2,2,2),name="!labelframeScale",sticky="nsew")
        tk.Label(lframeScale,bg=lframeScale.cget('bg'),bd=0,font=self.lblfont,
                                                text=" Amplitude :").grid(column=0,row=0,padx=5,rowspan=2,sticky="nsew")
        tk.Radiobutton(lframeScale,bg=lframeScale.cget('bg'),bd=0,text="10",value=10,variable=self.vradioScale,
                    font=self.lblfont,command=lambda: self.__changeScale(10),).grid(column=1,row=0,rowspan=2,sticky="w")
        tk.Radiobutton(lframeScale,bg=lframeScale.cget('bg'),bd=0,text="100",value=100,variable=self.vradioScale,
                    font=self.lblfont,command=lambda: self.__changeScale(100)).grid(column=2,row=0,rowspan=2,sticky="w")
        tk.Radiobutton(lframeScale,bg=lframeScale.cget('bg'),bd=0,text="1000",value=1000,variable=self.vradioScale,
                    font=self.lblfont,command=lambda: self.__changeScale(1000)).grid(column=3,row=0,rowspan=2,sticky="w")
        tk.Radiobutton(lframeScale,bg=lframeScale.cget('bg'),bd=0,text="10000",variable=self.vradioScale,value=100000,
                    font=self.lblfont,command=lambda: self.__changeScale(10000)).grid(column=4,row=0,rowspan=2,sticky="w")
        tk.Label(lframeScale,bg=lframeScale.cget('bg'),text=" Valeur:",
                                               font=self.lblfont,bd=0).grid(column=5,row=0,padx=5,rowspan=2,sticky="nsew")        
        self.radioScale = tk.Scale(lframeScale,from_=1,to=self.vradioScale.get(),variable=self.vsearchScale)
        self.radioScale.configure(font=('Consolas 8 bold italic'),digits=0,showvalue=True,orient='horizontal',bg=lframeScale.cget('bg'))
        self.radioScale.grid(column=6,row=0,columnspan=2,rowspan=2,sticky="ew")
        # ---------------------------------------------------------------------
        title = f" Options pour la lecture des fichiers 'CSV' "
        lframeRWcsv = My_LabelFrame(frame0,bg="#FCDFFD",bd=2,relief="ridge",col=0,row=13,cspan=10,
                                        font=self.frmfont,text=title,pad=(2,2,0,5),name="!labelframeRWcsv")
        tk.Label(lframeRWcsv,bg=lframeRWcsv.cget('bg'),bd=0,font=self.lblfont,
                                    text=" Séparateur de CSV : ").grid(column=0,row=0,pady=3,sticky="nsew")
        tk.Radiobutton(lframeRWcsv,bg=lframeRWcsv.cget('bg'),bd=0,text=":','",value=',',font=self.lblfont,
                                              variable=self.vseparatorCSV,).grid(column=1,row=0,padx=10,sticky="w")
        tk.Radiobutton(lframeRWcsv,bg=lframeRWcsv.cget('bg'),bd=0,text=":';'",value=';',font=self.lblfont,
                                              variable=self.vseparatorCSV,).grid(column=2,row=0,padx=10,sticky="w")
        tk.Radiobutton(lframeRWcsv,bg=lframeRWcsv.cget('bg'),bd=0,text=":Tabulation",value='\t',font=self.lblfont,
                                              variable=self.vseparatorCSV,).grid(column=3,row=0,padx=10,sticky="w")
        tk.Radiobutton(lframeRWcsv,bg=lframeRWcsv.cget('bg'),bd=0,text=":Espace",value='\h032',font=self.lblfont,
                                              variable=self.vseparatorCSV,).grid(column=4,row=0,padx=10,sticky="w")
        # ---------------------------------------------------------------------
        title = f" Options d'affichage de l'application "
        lframeScreensize = My_LabelFrame(frame0,bg="#FCD8DD",bd=2,relief="ridge",col=10,row=13,cspan=10,
                                        font=self.frmfont,text=title,pad=(2,2,0,5),name="!labelframeScreensize")
        tk.Checkbutton(lframeScreensize,bg=lframeScreensize.cget('bg'),text=": écran 'A propos'",font=self.lblfont,
                           variable=self.vsplashscreen,bd=0).grid(column=0,row=0,columnspan=2,padx=5,pady=3,sticky="w")
        tk.Checkbutton(lframeScreensize,bg=lframeScreensize.cget('bg'),text=": Plein écran ",font=self.lblfont,
              variable=self.vfullscreen,bd=0).grid(column=2,row=0,columnspan=2,padx=5,pady=3,rowspan=1,sticky="w")     
        tk.Label(lframeScreensize,bg=lframeScreensize.cget('bg'),font=self.lblfont,anchor="w",
                    text=f"Mode fenêtré actuel: {self.__options.app_size}").grid(column=4,row=0,columnspan=6,sticky="nsew")
        tk.Checkbutton(lframeScreensize,bg=lframeScreensize.cget('bg'),text=": Date longue",font=self.lblfont,
                                          variable=self.vdatelong,bd=0).grid(column=0,row=1,padx=5,pady=3,sticky="w")
        tk.Label(lframeScreensize,bg=lframeScreensize.cget('bg'),font=self.lblfont,anchor="w",
                    text=f"({My_Datetime(now.year,now.month,now.day)})").grid(column=1,row=1,columnspan=3,sticky="w")
        # ---------------------------------------------------------------------
        title = f" Paramétrage de l'impression "
        lframePrinter = My_LabelFrame(frame0,bg="#D3DCF8",bd=2,relief="groove",col=0,row=15,cspan=20,rspan=1,
                                                font=self.frmfont,text=title,pad=(2,2,0,5),name="!labelframePrinter")
        tk.Label(lframePrinter,bg=lframePrinter.cget('bg'),text=f" Imprimante à utiliser  :",anchor="w",
                                                font=self.lblfont).grid(column=0,row=0,columnspan=2,sticky="nsew")
        Combobox(lframePrinter,background=lframePrinter.cget('bg'),font=self.frmfont,name="!lframePrtCombobox",
                                             textvariable=self.vdefprinter,width=30,values=list(self.master.Printers.\
                                                dico_printers.keys())).grid(column=2,row=0,columnspan=2,ipady=3,sticky="w")
        tk.Label(lframePrinter,bg=lframePrinter.cget('bg'),text="Police chasse fixe  :",
                                                anchor="w",font=self.lblfont).grid(column=4,row=0,columnspan=1,sticky="w")
        Combobox(lframePrinter,background=lframePrinter.cget('bg'),font=self.frmfont,name="!lframePolicyCombobox",
                                                                  textvariable=self.vfontfamily,values=self.fixedfonts()).\
                                                                       grid(column=5,row=0,columnspan=2,ipady=3,sticky="w")                                                           
        tk.Label(lframePrinter,bg=lframePrinter.cget('bg'),text="Nombre de caractères/ligne :",
                                                anchor="w",font=self.lblfont).grid(column=7,row=0,columnspan=4,sticky="w")
        self.fontScale = tk.Scale(lframePrinter,from_=25,to=180,variable=self.vlinelength,name="!lframeLineLength")
        self.fontScale.configure(font=('Consolas 8 bold italic'),digits=0,showvalue=False,orient='horizontal',
                                                                   bg=lframePrinter.cget('bg'),command=self.__updateLinLen)
        self.fontScale.grid(column=11,row=0,columnspan=2,rowspan=2,sticky="ew")
        tk.Label(lframePrinter,bg=lframePrinter.cget('bg'),textvariable=self.vshowlinlen,
                                                                    font=self.lblfont).grid(column=14,row=0,sticky="nsew")
        # ---------------------------------------------------------------------
        buttons_frame = My_LabelFrame(frame0,0,16,pad=(2,2,0,0),cspan=20,bg=frame0.cget('bg'),bd=2,relief="raised",name="!buttonsFrame")
        tk.Button(buttons_frame,text="Annuler",font=self.btnfont,command=self.__cancel_command).grid(column=2,row=0,columnspan=2,padx=20,pady=3,sticky="w")
        tk.Button(buttons_frame,text="Sauvegarder",font=self.btnfont,command=self.__save_command).grid(column=8,row=0,columnspan=2,padx=20,pady=3,sticky="ew")
        tk.Button(buttons_frame,text="Valider",font=self.btnfont,command=self.__ok_command).grid(column=16,row=0,columnspan=2,padx=20,pady=3,sticky="e")
        # ---------------------------------------------------------------------        
        message = " Info : Fenètre de modification des paramètres de l'application"
        self.state_bar = Window_StateBar(self,"",0,col=0,row=17,cspan=20,pady=3,defMessage=message)
        self.__createEB_State()
    
    def __createEB_State(self):
        self.eventsentry.configure(state="disabled" if not bool(self.vcreatevtath.get()) else "normal")
        self.eventsbtn.configure(state=self.eventsentry.cget('state'))
        
    def __togglefullscreen(self):
        self.__options.fullscreen = bool(self.vfullscreen.get())
    
    def __activentry(self):
        self.regexEntry.configure(state="disabled" if not bool(self.vregexp.get()) else "normal")

    def __updateLinLen(self, event:tk.Event=None):
        self.vshowlinlen.set(f"({event})")
    
    def __changeScale(self, newscale:int):
        self.radioScale.configure(to=newscale)
        self.radioScale.set(newscale//2)
            
    def __chooseOlyfile(self, initial:tk.StringVar, mode:"Parameters.CMODE"):
        # ---------------------------------------------------------------------
        #from tkinter.filedialog import askopenfilename, asksaveasfilename
        # ---------------------------------------------------------------------
        fmode:dict = {"Oly":("des Olympiades",(("Olympiades","*.csv"),)),
                      "Bio":("des athlètes (BIO)",(("BIO des Athlètes","*.csv"),)),
                      "Noc":("des pays participants/organisateurs",(("Liste des PAYS","*.csv"),)),        
                      "Mdl":("des médailles/pays",(("MedalTally","*.csv"),)),        
                      "Res":("des résultats/edition",(("Résultats","*.csv"),)),        
                      "Spt":("des sports/épreuves",(("Sport/Events","*.csv"),)),        
                      "Evt":("des épreuves/athlètes",(("Events/Athlètes","*.csv"),)),        
                     }
        dmode:dict = {"Oly":(self.__options.edition_file,self.__options.olympicpath),
                      "Bio":(self.__options.athlete_file,self.__options.olympicpath),
                      "Noc":(self.__options.country_file,self.__options.olympicpath),
                      "Mdl":(self.__options.medal_file,self.__options.olympicpath),
                      "Res":(self.__options.result_file,self.__options.olympicpath),
                      "Spt":(self.__options.sport_file,self.__options.olympicpath),
                      "Evt":(self.__options.athevent_file,self.__options.olympicpath),
                     }
        title = f"Choix du fichier {fmode[mode][0]}"
        if mode != "Evt":
            dummyFile = askopenfilename(title=title,initialfile=dmode[mode][0],initialdir=dmode[mode][1],
                                                   filetypes=fmode[mode][1],parent=self,typevariable=initial)
        else: dummyFile = asksaveasfilename(title=title,initialfile=dmode[mode][0],initialdir=dmode[mode][1],
                                                   filetypes=fmode[mode][1],parent=self,typevariable=initial) 
        
        if dummyFile:
            self.state_bar.update_vltexte(" Info : Nom de fichier modifié",3)
            initial.set(op.basename(dummyFile))
        else:
            self.state_bar.update_vltexte(" Info : Aucune modification à faire !",3)
        
    def __chooseFile(self, initial:tk.StringVar, mode:"Parameters.CMODE"):
        # ---------------------------------------------------------------------
        #from tkinter.filedialog import askopenfilename
        # ---------------------------------------------------------------------
        fmode:dict = {"Bck":("d'arrière plan",(("JPEG files","*.jpg"),("GIF files","*.gif"),("PNG files","*.png"))),
                      "Hlp":("d'aide",(("HELP files","*.hlp"),)),
                      "Bio":("des athlètes (BIO)",(("BIO des Athlètes","*.csv"),)),
                      "Noc":("des pays participants/organisateurs",(("Liste des PAYS","*.csv"),)),        
                     }
        dmode:dict = {"Bck":(self.__options.backfilename,self.__options.imagepath), 
                      "Hlp":(self.__options.helpfilename,self.__options.datapath),
                      "Bio":(self.__options.athlete_file,self.__options.olympicpath),
                      "Noc":(self.__options.country_file,self.__options.olympicpath),
                     }
        title = f"Choix du fichier {fmode[mode][0]}"
        dummyFile = askopenfilename(title=title,initialfile=dmode[mode][0],initialdir=dmode[mode][1],
                                                        filetypes=fmode[mode][1],parent=self,typevariable=initial)
        if dummyFile:
            self.state_bar.update_vltexte(" Info : Nom de fichier modifié",3)
            initial.set(op.basename(dummyFile))
        else:
            self.state_bar.update_vltexte(" Info : Aucune modification à faire !",3)
        
    def __chooseFolder(self, initial:tk.StringVar, mode:"Parameters.CMODE"):
        # ---------------------------------------------------------------------
        #from tkinter.filedialog import askdirectory
        # ---------------------------------------------------------------------
        fmode:dict = {"sys":"systèmes", "Oly":"des Olympiades"}
        #fmode = "systèmes" if mode == "sys" else "des Olympiades" if mode == "Oly" else "images"
        title = f"Choix du chemin des fichiers {fmode.get(mode, 'images')}"
        dummyPath = askdirectory(parent=self,title=title,initialdir=initial.get(),mustexist=True)
        if dummyPath:
            self.state_bar.update_vltexte(" Info : Choix du dossier effectué",3)
            self.volyfoldLbl.set(f"...{dummyPath[-46:]}")
            initial.set(dummyPath)
        else:
            self.state_bar.update_vltexte(" Info : Aucune modification à faire !",3)
            
    def go(self):
        """ Methode qui permet de garder le focus sur la fenetre de choix
            de l'huile qui lors du choix renvoi le nom de l'huile choisie
            et ferme la fenetre Toplevel.
        """
        self.lift(self.__master)            # mise au premier plan de la Toplevel    
        self.how = self.__get_appOptions    # Procédure exécutée en sortie
        self.mainloop()                     # Entrée dans la Boucle principale, sortie par "self.Quit(how)"
        self.destroy()                      # Fermeture de la fenetre Toplevel
        return self.how

    def __get_appOptions(self) -> App_Options:
        self.__options.sport_file = self.vathletsportFile.get()
        self.__options.medal_file = self.vmedalTallyFile.get()
        self.__options.result_file = self.volyresultsFile.get()
        self.__options.athlete_file = self.vathletebioFile.get()
        self.__options.country_file = self.vcountryFile.get()
        self.__options.edition_file = self.volympicsFile.get()
        self.__options.athevent_file = self.veventsFile.get()
        self.__options.fullscreen = bool(self.vfullscreen.get())
        self.__options.saveCFGonquit = bool(self.vsaveonquit.get())
        self.__options.splashscreen = bool(self.vsplashscreen.get())
        self.__options.createEvtAthFile = bool(self.vcreatevtath.get())
        self.__options.search_options.cases = bool(self.vsearchCases.get())
        self.__options.search_options.whole = bool(self.vsearchWhole.get())
        self.__options.search_options.exact = bool(self.vsearchExact.get())
        self.__options.search_options.patronym = bool(self.vsearchPatrom.get())
        self.__options.search_options.multiId = bool(self.vhomonynId.get())
        self.__options.search_options.scaleId = self.vsearchScale.get()
        self.__options.search_options.regexp = bool(self.vregexp.get())
        self.__options.paramfilename = self.vconfigFile.get()
        self.__options.csvseparator = self.vseparatorCSV.get()
        self.__options.datelong = bool(self.vdatelong.get())
        self.__options.policy_family = self.vfontfamily.get()
        self.__options.default_printer = self.vdefprinter.get()
        self.__options.length_line = self.vlinelength.get()
        self.__options.datapath = self.vsystemFolder.get()
        self.__options.imagepath = self.vimageFolder.get()
        self.__options.backfilename = self.vbackground.get()
        self.__options.olympicpath = self.volympFolder.get()
        self.__options.helpfilename = self.vhelpFile.get()
        return self.__options
        
    def __ok_command(self, event:tk.Event=None):
        self.Quit(self.__get_appOptions())

    def __save_command(self):
        if __name__ != "__main__":
            self.__master.app_options = self.__get_appOptions()
            self.__master._save_CFG()
        else:
            self.Quit(self.__get_appOptions())

    def __cancel_command(self, event:tk.Event=None):
        """ Sortie de la Toplevel avec "None" en retour """
        self.Quit(None)            
                
    def Quit(self, how=None):
        self.how = how
        if self.how == None:
            self.state_bar.update_vltexte(" Info : Aucune modification des paramètres ne sera appliquée")
        else:
            self.state_bar.update_vltexte(" Info : Modification des paramètres effectuée")
        self.after(500, self.quit)    # Exit mainloop()

    @staticmethod
    def fixedfonts() -> list:
        from tkinter.font import Font, families
        return list(filter(lambda f:"Noto" not in f and Font(family=f).metrics("fixed") == True, sorted(families())))
    
    @staticmethod
    def witchScale(number:int) -> int:
        maxi,cpt = [10,100,1000,10000],0
        while maxi[cpt]-number < 0:
            if cpt == len(maxi)-1:
                break
            else:
                cpt += 1
        return maxi[cpt]

    
if __name__ == "__main__":
    
    from athlete import Athlete
    from linuxprt import Linux_InitPrinters
    from handle_csv import Handle_CSV
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")

    root = tk.Tk()
    options:App_Options = None
    root.msgbox = Win_MessageBox(root)
    root.infobox = Athlete_InfoWindow(root)

    root.app_parameters = Saveload_CFG()
    root.Printers = Linux_InitPrinters(root)
    if root.app_parameters.cfg_load():
        options = root.app_parameters.options
        new_options = Parameters(root, options).go()
        print(f"new_options:\n{new_options}")
        #options.createEvtAthFile = False
    else:
        print(f"Options not loaded. End of program")
        exit(2) 
    
    #handlecsv = Handle_CSV(root, options=options)

    #root.columnconfigure(list(range(20)), weight=1)
    #root.rowconfigure(list(range(20)), weight=1)
    
    #message = tk.StringVar( value="")
    #msgbox = Win_popup(root,message,title="essai")
    #msgbox.tag_configure("couleur", background="yellow")
    #msgbox.insert("1.0",f"Message\n","name","centre")
    #msgbox.insert(tk.END, f"\nligne 3, colonne 10\n")
    #msgbox.insert("end","Ligne 4\n")
    #msgbox.tag_add("couleur", "4.0","4.end+1c")
    
    #root.infobox.athlete = Athlete.ATHLETES_Dico[45153]
    #root.after(2000, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[57072],False)
    #root.after(2500, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[99797],False)
    #root.after(3000, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[5054],False)
    #root.after(3500, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[7011],False)
    #root.after(4000, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[126589],False)
    #root.after(4500, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[147283],False)
    #root.after(5000, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[132089],False)
    #root.after(5500, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[701866],False)
    #root.after(6000, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[1005730],False)
    #root.after(6500, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[11857],False)
    #root.after(2000, root.infobox.insert_athlete, Athlete.ATHLETES_Dico[13167],False)
    #root.after(9000, root.infobox.Quit)
    
    #resultats_List = list(set(Resultat.get_Olympics_Results_Details("obj",edition_id=1)))
    #resultbox = Resultat_InfoWindow(root, resultats_List)
    #root.after(9000, root.quit)
    root.mainloop()
