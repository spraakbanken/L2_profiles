# coding: utf-8
'''
Created on Oct 3, 2018

@author: David
'''
import sqlite3
from ll_config_local import SALDO_DB
#from scipy.io.arff.arffread import get_nominal

conn = sqlite3.connect(SALDO_DB)
c = conn.cursor()

def get_saldo_values(saldo_sense_key):
    c.execute("SELECT * FROM saldo WHERE sense_key = ?", (saldo_sense_key,))
    return c.fetchall()

def get_saldo_primary(saldo_sense_key):
    try:
        return get_saldo_values(saldo_sense_key)[1]
    except TypeError:
        return "NoPrimary"
    

def get_saldo_secondary(saldo_sense_key):
    try:
        return get_saldo_values(saldo_sense_key)[2]
    except TypeError:
        return "NoSecondary"

def get_lemgram(saldo_sense_key):
    try:
        return get_saldo_values(saldo_sense_key)[3]
    except TypeError:
        return "NoLemgram"

def get_lemma(saldo_sense_key):
    try:
        return get_saldo_values(saldo_sense_key)[4]
    except TypeError:
        return "NoLemma"
    
def get_pos(saldo_sense_key):
    try:
        return get_saldo_values(saldo_sense_key)[5]
    except TypeError:
        return "NoPos"
    
def get_pos_dec_like(saldo_sense_key):
    try:
        return get_saldo_values(saldo_sense_key)[6]
    except TypeError:
        return "NoDeclension"
    
def get_dec_like(saldo_sense_key):
    try:
        pdl = get_pos_dec_like(saldo_sense_key)
        if "_" not in pdl:
            return "NoDeclensionGender"
        return pdl.split("_", maxsplit=2)
    except TypeError:
        return "NoDeclension"
        
def get_nominal_declension(saldo_sense_key):
    try:
        a = get_dec_like(saldo_sense_key)[1]
        return a[0]
    except TypeError:
        return "NoDeclension"
    
def get_gender(saldo_sense_key):
    try:
        a = get_dec_like(saldo_sense_key)[1]
        return a[1]
    except TypeError:
        return "NoDeclension"
    
def get_voice(saldo_sense_key):
    try:
        a = get_dec_like(saldo_sense_key)[1]
        return a[1]
    except TypeError:
        return "NoDeclension"
    
def get_verb_declension(saldo_sense_key):
    try:
        a = get_dec_like(saldo_sense_key)[1]
        return a[0]
    except TypeError:
        return "NoDeclension"
    
def get_like(saldo_sense_key):
    try:
        return get_dec_like(saldo_sense_key)[2]
        
    except TypeError:
        return "NoDeclension"
    
if __name__ == "__main__":
    test = "grön..1"
    a = get_nominal_declension(test)
    # c = get_gender(test) # -> IndexError for adj
    b = get_like(test)
    print(a,b)