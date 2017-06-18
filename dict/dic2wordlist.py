#!/usr/bin/env python3
import sys
from string import Template
import operator
import csv
from datetime import datetime
import cgi
import string
import re

if __name__ == "__main__":
    with open(sys.argv[1]) as dictfile, open(sys.argv[2]) as exfile:
        dictionary = {}
        words = []
        for item in csv.reader(exfile):
            temp = []
            temp = item[3].split()
            words += temp
        for item in csv.reader(dictfile):
            temp = []
            temp = item[3].split()
            words += temp
        for item in words:
            word = item.strip()
            word = re.sub('['+string.punctuation+']', '', word)
            dictionary[word]=''
        wordlist = sorted(dictionary.keys())
        for word in wordlist:
            print(word)
