# python3
# extract dependency pairs from a conll file.
# assumes google universal-treebank annotation scheme.
# zcat treebank.gz |python extract_deps.py |gzip - > deps.gz
import sys
from collections import defaultdict
from vocab import char_ngrams

lower=True

ID,FORM,LEMMA,UPOS,CPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)

def read_conll(fh):
   root = (0,'*root*',-1,'rroot','proot')
   tokens = [root]
   for line in fh:
      if lower: line = line.lower()
      line=line.strip()
      if not line:
         if len(tokens)>1: yield tokens
         tokens = [root]
      else:
         tok=line.split("\t")
         try:
            tokens.append((int(tok[ID]),tok[FORM],int(tok[HEAD]),tok[DEPREL],tok[UPOS],tok[FEAT]))
         except:
            pass # these are usually multiword tokens without head
            #print >> sys.stderr,"BROKEN CONLLU",tok,repr(line.strip())
            #raise
   if len(tokens) > 1:
      yield tokens

def read_vocab(fh,THR):
   v = {}
   for line in fh:
      if lower: line = line.lower()
      line = line.strip().split()
      if len(line) != 2: continue
      if int(line[1]) >= THR:
         v[line[0]] = int(line[1])
   full_vocab=set(v.keys())
   words=sorted([(w,c) for w,c in v.items() if c >= THR and w != '' and w.startswith('char_')==False],key=lambda x:-x[1])
   most_common_words=set()
   for w,c in words[:round(len(words)/3)]:
      most_common_words.add(w)
   return full_vocab,most_common_words,len(words)


def extract_deps(vocab,most_common_words):
    for i,sent in enumerate(read_conll(sys.stdin)):
       if i % 100000 == 0:
            print(i,file=sys.stderr)
       if args.max_sent>0 and i>args.max_sent:
            break 
       #d = defaultdict(list)
       try:
          for tok in sent[1:]: # this skips root
             par = sent[tok[2]]
             m = tok[1] # token.form
             #if m not in vocab: continue
             rel = tok[3]
             upos = tok[4]
             feat = tok[5]
             if rel == 'adpmod': continue # this is the prep. we'll get there (or the PP is crappy)
             if rel == 'adpobj' and par[0] != 0:
                ppar = sent[par[2]]
                rel = "%s:%s" % (par[3],par[1])
                h = ppar[1]
             else:
                h = par[1] # parent token form
             #if h not in vocab: continue

             # parent char ngrams
             if h!="*root*":
                if h in most_common_words:
                    h_ngrams=[h]
                else:
                    h_ngrams=char_ngrams(h)
                for ngram in h_ngrams:
                    if ngram not in vocab:
                        continue
                    print(ngram,"O_"+rel)

             # token ngrams
             if m == "*root*":
                continue
             if m in most_common_words:
                m_ngrams=[m]
             else:
                m_ngrams=char_ngrams(m)
             for ngram in m_ngrams:
                if ngram not in vocab:
                    continue
                print(ngram,"I_"+rel)
                print(ngram,upos) # UPOS of the token
                if feat=="_":
                    print(ngram,"nofeat")
                else:
                    for fe in feat.split("|"):
                        print(ngram,fe)
       except:
          print("BROKEN CONLLU",file=sys.stderr)
          #d[h].append("_".join((rel,m)))
          #d[m].append("I_".join((rel,h)))
       #for w,cs in d.iteritems():
       #   print w," ".join(cs)

def main(args):

    vocab,most_common_words,total_words=read_vocab(open(args.vocab_file,"rt",encoding="utf-8"),args.freq_limit)

    print("full vocab:",len(vocab),file=sys.stderr) 
    print("most common words:",len(most_common_words),file=sys.stderr)   
    print("total words:",total_words,file=sys.stderr) 
    extract_deps(vocab,most_common_words)

if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='')

#    parser.add_argument('-i','--input_file', type=str, help='Input file')
    parser.add_argument('-v','--vocab_file', type=str, help='Vocabulary file')
    parser.add_argument('--freq_limit', type=int, default=10, help='Frequency limit')
    parser.add_argument('--max_sent', type=int, default=0, help='How many sentences to read, zero for all, default=0')
   
    args = parser.parse_args()
    main(args)


