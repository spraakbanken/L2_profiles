# coding: utf-8
'''
Created on 9 Jun 2019

@author: David
'''
#from global_linker import rlink
import codecs
import re

starlex_flag = "svalex" # svalex or swellex

# TODO PATH TO senstarlex
senstarlex_file = "/senstarlex_v4_clean_unique_saldo.csv"
# TODO PATH TO OUTFILES
outfile1 = "/senstarlex_v4_clean_unique_saldo_max3examples_{}.csv"
outfile2 = "/senstarlex_v4_clean_unique_saldo_no_examples_{}.csv"  # no examples

senstarlex = [x.rstrip().split("\t") for x in codecs.open(senstarlex_file, "r", encoding="utf-8")]
lexical_pos = ["NN", "VB", "AB", "JJ"]
counter = 0
out_format_template = "{}\t{}\t{}\t{}\t{}"

agg = []
no_sentence = []

if starlex_flag == "svalex":
    from coctaill_mixer import get_example_sentences
elif starlex_flag == "swellex":
    from swell_mixer import get_example_sentences
    
for entry in senstarlex:
    counter += 1
    if counter%1000==0:
        print("{}/{}".format(counter, len(senstarlex)))
    lemgram, sense, pos, prim, sec, cefr = entry
    m = re.search(r"^.+?\.\.[1-9]+?$", sense)
        
    if m is None:
        continue
    if pos in lexical_pos or "_" in lemgram:
#         vals = rlink(sense)
        m = re.search(r"..m", pos)
        spos = ""
        if m is not None:
            spos = pos[:2].upper()    
        examples = get_example_sentences(sense, pos, cefr, 3)
        if examples is None or len(examples) == 0:
            #print("No example for {} {} {}".format(sense, pos, cefr))
            if spos != "":
                if spos != pos:
                    examples = get_example_sentences(sense, spos, cefr, 3)
            if examples is None or len(examples) == 0:
                no_sentence.append("{}\t{}\t".format(lemgram, cefr))
                examples = ["None"]
        out_format_template_ex = out_format_template.format(lemgram, sense, pos, "example", "§".join(examples))
        agg.append(out_format_template_ex)
        out_format_template_ex2 = out_format_template.format(lemgram, sense, pos, "example_level", cefr)
        agg.append(out_format_template_ex2)
        
                        
out = codecs.open(outfile1.format(starlex_flag), "w", encoding="utf-8")
out.write("\n".join(agg))
out.close()
out2 = codecs.open(outfile2.format(starlex_flag), "w", encoding="utf-8")
out2.write("\n".join(no_sentence))
out2.close()

print("Done")