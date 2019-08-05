# coding: utf-8
'''
Created on Oct 4, 2018

@author: David
'''
import sqlite3
from ll_config_local import SWESAURUS_DB

conn = sqlite3.connect(SWESAURUS_DB)

def get_synonyms(saldo_sense_key):
    c = conn.cursor()
    c.execute("SELECT * FROM swesaurus WHERE sense_id = ?", (saldo_sense_key,))
    return c.fetchall()

if __name__ == "__main__":
    a = get_synonyms("fil..5")
    print(a)