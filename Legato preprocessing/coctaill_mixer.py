# coding: utf-8
'''
Created on 9 Jun 2019

@author: David
'''

import lxml.etree as ET

# TODO PATH TO COCTAILL sense annotated corpus
corpus = "/coctaill.xml"

tree = ET.parse(corpus)
root = tree.getroot()
lessons = root.findall(".//lesson")
texts_per_level = {"A1": [], "A2": [], "B1": [], "B2": [], "C1": []}

for lesson in lessons:
    lvl = lesson.attrib["level"]
    lessontexts = lesson.findall(".//lessontext")
    for lessontext in lessontexts:
        texts_per_level[lvl].append(lessontext)

non_pipe = ["pos", "msd", "ref", "dephead", "deprel", "sentiment", "sentimentclass"]

'''
Find targets where specified attribute occurs anywhere in values
'''
def find_targets(attrib_pairs, node): 
    # expects a dictionary of attribute pairs (pos: JJ, msd: JJ.KOM, sense:...)
    # <w pos="RG" msd="RG.NOM" lemma="|tre|" lex="|tre..nl.1|" sense="|tre..1:-1.000|" prefix="|" suffix="|" compwf="|" complemgram="|" ref="02" dephead="03" deprel="DT" blingbring="|" swefn="|" sentiment="0.3145" sentimentclass="neutral">tre</w>
    # No pipe if pos, msd, ref dephead, deprel, sentiment, sentimentclass
    
    q = './/sentence/w['
    for k,v in attrib_pairs.items():
        if k not in non_pipe:
            v = "|" + v
        if q[-1] == ")":
            q += " and "
        q += "contains(@{},'{}')".format(k,v)
    q += "]"
    
    return node.xpath(q)

'''
Find targets where the specified attribute is listed first
'''
def find_targets_first(attrib_pairs, node):
    q = './/sentence/w['
    for k,v in attrib_pairs.items():
        if k not in non_pipe:
            v = "|" + v
        if q[-1] == "]":
            q += "["
        q += "starts-with(@{},'{}')]".format(k,v)
        
    
    return node.xpath(q)

def get_sentence(target):
    return [x for x in target.iterancestors(tag='sentence')][0]

def linearize(words, target=None):
    linsen = []
    for w in words:
        if target is not None:
            if w == target:
                linsen.append("**")
                linsen.append(w.text)
                linsen.append("**")
            else:
                linsen.append(w.text)
    return " ".join(linsen)

def get_words(sentence):
    return sentence.findall(".//w") 

def get_example_sentence(sense, pos, cefr):
    ctexts = texts_per_level[cefr]
    attribs = {"sense": sense, "pos": pos}
    # try strict
    targets = set()
    for t in ctexts:
        targets.update(find_targets_first(attribs, t))
    if len(targets) == 0:
        for t in ctexts:
            targets.update(find_targets(attribs, t))
    if len(targets) == 0:
        #print("No sentence for {} ({}) [{}]".format(sense, pos, cefr))
        pass
    else:
        target = targets.pop()
        sentence = get_sentence(target)
        return linearize(get_words(sentence), target)
    
def get_example_sentences(sense, pos, cefr, maxnum):
    try:
        ctexts = texts_per_level[cefr]
    except KeyError:
        return []
    attribs = {"sense": sense, "pos": pos}
    # try strict
    targets = set()
    for t in ctexts:
        targets.update(find_targets_first(attribs, t))
    if len(targets) == 0:
        for t in ctexts:
            targets.update(find_targets(attribs, t))
    if len(targets) == 0:
        #print("No sentence for {} ({}) [{}]".format(sense, pos, cefr))
        pass
    else:
        pnum = min(len(targets), maxnum)
        sentences = []
        for _ in range(pnum):
            target = targets.pop()
            sentence = get_sentence(target)
            sentences.append(linearize(get_words(sentence), target))
        return sentences
        
if __name__ == "__main__":
    a = get_example_sentence("katt..1", "NN", "A1")
    print(a)