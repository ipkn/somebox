import os
from somebox.common.pathtool import find_base

bases = {'share':'share', 'othername':'/begin'}

def test_path_extraction():
    for p, result in [
            ('abc', None),
            ('share/def', 'share'),
            ('/begin/end', 'othername'),
            ]:
        base = find_base(p, bases)
        assert base is None and result is None or base is not None and base[0] == result

