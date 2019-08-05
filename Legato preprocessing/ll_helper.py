# coding: utf-8
'''
Created on Oct 4, 2018

@author: David
'''

import re
def pos_from_lemgram(lemgram):
    a = lemgram.split(".")
    return a[2]
    
def info_from_pos_dec_like(pos_dec_like):
    a = pos_dec_like.split("_", maxsplit=2)
    if len(a[1]) > 1:
        b,c = a[1][0], a[1][1]
        return a[0],b,c,a[2]
    return a

def infer_adj_comp_type(p,c,s):
    comp_reg = "re"
    sup_reg = "st"
    if not re.match(r"^.+?[aeiou]$", p):
        if not p.endswith("ng"):
            comp_reg = "are"
            sup_reg = "ast"
    # build tentative "regular" comparative and superlative forms
    comp_tent = "{}{}".format(p, comp_reg)
    sup_tent = "{}{}".format(p, sup_reg)
    
    # build tentative periphrastic comparative and superlative forms
    comp_tent_peri = "mer {}".format(p)
    sup_tent_peri = "mest {}".format(p)
    
    if c == comp_tent and s == sup_tent:
        return "morpho_regular"
    if c == comp_tent_peri and s == sup_tent_peri:
        return "periphrastic"
    return "morpho_irregular"

def infer_adj_declension(p,c,s):
    comp_type = infer_adj_comp_type(p, c, s)
    if comp_type == "morpho_regular":
        return "1"
    comp_reg = "re"
    sup_reg = "st"
    if not re.match(r"^.+?[aeiou]$", p):
        if not p.endswith("ng"):
            comp_reg = "are"
            sup_reg = "ast"
    star_p = re.sub(r"[aeiouyöäå]", "*", p, 1)
    star_c = re.sub(r"[aeiouyöäå]", "*", c, 1)
    star_s = re.sub(r"[aeiouyöäå]", "*", s, 1)
    comp_tent = "{}{}".format(star_p, comp_reg)
    sup_tent = "{}{}".format(star_p, sup_reg)
    if star_c == comp_tent and star_s == sup_tent:
        return "2"
    return "3"
        
def infer_gender_lexin(lemma, inflections):
    # useless, has been removed from entries
#     if ("~" in lemma):
#         lemma = "-"+lemma.split("~")[1]
    infl_count = len(inflections)
    # based on different inflectional patterns, retrieve gender
    if (infl_count < 1):
        print("No inflectional information found!")
        return -1
    # 1. only one form given
    # 1.1 ends with t -> ett
    # 1.2 else -> en
    if (infl_count == 1):
        if (inflections[0].endswith("t")):
            return 1
        return 0 
    # 2. two forms
    # 2.1. -n -r -> en
    # 2.2 "ett" + lemma -> ett
    if (infl_count == 2):
        if (inflections[1] == lemma and inflections[0] == "ett"):
            return 1
        if (inflections[1] == lemma and inflections[0] == "en"):
            return 0
        if (inflections[0].endswith("n") and inflections[1].endswith("r")):
            return 0
        if (inflections[0].endswith("t") and inflections[1].endswith("r")):
            return 2
        return -1 # or 0?
    # 3. three forms
    # 3.1. -t -0 -n -> ett
    # 3.2. -n -0 -a (?) -> en
    if (infl_count == 3):
        if (inflections[0].endswith("t") and inflections[1] == lemma and inflections[2].endswith("n")):
            return 1
        if (inflections[0].endswith("n") and inflections[1] == lemma and inflections[2].endswith("a")):
            return 0
        return -1 # or -1?
    
    # 4. four??
    
    # 7. seven elements -> both ett+en
    if (infl_count == 7):
        return 2
    
    
def mapLexinGender(lg):
    if lg == -1:
        return None
    if lg == 0:
        return "u"
    if lg == 1:
        return "n"
    if lg == 2:
        return "v"
    return None
if __name__ == "__main__":
    a = info_from_pos_dec_like("nn_o_sten_or_war")
    b = infer_adj_comp_type("grön", "grönare", "grönast")
    c = infer_adj_declension("tung", "tyngre", "tyngst")
    print(c)