# python3
import sys
from collections import Counter

lower=True
wc = Counter()
thr = int(sys.argv[1])
l = []
for i,w in enumerate(sys.stdin):
   if i % 1000000 == 0:
      #if i > 10000000: break
      print(i,len(wc),file=sys.stderr)
      wc.update(l)
      l = []
   if lower:
      l.append(w.lower())
   else:
      l.append(w)
wc.update(l)

for w,c in sorted([(w,c) for w,c in wc.items() if c >= thr and w != ''],key=lambda x:-x[1]):
   print("\t".join([w.strip(),str(c)]))

