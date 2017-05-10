import lwvlib # https://github.com/fginter/wvlib_light
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

def save_txt(words,data,fname):
    """
    save model in binary format
    """

    out=open(fname,"w")

    rows,dims=data.shape
    print("{} {}".format(rows,dims),file=out)
    counter=0

    for i,w in enumerate(words):
        print(w," ".join(("{:6f}".format(x) for x in data[i,:])),file=out)
    out.close()

def main(args):

    print("Reading",args.char_model,"model",file=sys.stderr)
    model=lwvlib.load(args.char_model)

    vocabulary=read_vocab(args.vocab)
    
    # TODO normalize?


    # words: the words themselves
    all_features=[]
    # data: the vector matrix
    data=np.zeros((len(vocabulary),model.vsize),np.float32)
    
    for feature,wcount in vocabulary:
        vector=np.zeros(model.vsize,np.float32)
        norm=0
        postag,feats=feature.split("|",1)
        for feat in feats.split("|"):
            vidx=model.get(postag+"|"+feat)
        if vidx!=None:
            vector=np.add(vector,model.vectors[vidx])
            norm+=1
        if norm==0:
            print("No vector for feature",feature,"with pos tag",postag,file=sys.stderr)
            continue
        vector=np.divide(vector,norm)
        data[len(all_features),:]=vector
        all_features.append(feature)

    # reshape data to len(words)
    data=data[:len(all_features),:]

    print("Original vector model:",len(model.words),model.vsize,file=sys.stderr)
    print("New vector model:",data.shape,file=sys.stderr)
    assert len(all_features)==data.shape[0]
    
    save_txt(all_features,data,args.output)


if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Build word vector model from character ngram vector model.')

    parser.add_argument('-m','--char_model', type=str, help='Trained character based vector model')
    parser.add_argument('-v','--vocab', type=str, help='vocabulary')
    parser.add_argument('-o','--output', type=str, help='Output file name')
   
    args = parser.parse_args()
    main(args)
