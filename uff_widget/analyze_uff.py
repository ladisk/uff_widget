import numpy as numpy
import pyuff

def cleanup(dic):
    re_keys = []
    for key in dic.keys():
        if dic[key] == []:
            re_keys.append(key)
    for key in re_keys:
        del dic[key]
    return dic

def get_points(path):
    file=pyuff.UFF(path)
    sets = file.get_set_types()
    sup_sets = file.get_supported_sets()

    uffdict = {}
    for a in sup_sets:
        index = []
        for i in range(len(sets)):
            if str(int(sets[i])) == a:
                index.append(i)
        uffdict[a] = index
    
    nodes55 = {'2':[], '3':[], '5':[], '7':[]}
    nodes58 = {'0':[], '1':[], '2':[], '3':[], '4':[], '6':[]}
    for i in uffdict['58']:
        node = file.read_sets(i)['ref_node'] #TODO for multiple response analysis
        f_type = file.read_sets(i)['func_type']
        if set([node]).issubset(nodes58[str(f_type)])==False:
            if set([float(node)]).issubset(file.read_sets(uffdict['15'])['node_nums']):
                nodes58[str(f_type)].append(node)
    for i in uffdict['55']:
        node = file.read_sets(i)['node_nums'] #TODO for multiple response analysis
        d_type = file.read_sets(i)['data_type']
        for n in node:
            if set([n]).issubset(nodes55[str(d_type)])==False:
                if set([float(n)]).issubset(file.read_sets(uffdict['15'])['node_nums']):
                    nodes55[str(d_type)].append(int(n))
    return {'55':cleanup(nodes55),'58':cleanup(nodes58)}
