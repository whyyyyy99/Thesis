import re

flags = kwargs.get("flags", 0)
case = kwargs.get("case", True)
regex = kwargs.get("regex", True)

pattern = pat if regex else re.escape(pat)
if not case:
    flags |= re.IGNORECASE

compiled = re.compile(pattern, flags)
return [c for c in data.columns if compiled.search(c)]
