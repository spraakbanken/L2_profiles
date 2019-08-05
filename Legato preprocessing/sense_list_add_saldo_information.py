'''
Created on Feb 19, 2018

@author: David
'''
import codecs
from SaldoInMemory import Saldo

# TODO PATH TO sense list
sense_list = "/senstarlex_v4_clean_unique.csv"
# TODO PATH TO OUTFILE
outfile = "/senstarlex_v4_clean_unique_saldo.csv"
# TODO PATH TO SALDO
sim_path = "/saldo_2.3/saldo_2.3/saldo20v03.txt"

out = codecs.open(outfile, "w", encoding="utf-8")

saldo = Saldo(sim_path)

with codecs.open(sense_list, "r", encoding="utf-8") as f:
    for l in f:
        if not l.strip():
            continue
        lemgram, pos, sense, cefr = l.rstrip().split("\t")
        primary = saldo.lookup_primary(sense)
        try:
            secondary = saldo.lookup_at(sense, 1)
        except IndexError:
            secondary = None
        out.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(lemgram, sense, pos, primary, secondary, cefr))
        
out.close()