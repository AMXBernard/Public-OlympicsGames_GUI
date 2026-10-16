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

from configs import *
from math import nan

class Medaille():
    
    @classmethod
    def get_medal_strength(cls, medal:MEDALTYPE) -> int:
        strength:dict = {"Gold":1, "Silver":2, "Bronze":3}
        return strength.get(medal, nan)
    
    
    def __init__(self, medaltype:MEDALTYPE=None):    
        self.__strenght:dict ={"Gold":1, "Silver":2, "Bronze":3} 
        self.__medal_code = self.__strenght.get(medaltype, None) 
        self.__medalType:MEDALTYPE = medaltype if medaltype in medalType_list else ""
    
    @property
    def medalType(self) -> MEDALTYPE:
        return  self.__medalType
    @medalType.setter
    def medalType(self, medaltype:MEDALTYPE):
        self.__medalType = medaltype if medaltype in medalType_list else ""
        self.medalCode = self.__strenght.get(medaltype, None)
    
    @property
    def medalCode(self) -> int:
        return self.__medal_code
    
    def __gt__(self, other:"Medaille") -> bool:
        return self.__strenght[self.__medalType] < other.__strenght[other.medalType]     
    
    def __eq__(self, other:"Medaille") -> bool:
        return self.__strenght[self.__medalType] == other.__strenght[other.medalType]
    
    def __hash__(self):
        return hash((self.__medal_code, self.__medalType))
        
    def __str__(self) -> str:
        return f"{self.medalType}"


if __name__ == "__main__":
    
    medal1 = Medaille("Gold")
    medal2 = Medaille("Silver")
    medal3 = Medaille("Bronze")
    
    for medaille in (medal1, medal2, medal3):    
        [print(f"{key:<17}: {getattr(medaille,key)}") for key in medaille.__dict__.keys()]
        print('-'*60)
    
    print(f"medal1 < medal2: {medal1 < medal2}")    
    print(f"medal2 < medal1: {medal2 < medal1}")
    print(f"medal1 > medal2: {medal1 > medal2}")  
    print(f"medal2 < medal3: {medal2 < medal3}")
    print(f"medal3 > medal1: {medal3 > medal1}")  
    print(f"medal3 = medal1: {medal3 == medal1}")  
    print(f"medal3 = medal3: {medal3 == medal3}")  

    