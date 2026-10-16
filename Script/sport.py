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

import pandas
import os.path as op

from configs import *
from gui_tools import *
from athlete import Athlete, AthleteEvents
from country import EditionGame, Country
from medailles import Medaille
from resultats import Resultat
from math import nan

class Sport():
    
    SPORTS_List:list = ([])
    SPORTS_Dico:dict = ({})
    SportAttributes = Literal['sport','edition','edition_id','noc','event','ath_id','athlete','ath_sex','position','medal','result_id','resultat','is_team']
    SUPPORTED_ATTRIBUTES = get_args(SportAttributes)
    POSITION_List:list = list([])
    
    @classmethod
    def get_Olympics_Sport_Result(cls,output:str, *, select=None, **filters) -> list:
        """ Méthode de classe qui permet de filtrer sur aucun, un ou plusieurs des attributs
            de la classe Sport(). 
            Exemples:
                get_Olympics_Events_List()                                  -> tous les events
                get_Olympics_Events_List(edition="2020")                    -> edition contenant "2020"
                get_Olympics_Events_List(edition="2020", athlete="Teddy")   -> edition contenant "2020" et athlete contenant "Teddy"
                get_Olympics_Events_List(noc=["FRA","GBR"])                 -> match si noc contient "FRA" ou "GBR"
        """
        # validation des clés par suppression des clés incorrectes
        fkeys = {key:val for key,val in filters.items()}
        for k in fkeys.keys():
            if k not in Sport.SUPPORTED_ATTRIBUTES:
                print(f" ---> Bad key: {k}={filters.pop(k,None)}")
        # normalization et validation du paramètre select
        sel_fields = None
        if select is not None:
            if isinstance(select, str):
                sel_fields = (select,)
            else:
                sel_fields = tuple(select)
            for f in sel_fields:
                if f not in Sport.SUPPORTED_ATTRIBUTES:
                    raise ValueError(f"'{f}' n'est pas un attribut valide de Sport")
        dummy_set, dummy_obj = set(), set()
        for sp in Sport.SPORTS_List:
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
    def load_sportfile(cls,msgbox:Win_MessageBox, options:App_Options) -> bool:
        position_set = set()
        spt_filename = op.join(options.olympicpath, options.sport_file)
        if op.isfile(spt_filename):
            if msgbox:
                msgbox.title("Chargement fichier des sports et épreuves")
                msgbox.message = f"{'Lecture fichier 7/7 en cours   0%':^50}"
            else:
                print("Lecture fichier des sports olympiques en cours ...")
            sp = pandas.read_csv(spt_filename, on_bad_lines="skip"); lsp = len(sp)
            # -------------------------------------------------------------
            athEvent:bool = (AthleteEvents.ATHEVENTS_Dico.__len__() != 0)
            file_exist = op.isfile(op.join(options.olympicpath, options.athevent_file))
            #if athEvent: print(f"athEvent: {athEvent}\n1/ ATHEVENTS_Dico[8300]: {AthleteEvents.ATHEVENTS_Dico[8300]}")
            # -----------------------------------------------------------------
            for i in range(lsp):
                # -------------------------------------------------------------
                edition = correct_edition(sp['edition'][i])
                country = Country.NOC_Dict[sp['country_noc'][i]].country
                dumAthlete = Athlete(sp['athlete_id'][i],sp['athlete'][i],"No genre","NA",nan,nan,country,sp['country_noc'][i],"","",[])
                athlete = Athlete.ATHLETES_Dico.get(int(sp['athlete_id'][i]), dumAthlete)
                # -------------------------------------------------------------
                if not athEvent:
                    city = EditionGame.EDITIONS_Dict.get(edition, EditionGame.DumEDITGAME()).city
                    resultat = Resultat.RESULTATS_Dico.get(int(sp['result_id'][i]),Resultat.DumRESULTAT())
                    age = athlete.athlete_event_age(athlete.born, resultat.result_date)
                    athlete_event = AthleteEvents(sp['athlete'][i],int(sp['athlete_id'][i]),athlete.sex,athlete.born,
                                                       age,athlete.height,athlete.weight,int(sp['result_id'][i]),edition,
                                                            city,sp['sport'][i],sp['event'][i],sp['pos'][i],sp['medal'][i])
                    # -------------------------------------------------------------
                    if int(sp['result_id'][i]) not in AthleteEvents.ATHEVENTS_Dico:
                        AthleteEvents.ATHEVENTS_Dico[int(sp['result_id'][i])] = athlete.add_event(athlete_event)   
                    AthleteEvents.ATHEVENTS_Dico[int(sp['result_id'][i])][0].add(athlete_event.athlete_id)
                # -------------------------------------------------------------
                Sport.SPORTS_List.append(Sport(sp['sport'][i],          edition,             int(sp['edition_id'][i]),
                                               sp['country_noc'][i],    sp['event'][i],      int(sp['athlete_id'][i]),      
                                               athlete,                 sp['pos'][i],        Medaille(sp['medal'][i]), 
                                               int(sp['result_id'][i]), sp['isTeamSport'][i]     
                                               )
                                         )                
                position_set.add(sp['pos'][i].replace('=',''))
                if sp['sport'][i] not in Sport.SPORTS_Dico:
                    Sport.SPORTS_Dico[sp['sport'][i]] = set()
                Sport.SPORTS_Dico[sp['sport'][i]].add(Sport.SPORTS_List[-1])    
                msg = f"Lecture fichier 7/7 en cours {(int(i/lsp*100)):>3}%"
                if msgbox:
                    if i%250 == 0: msgbox.message_update(f"{msg:^50}")  
                else:
                    print(f"{msg}", flush=True, end="\r")
            # -----------------------------------------------------------------
            #[print(ae.__repr__()) for ae in AthleteEvents.ATHEVENTS_List if ae.athlete_id == 13167]
            if not athEvent or not file_exist or options.createEvtAthFile:
                msgbox.message = f"Ecriture du fichier '{options.athevent_file}'"
                AthleteEvents.write_csv_eventsfile(AthleteEvents.ATHEVENTS_List, options)
            # -----------------------------------------------------------------
            #print(f"2/ ATHEVENTS_Dico[155045]: {AthleteEvents.ATHEVENTS_Dico[155045]}")
            Sport.POSITION_List = sorted(list(position_set))
            msgbox.noButton(False)
            return True
        else:
            return False

    @classmethod
    def get_Olympics_Sports_Dico(cls) -> dict:
        return {sport:sorted(list(events), key=lambda ev:ev.event) for sport,events in Sport.SPORTS_Dico.items()}

    @classmethod
    def DumSPORT(cls) -> "Sport":
        return Sport("All sports","All edition",0,"NHD","All events",0,Athlete.DumATHLETE(),"","",0,False)


    def __init__(self, sport:str, edition:str, edition_id:int, noc:str, event:str, athlete_id:int, 
                                                  athlete:Athlete,pos:str, medal:Medaille, result_id:int, is_team:str):
        self.sport:str = sport
        self.edition:str = edition
        self.edition_id:int = edition_id
        self.noc:str = noc
        self.event:str = event.strip()
        self.ath_id:int = athlete_id
        self.athlete:Athlete = athlete
        self.ath_sex:GENRETYPE = self.athlete.sex
        self.position:str = self.__correctPos(pos)
        self.medal:str = medal.medalType if isinstance(medal, Medaille) else ""
        self.result_id:int = result_id
        self.resultat:Resultat = self.__search_result(result_id)
        self.is_team:bool = is_team
    
    def __search_result(self, result_id:int) -> Resultat:
        return Resultat.RESULTATS_Dico.get(self.result_id, Resultat.DumRESULTAT())
    
    def __correctPos(self, pos:str) -> str:
        return pos.replace('=','')
        
    def __eq__(self, other:"Sport") -> bool:
        return (self.sport == other.sport and
                self.ath_id == other.ath_id and
                self.position == other.position and
                self.result_id == other.result_id)
    
    def __gt__(self, other:"Sport") -> bool:
        return (self.result_id == other.result_id)
    
    def __hash__(self) -> int:
        return hash((self.sport, self.result_id, self.ath_id, self.position))
        
    def __str__(self) -> str:
        medal = f"Medal: {self.medal}" if self.medal in medalType_list else ""
        return f"{self.edition} : {self.sport} ({self.event}), - {self.athlete.name} ({self.noc}) - (pos:{self.position}) {medal}"
    
    
if __name__ == "__main__":
    
    from random import seed,choices
    from linuxprt import Linux_InitPrinters
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")

    seed(2)
    
    root = tk.Tk()
    msgbox = Win_MessageBox(root)
    options:App_Options = None

    root.app_parameters = Saveload_CFG()
    root.Printers = Linux_InitPrinters(root)
    if root.app_parameters.cfg_load():
        options = root.app_parameters.options
    else:
        print(f"Options not loaded. End of program")
        exit(2) 
    
    Country.load_countryfile(msgbox, options)
    Resultat.load_resultsfile(msgbox, options)
    AthleteEvents.load_athlete_events(msgbox, options)
    Athlete.load_athlete_bio(msgbox, options)
    
    if Sport.load_sportfile(msgbox, options):
        AllSports = Sport.get_Olympics_Sports_Dico()
        for sport in choices(list(AllSports.keys()), k=2):
            sportList:list[Sport] = sorted(Sport.get_Olympics_Sport_Result("obj",sport=sport), key=lambda s:(s.result_id, s.athlete.name))
            print(f" ---> {sport} :")    
            if sportList:
                for sport in sportList:                
                    #age = AthleteEvents.ATHEVENTS_Dico.get(int(sport.result_id), ("No name", AthleteEvents.DumATHEVENT()))[1].age                
                    #print(f"\t{sport.resultat.__str__()} - {sport.athlete.name}{' '+age+'ans,' if age else ','} {sport.athlete.country.__repr__()}")
                    print(sport.__str__())    
        """
        print(TIRET*80)
        AllEvents = AthleteEvents.ATHEVENTS_Dico
        for event in choices(list(AllEvents.keys()), k=2):
            print(f"\n ---> {event} ({AllEvents[event][1].sport} - {AllEvents[event][1].event}):")
            [print(f"\t{ath}") for ath in AllEvents[event][0] ]
    
        print(TIRET*80)
        AllEvents = AthleteEvents.ATHEVENTS_List
        for event in choices(AllEvents, k=6):
            names = f"\n{' '*6}".join(AthleteEvents.ATHEVENTS_Dico[event.event_id][0]) + "\n"
            print(f"{event.event_id:<10}{event.sport:<22} ({event.event:^36}):\n{' '*6}{names}")
        
        print(TIRET*80)
        print(f"ATHEVENTS_Dico[8300]: {AthleteEvents.ATHEVENTS_Dico[8300]}")
        [print(item) for item in AthleteEvents.get_Olympics_Events_List("str",event_id=19000829)]
        
        athletes = Sport.get_Olympics_Sport_Result("obj",noc="ROC")
        print(f"\nAthletes number: {len(athletes)}")
        [print(athlete) for athlete in athletes]
        print('-'*80)
        results = sorted(Sport.SPORTS_Dico.get(choices(list(AllSports.keys()),k=1)[0],None), key=lambda cs:(cs[0],cs[2]))
        [print(f"\t{result[0]}: {result[1].name} ({result[1].country.noc}) - Pos: {result[2]}{result[3]}") for result in results]
        #events, = Sport.get_Olympics_Events_List(select=("edition","ed_id","sport","event",'athlete','medal'),edition="2016",event='Heavyweight, Men', noc="FRA")
        #print(f"Evènements trouvés: {len(events)}")
        #[print(event) for event in events]
        
        #events = Sport.get_Olympics_Events_List(medal=["Gold","Silver","Bronze"], noc="FRA")
        #print(f"Médaillés trouvés pour 2022 : {len(events)}")
        #[print(event) for event in events]
        """
    else:
        print(f"Bad file name")
