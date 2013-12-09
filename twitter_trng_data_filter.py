from __future__ import division
from __future__ import print_function
import re
from stemming import porter2
import sys

"""
Program to prefilter tweets crawled from various news twitter feeds.
Sorts based on a list of keywords, then the resulting tweet files are
looked through by hand to find good tweet examples for each class.

Input: txt files from twitter crawl separated by city, 6 files
Output: json files separated into the 8 categories, 1 category per file
"""


def tokenize(text):
    """
    Take a string and split it into tokens on word boundaries.

    A token is defined to be one or more alphanumeric characters,
    underscores, or apostrophes.  Remove all other punctuation, whitespace, and
    empty tokens.  Do case-folding to make everything lowercase. This function
    should return a list of the tokens in the input string.
    """
    tokens = re.findall("[\w']+", text.lower())
    return [porter2.stem(token) for token in tokens]

class TweetSearch(object):
    """ A search engine for tweets. """
    def __init__(self, ranker=None, classifier=None):
        """
        purpose: Create the search engine for tweets
        parameters:
            database - store tweets information
        """
        # self.tweets = []
        self.database = []  #{} main tweet database list
        self.invertedIndex = {} # inverted index of all tweets
        self.crime_homicide_keys = ['murder','degree','manslaught','assault',
            'beat','fight','shoot','kill','gun','knife','homicid','bullet',
            'attack','brawl','massacr','struck','stab','death','violence','batteri']
        self.crime_financial_keys = ['burglari','theft','rob','robberi','robber',
            'larceni','embezzl','loot','shoplift','money','launder','extort',
            'blackmail','bank','steal','stole','forgeri','heist','fraud','arm']
        self.crime_sex_keys = ['rape','statutori','sexual','assault','sex','pedofile',
            'offend','porn','prostitut','hooker','pimp','slaveri','incest',
            'date','rohypnol','ghb']
        self.crime_drugs_keys = ['alcohol','cocain','heroin','crack','weed','pot',
            'marijuana','lsd','drug','pcp','salvia','psilocybin','mushroom','meth',
            'amphetamin','prescipt','liquor']
        self.crime_general_keys = ['vandal','kidnap','abduct','dui','dwi','intox','arson',
            'indec','trespass']
        self.disaster_keys = ['disast','earthquak','flood','tornado','chemic','safeti','hurrican',
                'propan','leak','oil','lightn','thunder','gas','burn']
        self.accident_keys = ['traffic','accid','car','wreck','crash','collis',
                'altern','rout','detour']#,'hit','run']
        # self.matchList = [] # list to return with matching tweets fom query

    def open_files(self):
        self.fdWrite = []
        self.fdRead = []
        self.inFiles = ['houston_tweets.txt','el_paso_tweets.txt','fort_worth_tweets.txt',
            'san_antonio_tweets.txt','austin_tweets.txt','dallas_tweets.txt']
        self.outFiles = ['crime_homicide.json','crime_finance.json','crime_sex.json',
            'crime_drugs.json','crime_gen.json','disaster.json',
            'accident.json','misc.json']
        for file in self.inFiles:
            self.fdRead.append(open(file, 'r')) 
        for file in self.outFiles:
            self.fdWrite.append(open(file, 'w'))

    def close_files(self):
        for file in self.fdRead:
            file.close()
        for file in self.fdWrite:
            file.close()

    def index_tweets(self):
        """
        purpose: read the tweet and store them in the database
        preconditions: the database is empty
        returns: none
        """ 
        tweet_list = [[] for _ in range(6)] # houston, el_paso, fort_worth, san_antonio, austin, dallas
        index = 0
        for city in self.fdRead:
            for tweet in city:
                tweet_list[index].append(tweet)
            index += 1

        tweetNum = 0
        line_num = 0

        while   (tweet_list[0] or tweet_list[1] or tweet_list[2] or
                tweet_list[3] or tweet_list[4] or tweet_list[5]): # keep iterating till all lists are empty
            for num in range(6):
                if not tweet_list[num]:
                    break
                else:
                    tweet = tweet_list[num].pop()
                    http_index = tweet.find('http') - 1
                    http_end_index = tweet.find(' ', http_index + 1)
                    temp = (tweet.strip())
                    if (http_index > -1):
                        if (http_end_index > -1):
                            temp = temp[:http_index] + temp[http_end_index:]
                        else:
                            temp = temp[:http_index]
                    self.database.append(temp) # populate database list with tweets
                    tweet_text = tokenize(temp)
                    tweet_text = tweet_text[7:] # skip over date portion of tweet in txt file
                    for token in tweet_text: 
                        if tweetNum in self.invertedIndex:
                            self.invertedIndex[tweetNum].append(token) # add to list once term exists
                        else:
                            self.invertedIndex[tweetNum] = []  # init inv index, then add new entry
                            self.invertedIndex[tweetNum] = [token] 
                                               
                    tweetNum += 1 # move index number to next posting 
            line_num += 1
            value = (int) (100 * line_num/19326)
            print('Progress: ',value,'%', end='\r')
            if line_num == 19326:
                break
            

    def filter_tweets(self):
        """
        purpose: filter tweets with given keywords for categories
        """
        for tweet_num in self.invertedIndex:
            keyword_num = [0,0,0,0,0,0,0] # [homicide,financial,sex,drugs,general,disaster,accident]
            for token in self.invertedIndex[tweet_num]:
                if token in self.crime_homicide_keys:
                    keyword_num[0] += 1
                elif token in self.crime_financial_keys:
                    keyword_num[1] += 1
                elif token in self.crime_sex_keys:
                    keyword_num[2] += 1
                elif token in self.crime_drugs_keys:
                    keyword_num[3] += 1
                elif token in self.crime_general_keys:
                    keyword_num[4] += 1
                elif token in self.disaster_keys:
                    keyword_num[5] += 1
                elif token in self.accident_keys:
                    keyword_num[6] += 1

            # get max value and matching indices
            i = 0
            match_list = []
            max_value = max(keyword_num)
            if (max_value > 0):
                for value in keyword_num:
                    if keyword_num[i] == max_value: # find max value index
                        match_list.append(i)
                    i += 1
            elif max_value == 0:
                match_list.append(7)    # put tweet in miscellaneous bucket

            # write to matching category text files
            if len(match_list) < 2:
                for item_num in match_list:
                    doc = dict(date = self.database[tweet_num][:24], text = self.database[tweet_num][25:])
                    self.fdWrite[item_num].write(str(doc) + '\n')
            

if __name__ == "__main__":
    ts = TweetSearch()
    ts.open_files()
    ts.index_tweets()
    ts.filter_tweets()
    ts.close_files()
