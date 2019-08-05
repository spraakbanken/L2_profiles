# coding: utf-8
'''
Created on Oct 4, 2018

@author: David
'''
from saldo_linker import get_saldo_values, get_dec_like
from saldom_linker import get_pcs,get_pres_ind,get_entry as get_saldom_entry
from lexin_linker import get_entry as get_lexin_entry
from parole_linker import get_generic_by_saldo_sense
from simple_linker import get_try_saldo_first
from swesaurus_linker import get_synonyms
from blingbring_linker import get_by_saldo_sense as get_blingbring_values
from ll_helper import infer_adj_comp_type, info_from_pos_dec_like, infer_adj_declension, infer_gender_lexin, mapLexinGender

def mapToLexinPos(pos):
    if pos == "nn":
        return "subst."
    if pos == "vb":
        return "verb"
    if pos == "av":
        return "adj."
    if pos == "ab":
        return "adv."
    return None
    # räkn.
    
'''
Full lexical linking function.
Does not return values, prints them instead (debugging purposes)
'''
def link(saldo_sense_key):
    saldo_values = get_saldo_values(saldo_sense_key)
    if len(saldo_values) < 1:
        # TODO check Lexin instead?
        return "Nothing"
    
    for entry in saldo_values:
        
        saldo_primary = entry[1]
        saldo_secondary = entry[2]
        print("{} {}".format(saldo_primary, saldo_secondary))
        lemgram = entry[3]
        form = entry[4]
        pos = entry[5]
        pos_dec_like = entry[6]
        saldom_values = get_saldom_entry(lemgram)[0] # TODO  can this yield many?
        print(saldom_values)
        lemma = saldom_values[1]
        parole_values = get_generic_by_saldo_sense("*", saldo_sense_key)
        print(parole_values)
        synonyms = get_synonyms(saldo_sense_key)
        print(synonyms)
        blingbring_values = get_blingbring_values(saldo_sense_key)
        print(blingbring_values)
        
        declension = ""
        voice = ""
        gender = ""
        paradigm = ""
        
        if pos == "av":
            p,c,s = get_pcs(lemgram)[0]
            print("{} {} {}".format(p,c,s))
            adj_comp_type = infer_adj_comp_type(p, c, s)
            adj_decl = infer_adj_declension(p, c, s)
            print("{} {}".format(adj_decl, adj_comp_type))
            
            
        infos = info_from_pos_dec_like(pos_dec_like)    
        if len(infos) == 3:
            declension = infos[1]
            paradigm = infos[2]
        if len(infos) == 4:
            declension = infos[1]
            if pos == "vb":
                voice = infos[2]
            if pos == "nn":
                gender = infos[2]
            paradigm = infos[3]
        if pos == "vb":
            forms = get_pres_ind(lemgram)[0]  # check both forms?
            if forms[0] != "None":
                form = forms[0]
                if "\t" in forms[0]: # can contain alternatives
                    pass  
            else:
                form = forms[1]
                if "\t" in forms[1]:
                    pass
        print(pos)
        print(declension)
        
        if pos == "nn":
            print(gender)
        if pos == "vb":
            print(voice)
        print(paradigm)
        lpos = mapToLexinPos(pos)
        print(form, lpos)
        lexin_values = get_lexin_entry(form, lpos)
        
        print(lexin_values) # might yield zero or more than one result # check inferred lexin gender -> barr..3
        
        if len(lexin_values) > 0 and pos == "nn": # filter lexin values by gender => gender overlap
            for lv in lexin_values:
                lexin_gender = infer_gender_lexin(lemma, lv[2].split())
                # -1, 0, 1, 2
                lexin_gender_mapped = mapLexinGender(lexin_gender)
                
                if lexin_gender_mapped != gender:
                    continue
                
                print(lexin_gender)
                print(lexin_gender_mapped)
       
        simple_values = get_try_saldo_first(saldo_sense_key, form, pos)
        print(simple_values)

'''
Simplified lexical linking.
'''
def slink(saldo_sense_key):
    saldo_values = get_saldo_values(saldo_sense_key)
    if len(saldo_values) < 1:
        # TODO check Lexin instead?
        return "Nothing"
    return_vals = []
    for entry in saldo_values:
        
        saldo_primary = entry[1]
        saldo_secondary = entry[2]
        
        lemgram = entry[3]
        form = entry[4]
        pos = entry[5]
        pos_dec_like = entry[6]
        
        
        pos,dec,like = pos_dec_like.rsplit("_", maxsplit=2)
        if len(dec) > 1:
            return_vals.append(dec[0])
            return_vals.append(dec[1])
        else:
            return_vals.append(dec)
        saldom_values = get_saldom_entry(lemgram)[0] # TODO  can this yield many?
        
        lemma = saldom_values[1]
        #
        parole_values = get_generic_by_saldo_sense("*", saldo_sense_key)
        
        synonyms = get_synonyms(saldo_sense_key)
        return_vals.append(synonyms)
        
        
        blingbring_values = get_blingbring_values(saldo_sense_key)
        
        transitivity_values = set()
        if len(parole_values) > 0:
            for pv in parole_values: 
                tv = len(pv[2].split()) - 1
                if tv == 1:
                    transitivity_values.add("intransitive")
                if tv == 2:
                    transitivity_values.add("transitive")
                if tv == 3:
                    transitivity_values.add("ditransitive")
        
        return_vals.append(list(transitivity_values))
        declension = ""
        voice = ""
        gender = ""
        paradigm = ""
        
        if pos == "av":
            p,c,s = get_pcs(lemgram)[0]
            
            adj_comp_type = infer_adj_comp_type(p, c, s)
            adj_decl = infer_adj_declension(p, c, s)
            return_vals.append(adj_decl)
            return_vals.append(adj_comp_type)
            
            
        infos = info_from_pos_dec_like(pos_dec_like)    
        if len(infos) == 3:
            declension = infos[1]
            paradigm = infos[2]
        if len(infos) == 4:
            declension = infos[1]
            if pos == "vb":
                voice = infos[2]
            if pos == "nn":
                gender = infos[2]
            paradigm = infos[3]
        if pos == "vb":
            forms = get_pres_ind(lemgram)[0]  # check both forms?
            if forms[0] != "None":
                form = forms[0]
                if "\t" in forms[0]: # can contain alternatives
                    pass  
            else:
                form = forms[1]
                if "\t" in forms[1]:
                    pass
        
        
        
        if pos == "nn":
            pass
        if pos == "vb":
            pass
        
        lpos = mapToLexinPos(pos)
        
        lexin_values = get_lexin_entry(form, lpos)
        
        
        
        if len(lexin_values) > 0 and pos == "nn": # filter lexin values by gender => gender overlap
            for lv in lexin_values:
                lexin_gender = infer_gender_lexin(lemma, lv[2].split())
                # -1, 0, 1, 2
                lexin_gender_mapped = mapLexinGender(lexin_gender)
                
                if lexin_gender_mapped != gender:
                    continue
                
                
                
                # else
                # extract values
                
        #if pos == "nn" and (gender is None or gender == "") and len(lexin_values) > 0:
        #    gender = infer_gender_lexin(form, lexin_values[2].split())
        
       
        simple_values = get_try_saldo_first(saldo_sense_key, form, pos)
        
        return return_vals
    
'''
Reduces lexical linking.
'''
def rlink(saldo_sense_key):
    saldo_values = get_saldo_values(saldo_sense_key)
    if len(saldo_values) < 1:
        # TODO check Lexin instead?
        return "Nothing"
    return_vals = []
    for entry in saldo_values:
        
        saldo_primary = entry[1]
        saldo_secondary = entry[2]
        
        lemgram = entry[3]
        form = entry[4]
        pos = entry[5]
        pos_dec_like = entry[6]
        
        
        pos,dec,like = pos_dec_like.rsplit("_", maxsplit=2)
        if len(dec) > 1:
            return_vals.append(dec[0])
            return_vals.append(dec[1])
        else:
            return_vals.append(dec)
        saldom_values = get_saldom_entry(lemgram)[0] # TODO  can this yield many?
        
        lemma = saldom_values[1]
        #
        #parole_values = get_generic_by_saldo_sense("*", saldo_sense_key)
        
        synonyms = get_synonyms(saldo_sense_key)
        return_vals.append(synonyms)
        
        
        #blingbring_values = get_blingbring_values(saldo_sense_key)
        
        
        declension = ""
        voice = ""
        gender = ""
        paradigm = ""
        
        if pos == "av":
            p,c,s = get_pcs(lemgram)[0]
            
            adj_comp_type = infer_adj_comp_type(p, c, s)
            adj_decl = infer_adj_declension(p, c, s)
            return_vals.append(adj_decl)
            return_vals.append(adj_comp_type)
            
            
        infos = info_from_pos_dec_like(pos_dec_like)    
        if len(infos) == 3:
            declension = infos[1]
            paradigm = infos[2]
        if len(infos) == 4:
            declension = infos[1]
            if pos == "vb":
                voice = infos[2]
            if pos == "nn":
                gender = infos[2]
            paradigm = infos[3]
        if pos == "vb":
            forms = get_pres_ind(lemgram)[0]  # check both forms?
            if forms[0] != "None":
                form = forms[0]
                if "\t" in forms[0]: # can contain alternatives
                    pass  
            else:
                form = forms[1]
                if "\t" in forms[1]:
                    pass
        
        
        
        if pos == "nn":
            pass
        if pos == "vb":
            pass

        
        return return_vals