import os

def find_base(p, bases):
    for base_name, base_path in bases.items():
        r = os.path.relpath(p, base_path)
        if r and (r == '.' or r[0] != '.'):
            return base_name, r
    return None

