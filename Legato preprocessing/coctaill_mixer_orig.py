# coding: utf-8
'''
Created on 5 Aug 2019

@author: David
'''
import xml.etree.ElementTree as ET
import codecs
import re

# TODO PATH TO COCTAILL sense annotated
corpus = "/coctaill.xml"
# TODO PATH TO OUTFILE
outfile = "/sensvalex_v4.csv"

tree = ET.parse(corpus)
root = tree.getroot()

lessons = root.findall(".//lesson")

# define things
delimiters = ["MAD", "MID", "PAD", "PID"]
attribs = ["pos", "msd", "lemma", "lex", "sense", "prefix", "suffix", "compwf", "complemgram", "ref", "deprel", "blingbring", "swefn", "sentiment", "sentimentclass"]
mwe_regex = r"([^|]+?)\.\.(..m)\.(\d)"
mwe_regex_comp = r"[^|]+?\.\...m\.\d:\d+?\|"

freqs = dict()

# get texts per level
levels = ["A1", "A2", "B1", "B2", "C1"]
texts_per_level = {k: [] for k in levels}

for lesson in lessons:
    lvl = lesson.attrib["level"]
    lessontexts = lesson.findall(".//lessontext")
    for lessontext in lessontexts:
        texts_per_level[lvl].append(lessontext)
        
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
    
def distToCefr(dist):
    for i in range(len(dist)):
        if dist[i] != 0:
            return numToCefr(i)
        
def numToCefr(num):
    if num == 0:
        return "A1"
    if num == 1:
        return "A2"
    if num == 2:
        return "B1"
    if num == 3:
        return "B2"
    if num == 4:
        return "C1"
    if num == 5:
        return "C2"
    return "XX"

def removeBars(k):
    parts = []
    if "\t" in k:
        parts = k.split("\t")
        k = parts[0]
        pos = parts[1]
    if k.startswith("|") and k.endswith("|"):
        l = k[1:-1]
        if len(parts) == 2:
            l  += "\t{}".format(parts[1])
        return l
    return k

no_sense, no_lemma = 0,0
no_sense2 = 0

# extract tuples
tuples = []
# frequencies
freqs = dict()
# for debug purposes
mwe_tuples = []

for lesson in lessons:
    lvl = lesson.attrib["level"]
    lessontexts = lesson.findall(".//lessontext")
    for lessontext in lessontexts:
        sentences = lessontext.findall(".//sentence")
        for sentence in sentences:
            words = sentence.findall(".//w")
            for w in words:
                has_mwe = False
                sense_candidates = []
                pos = w.attrib["pos"]
                if pos is None or pos in delimiters:
                    continue
                lex = w.attrib["lex"]
                # try finding MWEs in LEX
                mwe_match = re.search(mwe_regex, lex)
                if mwe_match is not None:
                    mwe_match_comp = re.search(mwe_regex_comp, lex)
                    if mwe_match_comp is not None:
                        # don't count this again
                        continue
                    mwe_exp = mwe_match.group(1)
                    mwe_pos = mwe_match.group(2)
                    mwe_num = mwe_match.group(3)
                    
                    has_mwe = True
                senses = w.attrib["sense"]
                presense = ""
                if senses == "|":
                    no_sense += 1
                    lemma = w.attrib["lemma"]
                    senses = lemma[1:-1] + "..0"
                    presense = lemma[1:-1]
                    if lemma == "|":
                        no_lemma += 1
                        wordform = w.text
                        senses = wordform + "..0"
                        presense = wordform
                    senses = presense + ".." + pos.lower() + ".0"
                m = re.search(r"\d\|?$", senses)
                
                if m is None:
                    # there still is no number at the end
                    senses += "..0"
                for sense in senses.split("|"):
                    if len(sense.strip()) == 0:
                        pass
                    if has_mwe:
                        # check whether there is an MWE match in senses
                        sense_mwe = re.search(mwe_exp, senses)
                        if sense_mwe is not None: 
                            if sense.startswith(mwe_exp):
                                if ":" in sense:
                                    sense, prob = sense.split(":")
                                    if prob == "-1.000":
                                        # append to list of candidates?
                                        sense_candidates.append(sense)
                                    else:
                                        sense_candidates.append(sense)
                                        break
                        else: # no sense starting with expression
                            # search for other MWEs (alleviate m_m -> meter / med_mera problem)
                            if "_" in senses:
                                if "_" in sense: # check for föra_bort->bortföra 
                                    parts = sense.split("_")
                                    switched = parts[1] + parts[0]
                                    if sense.startswith(switched):
                                        if ":" in sense:
                                            sense, prob = sense.split(":")
                                        sense_candidates.append(sense)
                                        break
                                    if ":" in sense:
                                        sense, prob = sense.split(":")
                                        if prob == "-1.000":
                                            # append to list of candidates?
                                            sense_candidates.append(sense)
                                        else:
                                            sense_candidates.append(sense)
                                            break
                            else:
                                if ":" in sense:
                                    sense, prob = sense.split(":")
                                    if prob == "-1.000":
                                        # append to list of candidates?
                                        sense_candidates.append(sense)
                                    else:
                                        sense_candidates.append(sense)
                                        break
                    else:
                        if ":" in sense:
                            try:
                                sense, prob = sense.split(":")
                            except ValueError:
                                pass
                            if prob == "-1.000":
                                # append to list of candidates?
                                sense_candidates.append(sense) 
                            else:
                                # due to numerical order by probability, most probable will come first
                                sense_candidates.append(sense)
                                break
                        else:
                            # there is no probability for the sense -> there was no sense in the annotation
                            no_sense2 += 1
                if lex == "|":
                    lex = senses
                fkey = "DUMMY"
                if has_mwe:
                    rekey = "|{}..{}.{}|\t{}".format(mwe_exp, mwe_pos, mwe_num, pos)
                    key = {rekey: sense_candidates}
                    fkey = rekey
                    if key not in mwe_tuples: # for debugging purposes
                        mwe_tuples.append(key)
                else:
                    rkey = "{}\t{}".format(lex, pos)
                    key = {rkey: sense_candidates}
                    fkey = rkey
                if key not in tuples:
                    # TODO include level somewhere??
                    tuples.append(key)

                if fkey not in freqs:
                    freqs[fkey] = [0,0,0,0,0]
                freqs[fkey][mapCefrToInt(lvl)] += 1
                        
mwe_tuples_uniq = []
for it in mwe_tuples:
    for k,v in it.items():
        if len(v) == 1:
            mwe_tuples_uniq.append({k:v})

out = codecs.open(outfile, "w", encoding="utf-8")
for item in tuples:
    for k,v in item.items():
        frequency = freqs[k]
        cefr = distToCefr(frequency)
        l = removeBars(k)
        m = ";".join(v)
        out.write("{}\t{}\t{}\n".format(l,m,cefr))
out.close()
print("Done")

# write unique MWEs
# out = codecs.open("/sensvalex_v4_mwe_uniq.csv", "w", encoding="utf-8")
# for item in mwe_tuples_uniq:
#     for k,v in item.items():
#         frequency = freqs[k]
#         cefr = distToCefr(frequency)
#         l = removeBars(k)
#         if len(v) == 0:
#             print(item)
#         m = v[0]
#         out.write("{}\t{}\t{}\n".format(l,m,cefr))
# out.close()
# print("Done")