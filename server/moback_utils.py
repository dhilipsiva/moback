import urllib


def make_query(base_path, param_dict):
    return(base_path + '?' + urllib.urlencode(param_dict))
