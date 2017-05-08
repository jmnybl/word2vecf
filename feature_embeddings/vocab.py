# python3
import sys
from collections import Counter

ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)


def create_vocab(args):
    wc = Counter()
    thr = args.freq_limit
    l = []
    for i,w in enumerate(sys.stdin): # line is one conllu token line
       if i % 1000000 == 0:
          print(i,len(wc),file=sys.stderr)
          wc.update(l)
          l = []
       cols=w.strip().split("\t")
       for feat in cols[FEAT].split("|"):
          l.append("|".join([cols[UPOS],feat]))
    wc.update(l)

    for w,c in sorted([(w,c) for w,c in wc.items() if c >= thr and w != ''],key=lambda x:-x[1]):
       print("\t".join([w.strip(),str(c)]))

if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--freq_limit', type=int, default=10, help='Frequency limit')

   
    args = parser.parse_args()

    create_vocab(args)

