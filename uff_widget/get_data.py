import numpy as np
import pyuff

def ds58(uff,uffdict,dict58,drop,dof_in='ref_node'):
    """ds58 Function prepairs data for vizualization from informations
    stored in datasets 58 ralating to chosen data type and dictionary 
    with additional information. First key is dset, which has value 58
    and represent the dataset type. Second key can be dt or df. Both are
    abscissa spaceing. dt is for data type general and time response and
    df is for all other. For frequence response, the mesurment results are
    stored in data for both extremes of point oscillation. For each direction,
    point and each frequence bouth extremes are stored in forth axis of data array

    
    Parameters
    ----------
    uff : UFF class variable
        variable for access to data stored in uff
    uffdict : dictionary
        dictionary wirt all in file existing dataset types as keys
    dict58 : dictionary
        Dictionaray with 
    drop : widget
        some string widget with value from options 'General or Unknown',
        'Time Response', 'Auto Spectrum', 'Cross Spectrum', 'Frequency 
        Response Function'and 'complex eigenvalue second order (velocity)'
    
    Returns
    -------
    data numpy array 
        numpy array with size (three directions,,number of all points, length of mesurment) for time response 
        numpy array with size (three directions,,number of all points, length of mesurment,two extremes) for frequence response
    ditionary
        with keys 'dset'(always value 58) and 'dt' or 'df' regarding to drop.value
    """
    in_names ={'General or Unknown':'0',
              'Time Response':'1',
              'Auto Spectrum':'2',
              'Cross Spectrum':'3',
              'Frequency Response Function':'4',
              'complex eigenvalue second order (velocity)':'6'}
    
    if dof_in=='ref_node':
        node_dir='ref_dir'
    if dof_in=='resp_node':
        node_dir='resp_dir'
   
    d=in_names[drop.value]
    if d == '0' or d == '1': #for time response
        data = np.zeros((3,len(uff.read_sets(uffdict['15'][0])['node_nums']),len(uff.read_sets(dict58[d][0])['num_pts'])))
        dt = uff.read_sets(dict58[d][0])['abscissa_spacing']
        for index in dict58[d]:
            rset = uff.read_sets(index)
            data_i = np.zeros((3,rset['num_pts']))
            direc = np.sign(rset['rsp_dir'])*(np.abs(rset['rsp_dir'])-1)
            node = rset['rsp_node']
            data_i[abs(direc),:] = np.sign(direc)*rset['x']
            data_i=np.matmul(np.transpose(uff.read_sets(uffdict['2420'])['CS_matrices'][int(uff.read_sets(uffdict['15'])['disp_cs'][node])]),data_i)
            data[:,node,:]+=data_i
        return data, {'dset':58, 'dt':dt}

    else:#for freqence response
        data = np.zeros((3,len(uff.read_sets(uffdict['15'][0])['node_nums']),uff.read_sets(dict58[d][0])['num_pts'],2))
        df=uff.read_sets(dict58[d][0])['abscissa_spacing']
        for index in dict58[d]:
            rset = uff.read_sets(index)
            data_i = np.zeros((3,rset['num_pts']))
            direc = np.sign(rset[node_dir])*(np.abs(rset[node_dir])-1)
            node = rset[dof_in]
            data_i[abs(direc),:] = np.sign(direc)*rset['data']
            data_i=np.matmul(np.transpose(uff.read_sets(uffdict['2420'])['CS_matrices'][int(uff.read_sets(uffdict['15'])['disp_cs'][node])]),data_i)
            data[:,node,:,0]+=data_i
            data[:,node,:,1]+=-data_i
        return data, {'dset':58, 'df':df}

def ds55(uff,uffdict,dict55,drop):
    """ds55 Function prepairs data for vizualization from informations
    stored in datasets 55 ralating to chosen data type and dictionary 
    with additional information. First key is dset, which has value 55
    and represent the dataset type. Second key is freq. In second key are
    stored frequencies for which the data for individual points are given.
    Data from datasets is stored in data for both extremes of point oscillation.
    For each direction, point and each frequence bouth extremes are stored in 
    forth axis of data array.

    

    Parameters
    ----------
    uff : UFF class variable
        variable for access to data stored in uff
    uffdict : dictionary
        dictionary wirt all in file existing dataset types as keys
    dict58 : dictionary
        Dictionaray with 
    drop : widget
        some string widget with value from options 'normal mode',
        'complex eigenvalue first order (displacement)', 'frequency 
        response' and 'complex eigenvalue second order (velocity)'.
    
    Returns
    -------
    data numpy array
        numpy array with size (three directions, number of all points, number of frequences, two extremes)
    ditionary
        with keys 'dset'(always value 55) and 'freq'
    """ 

    in_names ={'normal mode':'2',
              'complex eigenvalue first order (displacement)':'3',
              'frequency response':'5',
              'complex eigenvalue second order (velocity)':'7'}

    d=in_names[drop.value]
    data = np.zeros((3,len(uff.read_sets(uffdict['15'][0])['node_nums']),len(dict55[d]),2))
    nfreq=[]
    for i in range(len(dict55[d])):
        rset = uff.read_sets(dict55[d][i])
        data_i = np.zeros((3,len(rset['node_nums'])))
        data_i[0,:] = rset['r1']
        data_i[1,:] = rset['r2']
        data_i[2,:] = rset['r3']
        data[:,rset['node_nums'].astype('int'),i,0] += -data_i
        nfreq.append(rset['freq'])
    for i in range(len(uff.read_sets(uffdict['15'][0])['node_nums'])):
        j=int(uff.read_sets(uffdict['15'][0])['disp_cs'][i])
        data[:,i,:,0] = np.matmul(np.transpose(uff.read_sets(uffdict['2420'])['CS_matrices'][j]),data[:,i,:,0])
    data[:,:,:,1] = -data[:,:,:,0]
    return data, {'dset':55, 'freq':nfreq}

def dinfo55(drop,uff,uffdict,dict55):
    in_names ={'normal mode':'2',
              'complex eigenvalue first order (displacement)':'3',
              'frequency response':'5',
              'complex eigenvalue second order (velocity)':'7'}

    d=in_names[drop.value]
    nfreq=[]
    for i in range(len(dict55[d])):
        rset = uff.read_sets(dict55[d][i])
        nfreq.append(rset['freq'])
    return nfreq

def dinfo58(drop,uff,uffdict,dict58):
    in_names ={'General or Unknown':'0',
              'Time Response':'1',
              'Auto Spectrum':'2',
              'Cross Spectrum':'3',
              'Frequency Response Function':'4',
              'complex eigenvalue second order (velocity)':'6'}
   
    d=in_names[drop.value]    
    return uff.read_sets(dict58[d][0])['abscissa_spacing'],uff.read_sets(dict58[d][0])['num_pts']