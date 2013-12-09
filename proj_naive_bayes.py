from __future__ import division
import re
import json
import math
import random
import operator
from stemming import porter2

def tokenize(text):
    """
    Take a string and split it into tokens on word boundaries.

    A token is defined to be one or more alphanumeric characters,
    underscores, or apostrophes.  Remove all other punctuation, whitespace, and
    empty tokens.  Do case-folding to make everything lowercase. This function
    should return a list of the tokens in the input string.
    """
    tkns = re.findall("[\w']+", text.lower())
    return [porter2.stem(tkn) for tkn in tkns]

def read_data(filename):
    """
    purpose: read all tweets from the json file.
    parameter: 
        filename - the path of json file in your local computer 
    return: a list containing all raw tweets each of which has the data structure of dictionary
    """
    data = []
    try:
        err = 'first line'
        with open(filename) as f:
            for line in f:
                err = line
                data.append(json.loads((line.strip()).encode('utf-8')))
    except:
        print "Failed to read json data!"
        print err
        # return []
    print "The json file has been successfully read!"
    return data

def read_data2(filename):
    """
    Used to read all tweets from the text file.
    """
    data2 = []
    try:
        err2 = 'first line'
        with open(filename) as f:
            for line in f:
                http_index = line.find('http') - 1
                http_end_index = line.find(' ', http_index+1)
                temp = (line.strip()).encode('utf-8')
                if (http_index > -1):
                    if (http_end_index > -1):
                        temp = temp[:http_index] + temp[http_end_index:]
                    else:
                        temp = temp[:http_index]
                dic = dict(date = temp[:24], text = temp[25:])
                err2 = temp[25:]
                data2.append(dic)
    except:
        print "Failed to read text data!"
        print err2
        # return []
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

        trngFiles = ['crime_homicide.json','crime_finance.json','crime_sex.json','crime_drugs.json','crime_gen.json','accident.json','misc.json','disaster.json']
        inFiles = ['austin_tweets.txt','dallas_tweets.txt','el_paso_tweets.txt','fort_worth_tweets.txt','houston_tweets.txt','san_antonio_tweets.txt']
        outFiles = []
        for trngf in trngFiles:
            self.training_data.append(read_data(trngf))
        for inf in inFiles:
            self.test_data.append(read_data2(inf))

        for no, td in enumerate(self.training_data):
            self.probabilities.append({})
            self.indiv_trng_docs.append(len(td))
            total_trng_docs += self.indiv_trng_docs[no]
            for line, doc in enumerate(td):
                # initialize each term freq and tf_idf vector
                self.term_freq[line] = {}
                self.tf_idf[line] = {}

                tokens = (doc['text'].replace('#',' ')).split() # tokenize each document
                # ********** may have to apply stemming instead **********
                # for each token/term in that document
                for token in tokens:
                    # first add to word list
                    if token not in self.word_list:
                        self.word_list.append(token)
                    if token not in self.freq_docs.keys():
                        self.freq_docs[token] = []
                    if token not in self.inverted_doc_freq.keys():
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

        # for each city (test doc)
        for num1, city in enumerate(inFiles):
            city_idx = city.find('tweets') - 1
            city_name = city[:city_idx]
            # create the output files
            for cls in trngFiles:
                cls_idx = cls.find('.')
                file_name = city_name + '_' + cls[:cls_idx] + '.json'
                print file_name
                outFiles.append(file_name)
                self.fdWrite.append(open(file_name, 'w'))

            # for each document in that test doc (infile)
            for tweet in self.test_data[num1]:
                probs = []
                # for each class
                for num2 in xrange(len(self.probabilities)):
                    # start with the general class probability
                    probs.append(self.indiv_trng_docs[num2] / total_trng_docs)
                    # for each token/term in that document
                    # ********** may have to apply stemming instead **********
                    for tkn in (tweet['text'].replace('#',' ')).split():
                        if tkn in self.probabilities[num2].keys():
                            probs[num2] *= self.probabilities[num2][tkn]
                        else:
                            probs[num2] *= 0.001
                # choose the max probability and assign the tweet to that class
                max_prob = max(probs)
                for num3, prob in enumerate(probs):
                    if (max_prob == prob):
                        if (tweet['text'].find('--**--**--') < 0):
                            converted_text = str(tweet).replace('\'','\"') + '\n'
                            self.fdWrite[((num1*len(trngFiles)) + num3)].write(converted_text)
                        break

        for f in self.fdWrite:
            f.close()

def main():
        nb = Naive_Bayes()
        nb.DoNB()

if __name__ == "__main__":
        main()
