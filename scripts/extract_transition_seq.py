# python 2
# needs also tree.py, code extracted form Turku Dependency Parser, stand-alone code to extract transition sequence from a given tree (and featurize it into word2vecf format)

import codecs
from tree import Token, Tree, Dep, State, Transition, conllu_reader

SHIFT=0
RIGHT=1
LEFT=2
SWAP=3

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
    features=[]
    state=State(sent,syn=False)
    while not state.tree.ready:
        next=transitions[len(state.transitions)]
        if next.move not in state.valid_transitions():
            raise ValueError("Invalid GS Transition")
        features+=create_features(state,next)        
        state.update(next)

    return features

actions=["SHIFT","RIGHT-ARC","LEFT-ARC","SWAP"]

def create_features(s,next):

    if len(s.stack)==0:
        return []

    features=[]
    features.append((s.stack[-1].text,u"stack1_"+actions[next.move]))
    if next.dType!=None:
        features.append((s.stack[-1].text,u"stack1_"+next.dType))
    if len(s.stack)>1:
        features.append((s.stack[-2].text,u"stack2_"+actions[next.move]))
        if next.dType!=None:
            features.append((s.stack[-2].text,u"stack2_"+next.dType))
    return features


def featurize_sent(s):

    transitions=transition_seq(s)
    features=drive_parser(transitions,s)

    return features

def main(inp):

    for s in conllu_reader(inp):
        

        features=featurize_sent(s)
        for w,f in features:
            print w,f
        for t in s:
            print t
        print


if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i','--input_file', type=str, help='Input file')
   # parser.add_argument('--max_sent', type=int, default=0, help='How many sentences to parse from the input? 0 for all.  (default %(default)d)')
   # parser.add_argument('--no_avg', default=False, action="store_true",  help='Do not use the averaged perceptron but the original weight vector (default %(default)s)')
    args = parser.parse_args()
    main(args.input_file)

