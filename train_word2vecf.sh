#!/bin/bash

name=$1
limit=$2
featurizer=$3
conllucolumn=$4

cat > data.tmp

cat data.tmp | grep -P '^[0-9]' | python3 scripts/vocab.py --freq_limit $limit  > $name.vocab

cat data.tmp | python3 scripts/extract_transition_seq.py -v $name.vocab --freq_limit $limit --conllu_column $conllucolumn --featurizer $featurizer > $name.dep.contexts

#zcat /wrk/jmnybl/word2vecf_tmpdir/$lang.dep.contexts | ./big_shuf.sh $lang > /wrk/jmnybl/word2vecf_tmpdir/$lang.dep.contexts.notokens

./count_and_filter -train $name.dep.contexts -cvocab $name.cv -wvocab $name.wv -min-count $limit

./word2vecf -train $name.dep.contexts -wvocab $name.wv -cvocab $name.cv -output $name.bin -size 100 -negative 5 -threads 4 -iters 10 -binary 1

rm -f data.tmp




