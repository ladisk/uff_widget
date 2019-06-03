import pyuff

def cleanup(dic):
    """cleanup deletes all empty keys in input dictionary
    
    Parameters
    ----------
    dic : dictionary
        arbitrary python dictionary
    
    Returns
    -------
    dictionary
        input dictionary without empty keys
    """
    re_keys = []
    for key in dic.keys():
        if dic[key] == []:
            re_keys.append(key)
    for key in re_keys:
        del dic[key]
    return dic

def analyze(path):
    """analyze 
    Reads whole uff on input path. Indices of datasets are sorted
    by dataset type and by stored data type in data sets 58 and 55.
    Defined are indices of points with data realating to the array
    of points from dataset 15.
    
    Parameters
    ----------
    path : string
        path to a UFF to be analysed
    
    Returns
    -------
    file: UFF class variable
    uffdict: dictionary
        dictionary wirt all in file existing dataset types as keys
        and indices of datasets sorted by type into belonging key
    dictionary
        dictionary with dictionaries for dataset type 55 and 58 with
        nodes indices
    dictionary
        dictionary with dictionar for dataset type 55 and 58 with
        dataset indices by stored data type
    """
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
    dict58 = {'0':[], '1':[], '2':[], '3':[], '4':[], '6':[]}
    dict55 = {'2':[], '3':[], '5':[], '7':[]}
    keys_58 = ['0', '1', '2', '3', '4', '6']
    keys_55 = ['2', '3', '5', '7']
    for i in uffdict['58']:
        node = file.read_sets(i)['ref_node'] #lahko bi bil tudi resp_node, če bi bil rezultati določeni v točkah odziva
        f_type = file.read_sets(i)['func_type']
        if set(str(f_type)).issubset(set(keys_58)):
            dict58[str(f_type)].append(i)
        if set([node]).issubset(nodes58[str(f_type)])==False:
            if set([float(node)]).issubset(file.read_sets(uffdict['15'])['node_nums']):
                nodes58[str(f_type)].append(node)
    for i in uffdict['55']:
        node = file.read_sets(i)['node_nums'] #lahko bi bil tudi resp_node, če bi bil rezultati določeni v točkah odziva
        d_type = file.read_sets(i)['data_type']
        if set(str(d_type)).issubset(set(keys_55)):
            dict55[str(d_type)].append(i)
        for n in node:
            if set([n]).issubset(nodes55[str(d_type)])==False:
                if set([float(n)]).issubset(file.read_sets(uffdict['15'])['node_nums']):
                    nodes55[str(d_type)].append(int(n))
    return file,uffdict,{'55':cleanup(nodes55),'58':cleanup(nodes58)},{'55':cleanup(dict55),'58':cleanup(dict58)}

def get_info(file,uffdict,nodes):
    """get_info prints out name and description of model stored in dataset 151
    
    Parameters
    ----------
    file : UFF class variable
        variable for access to data stored in uff
    uffdict : dictionary
        dictionary wirt all in file existing dataset types as keys
    nodes : dictionary
        dictionary with dictionaries for dataset type 55 and 58 with
        nodes indices
    """
    names55 ={'2': 'normal mode',
              '3': 'complex eigenvalue first order (displacement)',
              '5': 'frequency response',
              '7': 'complex eigenvalue second order (velocity)'}
    names58 ={'0': 'General or Unknown',
              '1': 'Time Response',
              '2': 'Auto Spectrum',
              '3': 'Cross Spectrum',
              '4': 'Frequency Response Function',
              '6': 'complex eigenvalue second order (velocity)'}
    for i in uffdict['151']:
        print('Name: %s \nDescription: %s'%(file.read_sets(i)['model_name'],file.read_sets(i)['description']))
    for i in range(len(uffdict['15'])):
        print('In %i. dataset15 is data for %i points'%(i+1,len(file.read_sets(uffdict['15'][i])['node_nums'])))
    print('In datasets 55 are data for:')
    for key in nodes['55'].keys():    
        print('                             %s in %i points'%(names55[key],len(nodes['55'][key])))
    print('In datasets 58 are data for:')
    for key in nodes['58'].keys():    
        print('                             %s in %i points'%(names58[key],len(nodes['58'][key])))