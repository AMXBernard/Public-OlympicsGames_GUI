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

import os
import cups
import locale
import os.path as op
import pickle as pkdata

from re import compile,IGNORECASE
#from dataclasses import dataclass
from typing import Literal,get_args
from itertools import zip_longest
from datetime import datetime

DEBUG:bool = True

GENRETYPE = Literal["Homme","Femme","Non genré","Male","Female","No genre"]
genreType_list = get_args(GENRETYPE)
# --------------------------------------------------------------------------- #
SEARCHTYPE = Literal["nom","olympiade","pays","global","multi","Id"]
searchType_List = get_args(SEARCHTYPE)
# --------------------------------------------------------------------------- #
SORTLISTYPE = Literal["name","country","edition","city","sport"]
sortlistType_List = get_args(SORTLISTYPE)
# --------------------------------------------------------------------------- #
MEDALTYPE = Literal["Gold","Silver","Bronze"]
medalType_list = get_args(MEDALTYPE)
# --------------------------------------------------------------------------- #
EDITIONTYPE = Literal["Winter","Summer","Intercalated","Equestrian"]
editiontype_list = get_args(EDITIONTYPE)
# --------------------------------------------------------------------------- #
#OGGFILETYPE = Literal["AthleteBIO","EvtResults","EvtAthlete","Edition",'Medaltally',"Country","Results"]
#oggfiletype_list = get_args(OGGFILETYPE)
# --------------------------------------------------------------------------- #
CMODETYPE = Literal["Sys","Oly","Noc","Img","Cfg","Bck","Hlp","Ath","Bio","Spt","Mdl","Res","Evt","Rnk","Sex"]
cmodetype_List = get_args(CMODETYPE)
# --------------------------------------------------------------------------- #
CSVSEPARATOR = Literal[",",";","\t"]
csvsep_list = get_args(CSVSEPARATOR)
# --------------------------------------------------------------------------- #
DATA_PATH = op.join(os.getcwd(),"Data")
OLYMPIC_PATH = op.join(os.getcwd(),"OlympicData")
IMAGE_PATH = op.join(os.getcwd(),"Image")
# --------------------------------------------------------------------------- #
HELP_file = "olympicgames.hlp"
CONFIG_file = "olympicgames.cfg"
BACK_file = "olympicgames.jpg"
# --------------------------------------------------------------------------- #
SPORT_file = "Olympic_Athlete_Event_Results.csv"
MEDAL_file = "Olympic_Games_Medal_Tally.csv"
EVENTS_file = "Olympic_athlete_events.csv"
ATHLETE_file = "Olympic_Athlete_Bio.csv"
COUNTRY_file = "Olympics_Country.csv"
RESULTS_file = "Olympic_Results.csv"
EDITION_file = "Olympics_Games.csv"
# --------------------------------------------------------------------------- #
now = datetime.now()        # --- objet datetime pour horodatage fichiers --- #
# --------------------------------------------------------------------------- #
offset_W, offset_H = 250, 150
GENRE_Dico:dict = { "Homme":"Male","Femme":"Female","Non genré":"No genre"}
MONTH_DICO:dict = { "January":"Janvier","February":"Février",   "March":"Mars",
                    "April":"Avril",    "May":"Mai",            "June":"Juin",
                    "July":"Juillet",   "August":"Août",        "September":"Septembre",
                    "October":"Octobre","November":"Novembre",  "December":"Décembre"}
MEDALCOLOR_Dico:dict = {"Gold":"#FAE955","Silver":"#CECCCC","Bronze":"#9B795E"}
TIRET = '–'   # --- Le tiret cadratin est encodé en Unicode comme U+2014 (décimal 8212) et représente en HTML &mdash
#print(f"'–' est le caractère {ord('–')}")

PATTERN_TITRE = compile(r',\s(Count|Marquis[e]?|Baron[ne]*|[Vi]*co[mn]?te[se]*|Grevinna)',flags=IGNORECASE)
PATTERN_PARTICLE = compile(r'\s([dl]\'|d[euaio](?:[sr]\b)*(?:\sla)*|v[ao]n(?:\sde[nr]\b)*)\s',flags=IGNORECASE)
PATTERN_PARENT = compile(r',\s([JS]r\.)$',flags=IGNORECASE)

COUNTRY_Dico = {"Afghanistan": "Afghanistan","Albania": "Albanie","Algeria": "Algérie","American Samoa": "Samoa américaines","Andorra": "Andorre",
    "Angola": "Angola","Antigua and Barbuda": "Antigua-et-Barbuda","Argentina": "Argentine","Armenia": "Arménie","Aruba": "Aruba","Australasia": "Australasie",
    "Australia": "Australie","Austria": "Autriche","Azerbaijan": "Azerbaïdjan","Bahrain": "Bahreïn","Bangladesh": "Bangladesh","Barbados": "Barbade",
    "Belarus": "Biélorussie","Belgium": "Belgique","Belize": "Belize","Benin": "Bénin","Bermuda": "Bermudes","Bhutan": "Bhoutan","Bohemia": "Bohême",
    "Bolivia": "Bolivie","Bosnia and Herzegovina": "Bosnie-Herzégovine","Botswana": "Botswana","Brazil": "Brésil","British Virgin Islands": "Îles Vierges britanniques",
    "Brunei Darussalam": "Brunéi Darussalam","Bulgaria": "Bulgarie","Burkina Faso": "Burkina Faso","Burundi": "Burundi","Cabo Verde": "Cap-Vert",
    "Cambodia": "Cambodge","Cameroon": "Cameroun","Canada": "Canada","Cayman Islands": "Îles Caïmans","Central African Republic": "République centrafricaine",
    "Chad": "Tchad","Chile": "Chili","Chinese Taipei": "Taïpei chinois","Colombia": "Colombie","Comoros": "Comores","Congo": "Congo","Cook Islands": "Îles Cook",
    "Costa Rica": "Costa Rica","Côte d'Ivoire": "Côte d'Ivoire","Crete": "Crète","Croatia": "Croatie","Cuba": "Cuba","Cyprus": "Chypre","Czechia": "Tchéquie",
    "Czechoslovakia": "Tchécoslovaquie","Democratic People's Republic of Korea": "République populaire démocratique de Corée","Democratic Republic of the Congo": "R.Dém. du Congo",
    "Denmark": "Danemark","Djibouti": "Djibouti","Dominica": "Dominique","Dominican Republic": "République dominicaine","East Germany": "Allemagne de l'Est",
    "Ecuador": "Équateur","Egypt": "Égypte","El Salvador": "Salvador","Equatorial Guinea": "Guinée équatoriale","Eritrea": "Érythrée","Estonia": "Estonie",
    "Eswatini": "Eswatini","Ethiopia": "Éthiopie","Federated States of Micronesia": "États fédérés de Micronésie","Fiji": "Fidji","Finland": "Finlande",
    "France": "France","Gabon": "Gabon","Georgia": "Géorgie","Germany": "Allemagne","Ghana": "Ghana","Great Britain": "Grande-Bretagne","Greece": "Grèce",
    "Grenada": "Grenade","Guam": "Guam","Guatemala": "Guatemala","Guinea": "Guinée","Guinea Bissau": "Guinée-Bissau","Guyana": "Guyana","Haiti": "Haïti",
    "Honduras": "Honduras","Hong Kong, China": "Hong Kong, Chine","Hungary": "Hongrie","Iceland": "Islande","Independent Olympic Athletes": "Athlètes olympiques indépendants",
    "India": "Inde","Individual Neutral Athletes": "Athlètes neutres individuels","Indonesia": "Indonésie","Iraq": "Irak","Ireland": "Irlande","Israel": "Israël",
    "Islamic Republic of Iran": "République islamique d'Iran","Italy": "Italie","Jamaica": "Jamaïque","Japan": "Japon","Jordan": "Jordanie","Kazakhstan": "Kazakhstan",
    "Kenya": "Kenya","Kingdom of Saudi Arabia": "Royaume d'Arabie saoudite","Kiribati": "Kiribati","Korea Team": "Équipe de Corée","Kosovo": "Kosovo","Kuwait": "Koweït",
    "Kyrgyzstan": "Kirghizistan","Lao People's Democratic Republic": "République démocratique populaire lao","Latvia": "Lettonie","Lebanon": "Liban","Lesotho": "Lesotho",
    "Liberia": "Libéria","Libya": "Libye","Liechtenstein": "Liechtenstein","Lithuania": "Lituanie","Luxembourg": "Luxembourg","Madagascar": "Madagascar","Malawi": "Malawi",
    "Malaya": "Malaisie","Malaysia": "Malaisie","Maldives": "Maldives","Mali": "Mali","Malta": "Malte","Marshall Islands": "Îles Marshall","Mauritania": "Mauritanie",
    "Mauritius": "Ile Maurice","Mexico": "Mexique","Mixed team": "Équipe mixte","Monaco": "Monaco","Mongolia": "Mongolie","Montenegro": "Monténégro","Morocco": "Maroc",
    "Mozambique": "Mozambique","Myanmar": "Myanmar","Namibia": "Namibie","Nauru": "Nauru","Nepal": "Népal","Netherlands": "Pays-Bas","Netherlands Antilles": "Antilles néerlandaises",
    "New Zealand": "Nouvelle-Zélande","Newfoundland": "Terre-Neuve","Nicaragua": "Nicaragua","Niger": "Niger","Nigeria": "Nigéria","North Borneo": "Bornéo du Nord",
    "North Macedonia": "Macédoine du Nord","North Yemen": "Yémen du Nord","Norway": "Norvège","Oman": "Oman","Pakistan": "Pakistan","Palau": "Palaos","Palestine": "Palestine",
    "Panama": "Panama","Papua New Guinea": "Papouasie-Nouvelle-Guinée","Paraguay": "Paraguay","Peru": "Pérou","Poland": "Pologne","People's Republic of China": "République populaire de Chine",
    "Philippines": "Philippines","Portugal": "Portugal","Puerto Rico": "Porto Rico","Qatar": "Qatar","Refugee Olympic Team": "Équipe olympique des réfugiés",
    "Republic of Korea": "République de Corée","Republic of Moldova": "Moldavie","Rhodesia": "Rhodésie","Romania": "Roumanie","Russian Federation": "Fédération de Russie",
    "Rwanda": "Rwanda","Saar": "Sarre","Saint Lucia": "Sainte-Lucie","Saint Kitts and Nevis": "Saint-Christophe-et-Niévès","Saint Vincent and the Grenadines": "Saint-Vincent-et-les-Grenadines",
    "Samoa": "Samoa","San Marino": "Saint-Marin","São Tomé and Príncipe": "Sao Tomé-et-Principe","Senegal": "Sénégal","Serbia": "Serbie","Serbia and Montenegro": "Serbie-et-Monténégro",
    "Seychelles": "Seychelles","Sierra Leone": "Sierra Leone","Singapore": "Singapour","Slovakia": "Slovaquie","Slovenia": "Slovénie","Solomon Islands": "Îles Salomon",
    "Somalia": "Somalie","South Africa": "Afrique du Sud","South Sudan": "Soudan du Sud","South Vietnam": "Sud Viêt Nam","South Yemen": "Yémen du Sud","Soviet Union": "Union soviétique",
    "Spain": "Espagne","Sri Lanka": "Sri Lanka","Sudan": "Soudan","Suriname": "Suriname","Sweden": "Suède","Switzerland": "Suisse","Syrian Arab Republic": "Syrie",
    "Tajikistan": "Tadjikistan","Thailand": "Thaïlande","The Bahamas": "Bahamas","The Gambia": "Gambie","Timor-Leste": "Timor oriental","Togo": "Togo","Tonga": "Tonga",
    "Trinidad and Tobago": "Trinité-et-Tobago","Tunisia": "Tunisie","Türkiye": "Turquie","Turkmenistan": "Turkménistan","Tuvalu": "Tuvalu","Uganda": "Ouganda",
    "Ukraine": "Ukraine","Unified Team": "Équipe unifiée","United Arab Emirates": "Émirats arabes unis","United Arab Republic": "République arabe unie","Unknown": "Inconnu",
    "United Republic of Tanzania": "République-Unie de Tanzanie","United States": "États-Unis","United States Virgin Islands": "Îles Vierges des États-Unis",
    "Uruguay": "Uruguay","Uzbekistan": "Ouzbékistan","Vanuatu": "Vanuatu","Venezuela": "Vénézuela","Vietnam": "Viêt Nam","West Germany": "Allemagne de l'Ouest",
    "West Indies Federation": "Fédération des Indes occidentales","Yemen": "Yémen","Zambia": "Zambie","Yugoslavia": "Yougoslavie","Zimbabwe": "Zimbabwe",
    "Russian Olympic Committee": "Comité olympique russe"
                }


def correct_filename(filename:str) -> str:
    goodchars = "abcdefghijklmnopqrstuvwxyz0123456789-_."
    if filename.count('.')==0:
        return "".join([c for c in filename if c.lower() in goodchars]) + ".CSV"
    else:
        name, ext = filename.rsplit('.',maxsplit=1)
        if ext.lower() != "csv": ext = 'CSV'
        return "".join([c for c in name if c.lower() in goodchars]) +"."+ ext

    
def correct_edition(edition:str) -> str:
    if "Olympics" in edition:
        return edition
    if "Games" in edition:
        return edition.replace('  ',' ').replace('Games','Olympics')
    else:
        return f"{edition.replace('  ',' ').strip()} Olympics"
            

"""
@dataclass
class Global_AthletesList(object):
    name:str
    country:str
    edition:str
    city:str
    sport:str
    
    def __str__(self) -> str:
        return f"{self.name:<40}|{self.country}|{self.edition:<20}|{self.city:<20}|{self.sport}"
"""        

class My_Datetime(datetime):

    Long:bool = False
    
    def __init__(self, year:int, month:int, day:int, h:int=0,m:int=0,s:int=0,ms:int=0,tz:int=None):
        super().__init__()
        self.__my_date = datetime(year=year,month=month,day=day,hour=h,minute=m,second=s,microsecond=ms,tzinfo=tz)
    
    def __str__(self) -> str:
        return datetime.strftime(datetime(self.__my_date.year,self.__my_date.month,self.__my_date.day),"%A %d %B %Y") \
                            if My_Datetime.Long else datetime.strftime(self.__my_date.date(),"%d/%m/%Y")  


class App_Size():
    def __init__(self, width:int=1450, height:int=910):
        self.__width:int = width
        self.__height:int = height

    @property
    def width(self) -> int:
        return self.__width
    
    @property
    def height(self) -> int:
        return self.__height
 
    @property
    def app_size(self) -> tuple:
        return self.__width,self.__height
    @app_size.setter
    def app_size(self, size:tuple):
        self.__width = size[0] if size[0] != None else self.__width
        self.__height = size[1] if size[1] != None else self.__height
        
    def __str__(self) -> str:
        return f"{self.app_size}"


class Search_Options():
    def __init__(self,cases:bool=True,whole:bool=False,exact:bool=False,regexp:bool=False,
                        scaleid:int=50,patronym:bool=False,multiId:bool=False,sortlist:SORTLISTYPE="name"):
        # ---------------------------------------------------------------------
        self.__sortlist:SORTLISTYPE = sortlist
        self.__cases:bool = cases
        self.__whole:bool = whole
        self.__exact:bool = exact
        self.__scaleId:int = scaleid
        self.__patronym:bool = patronym
        self.__multiId:bool = multiId
        self.__regexp:bool = regexp
        
    @property
    def sortList(self) -> SORTLISTYPE:
        return self.__sortlist
    @sortList.setter
    def sortList(self, sortlist:SORTLISTYPE):
        self.__sortlist = sortlist 

    @property
    def cases(self) -> bool:
        return self.__cases
    @cases.setter
    def cases(self, cases):
        self.__cases = bool(cases)
        
    @property
    def whole(self) -> bool:
        return self.__whole
    @whole.setter
    def whole(self, whole):
        self.__whole = bool(whole)
        
    @property
    def exact(self) -> bool:
        return self.__exact
    @exact.setter
    def exact(self, exact):
        self.__exact = bool(exact)  
        
    @property
    def regexp(self) -> bool:
        return self.__regexp
    @regexp.setter
    def regexp(self, regexp):
        self.__regexp = bool(regexp) 
        
    @property
    def patronym(self) -> bool:
        return self.__patronym
    @patronym.setter
    def patronym(self, patronym):
        self.__patronym = bool(patronym) 
        
    @property
    def multiId(self) -> int:
        return self.__multiId
    @multiId.setter
    def multiId(self, multiId:int):
        self.__multiId = multiId
        
    @property
    def scaleId(self) -> int:
        return self.__scaleId
    @scaleId.setter
    def scaleId(self, scaleid:int):
        self.__scaleId = scaleid

    def __str__(self) -> str:
        return f"sortList: {self.sortList}, case: {self.cases}, whole: {self.whole}, exact: {self.exact}, patronyme: {self.patronym}, scaleId: {self.scaleId}, MultiId: {self.multiId}, RegEx: {self.regexp}"


class App_Options(object):
    """ Classe regroupant tous les paramètres de l'application """    
    def __init__(self):
        # -------------------------------------------------
        self.__data_path:str = DATA_PATH
        self.__olympic_path:str = OLYMPIC_PATH
        self.__images_path:str = IMAGE_PATH
        # -------------------------------------------------
        self.__params_fname:str = CONFIG_file
        self.__help_filename:str = HELP_file
        self.__back_filename:str = BACK_file
        # -------------------------------------------------
        self.__sport_file:str = SPORT_file
        self.__medal_file:str = MEDAL_file
        self.__result_file:str = RESULTS_file
        self.__athlete_file:str = ATHLETE_file
        self.__country_file:str = COUNTRY_file
        self.__edition_file:str = EDITION_file
        self.__athevent_file:str = EVENTS_file
        # -------------------------------------------------
        self.__app_size = App_Size().app_size           # -- taille de l'application défaut: VESA (1366x768)
        self.__fullscreen:bool = False                  # -- bascule mode plein écran/fenêtré
        self.__date_long:bool = True                    # -- affichage des dates au format long (ie: lundi 4 mars 2025)
        self.__csv_separator:CSVSEPARATOR = ','         # -- caractère séparateur de fichiers 'CSV'
        # -------------------------------------------------
        self.__splashscreen:bool = False                # -- fenetre à propos au démarrage       
        self.__saveCFG_on_quit:bool = True              # -- sauvegarde config en quittant
        self.__createEvtAthFile:bool = False            # -- création dur fichier des épreuves par athlète
        self.__search_opt = Search_Options()            # -- boolean search options (case sensitive, whole word, exact word, regexp, searchsort)
        # -------------------------------------------------
        self.__default_printer = cups.Connection().getDefault()
        # -------------------------------------------------
        self.__policy_family:str = 'Consolas'
        self.__length_line:int = 120
    
    @property
    def sport_file(self) -> str:
        return self.__sport_file   
    @sport_file.setter
    def sport_file(self, sportfile:str):
        self.__sport_file = sportfile
    
    @property
    def medal_file(self) -> str:
        return self.__medal_file
    @medal_file.setter
    def medal_file(self, medalfile:str):
        self.__medal_file = medalfile
    
    @property
    def athevent_file(self) -> str:
        return self.__athevent_file
    @athevent_file.setter
    def athevent_file(self, atheventfile:str):
        self.__athevent_file = atheventfile
    
    @property
    def athlete_file(self) -> str:
        return self.__athlete_file
    @athlete_file.setter
    def athlete_file(self, athletefile:str):
        self.__athlete_file = athletefile
    
    @property
    def result_file(self) -> str:
        return self.__result_file
    @result_file.setter
    def result_file(self, resultfile:str):
        self.__result_file = resultfile
        
    @property
    def country_file(self) -> str:
        return self.__country_file
    @country_file.setter
    def country_file(self, countryfile:str):
        self.__country_file = countryfile
             
    @property
    def edition_file(self) -> str:
        return self.__edition_file
    @edition_file.setter
    def edition_file(self, editionfile:str):
        self.__edition_file = editionfile

    @property
    def csvseparator(self) -> CSVSEPARATOR:
        return self.__csv_separator
    @csvseparator.setter
    def csvseparator(self, csvseparator:CSVSEPARATOR):
        self.__csv_separator = csvseparator
        
    @property
    def policy_family(self) -> str:
        return self.__policy_family
    @policy_family.setter
    def policy_family(self, family:str):
        self.__policy_family = family
        
    @property
    def length_line(self) -> int:
        return self.__length_line
    @length_line.setter
    def length_line(self, length:int):
        self.__length_line = length
        
    @property
    def default_printer(self) -> str:
        return self.__default_printer
    @default_printer.setter
    def default_printer(self, prtname:str):
        if prtname != cups.Connection().getDefault():
            self.__default_printer = prtname
            cups.Connection().setDefault(prtname)
    
    @property
    def splashscreen(self) -> bool:
        return self.__splashscreen
    @splashscreen.setter
    def splashscreen(self, splashscreen:bool):
        self.__splashscreen = splashscreen
    
    @property
    def datelong(self) -> bool:
        return self.__date_long
    @datelong.setter
    def datelong(self, datelong:bool):
        self.__date_long = datelong
    
    @property
    def saveCFGonquit(self) -> bool:
        return self.__saveCFG_on_quit
    @saveCFGonquit.setter
    def saveCFGonquit(self, saveCFG_on_quit:bool):
        self.__saveCFG_on_quit = saveCFG_on_quit
    
    @property
    def createEvtAthFile(self) -> bool:
        return self.__createEvtAthFile
    @createEvtAthFile.setter
    def createEvtAthFile(self, createvtathfile:bool):
        self.__createEvtAthFile = createvtathfile
        
    @property
    def search_options(self) -> Search_Options:
        return self.__search_opt
    @search_options.setter
    def search_options(self, search_option):
        if isinstance(search_option, (tuple, list)):
            [setattr(self.__search_opt, key, param) for key,param in \
                 list(zip_longest(self.__search_opt.__dict__.keys(),search_option,fillvalue=False))]
        if isinstance(search_option, Search_Options):
            [setattr(self.__search_opt, key, param) for key,param in search_option.__dict__.items()]
    
    @property
    def app_size(self) -> tuple:
        return self.__app_size
    @app_size.setter
    def app_size(self, app_size:tuple):
        self.__app_size = app_size 
    
    @property
    def fullscreen(self) -> bool:
        return self.__fullscreen
    @fullscreen.setter
    def fullscreen(self, fullscreen):
        self.__fullscreen = fullscreen
        
    @property
    def paramfilename(self) -> str:
        return self.__params_fname
    @paramfilename.setter
    def paramfilename(self, filename:str):
        self.__params_fname = filename
        
    @property
    def olympicpath(self) -> str:
        return self.__olympic_path
    @olympicpath.setter
    def olympicpath(self, pathname:str):
        self.__olympic_path = pathname
        
    @property
    def datapath(self) -> str:
        return self.__data_path
    @datapath.setter
    def datapath(self, pathname):
        self.__data_path = pathname
        
    @property
    def imagepath(self) -> str:
        return self.__images_path
    @imagepath.setter
    def imagepath(self, pathname):
        self.__images_path = pathname

    @property
    def exportCSVpath(self) -> str:
        return self.__exportCSV_path
    @exportCSVpath.setter
    def exportCSVpath(self, pathname):
        self.__exportCSV_path = pathname
        
    @property
    def helpfilename(self) -> str:
        return self.__help_filename
    @helpfilename.setter
    def helpfilename(self, filename:str):
        self.__help_filename = filename
        
    @property
    def backfilename(self) -> str:
        return self.__back_filename
    @backfilename.setter
    def backfilename(self, filename:str):
        self.__back_filename = filename
        
    def __str__(self) -> str:
        return "\n".join([f"{key.replace('_App_Options',''):19}: {getattr(self, key)}" for key in self.__dict__.keys()])
            
                
class Saveload_CFG(object):
    
    def __init__(self):
        # --- Constructeur 'self.__options' avec les paramètres par défaut ----
        self.__options = App_Options()
        self.__filename = op.join(os.getcwd(),self.options.datapath, self.options.paramfilename)    
        self.__parameters = [getattr(self.__options, key) for key in self.__options.__dict__.keys()]
        # ---------------------------------------------------------------------
        self.__options.paramfilename = op.basename(self.__filename)
 
    @property
    def options(self) -> App_Options:
        return self.__options
    @options.setter
    def options(self, parameters:list):
        if isinstance(parameters, list):
            [setattr(self.__options, key, param) for key,param in list(zip(self.__options.__dict__.keys(),parameters))]
        elif isinstance(parameters, App_Options):
            [setattr(self.__options, key, param) for key,param in parameters.__dict__.items()]
    
    @property
    def parameters(self) -> list:
        return [getattr(self.__options, key) for key in self.__options.__dict__]
        
    def cfg_backup(self, options=None):
        if not isinstance(options, App_Options): options = None
        params = self.parameters if not options else options
        try:
            with open(self.__filename, 'wb') as outputfic:
                pkdata.dump(params, outputfic, pkdata.HIGHEST_PROTOCOL )
        except FileNotFoundError as msg:
            print(f" backup error {os.path.basename(self.__filename)}: {msg}")
            return False
        return True
        
    def cfg_load(self):
        if not op.isfile(self.__filename):
            if not op.isdir(op.join(os.getcwd(),DATA_PATH)):
                os.mkdir(path=DATA_PATH)
            if not op.isdir(op.join(os.getcwd(),IMAGE_PATH)):
                os.mkdir(path=IMAGE_PATH)
            if not op.isdir(op.join(os.getcwd(),OLYMPIC_PATH)):
                os.mkdir(path=OLYMPIC_PATH)
            self.cfg_backup()
        # ---------------------------------------------------------------------
        try:
            with open(self.__filename, 'rb') as inputfic:
                self.__parameters = pkdata.load(inputfic)
        except Exception as msg:
            print(f" load error {os.path.basename(self.__filename)}: {msg}")            
            return False
        # ---------------------- Paramètres sauvegardés -----------------------
        if self.__parameters:
            self.options = self.__parameters
            return True
        # ---------------------------------------------------------------------
        return False


if __name__ == "__main__":
    
    import tkinter as tk
    
    from country import EditionGame
    from linuxprt import Linux_InitPrinters
    from gui_tools import Parameters
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")
    # -------------------------------------------------------------------------
     
    root = tk.Tk()
    root.app_parameters = Saveload_CFG()
    root.Printers = Linux_InitPrinters(root)
    if root.app_parameters.cfg_load():
        EditionGame.load_editionGame(None, options=root.app_parameters.options)
        print(f"\nConfig file '{root.app_parameters.options.paramfilename}' lu")
        options = Parameters(root, root.app_parameters.options).go()
        if options != None:
            root.app_parameters.options = options
            root.app_parameters.cfg_backup()
    else:
        print(f"Bad config file")
        exit(1)
    print(f"Options:\n{root.app_parameters.options}")
        
    My_Datetime.Long = True
    long_date = My_Datetime(now.year, now.month, now.day)
    print(f"\ndate longue: {long_date}")
    My_Datetime.Long = False
    short_date = My_Datetime(now.year, now.month, now.day)
    print(f"date courte: {short_date}")

    print("correct_filename('aze(. ,-;12))}:op*.Csv' :",end="")
    print(correct_filename("'aze(. ,-;12))}:op*.Csv"))
    
    root.quit()
    