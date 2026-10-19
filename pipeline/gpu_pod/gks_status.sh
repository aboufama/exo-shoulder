V=/runpod-volume/exo-farm; R=$V/gpuk/out/gks1; date -u; cat $R/restart.txt 2>/dev/null; ls $R; ls $R/override/tools
for s in gpuk1 gpuk2 gpuk3 gpuk4; do echo "== $s queue: $(ls $V/$s/queue 2>/dev/null) out: $(ls $V/$s/out 2>/dev/null | tr '\n' ' ')"; done
for f in $R/log_*.txt; do echo "== $f"; grep -v '^+' $f | grep -v '^  ' | grep -v "^\s*$" | tail -10 | cut -c1-260; done
for f in $R/sobol_*.jsonl $R/cma_*.jsonl; do [ -f $f ] && echo "$f rows $(wc -l < $f) cuda $(grep -c CUDA $f) err $(grep -c '"err"' $f)"; done
ls $R/claims | wc -l; ls $R/claims | tail -5
