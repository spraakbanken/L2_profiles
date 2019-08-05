# coding: utf-8
'''
Created on Oct 4, 2018

@author: David
'''
import sqlite3
from ll_config_local import PAROLE_DB

conn = sqlite3.connect(PAROLE_DB)


def get_generic_by_parole_id(field, parole_id):
    c = conn.cursor()
    q = "SELECT {} FROM parole WHERE parole_id = ?".format(field)
    c.execute(q, (parole_id,))
    return c.fetchall()

def get_generic_by_wordform_pos(field, wordform, pos=None):
    c = conn.cursor()
    q = "SELECT {} FROM parole WHERE writtenform = ?".format(field)
    if pos is not None:
        q += " and pos = ?"
        c.execute(q, (wordform, pos))
        return c.fetchall()
    c.execute(q, (wordform,))
    return c.fetchall()

def get_generic_by_saldo_sense(field, saldo_sense_key):
    c = conn.cursor()
    q = "SELECT {} FROM parole WHERE saldo_sense = ?".format(field)
    c.execute(q, (saldo_sense_key,))
    
    return c.fetchall()

def get_valency(saldo_sense_key):
    c = conn.cursor()
    c.execute("SELECT valency FROM parole WHERE saldo_sense = ?", (saldo_sense_key,))
    return c.fetchall()

if __name__ == "__main__":
    a = get_valency("mosaik..1")
    
    c = get_generic_by_wordform_pos("*", "vara", "vb")
    d = get_generic_by_saldo_sense("*", "None")
    b = get_generic_by_parole_id("*", "US40502_40629")
    print(a,b,c,d)