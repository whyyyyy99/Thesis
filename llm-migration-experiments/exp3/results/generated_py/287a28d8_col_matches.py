import re

case = kwargs.get("case", True)
flags = kwargs.get("flags", 0)
regex = kwargs.get("regex", True)

if not case:
    flags |= re.IGNORECASE

if regex:
    pattern = re.compile(pat, flags)
    return [c for c in data.columns if pattern.search(c) is not None]
else:
    if case:
        return [c for c in data.columns if pat in c]
    pat_l = pat.lower()
    return [c for c in data.columns if pat_l in c.lower()]
