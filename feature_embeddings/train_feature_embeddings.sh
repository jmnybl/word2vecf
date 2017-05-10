#!/bin/bash

name=$1
limit=1

# input must be parsed text in conllu format

###cat > data.tmp

###cat data.tmp | grep -P '^[0-9]' | python3 vocab.py --freq_limit $limit  > $name.vocab

###cat data.tmp | python3 extract_transition_seq.py -v $name.vocab --freq_limit $limit > $name.dep.contexts

###cat data.tmp | python3 collect_vocab.py > all_features

####zcat /wrk/jmnybl/word2vecf_tmpdir/$lang.dep.contexts | ./big_shuf.sh $lang > /wrk/jmnybl/word2vecf_tmpdir/$lang.dep.contexts.notokens

###../count_and_filter -train $name.dep.contexts -cvocab $name.cv -wvocab $name.wv -min-count $limit

###../word2vecf -train $name.dep.contexts -wvocab $name.wv -cvocab $name.cv -output $name.vectors -size 20 -negative 5 -threads 1 -iters 10 -binary 0

python3 simulate_fasttext.py -m $name.vectors -v all_features -o $name.final.vectors

#rm -f data.tmp




