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


class Resultat():
    
    RESULTATS_Dico:dict = ({})
    RESULTATS_List:list = ([])
    ResultAttributes = Literal['result_id','edition_id','edition','sport','event','result_date','result_location','result_participants','result_format','result_detail','result_description']
    SUPPORTED_ATTRIBUTES = get_args(ResultAttributes)

    @classmethod
    def get_Olympics_Results_Details(cls,output:str, *, select=None, **filters) -> list:
        """ Méthode de classe qui permet de filtrer sur aucun, un ou plusieurs des attributs
            de la classe Resultat(). 
        """
        # validation des clés par suppression des clés incorrectes
        fkeys = {key:val for key,val in filters.items()}
        for k in fkeys.keys():
            if k not in Resultat.SUPPORTED_ATTRIBUTES:
                print(f" ---> Bad key: {k}={filters.pop(k,None)}")
        # normalization et validation du paramètre select
        sel_fields = None
        if select is not None:
            if isinstance(select, str):
                sel_fields = (select,)
            else:
                sel_fields = tuple(select)
            for f in sel_fields:
                if f not in Resultat.SUPPORTED_ATTRIBUTES:
                    raise ValueError(f"'{f}' n'est pas un attribut valide de Resultat()")
        dummy_set, dummy_list = set(), list()
        for sp in Resultat.RESULTATS_List:
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
            dummy_list.append(sp)
            #if sp not in dummy_list: dummy_list.append(sp)
        # ---------------------------------------------------------------------
        if output=="obj":
            return dummy_list
        else:
            return sorted(list(dummy_set))

    @classmethod
    def load_resultsfile(cls, msgbox, options:App_Options=None) -> bool:
        if not options: options = App_Options()
        # ---- Création dictionnaire des resultats ----
        filename_rst = op.join(options.olympicpath,options.result_file)
        if op.isfile(filename_rst):
            if msgbox:
                msgbox.boxtitle("Chargement fichier des résultats")
                msgbox.message = f"{'Lecture du fichier 4/7 en cours 0%':^50}"
            else:
                print("Lecture du fichier des résultats ...")
            rg = pandas.read_csv(filename_rst, on_bad_lines="skip"); lrg = len(rg)
            for i in range(len(rg)):
                # result_id,event_title,edition,edition_id,sport,sport_url,result_date,result_location,result_participants,result_format,result_detail,result_description
                Resultat.RESULTATS_Dico[int(rg['result_id'][i])] = Resultat(int(rg['result_id'][i]),rg['edition'][i],int(rg['edition_id'][i]),
                                                    rg['sport'][i],rg['event_title'][i],rg['result_date'][i],rg['result_location'][i],
                                                        rg['result_participants'][i],rg['result_format'][i],rg['result_detail'][i],rg['result_description'][i])                
                if msgbox:
                    msg = f"Lecture  du fichier 4/7 en cours {int(i/lrg*100):>2}%"
                    if i%100 == 0: msgbox.message_update(f"{msg:^50}")
                else:
                    print(f"{int(i/lrg*100):>3}%", flush=True, end="\r")
            Resultat.RESULTATS_List = sorted(list(Resultat.RESULTATS_Dico.values()), key=lambda r:r.result_id)
            return True
        else:
            return False
    
    @classmethod
    def DumRESULTAT(cls) -> "Resultat":
        return Resultat(0,"All editions Olympics",0,"All sports","","","","","","","")
        

    def __init__(self, result_id:int,edition:str,edition_id:int,sport:str,event:str,result_date:str,result_location:str,
                            result_participants:str,result_format:str,result_detail:str,result_description:str):
        # --------------------------- Champs du fichier CSV ---------------------------
        # result_id,event_title,edition,edition_id,sport,sport_url,result_date,result_location,result_participants,result_format,result_detail,result_description
        self.result_id:int = int(result_id)
        self.edition:str = self.__correct_edition(edition)
        self.edition_id:int = int(edition_id)
        self.sport:str = self.__preform(sport)
        self.event:str = self.__preform(event)
        self.result_date:str = result_date
        self.result_location:str = self.__preform(result_location)
        self.result_participants:str = self.__preform(result_participants)
        self.result_format = self.__preform(result_format)
        self.result_detail = self.__preform(result_detail)
        self.result_description = self.__preform(result_description)

    def get_result(self) -> str:
        return f"Résultat Id.{self.result_id:<8} : {self.sport} ({self.event}) en date du {self.result_date}, à(au) {self.result_location}" 
    
    def __correct_edition(self, edition:str) -> str:
        if "Olympics" in edition:
            return edition
        if "Games" in edition:
            return edition.replace('  ',' ').replace('Games','Olympics')
        else:
            return f"{edition.replace('  ',' ').strip()} Olympics"
            
    def __preform(self, item:str) -> str:
        #return item if item != 'na' else "" 
        return item if self.__is_valid_item_result(item) else ""
    
    def __is_valid_item_result(self, item:str) -> bool:
        """ Retourne True si au moins l'un des éléments de la liste est dans 'item' """
        return any(x in item for x in ["na", "NA", ""]) if isinstance(item, str) else True

    def __gt__(self, other:"Resultat") -> bool:
        return self.result_id > other.result_id
    
    def __eq__(self, other:"Resultat") -> bool:
        return self.result_id == other.result_id
    
    def __hash__(self) -> int:
        return hash((self.result_id, self.edition_id))
        
    def __str__(self) -> str:
        return f"{self.result_id}, {self.edition}: {self.sport} ({self.event})"
    
    
if __name__ == "__main__":
    
    import tkinter as tk
    
    from gui_tools import Win_MessageBox
    from linuxprt import Linux_InitPrinters
    from random import choices
        
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
        
    
    if Resultat.load_resultsfile(msgbox, options=options):
        #for resultat in choices(Resultat.RESULTATS_List, k=2):
        #    resultat = Resultat.RESULTATS_Dico[resultat.result_id]
        #    print(f"\n ---> {resultat}:")
        #    [print(f"\t{attr:<20}: {getattr(resultat, attr)}") for attr in resultat.__dict__.keys()]
            
        #[print(result) for result in Resultat.get_Olympics_Results_Details(output="obj",select=("sport","event"),sport="Boxing")]

        [print(result.get_result()) for result in Resultat.RESULTATS_List[:10]]