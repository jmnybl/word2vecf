# python 2
# needs also tree.py, code extracted form Turku Dependency Parser, stand-alone code to extract transition sequence from a given tree (and featurize it into word2vecf format)

import gzip
from tree import Token, Tree, Dep, State, Transition, conllu_reader
import sys

SHIFT=0
RIGHT=1
LEFT=2
SWAP=3

lower=True

def extract_transitions(gs_tree,sent):
    state=State(sent,syn=False)
    while not state.tree.ready:
        if len(state.queue)==0 and len(state.stack)==2: # only final ROOT arc needed (it's not part of a tree)
            move,=state.valid_transitions() # this is used to decide whether we need LEFT or RIGHT
            assert (move==RIGHT or move==LEFT)
            trans=Transition(move,u"ROOT")
            state.update(trans)
            continue
        if len(state.stack)>1:
            move,dType=extract_dep(state,gs_tree)
            if move is not None:
                trans=Transition(move,dType)
                if trans.move not in state.valid_transitions():
                    raise ValueError("Invalid transition:",trans.move)
                state.update(trans)
                continue
        # cannot draw arc
        if (len(state.stack)>1) and (gs_tree.projective_order is not None) and (state.stack[-2].index<state.stack[-1].index) and (gs_tree.is_proj(state.stack[-2],state.stack[-1])): # SWAP
                trans=Transition(SWAP,None)
        else: # SHIFT
            trans=Transition(SHIFT,None)
        if trans.move not in state.valid_transitions():
            raise ValueError("Invalid transition:",trans.move)
        state.update(trans)
    return state.transitions
            
def extract_dep(state,gs_tree):
    first,sec=state.stack[-1],state.stack[-2]
    t=gs_tree.has_dep(first,sec)
    if (t is not None) and subtree_ready(state,sec,gs_tree):
        return LEFT,t
    t=gs_tree.has_dep(sec,first)
    if (t is not None) and subtree_ready(state,first,gs_tree):
        return RIGHT,t
    return None,None      

def subtree_ready(state,tok,gs_tree):
    if len(gs_tree.childs[tok])==0 and len(state.tree.childs[tok])==0: return True
    elif gs_tree.childs[tok]!=state.tree.childs[tok]: return False
    else:
        for child in gs_tree.childs[tok]: return subtree_ready(state,child,gs_tree)


def transition_seq(sent):

    tree=Tree.new_from_conll(conll=sent,syn=True,conll_format=u"conllu")

    non_projs=tree.is_nonprojective()
    if len(non_projs)>0:
        tree.define_projective_order(non_projs)
    transitions=extract_transitions(tree,sent)
    return transitions


def drive_parser(transitions,sent):
    """ Sent is a list of conll lines."""
    state=State(sent,syn=False)
    while not state.tree.ready:
        next=transitions[len(state.transitions)]
        if next.move not in state.valid_transitions():
            raise ValueError("Invalid GS Transition")
        yield state, next       
        state.update(next)


actions=["SHIFT","RIGHT-ARC","LEFT-ARC","SWAP"]

def next_action(s,next):
    # predict where the word is combined to next action

    if len(s.stack)==0:
        return []

    features=[]
    features.append((s.stack[-1].text,(u"stack1_"+actions[next.move],None)))
    if next.dType!=None:
        features.append((s.stack[-1].text,(u"stack1_"+next.dType,None)))
    if len(s.stack)>1:
        features.append((s.stack[-2].text,(u"stack2_"+actions[next.move],None)))
        if next.dType!=None:
            features.append((s.stack[-2].text,(u"stack2_"+next.dType,None)))
    return features

def full_context_with_words(s,next):
    # predict where the word is and all its context words

    features=[]
    context_words=[]
    # queue
    for i in range(min(2,len(s.queue))):
        features.append((s.queue[i].text,("queue"+str(i),None)))
        context_words.append(s.queue[i].text)
    #stack
    for i in range(-1,max(-2,len(s.stack)*-1)-1,-1):
        features.append((s.stack[i].text,(u"stack"+str(i),None)))
        context_words.append(s.stack[i].text)

    # all pairs of context words
    for i in range(len(context_words)):
        for j in range(len(context_words)):
            if i==j:
                continue
            features.append((context_words[i],("",context_words[j])))

    
    return features


def featurize_sent(s,my_featurizer):
    # receives sentence and featurizer function

    transitions=transition_seq(s)
    features=[]
    for state,next in drive_parser(transitions,s):
        features+=my_featurizer(state,next)

    return features



def read_vocab(fh,THR):
   # function from the original word2vecf scripts/extract_deps.py
   global lower
   v = {}
   for line in fh:
      if lower: line = line.lower()
      line = line.strip().split()
      if len(line) != 2: continue
      if int(line[1]) >= THR:
         v[line[0]] = int(line[1])
   return v

def main(inp,vocab_file,freq_limit,my_featurizer):
    global lower

    vocab = set(read_vocab(open(vocab_file,"rt",encoding="utf-8"),freq_limit).keys())

    for i,s in enumerate(conllu_reader(inp,lower)):
        if i % 100000 == 0:
            print(i,file=sys.stderr)        

        features=featurize_sent(s,my_featurizer)
        for w1,(f,w2) in features:
            if w1 not in vocab:
                continue
            if w2!=None and w2 not in vocab:
                continue
            p=f+w2 if w2!=None else f
            print(w1,p)


if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i','--input_file', type=str, help='Input file')
    parser.add_argument('-v','--vocab_file', type=str, help='Vocabulary file')
    parser.add_argument('--freq_limit', type=int, default=10, help='Frequency limit')
    parser.add_argument('--featurizer', type=str, default='full_context_with_words', help='Featurizer function to use, options: full_context_with_words, next_action')

    featurizers={"full_context_with_words":full_context_with_words, "next_action":next_action}
   
    args = parser.parse_args()
    main(args.input_file,args.vocab_file,args.freq_limit,featurizers[args.featurizer])

