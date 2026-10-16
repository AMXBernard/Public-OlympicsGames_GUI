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

from sport import Sport
from athlete import Athlete
from country import Country,EditionGame,MedalTally

from random import seed,choice
from configs import *


class OlympicGames():
    
    @classmethod
    def get_Olympics_Medals_Tally(cls, *, select=None, **filters) -> list:
        """ Méthode de classe qui permet de filtrer sur aucun, un ou plusieurs des attributs
            de la classe MedalTally(). 
        """
        # validation des clés par suppression des clés incorrectes
        fkeys = {key:val for key,val in filters.items()}
        for k in fkeys.keys():
            if k not in MedalTally.SUPPORTED_ATTRIBUTES:
                print(f" ---> Bad key: {k}={filters.pop(k,None)}")
        # normalization et validation du paramètre select
        sel_fields = None
        if select is not None:
            if isinstance(select, str):
                sel_fields = (select,)
            else:
                sel_fields = tuple(select)
            for f in sel_fields:
                if f not in MedalTally.SUPPORTED_ATTRIBUTES:
                    raise ValueError(f"'{f}' n'est pas un attribut valide de MedalTally")
        
        dummy_set, dummy_list = set(), list()
        for sp in MedalTally.MEDALTALLY_List:
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
            if not sp in dummy_list: dummy_list.append(sp)
        return sorted(list(dummy_set)), sorted(dummy_list, key=lambda mt:(mt.year, mt.edition, mt.total))

    
    @classmethod
    def get_Olympics_Edition_Game(cls, *, select=None, **filters) -> list:
        """ Méthode de classe qui permet de filtrer sur aucun, un ou plusieurs des attributs
            de la classe EditionGame(). 
        """
        # validation des clés par suppression des clés incorrectes
        fkeys = {key:val for key,val in filters.items()}
        for k in fkeys.keys():
            if k not in EditionGame.SUPPORTED_ATTRIBUTES:
                print(f" ---> Bad key: {k}={filters.pop(k,None)}")
        # normalization et validation du paramètre select
        sel_fields = None
        if select is not None:
            if isinstance(select, str):
                sel_fields = (select,)
            else:
                sel_fields = tuple(select)
            for f in sel_fields:
                if f not in EditionGame.SUPPORTED_ATTRIBUTES:
                    raise ValueError(f"'{f}' n'est pas un attribut valide de EditionGame")
        
        dummy_set, dummy_list = set(), list()
        for sp in EditionGame.EDITIONS_List:
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
            # construction de la liste des objets EditionGame selon select
            if not sp in dummy_list: dummy_list.append(sp)
        return sorted(list(dummy_set)), sorted(dummy_list, key=lambda ed:(ed.year, ed.edition, ed.edition_id))


    @classmethod
    def get_Olympics_Sport_Result(cls, *, select=None, **filters) -> list:
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
        
        dummy_set, dummy_list = set(), list()
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
            if not sp in dummy_list: dummy_list.append(sp)
        return sorted(list(dummy_set)), sorted(dummy_list, key=lambda s:(s.edition,s.sport,s.event,s.position), reverse=False)


    def __init__(self):
        
        if not Athlete.load_athlete_bio(ATHLETE_file):
            print("Fichier des atlèlètes non lu.")
        self.athlete = Athlete.ATHLETES_Dico
        
        if not Country.load_countryfile(COUNTRY_file):
            print("Fichier des pays/évènements non lu.")
        self.country = Country.NOC_Dict
        
        if not Sport.get_sports_list(SPORT_file, self.athlete):
            print(f"Lecture du fichier des sports non OK")
        self.sports = Sport.SPORTS_Dico




if __name__ == "__main__":
    
    olympic_games = OlympicGames()
    
    str_events, obj_events = olympic_games.get_Olympics_Sport_Result(sport="Boxing",noc="FRA",medal="Gold")
    print(f"Sports trouvés: {len(str_events)} -/- {len(obj_events)}")
    [print(f"{event}") for event in str_events]
    print("-"*80)
    
    str_events, obj_events = olympic_games.get_Olympics_Medals_Tally(total=2)    
    [print(f"{event}") for event in obj_events]
    print(f"Total des médailles recherchées: {sum(list(map(lambda d:d.total, obj_events)))}  \
(G:{sum(list(map(lambda d:d.gold, obj_events)))} / S:{sum(list(map(lambda d:d.silver, obj_events)))} / B:{sum(list(map(lambda d:d.bronze, obj_events)))})")
    print("-"*80)

    str_events, obj_events = olympic_games.get_Olympics_Edition_Game(noc="USA")
    [print(f"{event}") for event in obj_events]
    print(f"Total des editions de jeux olympiques: {len(obj_events)}")
    print("-"*80)

    """
    noc = "FRA"
    events:list = ([])
    print(f"\nEn passant par le dictionnaire:")
    for eventname in MedalTally.MEDALTALLY_Dict.keys():
        events.extend(list(filter(lambda c:c.noc==noc and c.gold>=5 and "Summer" in c.edition, 
                                      MedalTally.get_event_medaltally_List(eventname=eventname))))
    [print(f"{event}") for event in events]
    total_medals = sum(list(map(lambda d:d.total, events)))
    gold_medals = sum(list(map(lambda d:d.gold, events)))
    silver_medals = sum(list(map(lambda d:d.silver, events)))
    bronze_medals = sum(list(map(lambda d:d.bronze, events)))
    print(f"total medals: {total_medals} - gold: {gold_medals} - silver: {silver_medals} - bronze: {bronze_medals}")
    events:list = ([])
    print(f"\nEn passant par la liste des MedalTally:")
    for medaltally in olympic_games.medaltally:
        if medaltally.noc==noc and ("2020" in medaltally.edition or "2022"in medaltally.edition):
            events.extend([medaltally,])
    print()
    dummies = olympic_games.get_Olympics_Sport_Result(medal="Gold")
    dummy_list = olympic_games.OLYMPICS_SPORT_RESULT_List
    [print(f"{dummy}") for dummy in dummies]
    print('1-'*80)
    [print(f"{dummy}") for dummy in dummy_list]
    print('2-'*80)
    
    total_medals = sum(list(map(lambda d:d.total, events)))
    gold_medals = sum(list(map(lambda d:d.gold, events)))
    silver_medals = sum(list(map(lambda d:d.silver, events)))
    bronze_medals = sum(list(map(lambda d:d.bronze, events)))
    print(f"total medals: {total_medals} - gold: {gold_medals} - silver: {silver_medals} - bronze: {bronze_medals}")
    """
    
    