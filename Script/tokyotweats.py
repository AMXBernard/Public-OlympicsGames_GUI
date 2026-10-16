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

from sport import *
from configs import *

"""
    csv file colums : id,user_name,user_location,user_description,user_created,user_followers,user_friends,user_favourites,user_verified,date,text,hashtags,source,retweets,favorites,is_retweet
"""

class Tweet():

    TWEETS_List:list = ([]) 
    
    @classmethod
    def load_tweetslist(cls, filename:str) -> bool:
        # ---- Création liste des tweats ----
        filename = op.join(os.getcwd(),"Project","OldData",filename)
        curatedfname = op.join(os.getcwd(),"Project","CuratedData","tweetNodes.csv")
        if op.isfile(filename):
            og = pandas.read_csv(filename).copy()
            [Tweet.TWEETS_List.append(Tweet(og['id'][i],og['user_name'][i],og['date'][i],og['text'][i],og['hashtags'][i])) \
                                                                                                        for i in range(len(og))]
            og = og.iloc[:,[0,1,10,11]]
            og.to_csv(curatedfname, sep=',', index=False, encoding='UTF8')
            return True
        else:
            return False
    

    def __init__(self, tweatID:int, username:str, date:str, text:str, hashtags:str):
        self.tweatID = tweatID
        self.user = username
        self.date = date
        self.text = self.__create_tweetext(text)
        self.hashtags:list = self.__create_hashtagsList(hashtags)
    
    def __create_tweetext(self, tweetext:str) -> str:
        return tweetext.replace('\n',' ').strip() if isinstance(tweetext, str) else tweetext
    
    def __create_hashtagsList(self, hashtag_text:str) -> list:
        try:
            return eval(hashtag_text,None,[list,])
        except TypeError:
            return hashtag_text.strip('[ ]\n').replace("'","").split(', ') if isinstance(hashtag_text, str) else []
        
    def __str__(self) -> str:
        return f"Tweat ID[{self.tweatID}] by {self.user} : {self.text[:80]}... Hashtags: {self.hashtags}" 
    
    
if __name__ == "__main__":
    
    if Tweet.load_tweetslist("tokyo_2020_tweets.csv"):
        print(" #---------- Class(Tweet). The fisrt Tweet.__str__() ----------#")
        [print(f"{key:<17}: {getattr(Tweet.TWEETS_List[0],key)}") for key in Tweet.TWEETS_List[0].__dict__.keys()]
        print(" #--------- Class(Tweet) list over 10 Tweet.__str__() ---------#")
        #[print(item) for item in Tweet.TWEETS_List[:10]]
        print(" #-------------- Same tweets from tweetnodes.csv --------------#")
        with open(file=op.join(os.getcwd(),"Project","CuratedData","tweetNodes.csv"),mode='rt',encoding='utf-8') as csvfile:
            [print(csvfile.readline().strip().replace('\n','')) for _ in range(20)]
    else:
        print(f"Bad file name")
            