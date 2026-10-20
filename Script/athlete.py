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

import pandas,csv

from configs import *
from math import isnan,nan
from re import search

 
class AthleteEvents():

    ATHEVENTS_Dico:dict = ({})
    ATHEVENTS_List:list = ([])
    EventAttributes = Literal['name','athlete_id','sex','born','age','height','weight','event_id','edition','city','sport','event','position','medal']
    SUPPORTED_ATTRIBUTES = get_args(EventAttributes)
    ATHIDEVENTS_Dico:dict = ({})
    
    @classmethod
    def get_Olympics_Events_List(cls,output:str, *, select=None, **filters) -> list:
        """ Méthode de classe qui permet de filtrer sur aucun, un ou plusieurs des attributs
            de la classe AthleteEvents(). 
            Exemples:
                get_Olympics_Events_List()                                  -> tous les events
                get_Olympics_Events_List(edition="2020")                    -> edition contenant "2020"
                get_Olympics_Events_List(edition="2020", athlete="Teddy")   -> edition contenant "2020" et athlete contenant "Teddy"
                get_Olympics_Events_List(noc=["FRA","GBR"])                 -> match si noc contient "FRA" ou "GBR"
        """
        # validation des clés par suppression des clés incorrectes
        fkeys = {key:val for key,val in filters.items()}
        for k in fkeys.keys():
            if k not in AthleteEvents.SUPPORTED_ATTRIBUTES:
                print(f" ---> Bad key: {k}={filters.pop(k,None)}")
        # normalization et validation du paramètre select
        sel_fields = None
        if select is not None:
            if isinstance(select, str):
                sel_fields = (select,)
            else:
                sel_fields = tuple(select)
            for f in sel_fields:
                if f not in AthleteEvents.SUPPORTED_ATTRIBUTES:
                    raise ValueError(f"'{f}' n'est pas un attribut valide de Sport")
        dummy_set, dummy_obj = set(), set()
        for sp in AthleteEvents.ATHEVENTS_List:
            ok = True
            for attr, val in filters.items():
                if val is None:
                    continue
                attr_val = getattr(sp, attr)
                # supporte liste/tuple/set de valeurs => OR, sinon comparaison
                if isinstance(val, (list, tuple, set)):
                    match = False
                    for v in val:
                        if isinstance(attr_val, (int, float)) and isinstance(v, (int, float)):
                            if attr_val == v:
                                match = True
                                break
                        else:
                            if str(v) in str(attr_val):
                                match = True
                                break
                    if not match:
                        ok = False
                        break
                else:
                    if isinstance(attr_val, (int, float)) and isinstance(val, (int, float)):
                        if attr_val != val:
                            ok = False
                            break
                    else:
                        if str(val) not in str(attr_val):
                            ok = False
                            break
            if not ok:
                continue
            # construction du string de la valeur retournée selon select
            if not sel_fields:
                dummy_set.add(f"{sp.__str__()})")
            elif len(sel_fields) == 1:
                dummy_set.add(str(getattr(sp, sel_fields[0])))
            else:
                dummy_set.add(tuple(str(getattr(sp, f)) for f in sel_fields))
            # construction de la liste des objets Sport selon select
            #if not sp in dummy_list: dummy_list.append(sp)
            dummy_obj.add(sp)
        # ---------------------------------------------------------------------
        if output=="obj":
            return sorted(list(dummy_obj))   #, key=lambda s:(s.edition,s.sport,s.event,s.position), reverse=False)
        else:
            return sorted(list(dummy_set))

    @classmethod
    def load_athlete_events(cls, msgbox, options:App_Options=None) -> bool:
        # ---------------------------------------------------------------------    
        name,ext = op.splitext(options.athevent_file) 
        fname = f"{name}_DEBUG{ext}" if DEBUG else options.athevent_file
        # ------------------ Création dictionnaire athlètes -------------------
        evt_filename = op.join(options.olympicpath, fname)
        if op.isfile(evt_filename) and not options.createEvtAthFile:
            if msgbox:
                msgbox.boxtitle("Chargement fichier participations aux JO des athlètes")
                msgbox.message = f"{'Lecture fichier 5/7 en cours  0%':^50}"
            else:
                print("Lecture du fichier des participations ...")
            vg = pandas.read_csv(evt_filename, on_bad_lines="skip"); lvg = len(vg)
            # -----------------------------------------------------------------
            for i in range(lvg):
                athlete_event = AthleteEvents(vg['Name'][i],vg['Athlete_id'][i],vg['Sex'][i],vg['Born'][i],
                                        vg['Age'][i],vg['Height'][i],vg['Weight'][i],vg['Event_id'][i],vg["Edition"][i],
                                                vg["City"][i],vg["Sport"][i],vg["Event"][i],vg["Position"][i],vg["Medal"][i])
                # -------------------------------------------------------------
                if int(vg['Event_id'][i]) not in AthleteEvents.ATHEVENTS_Dico:
                    AthleteEvents.ATHEVENTS_Dico[int(vg['Event_id'][i])] = (set({vg['Name'][i],}), athlete_event)
                AthleteEvents.ATHEVENTS_Dico[int(vg['Event_id'][i])][0].add(vg['Name'][i])
                # -------------------------------------------------------------
                if int(vg['Athlete_id'][i]) not in AthleteEvents.ATHIDEVENTS_Dico:
                    AthleteEvents.ATHIDEVENTS_Dico[int(vg['Athlete_id'][i])] = set()
                AthleteEvents.ATHIDEVENTS_Dico[int(vg['Athlete_id'][i])].add(athlete_event)    
                # -------------------------------------------------------------
                if msgbox:
                    msg = f"Lecture fichier 5/7 en cours {int(i/lvg*100):>3}%"
                    if i%100 == 0: msgbox.message_update(f"{msg:^50}")
                else:
                    print(f"{int(i/lvg*100):>3}%", flush=True, end="\r")
            [AthleteEvents.ATHEVENTS_List.append(events[1]) for events in sorted(AthleteEvents.ATHEVENTS_Dico.values())]
            # -----------------------------------------------------------------
            return True
        else:
            print(f"\nFile '{options.athevent_file}' not loaded !")
            return False

    
    @classmethod
    def write_csv_eventsfile(cls, eventlist:list, options:App_Options):
        if not eventlist:
            raise ValueError("List 'eventlist' can't be empty and not None") 
        if not (isinstance(eventlist, list) and isinstance(eventlist[0], AthleteEvents)):
            raise TypeError(f"List element had to be 'AthleteEvent' class, not '{type(eventlist[0])}'")
        # ---------------------------------------------------------------------
        lines:list = [[key.capitalize() for key in eventlist[0].__dict__.keys()],]
        for athleteEvent in sorted(eventlist, key=lambda ae:(ae.name, ae.edition)):
            lines.append([f"{getattr(athleteEvent,key)}" for key in athleteEvent.__dict__.keys()])
        # ---------------------------------------------------------------------        
        with open(op.join(options.olympicpath,options.athevent_file), mode="wt", newline="", encoding="UTF-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=options.csvseparator)
            writer.writerows(lines)
            
            
    @classmethod
    def DumATHEVENT(cls) -> "AthleteEvents":
        return AthleteEvents("No ",nan,"NA","NA","NA",nan,nan,nan,"No ","No ","No ","No event","No position","No medals")
        
        
    def __init__(self,name:str,athlete_id:int,sex:str,born:str,age:str,height:float,weight:float,
                                   event_id:int,games:str,city:str,sport:str,event:str,position:str,medal:MEDALTYPE):
        
        self.name = name.strip()
        self.athlete_id:int = int(athlete_id) if not isnan(event_id) else nan
        self.sex:GENRETYPE = sex if any(x==sex for x in ["Male","Female"]) else ""
        self.born:str = born
        self.age:str = f"{age}" if str(age).isdigit() else ""
        self.height:float = self.__preform_float(height)
        self.weight:str = self.__preform_str(weight)
        self.event_id = int(event_id) if not isnan(event_id) else nan
        self.edition:str = correct_edition(games) 
        self.city:str = city
        self.sport:str = sport
        self.event:str = event
        self.position:str = self.__correctPos(position)
        self.medal:MEDALTYPE = medal.capitalize() if isinstance(medal, str) else ""
        # ---------------------------------------------------------------------
        self.add_event()
    
    def add_event(self):
        AthleteEvents.ATHEVENTS_List.append(self)
        
    def __correctPos(self, position:str) -> str:
        return "".join([c for c in position if not any(x == c for x in ["=",])])
        
    def __preform_float(self, float64:float) -> float:
        if isinstance(float64, str):
            return float64
        return float(float64) if not isnan(float64) else nan
             
    def __preform_str(self, float64:float) -> str:
        if isinstance(float64, str):
            return float64
        return "-/- " if isnan(float64) else f"{float(float64)}"
    
    def __eq__(self, other:"AthleteEvents") -> bool:
        return (self.event_id == other.event_id and
                self.athlete_id == other.athlete_id and
                self.position == other.position and
                self.edition == other.edition and
                self.medal == other.medal)
 
    def __gt__(self, other:"AthleteEvents") -> bool:
        return (int(self.edition.split(' ')[0].strip()) and self.medal) > (int(other.edition.split(' ')[0].strip()) and other.medal)
    
    def __hash__(self) -> int:
        return hash((self.athlete_id, self.event_id, self.edition, self.position, self.medal))
    
    def __repr__(self) -> str:
        if self.position != TIRET:
            rank = f"{' - (pos: '+self.position+')' if self.position.isdigit() else ' - (rank: '+self.position+')'}"
        else: ''    
        medal = f"{' - (Medal:'+self.medal+')' if self.medal in medalType_list else ''}"
        return  f"{self.sport} ({self.event}{medal if medal else rank})"
     
    def __str__(self) -> str:
        age = f" {self.age}ans" if self.age not in ["NA","",nan] else "" 
        name = self.name if len(self.name) <24 else f"{self.name[:21]}..."
        medal = f" (Medal: {self.medal})" if self.medal in medalType_list else f"Pos: {self.position}"
        height = f"{self.height}cm" if self.height != '-/- ' else f""
        weight = f"{self.weight}Kg" if self.weight != "-/- " else f""
        center = f" / " if (height and weight) else " " if (not weight or not height) else "" 
        return f"{name:<24},{age} (({self.sex}) {height}{center}{weight}): {self.edition} ({self.city}), {self.sport} ({self.event}) {medal}"


class Athlete():
    
    ATHLETES_Dico:dict = ({})
    ATHLETES_List:list = ([])
    AthleteAttributes = Literal['name','athlete_id','sex','born','naissance','height','weight','country',
                                           'description','special','events','composed_name','firstname','lastname','particle','parent','titre']
    SUPPORTED_ATTRIBUTES = get_args(AthleteAttributes)
    ATHLETE_ID_Dico:dict = ({})
    MINID, MAXID = 0,0
    
    @classmethod
    def get_Olympics_Athletes_List(cls,mode:str, *, select=None, **filters) -> list:
        """ Méthode de classe qui permet de filtrer sur aucun, un ou plusieurs des attributs
            de la classe Athlete().
            Le paramètre 'mode' selectionne le retour de la méthode, une liste d'objets de la classe ou un tuple
            composé des paramètres renseignés dans 'select=()'.  
            Exemples:
                get_Olympics_Events_List()                                  -> tous les events dans des tuples
                get_Olympics_Events_List("obj", athlete="Teddy")            -> objets Athlete contenant "Teddy" dans le nom
                get_Olympics_Events_List("obj", noc=["France","Spain"])     -> match si country contient "FRance" ou "Spain"
        """
        # validation des clés par suppression des clés incorrectes
        fkeys = {key:val for key,val in filters.items()}
        for k in fkeys.keys():
            if k not in Athlete.SUPPORTED_ATTRIBUTES:
                print(f" ---> Bad key: {k}={filters.pop(k,None)}")
        # normalization et validation du paramètre select
        sel_fields = None
        if select is not None:
            if isinstance(select, str):
                sel_fields = (select,)
            else:
                sel_fields = tuple(select)
            for f in sel_fields:
                if f not in Athlete.SUPPORTED_ATTRIBUTES:
                    raise ValueError(f"'{f}' n'est pas un attribut valide de Sport")
        charset = """[]'"'"""        
        dummy_set, dummy_obj = set(), set()
        for sp in Athlete.ATHLETES_List:
            ok = True
            for attr, val in filters.items():
                if val is None:
                    continue
                attr_val = getattr(sp, attr)
                # supporte liste/tuple/set de valeurs => OR, sinon comparaison
                if isinstance(val, (list, tuple, set)):
                    match = False
                    for v in val:
                        if isinstance(attr_val, (int, float)) and isinstance(v, (int, float)):
                            if attr_val == v:
                                match = True
                                break
                        else:
                            if str(v) in str(attr_val).strip(charset).replace("'",""):
                                match = True
                                break
                    if not match:
                        ok = False
                        break
                else:
                    if isinstance(attr_val, (int, float)) and isinstance(val, (int, float)):
                        if attr_val != val:
                            ok = False
                            break
                    else:
                        if str(val) not in str(attr_val):
                            ok = False
                            break
            if not ok:
                continue
            # construction du string de la valeur retournée selon select
            if not sel_fields:
                dummy_set.add(f"{sp.__str__()})")
            elif len(sel_fields) == 1:
                dummy_set.add(str(getattr(sp, sel_fields[0])))
            else:
                dummy_set.add(tuple(str(getattr(sp, f)) for f in sel_fields))
            # construction de la liste des objets Sport selon select
            #if not sp in dummy_list: dummy_list.append(sp)
            dummy_obj.add(sp)
        # ---------------------------------------------------------------------
        #:
        return sorted(list(dummy_obj)) if mode=="obj" else sorted(list(dummy_set))
        #else:
        #    return sorted(list(dummy_set))

    @classmethod
    def load_athlete_bio(cls, msgbox, options:App_Options=None) -> bool:
        if not options: options = App_Options()
        # ---------------------------------------------------------------------
        name,ext = op.splitext(options.athlete_file) 
        fname = f"{name}_DEBUG{ext}" if DEBUG else options.athlete_file
        # --------------- Création du dictionnaire des athlètes ---------------
        bio_filename = op.join(options.olympicpath,fname)
        if op.isfile(bio_filename):
            if msgbox:
                msgbox.boxtitle("Chargement fichier des athlètes")
                msgbox.message = f"{'Lecture fichier 6/7 en cours  0%':^50}"
            else:
                print("Lecture du fichier des athletes ...")
            og = pandas.read_csv(bio_filename, on_bad_lines="skip"); log:int = len(og)
            # -----------------------------------------------------------------            
            for i in range(log):
                Athlete.ATHLETES_Dico[int(og['athlete_id'][i])] = Athlete(int(og['athlete_id'][i]),og['name'][i],
                                               og['sex'][i],og['born'][i],og['height'][i],og['weight'][i],og['country'][i],
                                                    og['country_noc'][i],og['description'][i],og['special_notes'][i],events=[])
                if AthleteEvents.ATHIDEVENTS_Dico.get(int(og['athlete_id'][i]), 0) != 0:
                    Athlete.ATHLETES_Dico[int(og['athlete_id'][i])].events = list(AthleteEvents.ATHIDEVENTS_Dico[int(og['athlete_id'][i])])
                # -------------------------------------------------------------
                if og['name'][i] not in Athlete.ATHLETE_ID_Dico:
                    Athlete.ATHLETE_ID_Dico[og['name'][i]] = []
                Athlete.ATHLETE_ID_Dico[og['name'][i]].append(int(og['athlete_id'][i]))                  
                # -------------------------------------------------------------        
                if msgbox:
                    msg = f"Lecture fichier 6/7 en cours {int(i/log*100):>2}%"
                    if i%100 == 0: msgbox.message_update(f"{msg:^50}")
                else:
                    print(f"{int(i/log*100):>3}%", flush=True, end="\r")
                # -------------------------------------------------------------            
            Athlete.ATHLETES_List = list(Athlete.ATHLETES_Dico.values())    
            return True
        else:
            return False
        
    @classmethod
    def DumATHLETE(cls) -> "Athlete":
        return Athlete(0,"All Athlete","No genre","No date",nan,"-/- ","No countries","No noc","","",[])

    @classmethod
    def Get_Athlete(cls, athleteId:int, dumAthlete=None) -> "Athlete":
        if not isinstance(dumAthlete, Athlete): dumAthlete = Athlete.DumATHLETE()
        return Athlete.ATHLETES_Dico.get(athleteId, dumAthlete)

        
    def __init__(self, athlete_id:int,name:str,sex:str,born:str,height:float,weight:str,
                           country:str,country_noc:str,description:str,special:str,events:list):
        
        from country import Country
        
        self.athlete_id:int = athlete_id
        self.name:str = name.strip()
        self.sex:GENRETYPE = sex.capitalize()
        self.born:str = self.__preform_str(born)
        self.height:str = self.__preform_float(height)
        self.weight:str = self.__preform_str(weight)
        self.country:Country = Country.NOC_Dict[country_noc] if country_noc in Country.NOC_Dict else Country(country, country_noc)
        self.description:str = self.__preform_str(description)
        self.special:str = self.__preform_str(special)
        self.events:list[AthleteEvents] = events
        self.composed_name:tuple = ([],[])
        self.firstname:str = ""
        self.lastname:str = ""
        self.particle:list = []
        self.parent:str = ""
        self.titre:str = ""
        # ---------------------------------------------------------------------
        dateborn = self.__preform_date(born) if isinstance(born, str) else " -/- " 
        self.naissance = My_Datetime.strftime(dateborn, "%d %B %Y") if not isinstance(dateborn, str) else dateborn    
        # ---------------------------------------------------------------------
        self.__get_firstlast_name(self.name)
        self.__minmax(athlete_id)
    
    def athlete_event_age(self, born:str, eventdate:str) -> str:
        byear, eyear = "NA", "NA"
        # ---- day,month,year = search(r"^\d{1,2}",born),search(r"\D+",born),search(r"\d{4}",born)
        year = search(r"\d{4}",born)
        if year: byear = year.group()
        year = search(r"\d{4}",eventdate)
        if year: eyear = year.group()
        return f"{int(eyear)-int(byear)}" if (byear not in [None,"NA"] and eyear not in [None,"NA"]) else "NA"

    def add_event(self, event:AthleteEvents) -> tuple:
        if event.athlete_id != 0 and not event in self.events:
            self.events.extend([event,])
            return (set({self.athlete_id,}), event)

    def __get_firstlast_name(self, name:str):
        """ Extrait prénom, nom, titre et particule du nom complet 'name' et les affecte aux 
            attributs correspondants de l'objet de classe Athlete.
        """
        new_name = name  
        TI_match = PATTERN_TITRE.search(name)
        TI_suffix = TI_match.group(1) if TI_match else ""
        JS_match = PATTERN_PARENT.search(name)
        JS_suffix = JS_match.group(1) if JS_match else ""
        PA_match = PATTERN_PARTICLE.findall(name)
        PA_suffix = PA_match[0] if PA_match else ""
        
        if TI_suffix:
            self.titre = TI_suffix.capitalize()  #(TI_suffix.capitalize(), TI_match.span(1))
            new_name = PATTERN_TITRE.sub(' T ', new_name).strip()
        if PA_suffix:
            self.particle = [particle.capitalize() for particle in PA_match]
            new_name = PATTERN_PARTICLE.sub(' P ', new_name).strip()
        if JS_suffix:
            self.parent = JS_suffix  #(JS_suffix, JS_match.span(1))
            new_name = PATTERN_PARENT.sub(' J ', new_name).strip()
        
        dummy = new_name.split()
        # ---------------------------------------------------------------------
        indexes:list = ([])
        #[indexes.append((item, dummy.index(item))) for item in dummy if item in "JPT"]
        [indexes.append((item, idx)) for idx,item in enumerate(dummy) if item in "JPT"]
        self.composed_name = (dummy, indexes)
        # ---------------------------------------------------------------------    
        if indexes and len(indexes) < 2 and indexes[0][0] =='P':
            if indexes[0][1] == 1:
                self.firstname =  ' '.join(item for item in dummy[:indexes[0][1]])
                self.lastname = self.particle[0]+' '+' '.join(dummy[indexes[0][1]+1:])
            if indexes[0][1] > 1:
                self.firstname =  ' '.join(item for item in dummy[:indexes[0][1]-1])
                self.lastname = ' '.join([dummy[indexes[0][1]-1], self.particle[0],' '.join(item for item in dummy[indexes[0][1]+1:])])
        # ---------------------------------------------------------------------    
        elif indexes and indexes[0][0] =='J' and indexes[0][1] == len(dummy)-1:
            self.firstname = dummy[0]
            self.lastname = ' '.join(item for item in dummy[1:indexes[0][1]])+' '+self.parent
        # ---------------------------------------------------------------------    
        elif indexes and len(indexes) >= 2:                             # ---> dummy    = ['Étienne', 'T', 'P', 'Zuylen', 'P', 'Nijevelt'] 
            titre = list(filter(lambda idx:idx[0]=="T", indexes))       # ---> titre    = [('T', 1)]
            particle = list(filter(lambda idx:idx[0]=="P", indexes))    # ---> particle = [('P', 2), ('P', 4)]
            parent = list(filter(lambda idx:idx[0]=="J", indexes))
            if particle and titre and (particle[0][1] - titre[0][1] == 1):
                self.firstname = dummy[0]
                self.lastname = self.particle[0]+' '+' '.join(item if item != 'P' else self.particle[-1] for item in dummy[particle[0][1]+1:])
            else:
                self.firstname = dummy[0]
                self.lastname = dummy[particle[0][1]-1]+' '+self.particle[0]+' '+ \
                           ' '.join(item if item != 'P' else self.particle[-1] for item in dummy[particle[0][1]+1:])
            if parent: self.lastname += ' '+parent[0][0]
        # ---------------------------------------------------------------------    
        if not indexes and dummy:
            self.firstname = dummy[0] if len(dummy) > 1 else "" 
            self.lastname = dummy[-1] if len(dummy) < 2 else ' '.join(item for item in dummy[1:])
        # ---------------------------------------------------------------------
        #if PA_match or TI_match or JS_match:
        #    firstname = f"{self.firstname}, {self.titre[0]}" if self.titre else self.firstname
        #    print(f"{len(indexes)}   self.firstname: {firstname:16} / self.lastname:{self.lastname:20} -> {dummy} / {indexes}")
            #print(f"{dummy} / {indexes}")

    def __minmax(self, athleteId:int):
        Athlete.MINID = athleteId if athleteId < Athlete.MINID else Athlete.MINID
        Athlete.MAXID = athleteId if athleteId > Athlete.MAXID else Athlete.MAXID
        
    def __preform_float(self, float64) -> str:
        return f"{float(float64)}" if not isnan(float64) else "-/- "
             
    def __preform_str(self, string:str) -> str:
        return "-/- " if not isinstance(string, str) else string
    
    def __preform_date(self, date:str) -> My_Datetime:
        parse_date = date.split(' '); lpd = len(parse_date)
        if lpd == 3:
            if parse_date[1] not in MONTH_DICO: return date
            pdate = f"{parse_date[0]} {MONTH_DICO[parse_date[1]]} {parse_date[2]}"
            return My_Datetime.strptime(pdate, "%d %B %Y")
        elif lpd == 2:
            if parse_date[0] not in MONTH_DICO: return date
            pdate = f"{MONTH_DICO[parse_date[0]]} {parse_date[1]}"         
            return My_Datetime.strptime(pdate, "%B %Y")
        elif lpd == 1:
            if not parse_date[0].isdigit(): return date
            return My_Datetime.strptime(parse_date[0], "%Y")
        else:
            return date
    
    def __eq__(self, other:"Athlete") -> bool:
        return self.athlete_id == other.athlete_id

    def __ne__(self, other:"Athlete") -> bool:
        return self.athlete_id != other.athlete_id
    
    def __gt__(self, other:"Athlete") -> bool:
        return self.athlete_id > other.athlete_id
    
    def __hash__(self):
        return hash((self.athlete_id, self.name, self.sex, self.born, self.country))
        
    def __str__(self) -> str:
        return f"{self.name} ({self.athlete_id}), {self.sex}, {self.weight}Kg, - {self.country.country} ({self.country.noc})"

    
if __name__ == "__main__":
    
    import tkinter as tk
    
    from country import Country
    from gui_tools import Win_MessageBox
    from linuxprt import Linux_InitPrinters
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")

    root = tk.Tk()
    msgbox = Win_MessageBox(root)
    options:App_Options = None

    root.app_parameters = Saveload_CFG()
    root.Printers = Linux_InitPrinters(root)
    if root.app_parameters.cfg_load():
        options = root.app_parameters.options
        options.createEvtAthFile = False
    else:
        print(f"Options not loaded. End of program")
        exit(2) 
    
    """    
    if AthleteEvents.load_athlete_events(msgbox, options=options):
        for _ in range(5):
            athletevents = AthleteEvents.ATHEVENTS_Dico[choice(  list(map(lambda ae:ae.event_id  ,AthleteEvents.ATHEVENTS_List))  )]
            [print(event.__str__()) for event in athletevents]
        print(f"\nDumATHEVENT: {AthleteEvents.DumATHEVENT()}\n")    
    else:
        print(f"Bad file name (athletes events)")    

    AthleteAttributes = Literal['name','athlete_id','sex','born','naissance','height','weight','country',
                                           'description','special','events','composed_name','firstname','lastname','particle','parent','titre']
    """
    if Country.load_countryfile(msgbox, options=options):
        AthleteEvents.load_athlete_events(msgbox, options=options)
        #for _ in range(2):
        #    athletevents = AthleteEvents.ATHEVENTS_Dico[choice(list(map(lambda ae:ae.event_id,AthleteEvents.ATHEVENTS_List)))]
        #    [print(f"\n{event.__str__()}") for event in athletevents]
        #print(f"\nDumATHEVENT: {AthleteEvents.DumATHEVENT()}\n")    
        if Athlete.load_athlete_bio(msgbox, options=options):
            for _ in range(1):
                #athlete:Athlete = choice(Athlete.ATHLETES_List)# if _ != 1 else Athlete.ATHLETES_Dico[13167]
                athletes = Athlete.get_Olympics_Athletes_List(mode="obj",country="France",name="Longo")
                for athlete in athletes:
                    #[athlete.add_event(event) for event in AthleteEvents.get_Olympics_Events_List("obj",athlete_id=athlete.athlete_id)]                   
                    for key in athlete.__dict__.keys():
                        if key == "naissance":
                            continue
                        elif key != "events":
                            print(f"{key:<17}: {getattr(athlete, key)}")
                        else:
                            if not athlete.events:
                                print(f"{key:<17}: No events") 
                            elif len(athlete.events) < 2:
                                [print(f"{key:<17}: {event.__str__()}") for event in athlete.events]
                            else:
                                print(f"{key:<17}:") 
                                [print(f"\t\t :{event.__str__()}") for event in athlete.events]
                    print('-'*80)
                    
                print(f"Min/Max Athlète Id: {Athlete.MINID}/{Athlete.MAXID}")
                #print('-'*80)
                """ EventAttributes = Literal['name','sex','born','age','height','weight','event_id','edition','city','sport','event','medal'] """
                #AthleteEvents.load_athlete_events(msgbox, EVENTS_file)
                #print("AthleteEvents.get_Olympics_Events_List():")
                #[print(item) for item in AthleteEvents.get_Olympics_Events_List("str",edition="1906",medal="Silver")]
                #print('-'*80)
                #[print(f"{key}: {values}") for key,values in list(filter(lambda id:len(id)>=0, AthleteEvents.ATH_NAMES_Dico.items()))]
        else:
            print(f"Bad file name (athletes bio)")
    else:
        print(f"Bad file name (countries)")
    
    ath1 = Athlete(1,"a","","",170.0,"100","France","FRA","","",[])
    ath2 = Athlete(1,"b","","",180.0,"100","France","FRA","","",[])
    ath3 = Athlete(3,"c","","",190.0,"100","France","FRA","","",[])
    
    print(f"ath1 = ath2: {ath1 == ath2}")
    print(f"ath1 = ath3: {ath1 == ath3}")
    
