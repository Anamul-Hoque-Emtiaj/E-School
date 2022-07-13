from logging.config import valid_ident


def multiset(d, keys, values):
    for k, v in zip(keys, values):
        d[k] = v

def multiget(d, keys):
    return [d[key] for key in keys]

def multidel(d, keys):
    for key in keys:
        del d[key]