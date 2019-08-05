'''
Created on Feb 19, 2018

@author: David
'''
import codecs

class Saldo():
    
    def __init__(self, saldofile, sep="\t"):
        self.saldo_dict = dict()
        
        with codecs.open(saldofile, "r", encoding="utf-8") as f:
            for l in f:
                if not l.strip():
                    continue
                el = l.rstrip().split(sep)
                sense = el.pop(0)
                self.saldo_dict[sense] = el
                
    def lookup(self, sense):
        if sense in self.saldo_dict.keys():
            return self.saldo_dict[sense]
        return [None]
    
    def lookup_primary(self, sense):
        return self.lookup_at(sense, 0)
    
    def lookup_at(self, sense, index):
        return self.lookup(sense)[index]
        