import lwvlib # https://github.com/fginter/wvlib_light
from vocab import char_ngrams
import numpy as np
import sys
import struct


def read_vocab(vocab_file):
    vocab=[]
    for line in open(vocab_file,"rt",encoding="utf-8"):
        line=line.strip()
        assert len(line.split("\t"))==2
        vocab.append(line.split("\t"))
    return vocab

def save_bin(words,data,fname):
    """
    save model in binary format
    """

    out=open(fname,"wb")

    rows,dims=data.shape
    out.write("{} {}\n".format(rows,dims).encode("utf-8"))
    counter=0

    for i,w in enumerate(words):
        out.write(w.encode("utf-8"))
        out.write(" ".encode("utf-8"))
        out.write(struct.pack("{}f".format(dims),*data[i,:]))
        counter+=1
            
    out.close()
    print("Model saved to",fname,file=sys.stderr)

def main(args):

    model=lwvlib.load(args.char_model)

    vocabulary=read_vocab(args.vocab)
    
    # TODO normalize?


    # words: the words themselves
    words=[]
    # data: the vector matrix
    data=np.zeros((len(vocabulary),model.vsize),np.float32)
    
    for w,wcount in vocabulary:
        if args.threshold!=0 and len(words)<args.threshold:
            # do not use character ngrams
            vidx=model.get(w)
            if vidx!=None:
                data[len(words),:]=model.vectors[vidx]
                words.append(w)
                continue
        # use also ngrams, or word not found in vector model
        ngrams=char_ngrams(w)
        assert len(ngrams)>0
        vector=np.zeros(model.vsize,np.float32)
        norm=0
        for ngram in ngrams:
            vidx=model.get(ngram)
            if vidx!=None:
                vector=np.add(vector,model.vectors[vidx])
                norm+=1
        if norm==0:
            print("No vector for word",w,file=sys.stderr)
            continue
        vector=np.divide(vector,norm)
        data[len(words),:]=vector
        words.append(w)

    # reshape data to len(words)
    data=data[:len(words),:]

    print("Original vector model:",len(model.words),model.vsize,file=sys.stderr)
    print("New vector model:",data.shape,file=sys.stderr)
    assert len(words)==data.shape[0]
    
    save_bin(words,data,args.output)


if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Build word vector model from character ngram vector model.')

    parser.add_argument('-m','--char_model', type=str, help='Trained character based vector model')
    parser.add_argument('-v','--vocab', type=str, help='vocabulary')
    parser.add_argument('-o','--output', type=str, help='Output file name')
    parser.add_argument('--threshold', type=int, default=0, help='How many most frequent wors are using just word embeddings (not average of word + character ngram embeddings)? Default: zero')
   
    args = parser.parse_args()
    main(args)
