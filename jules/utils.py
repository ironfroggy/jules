import os

from straight.plugin import load


def ensure_path(path):
    path_parts = os.path.split(path)
    for i in range(len(path_parts)):
        subpath = os.path.join(*path_parts[: i + 1 ])
        if subpath and not os.path.exists(subpath):
            os.mkdir(subpath)

def filter_bundles(from_bundles, order_key=None, order='asc', limit=None, **kwargs):
    if order == 'asc':
        reverse = False
    elif order == 'desc':
        reverse = True
    else:
        raise ValueError("Order can only be asc or desc")
    bundles = []
    for bundle in from_bundles:
        if order_key is not None:
            if order_key not in bundle.meta:
                continue
        ok = True
        for k, v in kwargs.items():
            if k == 'key':
                if bundle.key != v:
                    ok = False
                    break
            else:
                if k not in bundle.meta:
                    ok = False
                    break
                if bundle.meta[k] != v:
                    ok = False
                    break
        if ok:
            bundles.append(bundle)
    if order_key is not None:
        bundles.sort(key=lambda b: b.meta[order_key], reverse=reverse)
    if limit is not None:
        bundles = bundles[:limit]
    return bundles
