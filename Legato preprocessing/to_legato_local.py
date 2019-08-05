# coding: utf-8
'''
Created on 9 Jun 2019

@author: David
'''
from global_linker import rlink
import codecs
import re

# TODO PATH TO SENSVALEX FILE
sensvalex_file = "/senstarlex_v4_clean_unique_saldo.csv"
# TODO PATH TO OUTFILE
outfile_name = "/senstarlex_v4_clean_unique_saldo_linked.csv"

sensvalex = [x.rstrip().split("\t") for x in codecs.open(sensvalex_file, "r", encoding="utf-8")]
lexical_pos = ["NN", "VB", "AB", "JJ"]
counter = 0
out_format_template = "{}\t{}\t{}\t{}\t{}"

agg = []
no_sentence = []

def extract_synonyms(vals, pos):
    if pos > (len(vals) - 1):
        return []
    syns = vals[pos]
    
    if len(syns) == 0:
        return []
    syn = []
    for s in syns:
        if len(s) > 2:
            
            p = s[1]
            q = s[2]
            if q == "syn":
                syn.append(p)
    return syn

def _map_gender(gend):
    
    if gend == "n":
        return "ett"
    if gend == "u":
        return "en"
    if gend == "v":
        return "en,ett"
    return "none"

def _map_dec(dec):
    
    if dec not in ["1","2","3","4","5","6","7"]:
        return "other"
    return dec
def _map_conj(c):
    if c not in ["1","2","3","4"]:
        return "irregular"
    return c
def _map_jj(jj):
    if jj not in ["1","2"]:
        return "suppletive"
    return jj
def _map_jj_ab(ja):
    parts = ja.split("_")
    
    if len(parts) < 2:
        if parts[0] == "periphrastic":
            return "periphrastic/analytic"
        else:
            return []
    l1 = parts[0]
    l2 = parts[1]
    if l1 == "morpho":
        l1 = "non-periphrastic/synthetic"
    
    return "{},{}".format(l1,l2)


for entry in sensvalex:
    counter += 1
    if counter%1000==0:
        print("{}/{}".format(counter, len(sensvalex)))
    lemgram, sense, pos, prim, sec, cefr = entry
    m = re.search(r"^.+?\.\.[1-9]+?$", sense)
        
    if m is None:
        continue
    if pos in lexical_pos or "_" in lemgram:
        vals = rlink(sense)

        is_mwe = 0
        if "_" in lemgram:
            is_mwe = 1
        out_format_template_mwe = out_format_template.format(lemgram, sense, pos, "is_mwe", is_mwe)
        agg.append(out_format_template_mwe)
        
        if vals == "Nothing":
            continue
        esyn = []
        if pos == "JJ" or pos == "AB":
            
            esyn = extract_synonyms(vals, 1)
            
        else:
            esyn = extract_synonyms(vals, 2)
            
        esyns = ",".join(esyn)
    
        
        if len(esyns) > 0:
            # send synonyms
            out_format_template_2 = out_format_template.format(lemgram, sense, pos, "synonyms", esyns)
            agg.append(out_format_template_2)
        if pos == "NN":
            out_format_template_2 = out_format_template.format(lemgram, sense, pos, "nominal_gender", _map_gender(vals[1]))
            agg.append(out_format_template_2)
            out_format_template_3 = out_format_template.format(lemgram, sense, pos, "nominal_declension", _map_dec(vals[0]))
            agg.append(out_format_template_3)
        if pos == "VB":
            out_format_template_2 = out_format_template.format(lemgram, sense, pos, "verbal_conjugation", _map_conj(vals[0]))
            agg.append(out_format_template_2)
        # NN: nom dec, nom gender, synonyms
        # VB: verbal dec, voice, synonyms
        # AB: adj adv struct??, 
        # JJ: adj dec, syn, [-1] => struct
        if pos == "JJ" or pos == "AB":
            # compare vals[0] and vals[-2]
            if vals[0] == "i":
                out_format_template_2 = out_format_template.format(lemgram, sense, pos, "adjectival_declension", "indeclinable")
                agg.append(out_format_template_2)
            else:
                #print(vals)
                if len(vals) > 3:
                    if vals[0] != vals[-2]:
                        out_format_template_3 = out_format_template.format(lemgram, sense, pos, "adjectival_declension", _map_jj(vals[-2]))
                        agg.append(out_format_template_3)
                        struc = _map_jj_ab(vals[-1])
                        
                        if len(struc) > 0:
                            out_format_template_1 = out_format_template.format(lemgram, sense, pos, "adjectival_adverbial_structure", struc)
                            agg.append(out_format_template_1)
                    else:
                        out_format_template_3 = out_format_template.format(lemgram, sense, pos, "adjectival_declension", _map_jj(vals[-2]))
                        struc = _map_jj_ab(vals[-1])
                        if len(struc) > 0:
                            
                            out_format_template_2 = out_format_template.format(lemgram, sense, pos, "adjectival_adverbial_structure", struc)
                            agg.append(out_format_template_2)
                        agg.append(out_format_template_3)
                        
out = codecs.open(outfile_name, "w", encoding="utf-8")
out.write("\n".join(agg))
out.close()

print("Done")