# python 3
# collect all unique tag sequences from data + their pos tags and counts

import sys

ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)


def create_vocab():
    features={}
    for line in sys.stdin:
        line=line.strip()
        if not line or line.startswith("#"):
            continue
        cols=line.split("\t")
        if cols[FEAT] not in features:
            features[cols[FEAT]]=(0,[])
        features[cols[FEAT]]=(features[cols[FEAT]][0]+1,features[cols[FEAT]][1])
        if cols[UPOS] not in features[cols[FEAT]][1]:
            features[cols[FEAT]][1].append(cols[UPOS])

    for w,(count,upos) in sorted(features.items(),key=lambda x:x[1][0], reverse=True):
        print("\t".join([w,str(count),",".join(upos)]))


if __name__=="__main__":

    #import argparse
    #parser = argparse.ArgumentParser(description='')

    #parser.add_argument('--conllu_column', type=str, default='FORM', help='Which conllu column is used in input layer, i.e. do we train word, lemma or feature embeddings, options: FORM, LEMMA, UPOS, FEAT')

   
    #args = parser.parse_args()

    create_vocab()
