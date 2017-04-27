# python3
import sys
from collections import Counter

conllu="ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC".split(",")

def create_vocab(args):
    lower=True
    if args.conllu_column!="FORM" and args.conllu_column!="LEMMA": # no need to lowercase
        lower=False
    wc = Counter()
    thr = args.freq_limit
    l = []
    for i,w in enumerate(sys.stdin): # line is one conllu token line
       if i % 1000000 == 0:
          #if i > 10000000: break
          print(i,len(wc),file=sys.stderr)
          wc.update(l)
          l = []
       token=w.strip().split("\t")[conllu.index(args.conllu_column)]
       if lower:
          l.append(token.lower())
       else:
          l.append(token)
    wc.update(l)

    for w,c in sorted([(w,c) for w,c in wc.items() if c >= thr and w != ''],key=lambda x:-x[1]):
       print("\t".join([w.strip(),str(c)]))

if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--freq_limit', type=int, default=10, help='Frequency limit')
    parser.add_argument('--conllu_column', type=str, default='FORM', help='Which conllu column is used in input layer, i.e. do we train word, lemma or feature embeddings, options: FORM, LEMMA, UPOS, FEAT')

   
    args = parser.parse_args()
    create_vocab(args)

