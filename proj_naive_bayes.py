from __future__ import division
import re
import json
import math
import random
import operator

def read_data(filename):
    """
    purpose: read all tweets from the json file.
    parameter: 
        filename - the path of json file in your local computer 
    return: a list containing all raw tweets each of which has the data structure of dictionary
    """
    data = []
    try:
        with open(filename) as f:
            for line in f:
                data.append(json.loads((line.strip()).encode('utf-8')))
    except:
        print "Failed to read data!"
        return []
    print "The json file has been successfully read!"
    return data

def read_data2(filename):
    """
    Used to read all tweets from the text file.
    """
    data2 = []
    try:
        with open(filename) as f:
            for line in f:
                http_index = line.find('http') - 1
                temp = (line.strip()).encode('utf-8')
                if (http_index > -2):
                    temp = temp[:http_index]
                dic = dict(date = temp[:24], text = temp[25:])
                print dic
                data2.append(dic)
    except:
        print "Failed to read data!"
        return []
    print "The text file has been successfully read!"
    return data2

class Naive_Bayes():
    def __init__(self):
        # all the training data from the 8 classes
        self.training_data = []
        # all the test data, one for each city
        self.test_data = []
        # tf (dict of dict indexed by tweet id)
        self.term_freq = {}
        # idf (dict indexed by term)
        self.inverted_doc_freq = {}
        # probabilities (dict indexed by term)
        self.probabilities = []
        # tf-idf (dict of dict indexed by tweet id)
        self.tf_idf = {}
        # used to store the frequency of documents (dict indexed by term)
        self.freq_docs = {}
        # you might need this which is used to store all terms/tokens in out documents
        self.word_list = []
        # write file descriptors
        self.fdWrite = []
        # number of tweets/docs in each training set
        self.indiv_trng_docs = []

    def DoNB(self):
        random.seed()
        total_trng_docs = 0

        trngFiles = ['dallas_crime_homicide.json','dallas_crime_finance.json','dallas_crime_sex.json',
            'dallas_crime_drugs.json','dallas_crime_gen.json','dallas_accident.json','dallas_misc.json']
	# 'dallas_disaster.json',
        inFiles = ['houston_tweets.txt']
        outFiles = []
        for trngf in trngFiles:
            self.training_data.append(read_data(trngf))
        for inf in inFiles:
            self.test_data.append(read_data2(inf))
        print self.test_data[0][:10]

        for no, td in self.training_data:
            self.probabilities[no] = {}
            self.indiv_trng_docs[no] = len(td)
            total_trng_docs += self.indiv_trng_docs[no]
            for line, doc in enumerate(td):
                # initialize each term freq and tf_idf vector
                self.term_freq[line] = {}
                self.tf_idf[line] = {}

                tokens = doc['text'].split() # tokenize each document
                # for each token/term in that document
                for token in tokens:
                    # first add to word list
                    if token not in self.word_list:
                        self.word_list.append(token)
                    if token not in self.freq_docs.keys():
                        self.freq_docs[token] = []
                    if token not in self.houston_inverted_doc_freq.keys():
                        self.inverted_doc_freq[token] = 0
                    if token not in self.term_freq[line].keys():
                        self.term_freq[line][token] = 0

                    # increment the tf in the appropriate vector
                    self.term_freq[line][token] += 1.0
                    if (self.freq_docs[token].count(line) < 1):
                        self.inverted_doc_freq[token] += 1.0
                    else: # add the newest query to the list for that term
                        self.freq_docs[token].append(line)

                # make each tf vector into log-based version
                for key in self.term_freq[line].keys():
                    if self.term_freq[line][key] > 0:
                        self.term_freq[line][key] = 1.0 + math.log(self.term_freq[line][key], 2)

            self.probabilities[no] = self.inverted_doc_freq.copy()

            for term in self.inverted_doc_freq.keys():
                self.probabilities[no][term] /= len(self.training_data[no])
                if (self.inverted_doc_freq[term] != 0):
                    self.inverted_doc_freq[term] = math.log((len(self.training_data[no]) / self.inverted_doc_freq[term]), 2)
            # print 'The idf for ' + term + ' is ' + str(self.inverted_doc_freq[term]) + '.'

            for tweet in self.term_freq.keys():
                for trm in self.term_freq[tweet].keys():
                    self.tf_idf[tweet][trm] = self.term_freq[tweet][trm] * self.inverted_doc_freq[trm]

            # now re-initialize stuff for the next round
            self.term_freq = {}
            self.inverted_doc_freq = {}
            self.tf_idf = {}
            self.freq_docs = {}

        print str(len(self.word_list)) + ' unique terms'
        # now start the Naive Bayes

        '''
        for city in inFiles:
            # for each token/term in that document
            for tkn in self.term_freq[x].keys():
		# print tkn + ' = ' +  str(self.houston_probabilities[tkn]) + ' / ' + str(self.dallas_probabilities[tkn])
                if (self.houston_probabilities[tkn] != 0):
                    houston_probability *= self.houston_probabilities[tkn]
                if (self.dallas_probabilities[tkn] != 0):
                    dallas_probability *= self.dallas_probabilities[tkn]

            if (houston_probability > dallas_probability):
                houston_list.append(x)
            self.fdWrite.append(open(outf, 'w'))
        '''

def main():
        nb = Naive_Bayes()
        nb.DoNB()

if __name__ == "__main__":
        main()
