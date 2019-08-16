#!/usr/bin/env python
# coding: utf-8

import xml.etree.ElementTree as ET
import re
import codecs

corpus = "/coctaill.xml"

tree = ET.parse(corpus)
root = tree.getroot()

lessons = root.findall(".//lesson")

delimiters = ["MAD", "MID", "PAD", "PID"]
attribs = ["pos", "msd", "lemma", "lex", "sense", "prefix", "suffix", "compwf", "complemgram", "ref", "deprel", "blingbring", "swefn", "sentiment", "sentimentclass"]

class MyMatch:
    def __init__(self, num, sid, ws):
        self.pattern_num = num
        self.sentence_id = sid
        if not isinstance(ws, list):
            ws = [ws]
        self.words = ws
    def __str__(self):
        return linearize(self.words) + " (PA{})".format(self.pattern_num)
    def set_sentence_id(self, sentid):
        self.sentence_id = sentid
    def get_sentence_id(self):
        return self.sentence_id
    def is_pattern(self, num):
        return self.pattern_num == num
    def get_pattern(self):
        return self.pattern_num
    def get_words(self):
        return self.words

def linearize(words):
    linsen = []
    for w in words:
        linsen.append(w.text)
    return " ".join(linsen)

def mapCefrToInt(cefr):
    if cefr == "A1":
        return 0
    elif cefr == "A2":
        return 1
    elif cefr == "B1":
        return 2
    elif cefr == "B2":
        return 3
    elif cefr == "C1":
        return 4
    elif cefr == "C2":
        return 5
    elif cefr == "C1p":
        return 5
    else:
        return -1

# block 1, DET
p1 = r"DT\.(UTR|NEU|UTR\+NEU)\.SIN\.DEF"
p2 = r"(JJ\.(POS|KOM|SUV)\.(UTR|NEU|UTR\+NEU)\.(SIN|SIN\+PLU)\.(IND|DEF)\.NOM)|(R[GO]\.NOM)"
p3 = r"NN\.(UTR|NEU|UTR\+NEU)\.SIN\.DEF\.NOM"

p4 = r"NN\.(UTR|NEU|UTR\+NEU)\.SIN\.IND\.NOM"
p5 = r"(JJ\.(POS|KOM|SUV)\.(UTR|NEU|UTR\+NEU)\.(SIN|SIN\+PLU)\.(IND|DEF)\.NOM)|(R[GO]\.NOM)"

# block 2, PS
p6 = r"PS\.(UTR|NEU|UTR\+NEU)\.SIN\.DEF"
p62 = r"PS\.(UTR|NEU|UTR\+NEU)\.PLU\.DEF"
p63 = r"PS\.(UTR|NEU|UTR\+NEU)\.(SIN\+PLU)\.DEF"

# block 3, PLU
p7 = r"DT\.(UTR|NEU|UTR\+NEU)\.(PLU|SIN\+PLU)\.DEF"
p8 = r"(JJ\.(POS|KOM|SUV)\.(UTR|NEU|UTR\+NEU)\.(PLU|SIN\+PLU)\.DEF\.NOM)|(R[GO]\.NOM)"
p82 = r"(JJ\.(POS|KOM|SUV)\.(UTR|NEU|UTR\+NEU)\.(PLU|SIN\+PLU)\.IND\.NOM)|(R[GO]\.NOM)"
p9 = r"NN\.(UTR|NEU|UTR\+NEU)\.PLU\.DEF\.NOM"
p92 = r"NN\.(UTR|NEU|UTR\+NEU)\.PLU\.IND\.NOM"
# block 4, IND
p10 = r"DT\.(UTR|NEU|UTR\+NEU)\.(SIN|SIN\+PLU)\.IND"

# underspecified
#   definiteness
p11 = r"NN\.(UTR|NEU|UTR\+NEU)\.SIN\....\.NOM"
p112 = r"(JJ\.(POS|KOM|SUV)\.(UTR|NEU|UTR\+NEU)\.(SIN|SIN\+PLU)\....\.NOM)|(R[GO]\.NOM)"
#   number
p12 = r"NN\.(UTR|NEU|UTR\+NEU)\....\....\.NOM"
p122 = r"(JJ\.(POS|KOM|SUV)\.(UTR|NEU|UTR\+NEU)\....\....\.NOM)|(R[GO]\.NOM)"

# underspec genitive
p13 = r"^NN\..+?\.GEN$"
p132 = r"^PM\.GEN$"

p14 = r"NN\.(UTR|NEU|UTR\+NEU)\.PLU\.IND\.NOM"

# pa1 = p1 p2 p3 (den svarta katten)
# pa2 = p1 p2 p4 (den svarta katt)
# pa3 = p2 p3 (svarta katten)
# pa4 = p2 p4 (svarta katt)
# pa5 = p5 p4 (svart katt)

# pa6 = p6 p2 p4 (min svarta katt)
# pa7 = p6 p4 (min katt)

# pa8 = p7 p8 p9 (de svarta katter)
# pa9 = p8 p9 (svarta katter)

# pa10 = p3 (katten)
# pa11 = p10 p4 (en katt)
# pa12 = p4 (katt)

# elliptic ones

pslist = "min mitt mina din ditt dina sin hans hennes vår våra vårt dess deras er ert Min Mitt Mina Din Ditt Dina Sin Hans Hennes Vår Våra Vårt Dess Deras Er Ert".split(" ")

levels = ["A1", "A2", "B1", "B2", "C1"]
texts_per_level = {k: [] for k in levels}
for lesson in lessons:
    lvl = lesson.attrib["level"]
    lessontexts = lesson.findall(".//lessontext")
    for lessontext in lessontexts:
        texts_per_level[lvl].append(lessontext)

sumarray = {l: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] for l in levels}
def rmatch(sentence, lvl):
    results = []
    words = sentence.findall(".//w")
    senlen = len(words)
    sid = sentence.attrib["id"]
    q = []
    for i,word in enumerate(words):
        msd = word.attrib["msd"]
        wf = word.text
        assert isinstance(wf, str)
        wf = wf.lower()
        # hook 1 : den/det här/där A(-def) N(-def)
        if wf == "den" or wf == "det":
            if (i+2) < senlen:
                if wordform(words[i+1]) == "här" or wordform(words[i+1]) == "där":
                    m = re.search(p2, gmsd(words[i+2]))
                    if m is not None:
                        if (i+3) < senlen:
                            m2 = re.search(p3, gmsd(words[i+3]))
                            if m2 is not None:
                                # found PA 10 
                                results.append(MyMatch(10, sid, wi(words,i,i+3)))
                                sumarray[lvl][9] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                                q.append(i+3)
                    else: # no adjective_def found
                        m2 = re.search(p3,gmsd(words[i+2]))
                        if m2 is not None:
                            # found PA 9 
                            if i not in q:
                                results.append(MyMatch(9, sid, wi(words,i,i+2)))
                                sumarray[lvl][8] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                        
                    m3 = re.search(p5, gmsd(words[i+2]))
                    if m3 is not None:
                        if (i+3) < senlen:
                            m4 = re.search(p4, gmsd(words[i+3]))
                            if m4 is not None:
                                # found PA 12
                                if i not in q:
                                    results.append(MyMatch(12, sid, wi(words,i,i+3)))
                                    sumarray[lvl][11] += 1
                                    q.append(i)
                                    q.append(i+1)
                                    q.append(i+2)
                                    q.append(i+3)
                    else:
                        m4 = re.search(p4, gmsd(words[i+2]))
                        if m4 is not None:
                            # found PA 11
                            if i not in q:
                                results.append(MyMatch(11, sid, wi(words,i,i+2)))
                                sumarray[lvl][10] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                else:
                    m = re.search(p2, gmsd(words[i+1]))
                    if m is not None:
                        m2 = re.search(p3, gmsd(words[i+2]))
                        if m2 is not None:
                            # found PA 10
                            if i not in q:
                                results.append(MyMatch(10, sid, wi(words,i,i+2)))
                                sumarray[lvl][9] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                    else:
                        m2 = re.search(p3, gmsd(words[i+1]))
                        if m2 is not None:
                            # found PA 9
                            if i not in q:
                                results.append(MyMatch(9, sid, wi(words,i,i+1)))
                                sumarray[lvl][8] += 1
                                q.append(i)
                                q.append(i+1)
                    m3 = re.search(p5, gmsd(words[i+1]))
                    if m3 is not None:
                        if (i+2) < senlen:
                            m4 = re.search(p4, gmsd(words[i+2]))
                            if m4 is not None:
                                # found PA 12
                                if i not in q:
                                    results.append(MyMatch(12, sid, wi(words,i,i+2)))
                                    sumarray[lvl][11] += 1
                                    q.append(i)
                                    q.append(i+1)
                                    q.append(i+2)
                                    
                    else:
                        m4 = re.search(p4, gmsd(words[i+1]))
                        if m4 is not None:
                            # found PA 11
                            if i not in q:
                                results.append(MyMatch(11, sid, wi(words,i,i+1)))
                                sumarray[lvl][10] += 1
                                q.append(i)
                                q.append(i+1)
        if wf == "de":
            if (i+2) < senlen:
                if wordform(words[i+1]) == "här" or wordform(words[i+1]) == "där":
                    m = re.search(p8, gmsd(words[i+2]))
                    if m is not None:
                        if (i+3) < senlen:
                            m2 = re.search(p9, gmsd(words[i+3]))
                            if m2 is not None:
                                # found PA 20
                                if i not in q:
                                    results.append(MyMatch(20, sid, wi(words,i,i+3)))
                                    sumarray[lvl][19] += 1
                                    q.append(i)
                                    q.append(i+1)
                                    q.append(i+2)
                                    q.append(i+3)
                    else:
                        m2 = re.search(p9, gmsd(words[i+2]))
                        if m2 is not None:
                            # found PA 19
                            if i not in q:
                                results.append(MyMatch(19, sid, wi(words,i,i+2)))
                                sumarray[lvl][18] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                else:
                    m = re.search(p8, gmsd(words[i+1]))
                    if m is not None:
                        m2 = re.search(p9, gmsd(words[i+2]))
                        if m2 is not None:
                            # found PA 20
                            if i not in q:
                                results.append(MyMatch(20, sid, wi(words,i,i+2)))
                                sumarray[lvl][19] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                    else:
                        m2 = re.search(p9, gmsd(words[i+1]))
                        if m2 is not None:
                            # found PA 19
                            if i not in q:
                                results.append(MyMatch(19, sid, wi(words,i,i+1)))
                                sumarray[lvl][18] += 1
                                q.append(i)
                                q.append(i+1)
                                
            if (i+1) < senlen:
                m2 = re.search(p82, gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(p92, gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 22
                            if i not in q:
                                results.append(MyMatch(22, sid, wi(words,i,i+2)))
                                sumarray[lvl][21] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                else:
                    m3 = re.search(p92, gmsd(words[i+1]))
                    if m3 is not None:
                        # found PA 21
                        if i not in q:
                            results.append(MyMatch(21, sid, wi(words,i,i+1)))
                            sumarray[lvl][20] += 1
                            q.append(i)
                            q.append(i+1)
        # Starts with INDEF DET
        m = re.search(p10, msd)
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(p5, gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(p4, gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 4
                            if i not in q:
                                results.append(MyMatch(4, sid, wi(words,i,i+2)))
                                sumarray[lvl][3] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                else:
                    m3 = re.search(p4, gmsd(words[i+1]))
                    if m3 is not None:
                        # found PA 3
                        if i not in q:
                            results.append(MyMatch(3, sid, wi(words,i,i+1)))
                            sumarray[lvl][2] += 1
                            q.append(i)
                            q.append(i+1)
                            
        if wf == "detta" or wf == "denna":
            if (i+1) < senlen:
                m = re.match(r"^JJ\..+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m is not None:
                    if (i+2) < senlen:
                        m2 = re.match(r"^NN\..+", gmsd(words[i+2]))
                        if m2 is not None:
                            # found PA 14
                            if i not in q:
                                results.append(MyMatch(14, sid, wi(words,i,i+2)))
                                sumarray[lvl][13] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                else:
                    m2 = re.match(r"^NN\..+", gmsd(words[i+1]))
                    if m2 is not None:
                        # found PA 13
                        if i not in q:
                            results.append(MyMatch(13, sid, wi(words,i,i+1)))
                            sumarray[lvl][12] += 1
                            q.append(i)
                            q.append(i+1)
        if wf == "dessa":
            if (i+1) < senlen:
                m = re.search(r"^JJ\..+", gmsd(words[i+1]))
                if m is not None:
                    if (i+2) < senlen:
                        m2 = re.search(p12, gmsd(words[i+2]))
                        if m2 is not None:
                            # found PA 24
                            if i not in q:
                                results.append(MyMatch(24, sid, wi(words,i,i+2)))
                                sumarray[lvl][23] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                else:
                    m2 = re.search(p12, gmsd(words[i+1]))
                    if m2 is not None:
                        # found PA 23
                        if i not in q:
                            results.append(MyMatch(23, sid, wi(words,i,i+1)))
                            sumarray[lvl][22] += 1
                            q.append(i)
                            q.append(i+1)
        m = re.search(p6, msd)
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(r"^JJ.+(SIN|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(r"^NN.+SIN.+", gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 16
                            if i not in q:
                                results.append(MyMatch(16, sid, wi(words,i,i+2)))
                                sumarray[lvl][15] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m3 = re.search(r"^NN.+SIN.+", gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 15
                    if i not in q:
                        results.append(MyMatch(15, sid, wi(words,i,i+1)))
                        sumarray[lvl][14] += 1
                        q.append(i)
                        q.append(i+1)
        m = re.search(p13, msd) # both SIN + PLU
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(r"^JJ.+(SIN|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(r"^NN.+SIN.+", gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 16
                            if i not in q:
                                results.append(MyMatch(16, sid, wi(words,i,i+2)))
                                sumarray[lvl][15] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m3 = re.search(r"^NN.+SIN.+", gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 15
                    if i not in q:
                        results.append(MyMatch(15, sid, wi(words,i,i+1)))
                        sumarray[lvl][14] += 1
                        q.append(i)
                        q.append(i+1)
                m3 = re.search(r"^JJ.+(PLU|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m3 is not None:
                    if (i+2) < senlen:
                        m4 = re.search(r"^NN.+PLU.+", gmsd(words[i+2]))
                        if m4 is not None:
                            # found PA 26
                            if i not in q:
                                results.append(MyMatch(26, sid, wi(words,i,i+2)))
                                sumarray[lvl][25] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m4 = re.search(r"^NN.+PLU.+", gmsd(words[i+1]))
                if m4 is not None:
                    # found PA 25
                    if i not in q:
                        results.append(MyMatch(25, sid, wi(words,i,i+1)))
                        sumarray[lvl][24] += 1
                        q.append(i)
                        q.append(i+1)
        m = re.search(p132, msd) # both SIN + PLU
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(r"^JJ.+(SIN|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(r"^NN.+SIN.+", gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 16
                            if i not in q:
                                results.append(MyMatch(16, sid, wi(words,i,i+2)))
                                sumarray[lvl][15] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m3 = re.search(r"^NN.+SIN.+", gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 15
                    if i not in q:
                        results.append(MyMatch(15, sid, wi(words,i,i+1)))
                        sumarray[lvl][14] += 1
                        q.append(i)
                        q.append(i+1)
                        
                m3 = re.search(r"^JJ.+(PLU|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m3 is not None:
                    if (i+2) < senlen:
                        m4 = re.search(r"^NN.+PLU.+", gmsd(words[i+2]))
                        if m4 is not None:
                            # found PA 26
                            if i not in q:
                                results.append(MyMatch(26, sid, wi(words,i,i+2)))
                                sumarray[lvl][25] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m4 = re.search(r"^NN.+PLU.+", gmsd(words[i+1]))
                if m4 is not None:
                    # found PA 25
                    if i not in q:
                        results.append(MyMatch(25, sid, wi(words,i,i+1)))
                        sumarray[lvl][24] += 1
                        q.append(i)
                        q.append(i+1)                
        m = re.search(p62, msd)
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(r"^JJ.+(PLU|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(r"^NN.+PLU.+", gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 26
                            if i not in q:
                                results.append(MyMatch(26, sid, wi(words,i,i+2)))
                                sumarray[lvl][25] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m3 = re.search(r"^NN.+PLU.+", gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 25
                    if i not in q:
                        results.append(MyMatch(25, sid, wi(words,i,i+1)))
                        sumarray[lvl][24] += 1
                        q.append(i)
                        q.append(i+1)
        m = re.search(p63, msd)
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(r"^JJ.+(PLU|SIN\+PLU).+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(r"^NN.+PLU.+", gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 26
                            if i not in q:
                                results.append(MyMatch(26, sid, wi(words,i,i+2)))
                                sumarray[lvl][25] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m3 = re.search(r"^NN.+PLU.+", gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 25
                    if i not in q:
                        results.append(MyMatch(25, sid, wi(words,i,i+1)))
                        sumarray[lvl][24] += 1
                        q.append(i)
                        q.append(i+1)
        if wf in pslist:
            if (i+1) < senlen:
                m2 = re.search(r"^JJ.+$|(R[OG]\.NOM)", gmsd(words[i+1]))
                if m2 is not None:
                    if (i+2) < senlen:
                        m3 = re.search(r"^NN.+", gmsd(words[i+2]))
                        if m3 is not None:
                            # found PA 26
                            if i not in q:
                                results.append(MyMatch(26, sid, wi(words,i,i+2)))
                                sumarray[lvl][25] += 1
                                q.append(i)
                                q.append(i+1)
                                q.append(i+2)
                m3 = re.search(r"^NN.+", gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 25
                    if i not in q:
                        results.append(MyMatch(25, sid, wi(words,i,i+1)))
                        sumarray[lvl][24] += 1
                        q.append(i)
                        q.append(i+1)
        # ADJ underspecified
        m = re.search(p122, msd)
        if m is not None:
            if (i+1) < senlen:
                m2 = re.search(p9, gmsd(words[i+1]))
                if m2 is not None:
                    # found PA 18
                    if i not in q:
                        results.append(MyMatch(18, sid, wi(words,i,i+1)))
                        sumarray[lvl][17] += 1
                        q.append(i)
                        q.append(i+1)
                        
                m3 = re.search(p3, gmsd(words[i+1]))
                if m3 is not None:
                    # found PA 8
                    if i not in q:
                        results.append(MyMatch(8, sid, wi(words,i,i+1)))
                        sumarray[lvl][7] += 1
                        q.append(i)
                        q.append(i+1)
                m4 = re.search(p14, gmsd(words[i+1]))
                if m4 is not None:
                    # found PA 6
                    if i not in q:
                        results.append(MyMatch(6, sid, wi(words,i,i+1)))
                        sumarray[lvl][5] += 1
                        q.append(i)
                        q.append(i+1)
                m5 = re.search(p4, gmsd(words[i+1]))
                if m5 is not None:
                    # found PA 2
                    if i not in q:
                        results.append(MyMatch(2, sid, wi(words,i,i+1)))
                        sumarray[lvl][1] += 1
                        q.append(i)
                        q.append(i+1)
        m = re.search(p9, msd)
        if m is not None:
            # found PA 17
            if i not in q:
                results.append(MyMatch(17, sid, wi(words,i,i)))
                sumarray[lvl][16] += 1
                q.append(i)
        m = re.search(p3, msd)
        if m is not None:
            # found PA 7
            if i not in q:
                results.append(MyMatch(7, sid, wi(words,i,i)))
                sumarray[lvl][6] += 1
                q.append(i)
        m = re.search(p14, msd)
        if m is not None:
            # found PA 5
            if i not in q:
                results.append(MyMatch(5, sid, wi(words,i,i)))
                sumarray[lvl][4] += 1
                q.append(i)
        m = re.search(p4, msd)
        if m is not None:
            if i > 0:
                prev = words[i-1]
                # check if prev has deprel DET and POS != DET
                deprel = prev.attrib["deprel"]
                pos = prev.attrib["pos"]
                if pos != "DT" and deprel == "DT":
                    pass
                # if yes, other pattern
                # else
            # found PA 1
            if i not in q:
                results.append(MyMatch(1, sid, wi(words,i,i)))
                sumarray[lvl][0] += 1
                q.append(i)
    return results

def wordform(w):
    return w.text.lower()
def gmsd(w):
    return w.attrib["msd"]
def wi(arr, i, j):
    if j == i:
        return arr[i]
    return arr[i:j+1]

tres = []
for lvl in levels:
    for txt in texts_per_level[lvl]:
        for sentence in txt.findall(".//sentence"):
            res = rmatch(sentence, lvl)
            if len(res) > 0:
                tres.append(res)

def get_res_by_sid(sid):
    for a in tres:
        if a[0].get_sentence_id() == sid:
            return a
    return []

for lvl in levels:
    out = codecs.open("/{}_texts_acs13r.csv".format(lvl), "w", encoding="utf-8")
    for txt in texts_per_level[lvl]:
        sentences = txt.findall(".//sentence")
        for sentence in sentences:
            words = sentence.findall(".//w")
            sid = sentence.attrib["id"]
            res = get_res_by_sid(sid)
            if len(res) > 0:
                for r in res:
                    out.write("{}\t{}\t{}\n".format(linearize(words), linearize(r.get_words()), r.get_pattern()))
            else:
                    out.write("{}\t{}\t{}\n".format(linearize(words), "_", "_"))
        out.write("{}\t{}\t{}\n".format("*", "*", "*"))
    out.close()

sumout = open("/sumarray.csv", "w")
for lvl in sumarray:
    sumout.write("{}\t{}\n".format(lvl, "\t".join([str(x) for x in sumarray[lvl]])))
sumout.close()