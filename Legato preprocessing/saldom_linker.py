# coding: utf-8
'''
Created on Oct 3, 2018

@author: David
'''
import sqlite3
from ll_config_local import SALDOM_DB

conn = sqlite3.connect(SALDOM_DB)
c = conn.cursor()

def get_pcs(lemgram):
    c.execute("SELECT pos_indef_sg_u_nom, komp_nom, super_indef_nom FROM saldom WHERE lemgram=?", (lemgram,))
    return c.fetchall()

def get_entry(lemgram):
    c.execute("SELECT * FROM saldom WHERE lemgram=?", (lemgram,))
    return c.fetchall()

def get_pres_ind_aktiv(lemgram):
    return get_pres_ind(lemgram)[0][0]

def get_pres_ind_s_form(lemgram):
    return get_pres_ind(lemgram)[0][1]

def get_pres_ind(lemgram):
    c.execute("SELECT pres_ind_aktiv, pres_ind_s_form FROM wordforms WHERE lemgram=?", (lemgram,))
    return c.fetchall()

def get_inflected(lemgram):
    a = get_pres_ind_aktiv(lemgram)
    if a == "None":
        b = get_pres_ind_s_form(lemgram)
        if b == "None":
            return "NoInflectionFound"
        return b
    return a

if __name__ == "__main__":
#     print(get_entry("slaskig..av.1"))
#     print(get_pcs("slaskig..av.1"))
    a = get_inflected("finnas..vb.1")
    b = get_pres_ind("finnas..vb.1")
    c = get_pcs("lik..av.1")
    print(c)
    
