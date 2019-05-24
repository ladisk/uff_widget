import numpy as np
import pyuff

def ds58(file,uffdict,dict58,drop):
    in_names ={'General or Unknown':'0',
              'Time Response':'1',
              'Auto Spectrum':'2',
              'Cross Spectrum':'3',
              'Frequency Response Function':'4',
              'complex eigenvalue second order (velocity)':'6'}

    d=in_names[drop.value]
    if d == '0' or d == '1': #for time response
        data = np.zeros((3,len(file.read_sets(uffdict['15'][0])['node_nums']),len(file.read_sets(dict58[d][0])['num_pts'])))
        dt = file.read_sets(dict58[d][0])['abscissa_spacing']
        for index in dict58[d]:
            rset = file.read_sets(index)
            data_i = np.zeros((3,rset['num_pts']))
            direc = np.sign(rset['rsp_dir'])*(np.abs(rset['rsp_dir'])-1)
            node = rset['rsp_node']
            data_i[abs(direc),:] = np.sign(direc)*rset['x']
            data_i=np.matmul(np.transpose(file.read_sets(uffdict['2420'])['CS_matrices'][int(file.read_sets(uffdict['15'])['disp_cs'][node])]),data_i)
            data[:,node,:]+=data_i
        return data, {'dt':dt}

    else:#for freqence response
        data = np.zeros((3,len(file.read_sets(uffdict['15'][0])['node_nums']),len(file.read_sets(dict58[d][0])['num_pts']),2))
        df=file.read_sets(dict58[d][0])['abscissa_spacing']
        for index in dict58[d]:
            rset = file.read_sets(index)
            data_i = np.zeros((3,rset['num_pts']))
            direc = np.sign(rset['ref_dir'])*(np.abs(rset['ref_dir'])-1)
            node = rset['ref_node']
            data_i[abs(direc),:] = np.sign(direc)*rset['x']
            data_i=np.matmul(np.transpose(file.read_sets(uffdict['2420'])['CS_matrices'][int(file.read_sets(uffdict['15'])['disp_cs'][node])]),data_i)
            data[:,node,:,0]+=data_i
            data[:,node,:,1]+=-data_i
        return data, {'dset':58, 'df':df}

def ds55(file,uffdict,dict55,drop):
    in_names ={'normal mode':'2',
              'complex eigenvalue first order (displacement)':'3',
              'frequency response':'5',
              'complex eigenvalue second order (velocity)':'7'}

    d=in_names[drop.value]
    data = np.zeros((3,len(file.read_sets(uffdict['15'][0])['node_nums']),len(dict55[d]),2))
    nfreq=[]
    for i in range(len(dict55[d])):
        rset = file.read_sets(dict55[d][i])
        data_i = np.zeros((3,len(rset['node_nums'])))
        data_i[0,:] = rset['r1']
        data_i[1,:] = rset['r2']
        data_i[2,:] = rset['r3']
        data[:,:,i,0] += -data_i
        nfreq.append(rset['freq'])
    for i in range(len(file.read_sets(uffdict['15'][0])['node_nums'])):
        data[:,i,:,0] = np.matmul(np.transpose(file.read_sets(uffdict['2420'])['CS_matrices'][i]),data[:,i,:,0])
    data[:,:,:,1] = -data[:,:,:,0]
    return data, {'dset':58, 'freq':nfreq}