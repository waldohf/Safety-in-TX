from __future__ import division
import re
from stemming import porter2

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
        self.inFiles = 'dallas_tweets.txt'
        self.outFiles = ['dallas_crime_homicide.json','dallas_crime_finance.json','dallas_crime_sex.json',
            'dallas_crime_drugs.json','dallas_crime_gen.json','dallas_disaster.json',
            'dallas_accident.json','dallas_misc.json']
        self.fdRead = open(self.inFiles, 'r')
        for file in self.outFiles:
            self.fdWrite.append(open(file, 'w'))

    def close_files(self):
        self.fdRead.close()
        for file in self.fdWrite:
            file.close()

    def index_tweets(self):
        """
        purpose: read the tweet and store them in the database
        preconditions: the database is empty
        returns: none
        """     
        tweetDocID = 0
        
        for tweet in self.fdRead:
            http_index = tweet.find('http') - 1
            self.database.append(tweet[:http_index]) # populate database list with tweets
            tweet_text = tokenize(tweet)
            tweet_text = tweet_text[7:] # skip over date portion of tweet in txt file
            for token in tweet_text: 
                if token == 'http':
                    break
                else:
                    if tweetDocID in self.invertedIndex:
                        self.invertedIndex[tweetDocID].append(token) # add to list once term exists
                    else:
                        self.invertedIndex[tweetDocID] = []  # init inv index, then add new entry
                        self.invertedIndex[tweetDocID] = [token]                    
            tweetDocID += 1 # move index number to next posting 
            

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
            
            


        # knn classifier?
        # strip off 'http' part and separate date and text into
        # 2 separate dicts for each tweet, like in json part
     

    # print 'classifying ' + inFiles + 'into buckets'
    # outFiles[0].write('CRIME tweets')
    # outFiles[1].write('DISASTER tweets')
    # outFiles[2].write('TRAFFIC tweets')
    # for tweet in tweets:
    #     temp = str(tweet['created_at']).replace('+0000 ', '')
    #     files[tweeter[1]].write(temp + ' ' + this_doc + '\n')
    # files[tweeter[1]].write('--------------------------------------------\n')

    # for f in files:
    #     f.close()

if __name__ == "__main__":
    ts = TweetSearch()
    ts.open_files()
    ts.index_tweets()
    ts.filter_tweets()
    ts.close_files()
