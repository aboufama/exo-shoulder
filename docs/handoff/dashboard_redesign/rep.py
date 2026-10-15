import sys
class R:
    def __init__(self, p): self.p = p; self.s = open(p).read()
    def __call__(self, a, b, n=1):
        for cand in (a, a.replace('’', "'"), a.replace("'", '’')):
            c = self.s.count(cand)
            if c == n: self.s = self.s.replace(cand, b); return
        raise AssertionError((self.s.count(a), a[:100]))
    def save(self): open(self.p, 'w').write(self.s)
