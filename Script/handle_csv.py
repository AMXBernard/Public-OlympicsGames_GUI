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

import time, re
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk

from configs import *
from functools import wraps
from athlete import Athlete,AthleteEvents
from gui_tools import My_LabelFrame,Window_StateBar,ScrolledListbox,Win_MessageBox
from country import Country,EditionGame,MedalTally
from resultats import Resultat
from sport import Sport
from math import nan

# -------------------------------------------------------------------------
def chrono(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = f(*args, **kwargs)
        end = time.perf_counter()
        print(f"{f.__name__} durée = {end - start:.6f}s")
        return result
    return wrapper
# -------------------------------------------------------------------------
def correct_position(position) -> int:
    dummy = position.split(' ', maxsplit=1)
    if len(dummy) >= 1 and dummy[0].isdigit():
        return int(dummy[0])
    else: return nan
# -------------------------------------------------------------------------

RE_NAMEID:re.Pattern = re.compile(r'^([\D ]+?) \((\d*)',flags=0)
RE_ATHLETE:re.Pattern = re.compile(r'\(([\d]+?)\)',flags=0)

class Handle_CSV():
    
    def __init__(self, master, options:App_Options=None):
        
        self.__master = master
        self.__options:App_Options = options
        self.msgbox = Win_MessageBox(master, nobtn=True)
        
        # ------ Patterns compilés pour la recherche d'athlètes etc ... -------
        
        # --- Initialisation options par défaut si 'options' invalide|None ----
        if not isinstance(options, App_Options): self.__options = App_Options()

        # Loading files : Olympics_Country.csv, Olympics_Games.csv and Olympic_Games_Medal_Tally.csv 
        if not Country.load_countryfile(self.msgbox, options=self.__options):
            self.msgbox.message = f"{'Fichier des pays/organisateurs non lu.':^50}"
            self.msgbox.after(2000)

        # ---------------- Loading file : Olympic_Results.csv -----------------
        if not Resultat.load_resultsfile(self.msgbox, options=self.__options):
            self.msgbox.message = f"{'Fichier des résultats non lu.':^50}"
            self.msgbox.after(2000)

        # ----------------- Loading file : athlete_events.csv -----------------
        if not AthleteEvents.load_athlete_events(self.msgbox, options=self.__options):
            self.msgbox.message = f"{'Fichier des athlètes events non lu.':^50}"
            self.msgbox.after(500)

        # --------------- Loading file : Olympic_Athlete_Bio.csv --------------
        if not Athlete.load_athlete_bio(self.msgbox, options=self.__options):
            self.msgbox.message = f"{'Fichier des athlètes non lu.':^50}"
            self.msgbox.after(2000)

        # ---------- Loading file : Olympic_Athlete_Event_Results.csv ---------
        if not Sport.load_sportfile(self.msgbox, options=self.__options):
            self.msgbox.message = f"{'Fichier des sports/épreuves non lu.':^50}"
            self.msgbox.after(2000)
        # ---------------------------------------------------------------------
        self.athlete = Athlete.ATHLETES_Dico
        self.edition = EditionGame.EDITIONS_Dict
        self.athletevent = AthleteEvents.ATHEVENTS_Dico
        self.medaltally = MedalTally.MEDALTALLY_Dict
        self.resultat = Resultat.RESULTATS_Dico
        self.country = Country.COUNTRY_Dico
        self.sport = Sport.SPORTS_Dico
        
        self.GLOBAL_AthSortList:list = ([])
        self.GLOBAL_AthleteListId:list = ([])
        self.GLOBAL_AthleteListName:list = ([])
        self.GLOBAL_CountryList:list = self.country.values()
        self.GLOBAL_EventList:list = self.athletevent.values()
        self.GLOBAL_EditionList:list = self.edition.values()
        self.GLOBAL_SportList:list = self.sport.values()
        
    @property
    def get_options(self) -> App_Options:
        return self.__options

    def load_OGG_File(self, mode:CMODETYPE) -> bool:
        if any(m == mode for m in ["Bio","Spt","Evt","Oly","Mdl","Noc","Res"]):
            ogg_methode:dict = {"Bio":Athlete.load_athlete_bio,          "Spt":Sport.load_sportfile,
                                "Evt":AthleteEvents.load_athlete_events, "Oly":EditionGame.load_editionGame,
                                "Mdl":MedalTally.load_medalTally,        "Noc":Country.load_countryfile,
                                "Res":Resultat.load_resultsfile, 
                               }
            ogg_methode[mode](self.msgbox, self.__options)
            self.msgbox.noButton(False)
            return True
        return False


class GUI_SearchSportEvt(tk.Toplevel):
    
    def __init__(self, master, handleCSV:Handle_CSV, mode:CMODETYPE="Ath", *args, **kwargs):

        from gui_tools import Athlete_InfoWindow    

        self.__master = master
        self.__mode:CMODETYPE = mode
        self.__options:App_Options = master.app_options
        self.__handleCSV:Handle_CSV = handleCSV
        self.__resultat_infowin = Athlete_InfoWindow(master)

        self.ttl_font = tkFont.Font(family='ubuntu',size=14,weight="normal",slant='italic')
        self.lbl_font = tkFont.Font(family='Consolas',size=10,weight='bold',slant='italic')
        self.spb_font = tkFont.Font(family='Consolas',size=9,weight='bold',slant='italic')
        self.rbt_font = tkFont.Font(family='ubuntu',size=11,weight="normal",slant='italic')
        toplevel_Title = "Rechercher les sports et épreuves des Olympiades" 
        # ---------------------------------------------------------------------
        sportlist = sorted(self.__handleCSV.sport.keys())
        self.vsportlist = tk.StringVar(value=sportlist)
        self.vathletelist = tk.StringVar()
        self.veventlist = tk.StringVar()
        # ---------------------------------------------------------------------
        self.__sport__,self.__event__ = tk.IntVar(value=0),tk.IntVar(value=0)             
        # ---------------------------------------------------------------------                
        tab_options:dict = {'bd':2,'bg':'tan','relief':'flat','padx':2,'pady':2}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)  
        # ---------------------------------------------------------------------
        self.event_add("<<AthleteSelect>>",'<Double-Button-1>','<Return>','<KP_Enter>')         
        self.protocol("WM_DELETE_WINDOW", self.Quit)
        self.minsize(1280,700)              # - taille minimun fenetre       
        self.title(toplevel_Title)          # - Tetre de la fenetre modale
        self.columnconfigure(list(range(20)), weight=1)
        self.rowconfigure(list(range(6,20)), weight=1)        
        self.rowconfigure(list(range(0,5)), weight=1)
        self.grid_anchor("w")
        self.cree_Widgets()
        self.update()
    
    def cree_Widgets(self):
        text = " Recherche parmi tous les sports et épreuves des Jeux Olympiques modernes (cf. Pierre De Coubertin) "
        frame_sportEvt = My_LabelFrame(self,col=0,row=0,cspan=20,rspan=20,font=self.ttl_font,text=text)
        text = " Tous les Sports Olympiques "
        frameSport = My_LabelFrame(frame_sportEvt,col=0,row=1,cspan=4,rspan=19,bg="#FDE7D5",
                                                                 font=self.lbl_font,text=text,pad=(2,2,0,0))
        text = " Toutes les Epreuves/Evènements Olympiques de la discipline "
        frameEvent = My_LabelFrame(frame_sportEvt,col=4,row=1,cspan=16,rspan=4,bg="#E8FCD7",
                                                                 font=self.lbl_font,text=text,pad=(2,2,0,0))
        text = " Tous les Athlètes ayant participés aux épreuves (trier par ...)"
        frameAthlete = My_LabelFrame(frame_sportEvt,col=4,row=5,cspan=16,rspan=16,bg="#E4F8E5",
                                                                 font=self.lbl_font,text=text,pad=(2,2,0,0))
        # ---------------------------------------------------------------------
        frameButtons= My_LabelFrame(frameAthlete,cspan=16,bg='#FCEEDA',pad=(2,2,0,3)) 
        tk.Button(frameButtons,text=" Athlète ",command=lambda mode="Ath":self.__sorted__(None,mode),relief="flat",
                          bg="#FCEED5",overrelief="flat",font=self.spb_font).grid(column=2,row=0,columnspan=2,sticky=('w'))
        tk.Button(frameButtons,text="  Genre  ",command=lambda mode="Sex":self.__sorted__(None,mode),relief="flat",
                          bg="#FCEED5",overrelief="flat",font=self.spb_font).grid(column=5,row=0,columnspan=2,sticky=('w'))
        tk.Button(frameButtons,text="Olympiade",command=lambda mode="Oly":self.__sorted__(None,mode),relief="flat",
                          bg="#FCEED5",overrelief="flat",font=self.spb_font).grid(column=8,row=0,columnspan=2,sticky=('w'))
        tk.Button(frameButtons,text="Pays/Fed.",command=lambda mode="Noc":self.__sorted__(None,mode),relief="flat",
                          bg="#FCEED5",overrelief="flat",font=self.spb_font).grid(column=11,row=0,columnspan=2,sticky=('w'))
        tk.Button(frameButtons,text="Classement",command=lambda mode="Rnk":self.__sorted__(None,mode),relief="flat",
                          bg="#FCEED5",overrelief="flat",font=self.spb_font).grid(column=14,row=0,columnspan=2,sticky=('w'))
        # ---------------------------------------------------------------------
        self.athlete_list = ScrolledListbox(frameAthlete,self.vathletelist,row=1,cspan=16,name="!athleteScrlBox",
                                                       rspan=16,bg="#FCF8F5",font=self.lbl_font,vbar=True,vsel=True)
        self.athlete_list.bind("<<AthleteSelect>>", self.__win_event)
        self.athlete_list.selection_set(0)
        self.athlete_list.activate(0)        
        # ---------------------------------------------------------------------
        
        self.event_list = ScrolledListbox(frameEvent,self.veventlist,cspan=16,name="!eventScrlBox",
                                                              rspan=4,bg="#FCF8F5",vbar=True,vsel=True)
        self.event_list.bind("<<ListboxSelect>>", self.__select_athlete)
        self.event_list.selection_set(0)
        self.event_list.activate(0)        
        
        # ---------------------------------------------------------------------
        self.sport_list = ScrolledListbox(frameSport,self.vsportlist,cspan=4,name="!sportScrlBox",
                                                              rspan=20,bg="#FCF8F5",vbar=True,vsel=True)
        self.sport_list.bind("<<ListboxSelect>>", self.__select_event)
        self.sport_list.selection_set(0)
        self.sport_list.activate(0)
        # ---------------------------------------------------------------------
        self.sport_list.event_generate("<<ListboxSelect>>")
        
    def __select_event(self, event:tk.Event=None):
        w = event.widget if event else ScrolledListbox    # self.sport_list
        if w.curselection():
            # ---------- liste des épreuves fonction du sport choisi ----------    
            idx,sport = w.getSelectItem()
            self.veventlist.set(sorted(list(AthleteEvents.get_Olympics_Events_List("str",select=("event"),sport=sport))))
            self.__select_athlete(event)
        return 'break'    

    def __select_athlete(self, event:tk.Event=None):
        w = event.widget if isinstance(event,tk.Event) else self.event_list
        idx,evt = w.getSelectItem()
        if w._name == "!eventScrlBox": 
            self.__event__.set(idx) 
            w.activate(idx)
        elif w._name == "!sportScrlBox":
            self.event_list.activate(self.__event__.get())
            self.__sport__.set(idx)
        # --------- Affichage de la liste des athlètes selon '__mode' ---------
        self.__sorted__(event, self.__mode)
        return 'break'
            
    def __sorted__(self, evt:tk.Event, mode:CMODETYPE="Ath"):
        # ---------------------------------------------------------------------
        def position(pos:str) -> int:
            return int(pos) if pos.isdigit() else sum([ord(c) for c in pos])
        # ---------------------------------------------------------------------
        def athletes(sport:str, event:str) -> list:
            return AthleteEvents.get_Olympics_Events_List("obj",sport=sport,event=event)
        # ---------------------------------------------------------------------
        if evt and evt.widget._name == "!sportScrlBox":
            sport = evt.widget.getSelectItem()[1]
            event = self.event_list.get('active')
        elif evt and evt.widget._name == "!eventScrlBox":
            sport = self.sport_list.get('active')
            event = evt.widget.getSelectItem()[1]
        else:
            sport, event = self.sport_list.get('active'), self.event_list.get('active')
        # ---------------------------------------------------------------------
        if mode == "Ath":
            athletelist = sorted(athletes(sport=sport,event=event),key=lambda ae:ae.name)
        elif mode == "Sex":
            athletelist = sorted(athletes(sport=sport,event=event),key=lambda ae:ae.sex)
        elif mode == "Oly":
            athletelist = sorted(athletes(sport=sport,event=event),key=lambda ae:ae.edition)
        elif mode == "Noc":
            athletelist = sorted(athletes(sport=sport,event=event), 
                              #key=lambda ae:Athlete.ATHLETES_Dico.get(ae.athlete_id, Athlete.DumATHLETE()).country.noc)
                                    key=lambda ae:Athlete.Get_Athlete(ae.athlete_id).country.noc)
        elif mode == "Rnk":
            athletelist = sorted(athletes(sport=sport,event=event),key=lambda ae:position(ae.position))
        else:
            athletelist = athletes(sport=sport,event=event)
        # ---------------------------------------------------------------------
        if athletelist:
            maxl1 = len(max(athletelist, key=lambda ae:len(ae.name)).name)
            maxl2 = len(f"{max(athletelist, key=lambda ae:ae.athlete_id).athlete_id}")
            maxlength = max(0, maxl1 + maxl2)+3
        else:
            self.vathletelist.set("")
        # ----------- Création de la liste des athlètes à afficher ------------  
        self.vathletelist.set(list(map(lambda ae:self.__get_athleteEvent(ae, maxlength), athletelist)))        
        self.__mode = mode
        return 'break'
            
    def __win_event(self, event:tk.Event=None):
        w = event.widget if isinstance(event,tk.Event) else self.athlete_list
        if  w.curselection() and  w._name == "!athleteScrlBox":  
            idx,sport = w.getSelectItem()
            found = RE_ATHLETE.search(sport).groups()
            if found:
                self.__resultat_infowin.athlete = self.__handleCSV.athlete.get(int(found[0]))
            w.selection_set(idx)
            w.activate(idx)
        return 'break'    
            
    def __get_athleteEvent(self, athevent:AthleteEvents, maxl:int) -> str:
        dummy = f"{athevent.name} ({athevent.athlete_id})"
        name = f"{dummy:<{maxl}}"; sex = f"({athevent.sex[0]})"
        dummy = self.__handleCSV.athlete.get(athevent.athlete_id, Athlete.DumATHLETE()).country.noc
        noc = f"{dummy}" if not "No" in dummy else "   "
        medal = f" Medal: {athevent.medal}" if athevent.medal in medalType_list else f"Pos: {athevent.position}"
        event =  f"{athevent.edition} ({athevent.city}), {athevent.sport} ({athevent.event}) {medal}"
        return f"{name}{sex} - {noc} : {event}"
    
    def Quit(self):
        self.destroy()
        
        
class GUI_EditionGame(tk.Frame):
        
    def __init__(self,master,data:dict,col=0,row=0,cspan=1,rspan=1,pad=(0,0,0,0),sticky='nsew',*args,**kwargs):        # -------------------------------------------------

        from gui_tools import Athlete_InfoWindow    

        self.master = master
        self.edition_dico = data
        self.selected_edit:str = ""
        self.old_selected = -1
        self.BSPAN = 4
        self.CSPAN = max(8, cspan-self.BSPAN)
        
        self.vcitylist = tk.StringVar()
        self.vcountrylist = tk.StringVar()
        self.vatheventlist = tk.StringVar()
        self.vathletelist = tk.StringVar()
        self.vmedaltally = tk.StringVar()
        self.vsportevent = tk.StringVar()
        
        self.vedition_msg1 = tk.StringVar()
        self.vedition_msg2 = tk.StringVar()
        self.vedition_msg3 = tk.StringVar()
        
        # ----------- création de la liste des editions olympiques ------------
        self.editionsList = list(map(lambda ed:ed.edition.strip(),list(sorted(data.values(),key=lambda ed:(ed.year,ed.edition_id),reverse=False))))
        self.veditiongame = tk.StringVar(value=self.editionsList, name="!veditionGame")
        # ----- Création/Initialisation de la fenètre d'info des athlètes -----
        self.__athlete_infowindow = Athlete_InfoWindow(master)        
        
        self.consol10 = tkFont.Font(family='Consolas', size=10, weight='bold', slant='italic') 
        self.lbx_font = tkFont.Font(family='Serif', size=10, weight='bold', slant='italic')
        self.tle_font = tkFont.Font(family='Consolas', size=14, weight='bold', slant='italic') 
        self.lbl_font = tkFont.Font(family='Consolas', size=12, weight='bold', slant='italic') 
        self.btn_font = tkFont.Font(family='Helvetic', size=12, weight='normal', slant='italic') 
        
        tab_options:dict = { 'bg':'ivory', 'bd':3, 'relief':'sunken'}
        for key in tab_options:
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        
        super().__init__(master, *args, **kwargs)
        #self.grid(column=col,row=row,columnspan=self.BSPAN,rowspan=rspan,
        self.grid(column=col,row=row,padx=pad[0],pady=pad[1],ipadx=pad[2],ipady=pad[3],sticky=sticky)
        self.grid_anchor('center')
        
        self.editGame_Scrollbox = ScrolledListbox(self.master,self.veditiongame,0,0,cspan=self.BSPAN,rspan=rspan,vsel=True,
                                            pad=pad,ffont=self.consol10,ftext="  Editions Olympiques  ",width=20,sticky="nsew")
        self.editGame_Scrollbox.bind("<<ListboxSelect>>", self.get_select_EditionGame)
        self.editGame_Scrollbox.select_set(0)
        self.editGame_Scrollbox.activate(0)
        
        self.editFrame = My_LabelFrame(self.master,col=self.BSPAN,row=row,bd=3,relief="groove",font=self.consol10,
                  text=" Informations sur les éditions des Jeux Olympiques Modernes ",cspan=self.CSPAN,rspan=rspan,pad=(10,10,0,0),sticky="nsew")
        tk.Label(self.editFrame,bg="ivory",textvariable=self.vedition_msg1,
                    font=self.tle_font).grid(column=0,row=0,columnspan=self.CSPAN,sticky="nsew")
        tk.Label(self.editFrame,bg="ivory",textvariable=self.vedition_msg2,
                    font=self.lbl_font).grid(column=0,row=1,columnspan=self.CSPAN,sticky="nsew")
        tk.Label(self.editFrame,bg="ivory",textvariable=self.vedition_msg3,
                    font=self.lbl_font).grid(column=0,row=2,columnspan=self.CSPAN,sticky="nsew")
        # ---------------------------------------------------------------------
        defmessage = " Info : Sélectionnez un pays pour afficher les athlètes et les épreuves auquelles ils ont participé."
        self.statebar = Window_StateBar(self.editFrame,"",0,col=0,row=18,cspan=self.CSPAN,bd=3,relief="sunken",
                                                sticky="sew",padx=5,pady=3,txtfont=self.lbx_font,defMessage=defmessage)
        self.editFrame.grid_remove()
        # ---------------------------------------------------------------------
        self.vathletelist.initialize(["Veuillez sélectionner un pays pour visualiser les athlètes ayant participés à cette Olympiade.",])
        self.selected_edit = self.edition_dico[self.editGame_Scrollbox.get(0)]
        print(f"class GUI_EditionGame__selected_edit: {self.selected_edit}")
        self.create_edition_frame(0)

    def get_select_EditionGame(self, event:tk.Event=None):
        if event is not None:
            w = event.widget
            if w.curselection() and w == self.editGame_Scrollbox:
                selected = w.get(int(w.curselection()[0])).strip()
                # -------------------- RAZ of athlete list --------------------
                if self.selected_edit and selected != self.selected_edit.edition: 
                    self.vathletelist.initialize(["Veuillez sélectionner un pays pour visualiser les athlètes ayant participés à cette Olympiade.",])
                # -------------------------------------------------------------
                if not selected in self.selected_edit.edition:
                    self.selected_edit:EditionGame = self.edition_dico[selected]
                    self.statebar.update_vltexte(" Info : Lecture des données en cours ...")
                    self.create_edition_frame(w.curselection()[0])
                else:
                    return 'break'    
        else:        
            print(f"get_select_EditionGame(event): {event}")
        
    def create_edition_frame(self, index:int):
        if self.editFrame.winfo_ismapped() and self.old_selected == index:
            self.old_selected= -1
            return 'break'
        else:
            self.complete_edition_frame(index)
            self.old_selected = index 
            self.editFrame.grid()

    def __scHeight(self, height, maxi:int=2) -> int:
        return min(max(2,height),maxi)

    def __unmarkMarkSelected(self, index:int):
        """ Methode permettant de dé-selectionner puis sélectionner la nouvelle 
            édition Olympique choisie par l'intermédiaire de la liste des Villes 
            organisatrices ou de la liste des pays organisateurs.
        """
        # ---------------------------------------------------------------------
        self.statebar.update_vltexte(" Info : Lecture des données en cours ...")
        # ---------------------------------------------------------------------
        self.editGame_Scrollbox.unmark_selected(None)                
        self.editGame_Scrollbox.marked_Selected = [index,]
        self.editGame_Scrollbox.activate(index=index)
        self.editGame_Scrollbox.select_set(index)
        self.editGame_Scrollbox.see(index=index)


    def create_Info_Ville(self, edition:EditionGame):
        dummy = list(map(lambda cl:f"Ed.{cl.edition_id:>3} - {cl.edition} - {cl.competition_date if TIRET not in cl.competition_date else cl.isHeld}",
                                    list(filter(lambda c:c.city == edition.city and c.edition_id != edition.edition_id, EditionGame.EDITIONS_List))))
        self.vcitylist.set(sorted(dummy, key=lambda c:c.split('-')[0]))
        title = f" Autres éditions Olympiques dans cette même ville: {edition.city} "
        self.cityList = ScrolledListbox(self.editFrame, self.vcitylist,col=0,row=3,bg="#E0FCC1",frelief="ridge",name="!cityListBox",
                                pad=(10,5,0,0),ffont=('Consolas 9 bold italic'),fbg="#E0FCC1",cspan=self.CSPAN//2,vsel=True,ftext=title,
                                            activestyle="dotbox",font=self.lbx_font,height=self.__scHeight(len(dummy),3),vbar=(len(dummy)>3))
        self.cityList.bind("<<ListboxSelect>>", self.get_event_InfoVille)
        self.cityList.activate(0)

    def get_event_InfoVille(self, event:tk.Event=None):
        if event:
            w = event.widget
            if "!cityListBox" in w.name() and w.curselection():
                self.vathletelist.initialize(["Veuillez sélectionner un pays pour visualiser les athlètes ayant participés à cette Olympiade.",])
                selected = w.get(int(w.curselection()[0])).split(' - ')[1].strip()
                index = self.editGame_Scrollbox.index(self.editionsList.index(selected))
                self.selected_edit = EditionGame.EDITIONS_Dict[selected]
                self.__unmarkMarkSelected(index=index)
                self.create_edition_frame(index=index)
        else:        
            print(f"get_event_InfoVille(event): {event}")

    def create_Info_Country(self, edition:EditionGame):
        dummy = list(map(lambda cl:f"Ed.{cl.edition_id:>3} - {cl.edition} - {cl.competition_date if TIRET not in cl.competition_date else cl.isHeld}",
                                        list(filter(lambda c:c.noc == edition.noc and c.edition_id != edition.edition_id, EditionGame.EDITIONS_List))))
        self.vcountrylist.set(sorted(dummy, key=lambda c:c.split('-')[0]))
        title = f" Autres éditions Olympiques dans le même pays: {COUNTRY_Dico[Country.NOC_Dict[edition.noc].country]} "
        self.countryList = ScrolledListbox(self.editFrame, self.vcountrylist,col=self.CSPAN//2,row=3,bg="#AEE5FF",vbar=(len(dummy)>3),
                                                    name="!countryListBox",pad=(10,5,0,0),frelief="ridge",ffont=('Consolas 9 bold italic'),
                                                                vsel=True,fbg="#AEE5FF",cspan=1+self.CSPAN//2,font=self.lbx_font,ftext=title,
                                                                      selectborderwidth=0,activestyle="dotbox",height=self.__scHeight(len(dummy),3))
        self.countryList.bind("<<ListboxSelect>>", self.get_event_CountryList)
        self.countryList.activate(0)
    
    def get_event_CountryList(self, event:tk.Event=None):
        if event:
            w = event.widget
            if "!countryListBox" in w.name() and w.curselection():    
                self.vathletelist.initialize(["Veuillez sélectionner un pays pour visualiser les athlètes ayant participés à cette Olympiade.",])    
                selected = w.get(int(w.curselection()[0])).split(' - ')[1].strip()
                index = self.editGame_Scrollbox.index(self.editionsList.index(selected))
                # -------------------------------------------------------------
                if selected != self.selected_edit.edition: self.__unmarkMarkSelected(index=index)
                # -------------------------------------------------------------
                self.selected_edit = EditionGame.EDITIONS_Dict[selected]    
                self.create_edition_frame(index=index)
        else:        
            print(f"get_event_CountryList(event): {event}")

    def create_Info_Medaltally(self, edition:EditionGame):
        total_medals:int = 0
        war_dico:dict = {1916:"1ère guerre mondiale (1914-1918)",
                         1940:"2ème guerre mondiale (1939-1945)", 1944:"2ème guerre mondiale (1939-1945)"}
        
        # ----------------- on récupère les pays médaillés --------------------
        medalTally_List = MedalTally.MEDALTALLY_Dict.get(edition.edition,[])
        noc_medaltally = set(map(lambda mt:mt.noc, medalTally_List))
        # ----------- on récupère les pays avec les non médaillés -------------
        sports = Sport.get_Olympics_Sport_Result('obj', edition=edition.edition); 
        noc_sports = set(map(lambda sport:sport.noc, sports))
        # ------ Ajout des MedalTally des pays non médaillés à la liste -------
        [medalTally_List.append(MedalTally(edition.edition,edition.edition_id,edition.year,
                                    Country.NOC_Dict[noc].country,noc,0,0,0,0)) for noc in list(noc_sports - noc_medaltally)]
        # ---------------------------------------------------------------------
        if medalTally_List: total_medals = sum(list(map(lambda mt:mt.total, medalTally_List)))
        dummy = list(map(lambda mt:f"{mt.country:<22} : {self.__createString_Medals(mt)}", medalTally_List))
        dummy2 = list(map(lambda sp:f"{sp[0]} ({sp[1]})",
                        Sport.get_Olympics_Sport_Result("str", select=("sport","event"), edition=edition.edition)))
        self.vmedaltally.set(dummy); self.vsportevent.set(dummy2)
        # -------------------------------------------------------------
        title = f" Pays ayant participés à cette Olympiade: {total_medals} médailles gagnées "
        self.medaltallyList = ScrolledListbox(self.editFrame, self.vmedaltally,col=0,row=5,bg="#D6C6EB",font=self.consol10,
                        ftext=title, frelief="ridge",ffont=self.consol10, fbg="#D6C6EB", selectborderwidth=0, pad=(10,10,0,0),vsel=True,
                           activestyle="dotbox",cspan=self.CSPAN//2,name='!medalTallyBox',height=self.__scHeight(len(dummy),12),vbar=(len(dummy)>12))
        self.medaltallyList.bind("<<ListboxSelect>>", self.get_select_SportList)
        # -------------------------------------------------------------
        title2 = f" Evènements sportif de cette Olympiade: {len(dummy2)} épreuves "
        self.sporteventList = ScrolledListbox(self.editFrame,self.vsportevent,col=self.CSPAN//2,row=5,bg="#F0E4A4",font=self.consol10,
                        vsel=True,frelief="ridge",ffont=self.consol10,fbg="#F0E4A4",selectborderwidth=0,cspan=1+self.CSPAN//2,pad=(10,10,0,0),
                                   activestyle="dotbox",ftext=title2,name='!sportEventBox',height=self.__scHeight(len(dummy2),12),vbar=(len(dummy2)>12))
        self.sporteventList.bind("<<ListboxSelect>>", self.get_select_EventList)
        # -------------------------------------------------------------
        labelText = f"{' Nom des athlètes':^26}{'Sports et épreuves':^150}{'Classement':^30}"
        frameText = f"\tPays : {COUNTRY_Dico[Country.NOC_Dict[edition.noc].country]:^40}Olympiade (Ed.{edition.edition_id}):{edition.edition:^30}"
        self.athLblFrame = My_LabelFrame(self.editFrame,col=0,row=8,cspan=self.CSPAN,pad=(10,10,5,5),rspan=9,
                                                                            bg="#FFE3D3",text=frameText,font=self.lbl_font) 
        self.sportathletelistbox = ScrolledListbox(self.athLblFrame,self.vathletelist,col=0,row=0,cspan=self.CSPAN,activestyle="dotbox",
                                       rspan=13,ftext=labelText,ffont=self.lbx_font,name="!sportAthleteListbox",vbar=False,font=self.consol10)
        self.sportathletelistbox.bind("<<ListboxSelect>>", self.__athlete_InfoWin)
        # -------------------------------------------------------------
        #self.medaltallyList.selection_set(0)
        self.medaltallyList.activate(0)
        
    def __createString_Medals(self, mt:MedalTally) -> str:
        return f"{mt.total:>3} médaille(s), {mt.gold} Or, {mt.silver} Argent et {mt.bronze} Bronze" \
                                                if mt.total>0 else "  Aucune mdaille gagnée à cette Olympiade"
                                                
    def __athlete_InfoWin(self, event:tk.Event=None):
        if event and isinstance(event.widget, ScrolledListbox):
            w = event.widget
            if w.name() == "!sportAthleteListbox" and w.curselection():
                athname = w.get(w.curselection()[0]).split(' : ')[0].strip()
                #print(f"__athlete_InfoWin__w.get(curselection()[0]): {w.get(w.curselection()[0])}")
                #athlete = Athlete.ATHLETES_Dico.get(Athlete.ATHLETE_ID_Dico.get(athname, [0,])[0], Athlete.DumATHLETE())
                athlete = Athlete.Get_Athlete(Athlete.ATHLETE_ID_Dico.get(athname, [0,])[0])
                self.__athlete_infowindow.athlete = athlete
        else:        
            print(f"__athlete_InfoWin(event): {event}")

    def __prepareAthleteList(self, sport:Sport) -> str:
        medaltally_dico:dict = {'Gold':'M(Or)','Silver':'M(Argent)','Bronze':'M(Bronze)'}
        medaille = medaltally_dico.get(sport.medal, '')
        dumAthlete = Athlete(sport.ath_id,sport.athlete.name,"","",0.0,"",Country.NOC_Dict[sport.noc].country,sport.noc,"","",[])
        athlete = sport.athlete if isinstance(sport.athlete, Athlete) else dumAthlete
        sportEvent = f"{athlete.name:<26} : {sport.sport:<26} ({sport.event})"
        position = f"{sport.position}, {medaille} "
        return f"{sportEvent:<130} {position:<10}"
        
    def get_select_SportList(self, event:tk.Event=None):
        """ Affichage de la liste des athlètes lors de de sélection du pays """
        w = event.widget if event else self.medaltallyList
        if "!medalTallyBox" in w.name() and w.curselection():
            # ---------- Remise à blanc de la liste des athlètes ----------
            self.sportathletelistbox.selection_clear(0, tk.END)
            # -------------------------------------------------------------
            edition = self.selected_edit.edition
            selected = w.get(int(w.curselection()[0])); print(f"get_select_SportList(selected): {selected}")
            noc = list(filter(lambda cn:cn.country == selected.split(':')[0].strip(), Country.NOC_List))[0].noc
            athleteList = sorted(Sport.get_Olympics_Sport_Result("obj", select="athlete", edition=edition, noc=noc), 
                                                  key=lambda spt:(spt.sport,correct_position(spt.position),spt.athlete.name))
            if athleteList:
                self.vathletelist.set([self.__prepareAthleteList(athlete) for athlete in athleteList])
                self.__itemcolor_medalList(athleteList, self.sportathletelistbox)
            else:
                self.vathletelist.set(["Aucun athlète n'a été trouvé pour ce pays",])  
            # -------------------------------------------------------------
            frameText = f"\tPays : {COUNTRY_Dico[Country.NOC_Dict[noc].country]:^40}Olympiade (Ed.{self.selected_edit.edition_id}):{edition:^30}"
            self.athLblFrame.configure(text=frameText)
            # -------------------------------------------------------------
        else:
            print(f"get_select_SportList(event): {event}")
        
    def get_select_EventList(self, event:tk.Event=None):
        """ Affichage de la liste des athlètes lors de la sélection du sport/épreuve """
        w = event.widget if event else self.sporteventList
        if "!sportEventBox" in w.name() and w.curselection():
            # ---------- Remise à blanc de la liste des athlètes ----------
            self.sportathletelistbox.selection_clear(0, tk.END)
            # -------------------------------------------------------------
            try:
                s,e = w.get(int(w.curselection()[0])).split(' (', maxsplit=1)
                sport, spevent = s.strip(), e.strip().replace(")","")
            except ValueError as msg:
                print(f"ValueError: {w.get(int(w.curselection()[0]))}")    
            # -------------------------------------------------------------
            noc = Country.COUNTRY_Dico[self.medaltallyList.get('active').split(':')[0].strip()].noc 
            atheventList = sorted(Sport.get_Olympics_Sport_Result("obj",sport=sport,noc=noc,event=spevent,
                                   edition=self.selected_edit.edition),key=lambda spt:correct_position(spt.position))
            if atheventList:
                self.vathletelist.set([self.__prepareAthleteList(athlete) for athlete in atheventList])
                self.__itemcolor_medalList(atheventList, self.sportathletelistbox)
            else:
                self.vathletelist.set(["Aucun athlète n'a été trouvé pour cette épreuve sportive.",])  
        else:
            print(f"get_select_EventList(event): {event}")

    def __itemcolor_medalList(self, athletelist:list, listbox:ScrolledListbox):
        """ coloration de la rubrique de la listbox fonction de la médaille """
        for index in range(listbox.size()):
            medal = athletelist[index].medal
            listbox.itemconfigure(index,bg=MEDALCOLOR_Dico.get(medal, "ivory"))
        
    def complete_edition_frame(self, index:int):
        # ---------------------------------------------------------------------
        dico_type:dict = ({"Summer":"été", "Winter":"hiver","Intercalated":"Intercalés'","Equestrian":"Equestres'"})
        war_dico:dict = {1916:"1ère guerre mondiale (1914-1918)",
                         1940:"2ème guerre mondiale (1939-1945)", 1944:"2ème guerre mondiale (1939-1945)"}
        edition:EditionGame = EditionGame.EDITIONS_Dict[self.editGame_Scrollbox.get(index)]
        # ---------------------------------------------------------------------        
        msg1 = f"{edition.edition_id}{'ère' if edition.edition_id == 1 else 'ème'} édition des Jeux Olympiques \
{'d' if edition.type in ['Summer','Winter'] else ''}'{dico_type[edition.type]} pour l'année {edition.year}."
        debut = "Ils se dérouleront" if now.year < edition.year else "Ils se sont déroulés"
        msg2 = f"{debut} à {edition.city} ({Country.NOC_Dict[edition.noc].noc})."
        if edition.start_date:
            debut = "Ils auront lieu du" if now.year < edition.year else "Ils ont eu lieu du"
            msg3 = f"{debut} {edition.start_date} au {edition.end_date} et les compétitions du {edition.competition_date}"
        else:
            if edition.competition_date == TIRET and isinstance(edition.isHeld,str):
                if edition.year not in war_dico:
                    msg3 = 'Dates non communiquées, non référencées.'
                else:
                    msg3 = f"{war_dico[edition.year]}: Edition non maintenue."
            else:
                debut = "Les compétitions se dérouleront du" if now.year < edition.year else "Les compétitions ont eu lieu du"
                msg3 = f"{debut} {edition.competition_date}"
            
        self.vedition_msg1.set(f"{msg1:^90}")
        self.vedition_msg2.set(f"{msg2:^90}")
        self.vedition_msg3.set(f"{msg3:^90}")
        
        self.create_Info_Country(edition)
        self.create_Info_Ville(edition)
        self.create_Info_Medaltally(edition)
        self.statebar.update_vltexte("", 0)
        self.editGame_Scrollbox.focus()
        

class GUI_SearchAthlete(tk.Toplevel):
    
    def __init__(self, master=None, handleCSV:Handle_CSV=None, searchtype:SEARCHTYPE="global", *args, **kwargs):

        from gui_tools import Athlete_InfoWindow    

        self.__master = master
        self.__options:App_Options = master.app_options
        self.__handleCSV:Handle_CSV = handleCSV
        self.__searchtype:SEARCHTYPE = searchtype
        self.__athlete_infowindow = Athlete_InfoWindow(master)

        self.ttl_font = tk.font.Font(family='ubuntu',size=14,weight="normal",slant='italic')
        self.lbl_font = tk.font.Font(family='Consolas',size=10,weight='bold',slant='italic')
        self.spb_font = tk.font.Font(family='Consolas',size=9,weight='bold',slant='italic')
        self.rbt_font = tk.font.Font(family='ubuntu',size=11,weight="normal",slant='italic')
        toplevel_Title = "Recherche d'athlètes parmi les pays et/ou les Olympiades" 

        self.__caseSensitive:bool = self.__options.search_options.cases
        self.vcaseSensitive = tk.IntVar(value=int(self.__caseSensitive))
        self.__wholeWord:bool = self.__options.search_options.whole
        self.vwholeWord = tk.IntVar(value=int(self.__wholeWord))
        self.__exactWord:bool = self.__options.search_options.exact
        self.vexactWord = tk.IntVar(value=int(self.__exactWord))
        self.__patronym:bool = self.__options.search_options.patronym
        self.vpatronym = tk.IntVar(value=int(self.__patronym))
        self.__multiId:bool = self.__options.search_options.multiId
        self.vmultiId = tk.IntVar(value=self.__multiId)
        self.__scaleId:int = self.__options.search_options.scaleId
        self.vscaleId = tk.IntVar(value=self.__scaleId)
        self.optsearch_scaleId = self.vscaleId.get()
        
        self.__sortbyNCECS:SORTLISTYPE = ""
        self.vsortncecs = tk.StringVar(value=self.__options.search_options.sortList)
        
        self.vsearchAthList = tk.StringVar()
        self.vathleteNumber = tk.StringVar()
        self.vsearchEntry = tk.StringVar(value="")
        self.vsearchNbutton = tk.StringVar(value=" Rechercher par Nom ")
        self.vsearchIbutton = tk.StringVar(value=" Rechercher par Id ")
        self.vsearchbyname = tk.StringVar(value=" Nom à rechercher ...")
        self.vsearch_by_Id = tk.StringVar(value=" Id à rechercher ...")
        self.vbuttoncountry = tk.StringVar(value="Pressez ce bouton, choisissez un Pays/Com./Féd.")
        self.vbuttonedition = tk.StringVar(value="Pressez ce bouton, choisissez une Olympiade")
        self.vsearchedition = tk.StringVar(value="No edition")
        self.vsearchcountry = tk.StringVar(value="No country")
        # ---------------------------------------------------------------------
        self.vmultiButton = tk.StringVar(value=" Recherche des athlète par choix multi-critères selon les options définies ")
        self.vmultisport = tk.StringVar(value="All sports")
        self.vmultiedition = tk.StringVar(value="All editions")
        self.vmultiedition_id = tk.StringVar(value="All Id")
        self.vmulticountry = tk.StringVar(value=Country("-/-","All countries").noc)
        self.vmultievent = tk.StringVar(value="All events")
        self.vmultiathlete = tk.StringVar(value="All athletes")
        self.vmultiath_id = tk.StringVar(value="All athletes Id")
        self.vmultiathlete_sex = tk.StringVar(value="All genre")
        self.vmultiposition = tk.StringVar(value="All positions")
        self.vmultimedal = tk.StringVar(value="All medals")
        self.vmultis_team = tk.StringVar(value="All modes")
        self.vmultiresult = tk.StringVar(value="All results")
        self.vmultiresult_id = tk.StringVar(value="All results_id")
        self.vmultifirstname = tk.StringVar(value="... prénom ...")
        self.vmultilastname = tk.StringVar(value="... nom ...")

        self.dumStringvar = tk.StringVar(value='All ')
        self.sportStringvar = (self.vmultisport,self.vmultiedition,self.vmultiedition_id,self.vmulticountry,
                                 self.vmultievent,self.vmultiathlete,self.vmultiath_id,self.vmultiathlete_sex,
                                    self.vmultiposition,self.vmultimedal,self.vmultiresult_id,self.vmultiresult,self.vmultis_team)
        self.athleteStringvar = (self.vmultiedition_id,self.vmultiathlete,self.dumStringvar,self.dumStringvar,self.dumStringvar,
                                        self.dumStringvar,self.vmulticountry,self.dumStringvar,self.dumStringvar,self.vmultievent)
        self.resultStringvar = ()
        self.eventStringvar = ()
        # ---------------------------------------------------------------------
        self.vmultigenre = tk.StringVar(value="Non genré")
        self.vmultiAthleteInfo = tk.StringVar(value="Choisissez un athlète")
        self.__vmultiAthInfo = tk.StringVar(value=["All athletes",0])
        # ---------------------------------------------------------------------
        self.vmulticities = tk.StringVar(value="All cities")
        # ---------------------------------------------------------------------        
        self.athleteList, self.sportObjList = [], []      
        self.editionList,self.nocList,self.countryList = [] ,[], []
        self.sportList,self.eventList,self.positionList  = [] ,[], []
        # ---------------------------------------------------------------------        
        self.button_image = tk.PhotoImage(file=op.join(self.__options.imagepath,"cross-circle_24.png"))
        # ---------------------------------------------------------------------        
        # ---------------------------------------------------------------------                
        tab_options:dict = {'bd':2, 'bg':'tan', 'relief':'flat' }        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)

        super().__init__(master, *args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.Quit)
        self.minsize(1024, 768)             # - taille minimun fenetre       
        self.title(toplevel_Title)          # - Tetre de la fenetre modale
        self.event_add("<<GlobalListboxSelect>>","<Double-Button-1>","<Return>")
        self.event_add("<<GlobalListboxSearch>>","<KP_Enter>")
        self.bind("<<GlobalListboxSearch>>", self.__search_by_multipass)
        self.columnconfigure(list(range(16)), weight=1)
        self.rowconfigure(list(range(3,19)), weight=1)
        self.grid_anchor("w")
        self.cree_Widgets()
        self.update()
    
    def cree_Widgets(self):
        # -------------- construction des widgets de la fenètre ---------------
        label = f" Athlètes trouvé(e)s pour l'Olympiade ou les Olympiades sélectionnée(s) tous Pays/Comité/Fédérations confondus : "
        self.vathleteNumber.set(label); scolor = "#FFF0DE"
        self.labelFrame = My_LabelFrame(self,cspan=16,rspan=2,bd=3,bg="#D48151",relief="groove",pad=(2,0,0,2))
        tk.Label(self.labelFrame,bg='ivory',anchor="center",font=self.ttl_font,relief="flat",bd=0,
                        textvariable=self.vathleteNumber).grid(column=0,row=0,columnspan=16,ipady=5,sticky="nsew")
        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        athleteFrame = My_LabelFrame(self,col=0,row=3,cspan=16,rspan=16,bd=3,relief="ridge",pad=(2,3,0,0))
        titre_ath = f"{' Nom des athlètes (Id)':^40}{'Pays/fédération d origine':^64}{'sexe':^12}{'Corpulence':^16}{'Sports/épreuves auquel il(le) a participé':^80}"
        titre_edt = f"{' Nom des athlètes (Id)':^40}{'Pays/fédération d origine':^64}{'Olympiade':^30}{'  Ville  ':^20}{'Sports/épreuves auquel il(le) a participé':^80}"
        self.global_scrollbox = ScrolledListbox(athleteFrame,self.vsearchAthList,0,0,cspan=16,rspan=16,hbar=True,
                                            name="!globalScrollBox",frelief="groove",ffont=self.lbl_font,font=self.lbl_font)
        titre = titre_ath if self.__searchtype in ["nom","Id"] else \
                titre_edt if self.__searchtype in ["olympiade","pays","multi"] else f"{' ':^100}"
        self.global_scrollbox.fconfigure(text=titre,bg="wheat", font=("Helvetic 11 normal italic"), labelanchor="nw")
        #self.global_scrollbox.bind("<<GlobalListboxSearch>>", self.__search_by_multipass)
        self.global_scrollbox.bind("<<GlobalListboxSelect>>",self.__athlete_InfoSelect)
        self.global_scrollbox.bind("<<ListboxSelect>>",self.__athlete_ButtonSelect)
        # ---------------------------------------------------------------------
        if self.__searchtype == "global":
            self.sortFrame = My_LabelFrame(self, col=0,row=3,cspan=16,bd=0,bg="wheat",relief="flat",pad=(15,6,0,0),sticky="new")
            self.sortFrame.columnconfigure(list(range(8)), weight=0)
            tk.Radiobutton(self.sortFrame,bg="wheat",text="  Nom des Athlètes (Id)  ",variable=self.vsortncecs,
                    anchor="center",value="name",activebackground="wheat",font=self.rbt_font,command=lambda method="name":self.__sort_GlobalMethod(method),
                                       bd=0,highlightthickness=0,indicatoron=False).grid(column=0,row=0,padx=90,sticky="new")
            tk.Radiobutton(self.sortFrame,bg="wheat",text="  Pays/Fédération d'origine  ",bd=0,variable=self.vsortncecs,
                                        anchor="center",activebackground="wheat",font=self.rbt_font,command=lambda method="country":self.__sort_GlobalMethod(method),
                                            value="country",highlightthickness=0,indicatoron=False).grid(column=2,row=0,padx=40,sticky="new")
            tk.Radiobutton(self.sortFrame,bg="wheat",text="  Olympiade  ",bd=0,variable=self.vsortncecs,
                    anchor="center",value="edition",activebackground="wheat",font=self.rbt_font,command=lambda method="edition":self.__sort_GlobalMethod(method),
                                            highlightthickness=0,indicatoron=False).grid(column=5,row=0,padx=90,sticky="new")
            tk.Radiobutton(self.sortFrame,bg="wheat",text="  Ville  ",variable=self.vsortncecs,command=lambda method="city":self.__sort_GlobalMethod(method),
                                               anchor="center",value="city",activebackground="wheat",font=self.rbt_font,bd=0,
                                                 highlightthickness=0,indicatoron=False).grid(column=6,row=0,padx=20,sticky="new")
            tk.Radiobutton(self.sortFrame,bg="wheat",text="  Sports/Epreuves auxquel il a participé  ",command=lambda method="sport":self.__sort_GlobalMethod(method),
                        variable=self.vsortncecs,anchor="center",activebackground="wheat",font=self.rbt_font,value="sport",
                             bd=0,highlightthickness=0,indicatoron=False).grid(column=8,row=0,padx=100,columnspan=8,sticky="new")
        # ---------------------------------------------------------------------
        message = """ Info : Pour afficher des informations de résultats: sélectionnez une édition Olympique. \
puis filtrez sur le 'sport' et/ou l'évènement'"""
        self.search_Statebar = Window_StateBar(athleteFrame,"",0,col=0,row=20,cspan=16,pady=2,defMessage=message,txtfont=self.lbl_font)
        # ---------------------------------------------------------------------
        self.search_by_nameId_frame = My_LabelFrame(self.labelFrame,bg='wheat',col=0,row=1,cspan=16,rspan=2,relief="ridge",bd=2,pad=(0,0,0,0))
        # ---------------------------------------------------------------------
        self.search_by_name_frame = My_LabelFrame(self.search_by_nameId_frame,bg=scolor,col=0,row=0,cspan=7,relief="groove",bd=2,pad=(5,2,0,0))
        tk.Label(self.search_by_name_frame,text=" Rechercher un athlète par son nom: ",anchor="center",bg=scolor,
                                                font=self.lbl_font).grid(column=0,row=0,columnspan=3,sticky="nsew")
        self.searchbyname_entry = tk.Entry(self.search_by_name_frame,bg="wheat",bd=2,relief="ridge",
                                                            name='!searchByNameentry',textvariable=self.vsearchbyname)
        self.searchbyname_entry.grid(column=3,row=0,columnspan=4,padx=5,pady=2,ipady=2,sticky="ew")
        tk.Checkbutton(self.search_by_name_frame,text=" : suit la casse ",activebackground="ivory",
                               variable=self.vcaseSensitive,font=self.spb_font,bg=scolor,anchor="w",bd=0,relief="sunken",
                                    command=None).grid(column=0,row=1,padx=5,pady=5,sticky="nsew")
        self.checkwhole = tk.Checkbutton(self.search_by_name_frame,text=" : mot entier ",activebackground="ivory",
                    variable=self.vwholeWord,font=self.spb_font,bg=scolor,anchor="w",bd=0,relief="sunken",command=None)
        self.checkwhole.grid(column=1,row=1,columnspan=2,padx=0,pady=5,sticky="nsew")
        self.checkexact = tk.Checkbutton(self.search_by_name_frame,text=" : mot exact ",activebackground="ivory",
                    variable=self.vexactWord,font=self.spb_font,bg=scolor,anchor="w",bd=0,relief="sunken",command=None)
        self.checkexact.grid(column=3,row=1,columnspan=2,padx=5,pady=5,sticky="nsew")
        tk.Checkbutton(self.search_by_name_frame,text=" : patronyme ",activebackground="ivory",
                               variable=self.vpatronym,font=self.spb_font,bg=scolor,anchor="w",bd=0,relief="sunken",
                                    command=self.__patronym_state).grid(column=5,row=1,columnspan=2,padx=5,pady=5,sticky="nsew")
        # ---------------------------------------------------------------------
        self.search_by_id_frame = My_LabelFrame(self.search_by_nameId_frame,bg=scolor,col=7,row=0,cspan=7,relief="groove",bd=2,pad=(0,2,0,0))
        tk.Label(self.search_by_id_frame,text=" Rechercher un athlète par son Id: ",anchor="center",bg=scolor,
                                                    font=self.lbl_font).grid(column=0,row=0,columnspan=3,sticky="ew")
        self.search_by_Id_entry = tk.Entry(self.search_by_id_frame,bg="wheat",bd=2,relief="ridge",textvariable=self.vsearch_by_Id)
        self.search_by_Id_entry.grid(column=3,row=0,columnspan=4,padx=5,pady=2,ipady=2,sticky="ew")
        self.checkHomonym = tk.Checkbutton(self.search_by_id_frame,text=" : Homonymes/multi Id ",bg=scolor,bd=0,anchor="w",
            activebackground='ivory',variable=self.vmultiId,font=self.spb_font,relief="sunken",command=self.__checkmultiBtn)
        self.checkHomonym.grid(column=0,row=1,columnspan=2,padx=5,pady=5,sticky="nsew")
        tk.Label(self.search_by_id_frame,bg=scolor,text="fenètre : ",font=self.spb_font).grid(column=2,row=1,sticky="nsew")
        self.scale_Id = tk.Scale(self.search_by_id_frame,from_=1,to=self.vscaleId.get(),variable=self.vscaleId,
                               bg=scolor,orient="horizontal",command=self.__scale_toggle,showvalue=False,font=self.spb_font)
        self.scale_Id.grid(column=3,row=1,columnspan=2,pady=5,sticky="nsew")
        tk.Label(self.search_by_id_frame,bg=scolor,text="(+/-: ",font=self.spb_font).grid(column=5,row=1,sticky="w")
        tk.Label(self.search_by_id_frame,bg=scolor,textvariable=self.vscaleId,font=self.spb_font).grid(column=5,row=1,sticky="e")
        tk.Label(self.search_by_id_frame,bg=scolor,text=" )",font=self.spb_font).grid(column=6,row=1,sticky="w")    
        # ---------------------------------------------------------------------
        self.searchNbutton = tk.Button(self.search_by_nameId_frame,bg="#6DBEB3",activebackground="#97FFF1",font=("Helvetic 10 bold italic"))
        self.searchNbutton.configure(textvariable=self.vsearchNbutton,state="disabled")
        self.searchNbutton.grid(column=14,row=0,columnspan=2,padx=4,pady=2,sticky="new")
        # ---------------------------------------------------------------------
        self.searchIbutton = tk.Button(self.search_by_nameId_frame,bg="#92BE6D",activebackground="#C0F892",font=("Helvetic 10 bold italic"))
        self.searchIbutton.configure(textvariable=self.vsearchIbutton,state="disabled")
        self.searchIbutton.grid(column=14,row=0,columnspan=2,padx=4,pady=2,sticky="sew")
        self.search_by_nameId_frame.grid_remove()
        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        self.search_by_editcountry_frame = My_LabelFrame(self.labelFrame,bg="ivory",col=0,row=1,cspan=16,relief="flat",bd=0,pad=(0,0,2,3))
        tk.Label(self.search_by_editcountry_frame,text=" Rechercher les athlète par edition ",anchor="center",bg="ivory",
                                                              font=self.lbl_font).grid(column=0,row=0,columnspan=4,sticky="ew")
        self.comboboxEdition = ttk.Combobox(self.search_by_editcountry_frame,background='ivory1',height=30,width=30,
                                       textvariable=self.vsearchedition,font=('Consolas 12 bold italic'),name="!comboboxEdition")
        self.comboboxEdition.configure(state="disabled",values=list(map(lambda ed:ed.edition, EditionGame.EDITIONS_List)))
        self.comboboxEdition.grid(column=4,row=0,columnspan=4,padx=4,pady=2,sticky="ew")
        self.comboboxEdition.bind("<<ComboboxSelected>>",self.__search_edition)
        tk.Label(self.search_by_editcountry_frame,text=" Rechercher les athlète par Pays/Comité/Fédération ",anchor="center",
                                                          bg="ivory",font=self.lbl_font).grid(column=8,row=0,columnspan=4,sticky="ew")
        self.comboboxCountry = ttk.Combobox(self.search_by_editcountry_frame,background='ivory1',height=30,width=30,
                                       textvariable=self.vsearchcountry,font=('Consolas 12 bold italic'),name="!comboboxCountry")
        #self.comboboxCountry.configure(state="disabled",values=list(map(lambda c:f"{c[0]} ({c[1].noc})",Country.COUNTRY_Dico.items())))
        self.comboboxCountry.configure(state="disabled",values=list(map(lambda c:f"{c.country} ({c.noc})",self.__handleCSV.GLOBAL_CountryList)))
        self.comboboxCountry.grid(column=12,row=0,columnspan=4,padx=4,pady=2,sticky="ew")
        self.global_scrollbox.bind("<<GlobalListboxSelect>>",self.__athlete_InfoSelect)
        self.comboboxCountry.bind("<<ComboboxSelected>>",self.__search_country)
        self.search_by_editcountry_frame.grid_remove()
        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        self.search_by_multichoice_frame = My_LabelFrame(self.labelFrame,bg="ivory",col=0,row=1,rspan=5,
                                                                    cspan=16,relief="flat",bd=0,pad=(0,0,2,3))
        self.optionmenu_frame = My_LabelFrame(self.search_by_multichoice_frame,bg="ivory",col=0,row=1,bd=2,
                                                                    rspan=3,cspan=16,relief="ridge",pad=(2,2,0,0))
        self.buttonMulti = tk.Button(self.optionmenu_frame,background="tan2",borderwidth=2,textvariable=self.vmultiButton)
        self.buttonMulti.configure(activebackground='wheat',overrelief="ridge",command=self.__search_by_multipass)
        self.buttonMulti.grid(column=0,row=0,columnspan=16,padx=2,pady=2,sticky="nsew")
        self.search_by_multichoice_frame.grid_remove()
        # ---------------------------------------------------------------------        
        frameEdition = My_LabelFrame(self.optionmenu_frame,text=f" Choix de l'Edition - Ed.Id  -          Ville ",
                                   pad=(0,0,2,2),font=self.lbl_font,bg="#F8D881",col=0,row=1,cspan=6,sticky="nsew")
        self.editionList = ["All editions",] + list(self.__handleCSV.edition.keys())
        # ---------------------------------------------------------------------
        self.editionMulti = ttk.Combobox(frameEdition,textvariable=self.vmultiedition,height=30,
                                            postcommand=self.__update_edition,values=self.editionList,state="readonly")
        self.editionMulti.configure(background="#F7D4A6",height=min(20,len(self.editionList)),font=self.lbl_font)
        self.editionMulti.grid(column=0,row=0,columnspan=3,padx=2,ipady=2,sticky="ew")
        self.editionMulti.bind("<<ComboboxSelected>>", self.__update_country)
        # ---------------------------------------------------------------------
        self.editionIdMulti = tk.Label(frameEdition,textvariable=self.vmultiedition_id,
                                        state="disabled",anchor="center",width=3,bd=3,relief="sunken")
        self.editionIdMulti.configure(background="#F7D4A6",disabledforeground="black",font=self.lbl_font)
        self.editionIdMulti.grid(column=3,row=0,columnspan=1,ipadx=2,pady=2,sticky="ew")
        # ---------------------------------------------------------------------
        self.editionIdMulti = tk.Label(frameEdition,textvariable=self.vmulticities,
                                         state="disabled",anchor="center",bd=3,width=20,relief="sunken")
        self.editionIdMulti.configure(background="#F7D4A6",disabledforeground="black",font=self.lbl_font)
        self.editionIdMulti.grid(column=4,row=0,columnspan=2,ipadx=2,pady=2,sticky="ew")
        # ---------------------------------------------------------------------
        frameCountry =  My_LabelFrame(self.optionmenu_frame,text=" Choix du Pays ",pad=(0,0,2,2),
                                        font=self.lbl_font,bg=frameEdition.cget('bg'),col=6,row=1,cspan=2)
        self.countryList = ["All countries"] + list(map(lambda mt:mt.country,
                                        MedalTally.MEDALTALLY_Dict.get(self.vmultiedition.get(),[Country.DumCOUNTRY(),])))
        # ---------------------------------------------------------------------
        self.countryMulti = ttk.Combobox(frameCountry,textvariable=self.vmulticountry,values=self.countryList,state="readonly")
        self.countryMulti.configure(background="#E0F3B5",font=('Consolas 9 bold italic'))
        self.countryMulti.grid(column=0,row=0,columnspan=2,ipady=2,sticky="ew")
        self.countryMulti.bind("<<ComboboxSelected>>", self.__update_sport)
         # ---------------------------------------------------------------------
        frameSport =  My_LabelFrame(self.optionmenu_frame,text=" Choix du Sport individuel/par équipe ",pad=(0,0,2,2),
                                        font=self.lbl_font,bg=frameEdition.cget('bg'),col=8,row=1,cspan=4)
        self.sportList = Sport.get_Olympics_Sport_Result("str",select=('sport'),edition=self.editionList[0])
        # ---------------------------------------------------------------------
        self.sportMulti = ttk.Combobox(frameSport,textvariable=self.vmultisport,values=self.sportList,state="readonly")
        self.sportMulti.configure(background="#D7B5F3",height=min(20,len(self.sportList)),font=('Consolas 9 bold italic'))
        self.sportMulti.grid(column=0,row=0,columnspan=3,ipady=2,sticky="ew")
        self.sportMulti.bind("<<ComboboxSelected>>", self.__update_events)
         # ---------------------------------------------------------------------
        self.isteamMulti = tk.Checkbutton(frameSport,variable=self.vmultis_team,onvalue="True",offvalue="All modes",relief="sunken",bd=2) 
        self.isteamMulti.configure(background="#F7D4A6",font=('Consolas 9 bold italic'),text=" : par équipe",activebackground="#F7D4A6")
        self.isteamMulti.grid(column=3,row=0,columnspan=1,ipady=2,sticky="ew")
         # ---------------------------------------------------------------------
        frameEvent = My_LabelFrame(self.optionmenu_frame,bg=frameEdition.cget('bg'),text=" Choix de l'épreuve sportive ",
                                                               pad=(0,0,2,2),font=self.lbl_font,col=12,row=1,cspan=4)
        self.eventList = list(map(lambda evt:evt, self.__handleCSV.sport.get(self.vmultisport.get(), ["All events",])))
        # ---------------------------------------------------------------------
        self.eventMulti = ttk.Combobox(frameEvent,textvariable=self.vmultievent,values=self.eventList,state="readonly")
        self.eventMulti.configure(background="#F7A0A0",height=min(20,len(self.eventList)),font=('Consolas 9 bold italic'))
        self.eventMulti.grid(column=0,row=0,columnspan=4,ipady=2,sticky="ew")
        self.eventMulti.bind("<<ComboboxSelected>>", self.__update_position)
        # ---------------------------------------------------------------------        
        framePosMedal = My_LabelFrame(self.optionmenu_frame,col=0,row=2,text=" Classement JO. / Médaille ",cspan=2,
                                            bg=frameEdition.cget('bg'),pad=(0,0,2,2),font=self.lbl_font,sticky="nsew")
        self.positionList = ["All positions",] + Sport.POSITION_List
        self.positionMulti = ttk.Combobox(framePosMedal,textvariable=self.vmultiposition,values=self.positionList,width=12,state="readonly")
        self.positionMulti.configure(background="#A8F3E7",postcommand=self.__update_medaille,font=self.lbl_font)
        self.positionMulti.grid(column=0,row=0,columnspan=1,padx=2,ipady=2,sticky="ew")
        self.positionMulti.bind("<<ComboboxSelected>>", self.__update_medaille)
        # ---------------------------------------------------------------------
        self.medalList = ["All medals",] + list(medalType_list)
        self.medalMulti = ttk.Combobox(framePosMedal,textvariable=self.vmultimedal,values=self.medalList,state="readonly")
        self.medalMulti.configure(background="#F8D881",font=self.lbl_font,height=4,width=8)
        self.medalMulti.grid(column=1,row=0,columnspan=1,padx=2,ipady=2,sticky="ew")
        self.medalMulti.bind("<<ComboboxSelected>>", self.__update_position)
        # ---------------------------------------------------------------------
        frameGenre = My_LabelFrame(self.optionmenu_frame,bg=frameEdition.cget('bg'),text=" Genre ",
                                                               pad=(0,0,2,2),font=self.lbl_font,col=2,row=2,cspan=2)
        #self.genreMulti = ttk.Combobox(frameGenre,textvariable=self.vmultigenre,values=genreType_list[:3],state="readonly")
        self.genreMulti = ttk.Combobox(frameGenre,textvariable=self.vmultigenre,values=genreType_list[:3],state="readonly")
        self.genreMulti.configure(background="#F7A0A0",height=4,font=self.lbl_font,width=8)
        self.genreMulti.grid(column=0,row=0,columnspan=2,ipady=2,sticky="ew")
        self.genreMulti.bind("<<ComboboxSelected>>", self.__update_genre)
        # ---------------------------------------------------------------------
        title = f" Recherche sur le Nom et/ou le prénom (Insensible à la casse)"
        frameFirstLastName = My_LabelFrame(self.optionmenu_frame,bg="#FDF184",text=title,
                                                   pad=(0,0,2,2),font=self.lbl_font,col=4,row=2,cspan=6)
        tk.Label(frameFirstLastName,justify="left",bg=frameFirstLastName.cget('bg'),text=' Prénom :',
                                           font=self.lbl_font).grid(column=0,row=0,padx=0,pady=2,sticky="ew")
        frameFirstname = My_LabelFrame(frameFirstLastName,bg="#FDF184",col=1,row=0,cspan=2,sticky="ew")
        tk.Entry(frameFirstname,justify="left",bg='ivory',textvariable=self.vmultifirstname,width=24,
                                                 font=self.lbl_font).grid(column=0,row=0,pady=2,sticky="ew")
        button_fname = tk.Button(frameFirstname,compound="center",font=self.spb_font,bg="#FCD4AF",
                            image=self.button_image,activebackground="#FCAFAF",command=self.__firstname_rst__)
        button_fname.grid(column=1,row=0,ipadx=2,sticky="nsew")
        tk.Label(frameFirstLastName,justify="left",bg=frameFirstLastName.cget('bg'),text='Nom :',
                                           font=self.lbl_font).grid(column=3,row=0,padx=0,pady=2,sticky="ew")
        frameLastname = My_LabelFrame(frameFirstLastName,bg="#FDF184",col=4,row=0,cspan=2,sticky="ew")
        tk.Entry(frameLastname,justify="left",bg='ivory',textvariable=self.vmultilastname,width=24,
                                                 font=self.lbl_font).grid(column=0,row=0,pady=2,sticky="ew")
        button_lname = tk.Button(frameLastname,compound="center",font=self.spb_font,bg="#FCD4AF",
                               image=self.button_image,activebackground="#FCAFAF",command=self.__lastname_rst__)
        button_lname.grid(column=1,row=0,ipadx=2,sticky="nsew")
        # ---------------------------------------------------------------------
        frameAthInfo = My_LabelFrame(self.optionmenu_frame,col=10,row=2,text=" Info. sur l'athlète ",cspan=3,
                                            bg="#FDF184",pad=(0,0,2,2),font=self.lbl_font,sticky="nsew")
        self.multiAthleteInfoBtn = tk.Button(frameAthInfo,textvariable=self.vmultiAthleteInfo,
                                                   bg="#F7D4A6",font=self.lbl_font,command=self.__athlete_InfoSelect)
        self.multiAthleteInfoBtn.configure(state="normal",activebackground=frameEdition.cget('bg'))
        self.multiAthleteInfoBtn.grid(column=0,row=0,columnspan=3,sticky="nsew")
        # ---------------------------------------------------------------------
        frameResult = My_LabelFrame(self.optionmenu_frame,col=13,row=2,text=" Résultats des épreuves ",cspan=3,
                                        bg="#F3D4FF",pad=(0,0,2,2),font=self.lbl_font,sticky="nsew")
        self.multiResultInfoBtn = tk.Button(frameResult,text=" Info résultats ",
                                                   bg="#F9C7FF",font=self.lbl_font,command=self.__resultInfo_window)
        self.multiResultInfoBtn.configure(state="normal",activebackground="#F8B9FF")
        self.multiResultInfoBtn.grid(column=0,row=0,columnspan=3,sticky="nsew")
        self.search_by_multichoice_frame.grid_remove()
        # ---- Création listes globales des athlètes pour affichage -> liste de 'str'
        # ----   class HandleCSV.GLOBAL_AthleteNames et HandleCSV.GLOBAL_Athlete_Id
        # ---- "self.athletesList" renvoi la liste entière des objets de classe 'Athlete' ----
        self.homonym_maxsize = max(2, max(list(map(lambda ath:len(ath), Athlete.ATHLETE_ID_Dico.values()))))
        self.athletesList = self.__create_AthletesList()
        # ---------------------------------------------------------------------
        if self.__searchtype == "global":
            self.__search_global()
        elif self.__searchtype == "nom":
            self.__search_name()
        elif self.__searchtype == "Id":
            self.__search_athleteId()
        elif self.__searchtype == "olympiade":
            self.__search_edition()
        elif self.__searchtype == "pays":
            self.__search_country()
        elif self.__searchtype == "multi":
            self.__search_multipass(list(self.__handleCSV.edition.keys())[0])
              
    def __resultInfo_window(self):

        from gui_tools import Resultat_InfoWindow

        title = f"Fenêtre d'information des Olympiade Modernes"
        edition_id = int(self.vmultiedition_id.get()) if self.vmultiedition_id.get() != "All Id" else 0
        self.__update_results(edition_id)
        opened_Win_popup:list = list(filter(lambda t:t.title()==title, [self.nametowidget(pathname) \
                                                    for pathname in self.children.keys() if pathname=="!win_ResultPopup"]))
        if not opened_Win_popup:
            resultWindow = Resultat_InfoWindow(self, self.resultatList)
        else:
            [win_popup.lift() for win_popup in opened_Win_popup]
                    
    def __update_results(self, edition_id:int=0):
        filters:dict = ({})
        edition_id = "All Id" if edition_id == 0 else edition_id
        # ----- On affecte une valeur aux attributs concernés de 'Sport' ------
        tab_options:dict = {key:self.sportStringvar[idx].get() for idx,key in enumerate(Sport.SUPPORTED_ATTRIBUTES)}
        tab_options['noc'] = Country.COUNTRY_Dico.get(self.vmulticountry.get(),Country.DumCOUNTRY()).noc
        [filters.update({key:value}) for key,value in tab_options.items() if not self.__is_valid_filter_value(value)]
        #print(f"\nself.__update_results(filters): {filters}\n")
        # ---------------------------------------------------------------------
        dumList = list(set(map(lambda sport:sport.resultat, Sport.get_Olympics_Sport_Result("obj",select=('resultat'),**filters))))
        self.resultatList = sorted(dumList, key=lambda r:r.result_id)
        self.multiResultInfoBtn.configure(state="active")

    #@chrono
    def __sort_GlobalMethod(self, method:SORTLISTYPE="name"):
        #from random import randint
        if self.__sortbyNCECS == method: return 
        if method == "name":
            athletesList = self.__handleCSV.GLOBAL_AthleteListName
        elif method == "country":
            athletesList = sorted(self.__handleCSV.GLOBAL_AthleteListName, key=lambda line:(line[40:81]).strip())
        elif method == "edition":
            athletesList = sorted(self.__handleCSV.GLOBAL_AthleteListName, key=lambda line:(line[81:101]).strip())
        elif method == "city":
            athletesList = sorted(self.__handleCSV.GLOBAL_AthleteListName, key=lambda line:(line[102:122]).strip())
        elif method == "sport":
            athletesList = sorted(self.__handleCSV.GLOBAL_AthleteListName, key=lambda line:(line[122:]).strip())
        # ---------------------------------------------------------------------
        #dummy = ""    
        #while not dummy:
        #    item = self.__handleCSV.GLOBAL_AthleteListName[randint(0,6000)]
        #    dummy = item.find("Olympic") != -1
        #print(f"-> |{item[:40]}|{item[40:81]}|{item[81:101]}|{item[102:122]}|{item[122:]}")            
        # ---------------------------------------------------------------------
        self.vsearchAthList.set(athletesList)
        self.__sortbyNCECS = method

    def __firstname_rst__(self):
        self.vmultifirstname.initialize("... prénom ...")

    def __lastname_rst__(self):
        self.vmultilastname.initialize("... nom ...")
    
    def __name_id__(self, w:tk.Widget) -> tuple:
        selected = w.get(w.curselection()[0])            
        name, id = RE_NAMEID.search(selected).groups()
        return name, id

    def __select_athlete_by_firstlastname(self, athlete:Athlete) -> bool:
        searchfname,  searchlname  = self.vmultifirstname.get().lower(), self.vmultilastname.get().lower()
        athletefname, athletelname = athlete.firstname.lower(), athlete.lastname.lower()
        if athlete == Athlete.DumATHLETE():
            return False
        if "... prénom ..." not in searchfname and "... nom ..." not in searchlname:
            return (searchfname in athletefname) and (searchlname in athletelname)
        if "... prénom ..." not in searchfname and "... nom ..." in searchlname:    
            return (searchfname in athletefname)
        if "... prénom ..." in searchfname and "... nom ..." not in searchlname:
            return (searchlname in athletelname)
        return True
                
    def __athlete_ButtonSelect(self, event:tk.Event=None):
        """ Affichage de la fenetre Info Athlète avec le bouton multisearch """
        if event and isinstance(event.widget, ScrolledListbox):
            w = event.widget
            if "!globalScrollBox" == w.name() and w.curselection():
                name, id = self.__name_id__(w)
                self.__vmultiAthInfo.initialize((name, id))           
                self.vmultiAthleteInfo.set(f"{name:^21}" if len(name) < 18 else f"{name[:18]}...")
            
    def __athlete_InfoSelect(self, event:tk.Event=None):
        if self.__searchtype == "multi":
            # -- on a déjà le 2-tuple (name, id) dans le StringVar --
            name, id = eval(self.__vmultiAthInfo.get())
        elif event and event.widget.name() == "!globalScrollBox":
            if event.widget.curselection():
                name, id = self.__name_id__(event.widget)
        else:
            name, id = "No athlete", "0"            
        # ---------------------------------------------------------------------            
        #self.__athlete_infowindow.athlete = Athlete.ATHLETES_Dico.get(int(id), Athlete.DumATHLETE())
        self.__athlete_infowindow.athlete = Athlete.Get_Athlete(int(id))
        self.__vmultiAthInfo.initialize((name, id))
                        
    def __update_edition(self, event=None):
        selected = event if event else self.vmultiedition.get()
        self.search_Statebar.update_vltexte("Info : Recherche des données des Olympiades en cours ...",2)
        #print(f"__update_edition(selected): {selected}")
        self.vmultiedition.set(selected)
        #if "All " in selected: self.vmultiedition_id.set("All Id")
        self.__athlete_infowindow.athlete = Athlete.DumATHLETE()
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")

    def __update_country(self, event=None):
        filters:dict = ({})
        selected = event.widget.get() if event else self.editionMulti.get()
        self.search_Statebar.update_vltexte("Info : Recherche des données des Pays participants en cours ...",2)
        #print(f"__update_country(selected): {selected}")
        # ---------------------------------------------------------------------            
        tab_options:dict = {key:self.sportStringvar[idx].get() for idx,key in enumerate(Sport.SUPPORTED_ATTRIBUTES)}
        [filters.update({key:value}) for key,value in tab_options.items() if not self.__is_valid_filter_value(value)]
        # ---------------------------------------------------------------------
        self.nocList = Sport.get_Olympics_Sport_Result("str", select=("noc"), **filters)            
        self.countryList = [Country.NOC_Dict[noc].country for noc in self.nocList]
        self.countryMulti.configure(values=["All countries"] + self.countryList,height=min(20,len(self.countryList)+1))
        # ---------------------------------------------------------------------
        edition = EditionGame.EDITIONS_Dict[selected] if selected != "All editions" else EditionGame.DumEDITGAME()
        self.__update_results(edition.edition_id)
        # ---------------------------------------------------------------------
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")
        # ---------------------------------------------------------------------
        self.vmultiedition_id.set(edition.edition_id) 
        self.vmulticities.set(edition.city)
        
    def __update_sport(self, event=None):
        filters:dict = ({})
        selected = event.widget.get() if event else self.countryMulti.get()        
        self.search_Statebar.update_vltexte("Info : Recherche des données des sports pratiqués en cours ...",2)
        #print(f"__update_sport(selected): {selected}")            
        # ---------------------------------------------------------------------
        tab_options:dict = {key:self.sportStringvar[idx].get() for idx,key in enumerate(Sport.SUPPORTED_ATTRIBUTES)}
        tab_options.update({'noc':Country.COUNTRY_Dico.get(self.vmulticountry.get(),Country.DumCOUNTRY()).noc}) 
        [filters.update({key:value}) for key,value in tab_options.items() if not self.__is_valid_filter_value(value)]
        self.sportList = Sport.get_Olympics_Sport_Result("str",select=('sport'),**filters)
        #print(f"__update_sport(filters): {filters}")
        # ---------------------------------------------------------------------
        self.sportMulti.configure(values=["All sports"] + self.sportList,height=min(20,len(self.sportList)+1))
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")
        
    def __update_events(self, event=None):
        filters:dict = ({})
        selected = event.widget.get() if event else self.eventMulti.get()        
        self.search_Statebar.update_vltexte("Info : Recherche des données des épreuves sportives en cours ...",2)
        #print(f"__update_events(selected): {selected}")
        sports = self.sportList if self.vmultisport.get() == "All sports" else [selected,]
        # ---------------------------------------------------------------------
        tab_options:dict = {key:self.sportStringvar[idx].get() for idx,key in enumerate(Sport.SUPPORTED_ATTRIBUTES)}
        tab_options.update({'noc':Country.COUNTRY_Dico.get(self.vmulticountry.get(),Country.DumCOUNTRY()).noc}) 
        [filters.update({key:value}) for key,value in tab_options.items() if not self.__is_valid_filter_value(value)]
        self.eventList = Sport.get_Olympics_Sport_Result("str",select=('event'),**filters)
        #print(f"__update_events(filters): {filters}")
        # ---------------------------------------------------------------------
        self.eventMulti.configure(values=["All events"] + self.eventList,height=min(20,len(self.eventList)+1))     
        self.__update_results(self.vmultiedition_id.get())
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")
    
    def __update_position(self, event=None):
        MEDAL_DICO:dict = {"Gold":"1","Silver":"2","Bronze":"3"}
        selected = event.widget.get() if event else self.positionMulti.get()        
        #print(f"__update_position(selected): {selected}")
        self.vmultiposition.set(MEDAL_DICO.get(selected,"All positions"))
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")
            
    def __update_medaille(self, event=None):
        MEDAL_DICO:dict = {"1":"Gold","2":"Silver","3":"Bronze"}
        selected = event.widget.get() if event else self.positionMulti.get()        
        #print(f"__update_medaille(selected): {selected}")
        self.vmultimedal.set(MEDAL_DICO.get(selected,"All medals"))
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")
                    
    def __update_genre(self, event=None):
        filters:dict = ({})
        if event and not isinstance(event, str):
            selected = event.widget.get()
        else: selected = event    
        #self.vmultiathlete_sex.set(GENRE_Dico[selected] if selected in genreType_list else GENRE_Dico[self.vmultigenre.get()])
        #if selected != "Non genré":
        self.vmultiathlete_sex.set(GENRE_Dico[selected]) if selected in genreType_list else self.vmultigenre.get()
        if self.vmultiathlete_sex.get() != "No genre":
            #print(f"self.vmultiathlete_sex.get(): {self.vmultiathlete_sex.get()} -/- self.vmultigenre.get(): {self.vmultigenre.get()}")
            tab_options:dict = {key:self.sportStringvar[idx].get() for idx,key in enumerate(Sport.SUPPORTED_ATTRIBUTES)}
            tab_options.update({'noc':Country.COUNTRY_Dico.get(self.vmulticountry.get(),Country.DumCOUNTRY()).noc}) 
            [filters.update({key:value}) for key,value in tab_options.items() if not self.__is_valid_filter_value(value)]
            athletesList = Sport.get_Olympics_Sport_Result("obj", select="athlete", **filters)
            #print(f"__update_genre(filters): {filters}")
        else:
            athletesList = self.sportObjList
        if athletesList:
            dumList = set([self.__prepare_athlete_list(sport.athlete) for sport in athletesList])
            athletesList = sorted(list(dumList), key=lambda sport:sport.split(' (')[0].strip())
        self.__vmultiAthInfo.initialize(["All athletes", 0])
        self.vmultiAthleteInfo.set("Choisissez un athlète")
        self.vsearchAthList.set(athletesList)
        self.athleteList = athletesList
        self.__ajust_size(selected)
    
    def __ajust_size(self, genre:GENRETYPE):
        length = f"{len(self.athleteList)} {genre+'(s)' if 'All' not in genre else ''}"
        self.vathleteNumber.set(f"{self.vathleteNumber.get().split(':')[0].strip()}: {length}")
    
    def __is_valid_filter_value(self, value:str) -> bool:
        """ Retourne True si au moins l'un des éléments de la liste est dans 'value' """
        return value=="0" or any(x in value for x in ["All ", "No ", "NHD"]) 
    
    def __patronym_state(self):
        dico_state:dict = {1:"disabled", 0:"normal"}
        self.checkexact.configure(state=dico_state[self.vpatronym.get()])
    
    def __scale_toggle(self, scale:str):
        if int(scale) == 1: self.checkHomonym.deselect()

    def __search_idrange(self, athlete:Athlete, idsearch:int, scale:int) -> bool:
        return bool(idsearch in range(athlete.athlete_id-scale, athlete.athlete_id+scale))

    def __checkmultiBtn(self):
        state_dico:dict = {0:"normal",1:"disabled"}
        self.search_by_Id_entry.configure(state=state_dico.get(self.vmultiId.get(), 0))
        if bool(self.vmultiId.get()) and self.homonym_maxsize >= 2:
            self.optsearch_scaleId = self.vscaleId.get() 
            self.scale_Id.config(from_=2, to=self.homonym_maxsize)
        else:
            self.scale_Id.config(from_=1, to=self.__options.search_options.scaleId,)
            self.scale_Id.set(self.optsearch_scaleId)
        
    #@chrono        
    def __search_multipass(self, selected:str):
        self.editionList = [selected,]    
        self.__search_by_multipass(edition=selected)
        self.search_by_multichoice_frame.grid()
            
    def __search_by_multipass(self, event:tk.Event=None, **selected):
        filters:dict = ({})
        self.search_Statebar.update_vltexte(" Info : Traitement des données pour une recherche multi-critères en cours ...",2)
        # ---------------------------------------------------------------------        
        tab_options:dict = {key:self.sportStringvar[idx].get() for idx,key in enumerate(Sport.SUPPORTED_ATTRIBUTES)}
        tab_options['noc'] = Country.COUNTRY_Dico.get(self.vmulticountry.get(),Country.DumCOUNTRY()).noc
        [filters.update({key:value}) for key,value in tab_options.items() if not self.__is_valid_filter_value(value)]
        # ---------------------------------------------------------------------            
        if selected:
            filters.update(selected)
            self.vmultiedition.set(list(selected.values())[0])
        #print(f"__search_by_multipass(selected): {selected}")
        # ---------------------------------------------------------------------            
        print(f"__search_by_multipass(filters): {filters}")
        if not filters and "prénom" in self.vmultifirstname.get() and "... nom ..." in self.vmultilastname.get():
            athleteList = self.__handleCSV.GLOBAL_AthleteListName
        else:
            self.sportObjList = list(Sport.get_Olympics_Sport_Result("obj",select=('athlete') ,**filters))
            athleteList = set([self.__prepare_athlete_list(sport.athlete) \
                                for sport in self.sportObjList if self.__select_athlete_by_firstlastname(sport.athlete)])
        # ---------------------------------------------------------------------            
        self.vsearchAthList.set(sorted(list(athleteList), key=lambda item:item.split(' (')[0].strip()))
        self.vathleteNumber.set(f"{self.vathleteNumber.get().split(':')[0].strip()} : {len(athleteList)}")
        # -------- Update des infos des Combobox Pays/Sport/Evènement ---------          
        self.__update_edition()
        self.__update_country()
        self.__update_sport()
        self.__update_events()
        # ------- Update du bouton 'Info Athlète' et de la barre d'état -------           
        self.vmultiAthleteInfo.set("Choisissez un athlète")
        self.search_Statebar.update_vltexte("",0)
        
    #@chrono
    def __search_country(self, event:tk.Event=None):
        self.search_Statebar.update_vltexte(" Info : Recherche des données par 'Pays' en cours de traitement ...",2)
        self.search_Statebar.message = " Info : Selectionnez un pays pour rechercher les athletes toutes éditions confondues"
        self.comboboxCountry.configure(state="normal")
        if event and isinstance(event, tk.Event):
            w = event.widget; country = w.get()
            noc = country.split(" (")[1].strip(""" )""")
            sportList = Sport.get_Olympics_Sport_Result("obj",select=("athlete"),noc=noc)
            self.athleteList = set([self.__prepare_athlete_list(sport.athlete) for sport in sportList])
            self.vsearchAthList.set(value=sorted(list(self.athleteList), key=lambda l:l.split(' (')[0].strip()))
            # ---------------------------------------------------------------------
            sportList = self.vsearchAthList.get().replace("'","").split(', '); lsp = len(sportList)
            label = f" {lsp} Athlète{' a' if lsp < 2 else 's ont'} participé à toutes les Olympiades pour le pays/comité/fédération : {country}"
            self.vathleteNumber.set(label)    
        self.search_by_editcountry_frame.grid()

    #@chrono
    def __search_edition(self, event:tk.Event=None):
        self.search_Statebar.update_vltexte(" Info : Recherche des données par Olympiade en cours de traitement ... ",2)
        self.search_Statebar.message = " Info : [Dbl-Gauche] ou [Entrée] pour afficher une fenètre d'information sur l'athlète sélectionné"
        self.comboboxEdition.configure(state="normal")
        if event and isinstance(event, tk.Event):
            w = event.widget; edition = w.get()
            sportList = Sport.get_Olympics_Sport_Result("obj",select=("athlete"),edition=edition)
            self.athleteList = set([self.__prepare_athlete_list(sport.athlete) for sport in sportList])
            self.vsearchAthList.set(value=sorted(list(self.athleteList),key=lambda ath:ath.split(' (')[0].strip()))
            # ---------------------------------------------------------------------
            sportList = self.vsearchAthList.get().replace("'","").split(', '); lsp = len(sportList)
            label = f" {lsp} Athlète{' a' if lsp < 2 else 's ont'} participé à cette Olympiade '{edition}' tous pays/comités/fédérations confondus."
            self.vathleteNumber.set(label)        
        self.search_by_editcountry_frame.grid()

    def __search_athleteId(self):
        self.searchIbutton.configure(state="active",command=self.__search_by_AthleteId)
        self.search_Statebar.update_vltexte(" Info : Recherche des données par l'Id' d'athlètes en cours ...",5)
        self.search_Statebar.message = " Info : Veuillez saisir tout ou partie d'un Id, utiliser la fenêtre pour les Id(s) proches"
        # ---------------------------------------------------------------------
        self.searchbyname_entry.configure(state="disabled")
        self.search_by_nameId_frame.grid()
        self.__search_by_AthleteId()
        
    @chrono
    def __search_by_AthleteId(self):
        # ---------------------------------------------------------------------
        searchathleteId = "".join([c for c in self.search_by_Id_entry.get() if c.isdigit()])
        # ------------ Une entrée est saisie et homonymes = False -------------
        if searchathleteId and not bool(self.vmultiId.get()):
            searchathleteId = int(searchathleteId)
            # ---- Id recherché PAS dans les clés du dico : lecture fenetre ---
            if searchathleteId not in self.__handleCSV.athlete:
                athletesList = list(filter(lambda athlete:self.__search_idrange(athlete,searchathleteId,
                                                                                    self.vscaleId.get()),self.athletesList))    
            else:
                athletesList = [self.__handleCSV.athlete[searchathleteId],]
            athleteList = [self.__prepare_athlete_list(athlete) for athlete in sorted(athletesList,key=lambda ath:(ath.athlete_id))]            
        # -------------- Pas d'entrée saisie et homonymes = True --------------
        elif bool(self.vmultiId.get()) and self.homonym_maxsize >= 2:
            nbr = self.vscaleId.get()
            athletesIdList,athletesList = [], []
            self.scale_Id.configure(from_=2, to=self.homonym_maxsize)
            [athletesIdList.extend(athleteId) for athleteId in list(filter(lambda ath:len(ath)>1, 
                                                       Athlete.ATHLETE_ID_Dico.values())) if len(athleteId) == nbr]
            [athletesList.append(Athlete.ATHLETES_Dico[athleteId]) for athleteId in athletesIdList]
            athleteList = [self.__prepare_athlete_list(athlete) for athlete in sorted(athletesList,key=lambda ath:(ath.name))]            
        # -------------- Liste complete des athlètes triée par Id -------------
        else:
            athleteList:list = ([])
            self.vsearch_by_Id.initialize("Rechercher par Id ...")
            athleteList.extend(self.__handleCSV.GLOBAL_AthleteListId)
        # ---------------------------------------------------------------------
        self.vathleteNumber.set(f"{self.vathleteNumber.get().split(':')[0].strip()} : {len(athleteList)}")
        self.vsearchAthList.set(value=athleteList)
        #self.search_Statebar.update_vltexte("",0)

    def __search_name(self):
        self.searchNbutton.configure(state="active",command=self.__search_by_name)
        self.search_Statebar.update_vltexte(" Info : Recherche des données par 'nom/Id' d'athlètes en cours ...",5)
        self.search_Statebar.message = " Info : Veuillez saisir tout ou partie du nom, utiliser les cases à cocher pour affiner la recherche / la fenêtre pour les Id(s) proches"
        # ---------------------------------------------------------------------
        self.search_by_Id_entry.configure(state="disabled")
        self.checkHomonym.configure(state="disabled")
        self.search_by_nameId_frame.grid()
        self.__search_by_name()

    @chrono
    def __search_by_name(self, event:tk.Event=None):
        self.__patronym_state()
        # ---------------------------------------------------------------------    
        searchname = " ".join([item.strip() for item in self.searchbyname_entry.get().split(' ')])
        # ---------------------------------------------------------------------    
        if not searchname or "rechercher" in searchname:
            self.vsearchbyname.initialize("Nom à rechercher ...")
            athleteList = self.athletesList
        else:
            athleteList = list(filter(lambda athlete: self.__search_style(searchname, athlete.name), self.athletesList))
        athleteList = [self.__prepare_athlete_list(athlete) for athlete in \
                                        sorted(athleteList, key=lambda ath:(ath.lastname,ath.firstname,ath.country.noc))]
        self.vathleteNumber.set(f"{self.vathleteNumber.get().split(':')[0]}: {len(athleteList)}")
        self.vsearchAthList.set(value=athleteList)
    
    @chrono        
    def __search_global(self):
        def_message = """ Info : La sélection d'un entête modifie l'ordre d'affichage des athlètes / [Dbl-Gauche] ou [Enter] pour afficher la fenètre d'informations"""
        self.search_Statebar.update_vltexte(" Info : Recherche des données globales en cours de traitement ...",2)
        self.search_Statebar.message = def_message
        # ---------------------------------------------------------------------
        self.vathleteNumber.set(f"{self.vathleteNumber.get().split(':')[0].strip()} : {len(self.__handleCSV.GLOBAL_AthleteListName)}")
        self.__sort_GlobalMethod(self.__options.search_options.sortList)
    
    def __search_style(self, searchname:str, athlete:str) -> bool:
        l = len(searchname)
        # -------------------------- case sensitive ---------------------------
        if not self.vcaseSensitive.get():
            searchname, athlete = searchname.lower(), athlete.lower()
        # ---------------------------- whole word -----------------------------
        if self.vwholeWord.get() and not self.vexactWord.get() and not self.vpatronym.get():
            return bool(f" {searchname} " in athlete or f"{searchname} " in athlete[:l+1] or f" {searchname}" in athlete[-(l+1):])
        # ----------------------------- patronyme -----------------------------
        if self.vexactWord.get() and not self.vwholeWord.get() and not self.vpatronym.get():
            return bool(f" {searchname} " in athlete or f" {searchname}" in athlete[-(l+1):])
        # ----------------------------- patronyme -----------------------------
        if self.vpatronym.get():
            fullname = athlete.split()
            nom = fullname[-1] if len(fullname) > 1 else ""
            return bool(searchname == nom) if bool(self.vwholeWord.get()) else bool(searchname in nom)
        # -------------- not case, not wholeword & not patronyme --------------
        return bool(searchname in athlete)

    def __prepare_athlete_list(self, athlete:Athlete) -> str:
        if athlete.athlete_id == 0: return
        country_noc = athlete.country.__repr__()
        ath = f"{athlete.name[:30]} ({athlete.athlete_id})"
        country = f"{country_noc:<40}" if len(country_noc) < 40 else f"{country_noc[:14]} ... {country_noc[22:]}"
        # ---------------------------------------------------------------------
        if self.__searchtype in ["nom","Id"]:
            poids = f"{athlete.weight}Kg" if athlete.weight != '-/- ' else f"{' ':<12}"
            taille = f" {athlete.height}cm, " if '.' in athlete.height else f"{' ':<8}"
            Info = f"{athlete.sex:<6}{taille:<8}{poids:<10}"
        else:
            if athlete.events:
                event:AthleteEvents = athlete.events[0]
                found = list(filter(lambda evt:(evt.edition==self.vmultiedition.get()), athlete.events))
                event = found[0] if found else event
                edition = event.edition if len(event.edition)<21 else f"{event.edition[:10]}...{event.edition[-7:]}"
                Info = f"{edition:<20},{event.city:^20}"
            else: Info = "" #"Aucun évènement n'a été trouvé!"   #f"{' ':<38}"
        event = self.__prepare_athlete_events(athlete)
        # ---------------------------------------------------------------------
        return f"{ath:<40}{country:<40} {Info}{event}"
 
    def __prepare_athlete_events(self, athlete:Athlete) -> str:
        events:list = ([])
        # ---------------------------------------------------------------------
        if not "All " in self.editionMulti.get() and len(athlete.events)>=2:
            athlete.events = self.__reorg_eventList__(athlete.events)
        # ---------------------------------------------------------------------
        for idx,item in enumerate(athlete.events):
            if idx == 0 or item.edition == self.vmultiedition.get():
                events.append(item.__repr__())
            else:
                events.append("".join((f"{item.edition[:4]} {item.city}",' ',item.__repr__())))
        # ---------------------------------------------------------------------
        event = ", ".join([f"{item}" for item in events])
        return event    

    #@chrono
    def __reorg_eventList__(self, events: list) -> AthleteEvents:
        """ Reorganisation de la liste des events selon l'Olympiade. En premiers ceux de l'édition 
        courante, puis dans l'ordre croissant ceux des autres éditions olympiques.
        """
        edition = self.editionMulti.get()
        return [e for e in events if e.edition == edition] + \
                               sorted([e for e in events if e.edition != edition], key=lambda e:int(e.edition[:3]))

    @chrono
    def __create_AthletesList(self) -> list:
        """ Retourne la liste des objets de classe 'Athlete' et met à jour les listes 
            globales de la classe Handle_CSV: GLOBAL_AthleteListName et GLOBAL_AthleteListId
        """
        objList = list(self.__handleCSV.athlete.values())
        if not self.__handleCSV.GLOBAL_AthleteListName:
            self.__handleCSV.GLOBAL_AthleteListName.extend([self.__prepare_athlete_list(athlete) \
                                              for athlete in sorted(objList, key=lambda ath:(ath.name,ath.naissance,ath.country.noc))])
        if not self.__handleCSV.GLOBAL_AthleteListId:
            self.__handleCSV.GLOBAL_AthleteListId.extend([self.__prepare_athlete_list(athlete) \
                                         for athlete in sorted(objList,key=lambda ath:(ath.athlete_id))])
        return objList
        
    def Quit(self):
        if self.__options.saveCFGonquit:
            self.__options.search_options.sortList = self.__sortbyNCECS
        self.destroy()



if __name__ == "__main__":
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")
    
    root = tk.Tk()
    root.msgbox = Win_MessageBox(root)
    config = Saveload_CFG()
    if config.cfg_load():
        root.app_options = config.options
    handlecsv = Handle_CSV(root, root.app_options)
    
    root.columnconfigure(list(range(20)), weight=1)
    root.rowconfigure(list(range(20)), weight=1)
    
    if handlecsv.edition:
        
        EdGame = GUI_EditionGame(root, EditionGame.EDITIONS_Dict,0,0,cspan=20,rspan=20)
        
        #winnameid = SearchAthlete(root, handleCSV=handlecsv, searchtype="global")
        #winnameid = SearchAthlete(root, handleCSV=handlecsv, searchtype="nom")
        #winnameid = SearchAthlete(root, handleCSV=handlecsv, searchtype="Id")
        #winedition = SearchAthlete(root, handleCSV=handlecsv, searchtype="olympiade")
        #wincountry = SearchAthlete(root, handleCSV=handlecsv, searchtype="pays")
        #winmulti = SearchAthlete(root, handleCSV=handlecsv, searchtype="multi")
        
        #sportevt = GUI_SearchSportEvt(root, handlecsv, "Ath")
                
    root.mainloop()
        
    #print(f"Athlètes: {list(Athlete.ATHLETES_Dico.keys())[:10]}")
    #print(f"Editions: {list(EditionGame.EDITIONS_Dict.keys())[:3]}")
    #print(f"Médailles: {list(map(lambda mt:mt.__str__(), list(MedalTally.MEDALTALLY_Dict.values())[0][:1]))}")
    #print(f"Résultats: {Resultat.RESULTATS_List[:10]}")
    #print(f"Pays: {list(Country.NOC_Dict.keys())[:10]}")
    #print(f"Sports: {list(Sport.SPORTS_Dico.keys())[:5]}")
    