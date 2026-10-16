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

from configs import *

class MedalTally():
    
    MEDALTALLY_Dict:dict=({})
    MEDALTALLY_List:list=([])
    MedaltallyAttributes = Literal['edition', 'edition_id', 'year', 'country', 'noc', 'total', 'gold', 'silver', 'bronze']
    SUPPORTED_ATTRIBUTES = get_args(MedaltallyAttributes)
    
    @classmethod
    def load_medalTally(cls, msgbox, options:App_Options=None) -> bool:
        if not options: options = App_Options()
        # ---- Création dictionnaire des médailles/pays ----
        filename_tal = op.join(options.olympicpath, options.medal_file)
        if op.isfile(filename_tal):
            if msgbox:
                msgbox.title("Chargement du fichier des médailles gagnées")
                msgbox.message = f"{'Lecture du fichier 3/7 en cours ...':^50}"
            else:
                print("Lecture du fichier des médailles gagnées")
            mt = pandas.read_csv(filename_tal); lmt = len(mt)
            for i in range(lmt):
                edition = correct_edition(mt['edition'][i])
                if edition not in MedalTally.MEDALTALLY_Dict:
                    MedalTally.MEDALTALLY_Dict[edition] = []
                MedalTally.MEDALTALLY_Dict[edition].append(MedalTally(edition,int(mt['edition_id'][i]),int(mt['year'][i]),
                    mt['country'][i],mt['country_noc'][i],int(mt['total'][i]),int(mt['gold'][i]),int(mt['silver'][i]),int(mt['bronze'][i])))
                msg = f"Lecture du fichier 3/7 en cours {int(i/lmt*100):>3}%"
                if msgbox:
                    msgbox.message_update(f"{msg:^50}")
                else:
                    print(f"{msg}", flush=True, end="\r")
            [MedalTally.MEDALTALLY_List.extend(medaltally) for medaltally in MedalTally.MEDALTALLY_Dict.values()]
            return True
        else:
            return False
    
    @classmethod
    def DumMEDALTALLY(cls) -> "MedalTally":
        return MedalTally("All editions Olympics",0,0,"All country","NHD",0,0,0,0)
    
    @classmethod
    def get_event_medaltally_List(cls, eventname:str) -> list:
        return MedalTally.MEDALTALLY_Dict.get(eventname, [])
    
    
    def __init__(self, edition:str, edition_id:int, year:int, country:str, country_noc:str, total:int, gold:int=0, silver:int=0, bronze:int=0):
        self.edition = edition
        self.edition_id = int(edition_id)
        self.year = int(year)
        self.country = country
        self.noc = country_noc
        self.__total = int(total)
        self.__gold = int(gold)
        self.__silver = int(silver)
        self.__bronze = int(bronze)

    @property
    def total(self) -> int:
        return self.__total
    
    @property
    def gold(self) -> int:
        return self.__gold
    
    @property
    def silver(self) -> int:
        return self.__silver
    
    @property
    def bronze(self) -> int:
        return self.__bronze
            
    def __eq__(self, other:"MedalTally") -> bool:
        return (self.total == other.total and
                self.gold == other.gold and
                self.silver == other.silver and
                self.bronze == other.bronze)
    
    def __gt__(self, other:"MedalTally") -> bool:
        if self.__total > other.total:
            return True
        if self.__total == other.total:
            if self.__gold > other.gold:
                return True
            if self.__gold == other.gold:
                if self.__silver > other.silver:
                    return True
                if self.__silver == other.silver:
                    if self.__bronze > other.bronze:
                        return True
        return False

    def total_medals(self):
        return self.__gold + self.__silver + self.__bronze

    def __medals__(self) -> str:
        return f"{self.country} -> Medals: {self.__total} (Gold:{self.__gold} / Silver:{self.__silver} / Bronze:{self.__bronze})"

    def __hash__(self) -> int:
        return hash((self.edition_id, self.total, self.__gold, self.__silver, self.__bronze))

    def __str__(self) -> str:
        return f"{self.edition}: {self.country:<20} - Medals: {self.__total} (G:{self.__gold} / S:{self.__silver} / B:{self.__bronze})"


class EditionGame():
    
    EDITIONS_Dict:dict=({})
    EDITIONS_List:list=([])
    EditionAttributes = Literal['edition', 'edition_id', 'type', 'year', 'flag', 'city', 'noc', 'start_date', 'end_date', 'competition_date', 'isHeld']
    SUPPORTED_ATTRIBUTES = get_args(EditionAttributes)
    
    FirstEdition:int = 0
    LastEdition:int = 0
    
    @classmethod
    def load_editionGame(cls, msgbox, options:App_Options) -> bool:
        if not options: options = App_Options()
        # ---- Création dictionnaire pays ----
        filename_edt = op.join(options.olympicpath, options.edition_file)
        if op.isfile(filename_edt):
            if msgbox:
                msgbox.title("Chargement du fichier des Evènements olympiques")
                msgbox.message = f"{'Lecture du fichier 2/7 en cours ...':^50}"
            else:
                print("Chargement du fichier des Evènements olympiques")
            og = pandas.read_csv(filename_edt); log = len(og)
            for i in range(log):
                edition = correct_edition(og['edition'][i])
                EditionGame.EDITIONS_Dict[edition] = EditionGame(edition,int(og['edition_id'][i]),int(og['year'][i]),og['city'][i],
                         og['country_flag_url'][i],og['country_noc'][i],og['start_date'][i],og['end_date'][i],og['competition_date'][i],og['isHeld'][i])
                msg = f"Lecture du fichier 2/7 en cours {int(i/log*100):>3}%"
                if msgbox:
                    msgbox.message_update(f"{msg:^50}")
                else:
                    print(f"{msg}", flush=True, end="\r")
            # -----------------------------------------------------------------
            EditionGame.EDITIONS_List = list(EditionGame.EDITIONS_Dict.values())
            years_list = list(filter(lambda ed:ed.competition_date != TIRET and ed.isHeld == "", EditionGame.EDITIONS_List))
            EditionGame.FirstEdition = min(years_list).year; EditionGame.LastEdition = max(years_list).year
            # -----------------------------------------------------------------
            return True
        else:
            return False
    
    @classmethod
    def DumEDITGAME(cls) -> "EditionGame":
        return EditionGame("All editions Olympics","All Id",0,"","","NHD","","","","")
    
        
    def __init__(self, edition:str, edition_id:int, year:int, city:str, flag:str, noc:str, start_date:str, end_date:str, competition_date:str, isheld:str=''):
        self.edition:str = edition
        self.edition_id = int(edition_id) if f"{edition_id}".isdigit() else 0
        self.type:EDITIONTYPE = edition.split()[1]
        self.year = int(year)
        self.city:str = city
        self.noc:str = noc
        self.flag = flag
        self.start_date:str = self.__datetime_se_date(start_date)
        self.end_date:str = self.__datetime_se_date(end_date)
        self.competition_date:str = self.__datetime_competime(competition_date)
        self.isHeld:str = "" if not isinstance(isheld, str) else isheld
            
    def __eq__(self, other:"EditionGame") -> bool:
        return self.edition_id == other.edition_id
    
    def __gt__(self, other:"EditionGame") -> bool:
        return self.edition_id > other.edition_id
    
    def __hash__(self) -> int:
        return hash(self.edition_id)        
    
    def __datetime_se_date(self, date:str) -> str:
        if date and isinstance(date, str):
            d = date.strip().split(' ')
            # ------------------------------------------------------------
            if len(d) == 3:
                masque = "%d %B %Y"
                day, month, year = d 
            else:
                masque = "%d %B"
                day, month = d; year = self.year
                day = f"0{day}" if int(day) in list(range(1,10)) else day
            # ------------------------------------------------------------
            date = datetime.strptime(f"{day} {MONTH_DICO.get(month,month)} {year}", "%d %B %Y")
            return date.strftime(masque)
        else:
            return ''
                
    def __datetime_competime(self, competition_date:str) -> str:
        dates:list = ([])
        [dates.extend(item) for item in list(map(lambda e:e.strip().split(' '), competition_date.strip().split(f'{TIRET}')))]
        #print(f"dates: {self.year} - {dates}")
        if not dates[0].isalnum():
            return f"{TIRET}"
        if len(dates) == 2 and dates[0].isdigit() and dates[1].isalpha():
            return f"{dates[0]} {MONTH_DICO[dates[1]]}"
        if len(dates) == 3 and dates[0].isdigit() and dates[1].isdigit():
            return f"{dates[0]} au {dates[1]} {MONTH_DICO[dates[2]]}"
        if len(dates) >= 4 and dates[0].isdigit() and dates[2].isdigit():
            return f"{dates[0]} {MONTH_DICO[dates[1]]} au {dates[2]} {MONTH_DICO[dates[3]]} {dates[4] if len(dates) > 4 else ''}"
        
    def __str__(self) -> str:
        return f"Ed.{self.edition_id:>2} - {self.edition:<20}: {self.city:<25} {self.competition_date} {self.isHeld}"
        
    
class Country():
    
    NOC_Dict:dict = ({})
    NOC_List:list = ([])
    COUNTRY_Dico:dict = ({})
    CountryAttributes = Literal['country','noc','editions','medalstally']
    SUPPORTED_ATTRIBUTES = get_args(CountryAttributes)
    
    @classmethod
    def load_countryfile(cls, msgbox, options:App_Options=None) -> bool:
        if not options: options = App_Options()
        # ---- Création dictionnaire pays ----
        filename_noc = op.join(options.olympicpath,options.country_file)
        if op.isfile(filename_noc) and EditionGame.load_editionGame(msgbox, options) and MedalTally.load_medalTally(msgbox, options):
            if msgbox:
                msgbox.title("Chargement fichier des pays participants/organisateurs")
                msgbox.message = f"{'Lecture du fichier 1/7 en cours   0%':^50}"
            else:
                print("Chargement fichier des pays participants/organisateurs")
            pdcsv = pandas.read_csv(filename_noc); lpd = len(pdcsv)
            for i in range(lpd):
                # ----------------------------------------------------------
                Country.NOC_Dict[pdcsv['noc'][i]] = Country(pdcsv['country'][i], pdcsv['noc'][i])
                editions = list(filter(lambda eg:eg.noc == pdcsv['noc'][i], EditionGame.EDITIONS_Dict.values()))          
                [Country.NOC_Dict[pdcsv['noc'][i]].add_medaltally(edition) for edition in editions]
                [Country.NOC_Dict[pdcsv['noc'][i]].add_edition(edition) for edition in editions]
                # ----------------------------------------------------------
                msg = f"Lecture du fichier 1/7 en cours {int(i/lpd*100):>3}%"
                if msgbox:
                    msgbox.message_update(f"{msg:^50}")  
                else:
                    print(f"{msg}", flush=True, end="\r")
            Country.NOC_List = list(Country.NOC_Dict.values())
            Country.COUNTRY_Dico = {value.country:value for value in Country.NOC_Dict.values()}
            return True
        else:
            return False
    
    @classmethod
    def DumCOUNTRY(cls):
        return Country("All countries", "NHD")
    
    
    def __init__(self, country:str, noc:str):
        self.country = country
        self.noc = noc
        self.pays = COUNTRY_Dico.get(country, country)
        self.editions:list[EditionGame] = ([])
        self.medalstally:list[MedalTally] = ([])
    
    def add_edition(self, edition:EditionGame):
        self.editions.append(edition)
    
    def add_medaltally(self, edition:EditionGame):
        self.medalstally.extend(MedalTally.get_event_medaltally_List(edition.edition))
    
    def __eq__(self, other:"Country") -> bool:
        return (self.country == other.country and self.noc == other.noc)
    
    def __gt__(self, other:"Country") -> bool:
        return self.country > other.country
    
    def __hash__(self) -> int:
        return hash((self.country, self.noc))
        
    def __str__(self) -> str:
        return f"{self.noc}, {self.country}:\n\t" + "\n\t".join([ed.__str__() for ed in self.editions])

    def __repr__(self) -> str:
        return f"{self.country} ({self.noc})"

if __name__ == "__main__":
    
    import tkinter as tk
    from random import choice,choices,randint
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
        
    if EditionGame.load_editionGame(msgbox, options=options):
        print(f"First edition: {EditionGame.FirstEdition} / Last edition: {EditionGame.LastEdition}")
        print('-'*40); print('class EditionGame() :')
        #for edition in choices(list(EditionGame.EDITIONS_Dict.keys()), k=3):
        for edition in EditionGame.EDITIONS_Dict.keys():
            ed = EditionGame.EDITIONS_Dict[edition]
            if any(e in edition for e in ["Equestrian","Intercalated"]):
                [print(f"{key:<17}: {getattr(ed,key)}") for key in ed.__dict__.keys()]
                print('-'*40)
        print()      
    else:
        print(f"Bad EditionGame file name")
    """
    if Country.load_countryfile(msgbox, options=options):
        # ------- print of each parameter of one instance of Country() ------ #
        country = choice(list(filter(lambda c:c.editions != [], Country.NOC_Dict.values()))); noc = country.noc
        #for noc in ["URS","RUS","ROC"]:
        #    country = Country.NOC_Dict[noc]
        #    [print(f"{key:<17}: {getattr(country,key) }") for key in country.__dict__.keys()]
        #for country in choices(list(Country.COUNTRY_Dico.keys()), k=3):
        #    pays = Country.COUNTRY_Dico[country]
        #    [print(f"{key:<17}: {getattr(pays,key)}") for key in pays.__dict__.keys()]
        #    print('-'*40)
        # ------- print of instance of Country() if Country.noc == noc ------ #    
        
        for edition in sorted(country.editions,key=lambda c:c.year):
            print(f"{' ':19}{edition.__str__()}")
            [print(f"{' ':24}{medaltally.__medals__()}") for medaltally in country.medalstally \
                                if edition.edition_id == medaltally.edition_id] # and edition.noc == medaltally.noc]
    else:
        print(f"Bad file name")
    """
    print(f"\nclass MedalTally() :")    
    if MedalTally.load_medalTally(msgbox, options=options):
        editions = choice(list(MedalTally.MEDALTALLY_Dict.values()))
        for idx,edition in enumerate(sorted(editions, key=lambda c:c.total, reverse=True)):
            print(f"\t{idx:>2} - {edition}")
        print("-"*80)
        a,b = [randint(0,len(editions)-1) for _ in range(2)]
        print(f"medaltally_{a} > medaltally_{b}: {editions[a] > editions[b]}")
    else:
        print(f"Bad file name")
