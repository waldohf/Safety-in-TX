#!/usr/bin/env python
# -*- coding: utf-8  -*-
#encoding=utf-8

import tweepy
import time
import math
import sys
from random import randint

class TwitterCrawler():
    # Fill in the blanks here for your own Twitter app.
    consumer_key = ""
    consumer_secret = ""
    access_key = ""
    access_secret = ""
    auth = None
    api = None

    def __init__(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())
        # print self.api.rate_limit_status()

    def re_init(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())

    def check_api_rate_limit(self, sleep_time):
        try:
            rate_limit_status = self.api.rate_limit_status()
        except Exception as error_message:
            if error_message['code'] == 88:
                print "Sleeping for %d seconds." %(sleep_time)
                print rate_limit_status['resources']['statuses']
                time.sleep(sleep_time)

        while rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] < 10:
            print "Sleeping for %d seconds." %(sleep_time)
            print rate_limit_status['resources']['statuses']
            time.sleep(sleep_time)
            rate_limit_status = self.api.rate_limit_status()
        print rate_limit_status['resources']['statuses']['/statuses/user_timeline']

    def crawl_user_profile(self, user_id):
        self.check_api_rate_limit(900)
        try:
            user_profile = self.api.get_user(user_id)
        except:
            return None
        return user_profile

    def crawl_user_tweets(self, user_id, the_count, total_tweets, attempts, prev_max_id):
        self.check_api_rate_limit(900)
        try:
            if (prev_max_id > 0):
                tweets = self.api.user_timeline(user_id, count = the_count, max_id = prev_max_id)
                # tweets = self.api.user_timeline(user_id, count = the_count, max_id = prev_max_id, exclude_replies = 'true', include_rts = 'false')
            else:
                tweets = self.api.user_timeline(user_id, count = the_count)
                # tweets = self.api.user_timeline(user_id, count = the_count, exclude_replies = 'true', include_rts = 'false')
        except:
            tweets = None

        tried_count = 0
        temp_max = [0 for x in range(3)]
        temp_max.append(tweets[len(tweets)-1]['id'])
        newest = tweets[0]['id']
        while len(tweets) < total_tweets:
            try:
                temp_max[0:1] = []
                temp_max.append(temp_max[2])
                for tweet in tweets:
                    if (temp_max[3] > tweet['id']):
                        temp_max[3] = tweet['id']

                print temp_max[3]
                if (temp_max[0] == temp_max[3]):
		    return (tweets, temp_max[3], newest)

                tweets.extend(self.api.user_timeline(user_id, count = the_count, max_id = temp_max[3]-1))
                # tweets.extend(self.api.user_timeline(user_id, count = the_count, max_id = temp_max, exclude_replies = 'true', include_rts = 'false'))
            except:
                pass
            tried_count += 1
            if tried_count == attempts:
                break
        return (tweets, temp_max[3], newest)

def main():
    tc = TwitterCrawler()
    # API.user_timeline() takes either id or user_id or screen_name
    filenames = ['dallas_tweets.txt', 'fort_worth_tweets.txt', 'houston_tweets.txt', 'austin_tweets.txt', 'san_antonio_tweets.txt', 'el_paso_tweets.txt']

    files = []
    for filename in filenames:
        # files.append(open(filename, 'w'))
        files.append(open(filename, 'a'))

    # Dallas (index 0)
    # @DallasNews 28,319
    # @dallasnews_com 43,775
    # @TotalTrafficDFW 47,274 (TRAFFIC)

    # Fort Worth (index 1)
    # @FtWorthNews 67,497
    # @News_FortWorth 32,639
    # @News_Fort_Worth 18,510
    # @SDaviesNBC5 7,959 (TRAFFIC)

    # Houston (index 2)
    # @abc13houston 69,847
    # @MyFoxHouston 67,440
    # @HoustonTraffic 48,928 (TRAFFIC)
    # @News_Houston_TX 51,821
    # @HoustonChron 63,620
    # @KHOU 56,241
    # @Houston_Traffic 1,857 (TRAFFIC)

    # Austin (index 3)
    # @foxaustin 19,766
    # @KVUE 40,178
    # @YNNAustin 37,518 (KINDA TRAFFIC?)
    # @KXAN_News 28,274

    # San Antonio (index 4)
    # @ksatnews 56,691
    # @News4SA 45,245
    # @KENS5 28,887
    # @TotalTrafficSAT 11,971 (TRAFFIC)
    # @mySA 39,033

    # El-Paso (index 5)
    # @elpasotimes 35,047
    # @NewsElPasoTX 44,247
    # @ElPaso__News 15,238
    # @NC9 12,602

    # the format is: twitter ID or screen name, which file index to write to, 0, then 0
    # tweeters = [['DallasNews', 0, 0, 0], ['FtWorthNews', 1, 0, 0], ['abc13houston', 2, 0, 0], ['foxaustin', 3, 0, 0], ['ksatnews', 4, 0, 0], ['elpasotimes', 5, 0, 0], ['dallasnews_com', 0, 0, 0], ['News_FortWorth', 1, 0, 0], ['MyFoxHouston', 2, 0, 0], ['KVUE', 3, 0, 0], ['News4SA', 4, 0, 0], ['NewsElPasoTX', 5, 0, 0], ['TotalTrafficDFW', 0, 0, 0], ['News_Fort_Worth', 1, 0, 0], ['HoustonTraffic', 2, 0, 0], ['YNNAustin', 3, 0, 0], ['KENS5', 4, 0, 0], ['ElPaso__News', 5, 0, 0]]
    # tweeters = [['SDaviesNBC5', 1, 0, 0], ['News_Houston_TX', 2, 0, 0]]
    tweeters = [['HoustonChron', 2, 0, 0], ['KHOU', 2, 0, 0], ['KXAN_News', 3, 0, 0], ['TotalTrafficSAT', 4, 0, 0], ['mySA', 4, 0, 0], ['NC9', 5, 0, 0]]

    # flags to tell whether all tweets were pulled from each individual tweeter
    complete = [0 for x in range(len(tweeters)+1)]
    last = len(complete)-1

    while (complete[last] == 0):
        for index, tweeter in enumerate(tweeters):
            tc.check_api_rate_limit(300)
            user = tc.crawl_user_profile(tweeter[0])
            print user['screen_name'] + ' has ' + str(user['statuses_count']) + ' tweets.'

            tweets = tc.crawl_user_tweets(tweeter[0], 800, (user['statuses_count']-tweeter[3]), int(math.ceil(user['statuses_count']/200.0)), tweeter[2])
            print 'retreived ' + str(len(tweets[0])) + ' of those tweets.\n'
            # update that tweeter's total tweets pulled
            tweeters[index][3] += len(tweets[0])
            # update that tweeter's min tweet ID
            tweeters[index][2] = tweets[1]
            if (tweeters[index][3] > 3199):
                complete[index] = 1

            for tweet in tweets[0]:
                temp = tweet['text'].encode('utf-8')
                temp = (temp.lower()).strip(' \t\n\r')
                temp = (temp.replace('\n',' ')).replace('\r',' ')
                temp = (temp.replace('\'',' ')).replace('\"',' ')
                temp = (temp.replace('-',' ')).replace('!',' ')
                temp = (temp.replace('[',' ')).replace(']',' ')
                this_doc = temp.replace('?',' ')
                temp = str(tweet['created_at']).replace('+0000 ', '')
                files[tweeter[1]].write(temp + ' ' + this_doc + '\n')
            files[tweeter[1]].write('--**--**-- ' + tweeter[0] + ', since ID = ' + str(tweets[2]) + ' --**--**--\n')

        complete[last] = 1
        for idx in range(last):
            if (complete[idx] == 0):
                complete[last] = 0
                break
        time.sleep(3600)

    for f in files:
        f.close()

if __name__ == "__main__":
    main()
