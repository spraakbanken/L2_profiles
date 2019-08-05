# coding: utf-8
'''
Created on Oct 3, 2018

@author: David
'''
import sqlite3
from ll_config_local import LEXIN_DB

conn = sqlite3.connect(LEXIN_DB)



def get_generic(field, form, pos=None):
    c = conn.cursor()
    q = "SELECT {} FROM lexin WHERE".format(field)
    q += " form = ?"
    if pos is not None:
        q += " and pos = ?"
        c.execute(q, (form, pos))
        return c.fetchall()
    c.execute(q, (form,))
    return c.fetchall()

def get_pronunciation(form, pos=None):
    return get_generic("pronunciation", form, pos)

def get_inflection(form, pos=None):
    return get_generic("inflection", form, pos)

def get_pos(form):
    return get_generic("pos", form)

def get_definition(form, pos=None):
    return get_generic("definition", form, pos)

def get_usage(form, pos=None):
    return get_generic("usage", form, pos)

def get_comment(form, pos=None):
    return get_generic("comment", form, pos)

def get_valency(form, pos=None):
    return get_generic("valency", form, pos)

def get_grammat_comm(form, pos=None):
    return get_generic("grammat_comm", form, pos)

def get_definition_comm(form, pos=None):
    return get_generic("def_comm", form, pos)

def get_examples(form, pos=None):
    return get_generic("examples", form, pos)

def get_idioms(form, pos=None):
    return get_generic("idioms", form, pos)

def get_compounds(form, pos=None):
    return get_generic("compounds", form, pos)

def get_entry(form, pos=None):
    return get_generic("*", form, pos)

if __name__ == "__main__":
    print("\n".join([str(x) for x in get_examples("god")]))