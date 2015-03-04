def flatten(lst):
    return sum(([l] if not isinstance(l, list) else flatten(l)
                for l in lst), [])
