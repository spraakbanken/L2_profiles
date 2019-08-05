# coding: utf-8
'''
Created on Oct 4, 2018

@author: David
'''
import sqlite3
from ll_config_local import BLINGBRING_DB

conn = sqlite3.connect(BLINGBRING_DB)

def get_by_saldo_sense(saldo_sense_key):
    c = conn.cursor()
    c.execute("SELECT * FROM blingbring WHERE saldo_sense = ?", (saldo_sense_key,))
    return c.fetchall()


if __name__ == "__main__":
    a = get_by_saldo_sense("omdöme..1")
    print(a)