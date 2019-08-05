# coding: utf-8
'''
Created on Oct 3, 2018

@author: David
'''
import sqlite3
from ll_config_local import SIMPLE_DB

conn = sqlite3.connect(SIMPLE_DB)
c = conn.cursor()

def get_by_saldo_sense(saldo_sense_key):
    c.execute("SELECT * FROM simple WHERE saldo_sense=?", (saldo_sense_key,))
    return c.fetchall()

def get_by_form_pos(form, pos=None):
    q = "SELECT * FROM simple WHERE form = ?"
    if pos is not None:
        q += " and pos=?"
        c.execute(q, (form, pos))
        return c.fetchall()
    c.execute(q, (form,))
    return c.fetchall()

def get_try_saldo_first(saldo_sense_key, form, pos):
    a = get_by_saldo_sense(saldo_sense_key)
    if len(a) == 0:
        return get_by_form_pos(form, pos)
    return a


if __name__ == "__main__":
    a = get_try_saldo_first("framlägga..1", "framlägger", "vb")
    b = get_by_saldo_sense("fresta..2")
    print(b)