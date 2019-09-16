import numpy as np
import matplotlib.pyplot as plt
import pyuff
import ipyvolume as ipv
import ipywidgets as widgets
from IPython.display import display
import warnings
warnings.filterwarnings('ignore')

__version__ = '0.3'

class widgetuff:
    """ 
    Manage to read and in jupyter notebook visualize data from UFF. It can extract
    some metadata about in UFF stored geometry of mesured structure, mesurments and 
    data analysis. Wiht help of extracted meta data it plots results of mesurments
    and visualize structure geomety in 3D and it vibrations depending on chosen
    freguence. For 3D visualization si used ipyvolume and for constructing user
    interface outputs is used ipywidgets.
    
    """

    def __init__(self,path,dof_in='ref_node'):
        """
        Initalize object of class widgetuff
        
        Parameters
        ----------
        path : str
            path to specific UFF on local machine with data of structure gometry, 
            results of modal testing mesurments and modal analysis
        dof_in : str, optional
            defines if ther are DOFs in response nodes (value of parameter must be 
            set on 'dsp_node') or if ther are DOFs in reference nodes (value of 
            prameter must be set on 'ref_node'), by default 'ref_node'
        
        Attributes
        ----------
        path : str
            stores path parameter
        uff : object of class UFF
            object for access to data stored in UFF on in parameters defined path
        dof_in : str
            stored value of dof_in parameter
        """
        self.path = path
        self.uff = pyuff.UFF(path)
        self.dof_in = dof_in

    def read_uff(self):
        """raed_uff 
        Reads whole uff on input path. Indices of datasets are sorted
        by dataset type and by stored data type in data sets 58 and 55.
        Defined are indices of points with data realating to the array
        of points from dataset 15. Prepares for next metodes aquired 
        atributes

        Attributes
        ----------
        uffdict: dictionary
            dictionary wirt all in file existing dataset types as keys
            and indices of datasets sorted by type into belonging key
        ref_nodes : list
            list of indices of points that are reference nodes
        rsp_nodes : list
            list of indices of points that are response nodes
        nodes : dictionary
            dictionary with dictionaries for dataset type 55 and 58 with
            nodes indices
        indices : dictionary
            dictionary with dictionar for dataset type 55 and 58 with
            dataset indices by stored data type
        """
        
        sets = self.uff.get_set_types()
        sup_sets = self.uff.get_supported_sets()

        self.uffdict = {}
        for a in sup_sets:
            index = []
            for i in range(len(sets)):
                if str(int(sets[i])) == a:
                    index.append(i)
            self.uffdict[a] = index

        nodes55 = {'2':[], '3':[], '5':[], '7':[]}
        nodes58 = {'0':[], '1':[], '2':[], '3':[], '4':[], '6':[]}
        self.ref_nodes = {}
        self.rsp_nodes = {}
        dict58 = {'0':[], '1':[], '2':[], '3':[], '4':[], '6':[]}
        dict55 = {'2':[], '3':[], '5':[], '7':[]}
        keys_58 = ['0', '1', '2', '3', '4', '6']
        keys_55 = ['2', '3', '5', '7']

        for i in self.uffdict['58']:
            node = self.uff.read_sets(i)[self.dof_in]
            ref_node = self.uff.read_sets(i)['ref_node']
            rsp_node = self.uff.read_sets(i)['rsp_node']
            f_type = self.uff.read_sets(i)['func_type']
            if set(str(f_type)).issubset(set(keys_58)):
                dict58[str(f_type)].append(i)
            if set([node]).issubset(nodes58[str(f_type)])==False:
                if set([float(node)]).issubset(self.uff.read_sets(self.uffdict['15'])['node_nums']):
                    nodes58[str(f_type)].append(node)
            if set([ref_node]).issubset(set(self.ref_nodes.keys()))==False:
                self.ref_nodes[ref_node]=[i]
            else:
                self.ref_nodes[ref_node].append(i)
            if set([rsp_node]).issubset(set(self.rsp_nodes.keys()))==False:
                self.rsp_nodes[rsp_node]=[i]
            else:
                self.rsp_nodes[rsp_node].append(i)

        for i in self.uffdict['55']:
            node = self.uff.read_sets(i)['node_nums']
            d_type = self.uff.read_sets(i)['data_type']
            if set(str(d_type)).issubset(set(keys_55)):
                dict55[str(d_type)].append(i)
            for n in node:
                if set([n]).issubset(nodes55[str(d_type)])==False:
                    if set([float(n)]).issubset(self.uff.read_sets(self.uffdict['15'])['node_nums']):
                        nodes55[str(d_type)].append(int(n))
        self.uffdict = cleanup(self.uffdict)
        self.nodes = {'55':cleanup(nodes55),'58':cleanup(nodes58)}
        self.indices = {'55':dict55,'58':cleanup(dict58)}

    def get_info(self):
        """
        get_info prints out name and description of model stored in dataset 151.
        Returns how many points is stored in data set 15. How many and what type of
        datasets 55 and 58 are in UFF. How many is refence and how many response nodes.
 
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
        for i in self.uffdict['151']:
            print('Name: %s \nDescription: %s'%(self.uff.read_sets(i)['model_name'],self.uff.read_sets(i)['description']))
        for i in range(len(self.uffdict['15'])):
            print('In %i. dataset 15 is data for %i points'%(i+1,len(self.uff.read_sets(self.uffdict['15'][i])['node_nums'])))
        print('In datasets 55 are data for:')
        for key in self.nodes['55'].keys():    
            print('                             %s in %i points'%(names55[key],len(self.nodes['55'][key])))
        print('In datasets 58 are data for:')
        for key in self.nodes['58'].keys():    
            print('                             %s in %i points'%(names58[key],len(self.nodes['58'][key])))
        print('Model has: \n- {} reference node/-s \n- {} response node/-s'.format(len(self.ref_nodes.keys()),len(self.rsp_nodes.keys())))
    
    def _get_data58(self,drop):
        """
        ds58 Function prepairs data for vizualization from informations
        stored in datasets 58 ralating to chosen data type and dictionary 
        with additional information. First key is dset, which has value 58
        and represent the dataset type. Second key can be dt or df. Both are
        abscissa spaceing. dt is for data type general and time response and
        df is for all other. For frequence response, the mesurment results are
        stored in data for both extremes of point oscillation. For each direction,
        point and each frequence bouth extremes are stored in forth axis of data array

        
        Parameters
        ----------
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
        dict58 = self.indices['58']
        if self.dof_in=='ref_node':
            node_dir='ref_dir'
        if self.dof_in=='resp_node':
            node_dir='resp_dir'
    
        d=in_names[drop.value]
        if d == '0' or d == '1': #for time response
            data = np.zeros((3,len(self.uff.read_sets(self.uffdict['15'][0])['node_nums']),len(self.uff.read_sets(dict58[d][0])['num_pts'])))
            dt = self.uff.read_sets(dict58[d][0])['abscissa_spacing']
            for index in dict58[d]:
                rset = self.uff.read_sets(index)
                data_i = np.zeros((3,rset['num_pts']))
                direc = np.sign(rset['rsp_dir'])*(np.abs(rset['rsp_dir'])-1)
                node = rset['rsp_node']
                data_i[abs(direc),:] = np.conjugate(np.sign(direc)*rset['x'])
                data_i=np.matmul(np.transpose(self.uff.read_sets(self.uffdict['2420'])['CS_matrices'][int(self.uff.read_sets(self.uffdict['15'])['disp_cs'][node])]),data_i)
                data[:,node,:]+=data_i
            return data, {'dset':58, 'dt':dt}

        else:#for freqence response
            data = np.zeros((3,len(self.uff.read_sets(self.uffdict['15'][0])['node_nums']),self.uff.read_sets(dict58[d][0])['num_pts'],2))
            df=self.uff.read_sets(dict58[d][0])['abscissa_spacing']
            for index in dict58[d]:
                rset = self.uff.read_sets(index)
                data_i = np.zeros((3,rset['num_pts']))
                direc = np.sign(rset[node_dir])*(np.abs(rset[node_dir])-1)
                node = rset[self.dof_in]
                data_i[abs(direc),:] = np.sign(direc)*rset['data']
                data_i=np.matmul(np.transpose(self.uff.read_sets(self.uffdict['2420'])['CS_matrices'][int(self.uff.read_sets(self.uffdict['15'])['disp_cs'][node])]),data_i)
                data[:,node,:,0]+=data_i
                data[:,node,:,1]+=-data_i
            return data, {'dset':58, 'df':df}

    def _get_data55(self,drop):
        """
        ds55 Function prepairs data for vizualization from informations
        stored in datasets 55 ralating to chosen data type and dictionary 
        with additional information. First key is dset, which has value 55
        and represent the dataset type. Second key is freq. In second key are
        stored frequencies for which the data for individual points are given.
        Data from datasets is stored in data for both extremes of point oscillation.
        For each direction, point and each frequence bouth extremes are stored in 
        forth axis of data array.

        Parameters
        ----------
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
        dict55 = self.indices['55']
        d=in_names[drop.value]
        data = np.zeros((3,len(self.uff.read_sets(self.uffdict['15'][0])['node_nums']),len(dict55[d]),2))
        nfreq=[]
        for i in range(len(dict55[d])):
            rset = self.uff.read_sets(dict55[d][i])
            data_i = np.zeros((3,len(rset['node_nums'])))
            data_i[0,:] = rset['r1']
            data_i[1,:] = rset['r2']
            data_i[2,:] = rset['r3']
            data[:,rset['node_nums'].astype('int'),i,0] += -data_i
            nfreq.append(rset['freq'])
        for i in range(len(self.uff.read_sets(self.uffdict['15'][0])['node_nums'])):
            j=int(self.uff.read_sets(self.uffdict['15'][0])['disp_cs'][i])
            data[:,i,:,0] = np.matmul(np.transpose(self.uff.read_sets(self.uffdict['2420'])['CS_matrices'][j]),data[:,i,:,0])
        data[:,:,:,1] = -data[:,:,:,0]
        return data, {'dset':55, 'freq':nfreq}

    def _dinfo55(self,drop):
        in_names ={'normal mode':'2',
                'complex eigenvalue first order (displacement)':'3',
                'frequency response':'5',
                'complex eigenvalue second order (velocity)':'7'}
        dict55 = self.indices['55']
        d=in_names[drop.value]
        nfreq=[]
        for i in range(len(dict55[d])):
            rset = self.uff.read_sets(dict55[d][i])
            nfreq.append(rset['freq'])
        return nfreq

    def _dinfo58(self,drop):
        in_names ={'General or Unknown':'0',
                'Time Response':'1',
                'Auto Spectrum':'2',
                'Cross Spectrum':'3',
                'Frequency Response Function':'4',
                'complex eigenvalue second order (velocity)':'6'}
        dict58 = self.indices['58']
        d=in_names[drop.value]    
        return self.uff.read_sets(dict58[d][0])['abscissa_spacing'],self.uff.read_sets(dict58[d][0])['num_pts']

    def show_3D(self):
        """show_3D 
        Vizualization of structure geometry, marking reference and
        response points, showing local coordinate sistem and animating
        oscialtion of structure by results of modal or harmonic analysis
        and chosen frequence in 3D on canvas constructed by ipyvolume.
        The output on 3D canvas is simultaneously controld by ipywidgets.
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
        ref_nodes_keys = self.ref_nodes
        rsp_nodes_keys = self.rsp_nodes

        x = np.asarray(self.uff.read_sets(self.uffdict['15'])['x'])
        y = np.asarray(self.uff.read_sets(self.uffdict['15'])['y'])
        z = np.asarray(self.uff.read_sets(self.uffdict['15'])['z'])
        
        def points(x=x,y=y,z=z):
            return ipv.scatter(x, y, z, size=2, marker='sphere',color='red')
        def lines(x=x,y=y,z=z):
            l=[]
            if set(['82']).issubset(set(self.uffdict.keys())):
                pairs=[]
                for i in self.uffdict['82']:
                    for j in range(1,self.uff.read_sets(i)['n_nodes']):
                        pairs.append([int(self.uff.read_sets(i)['nodes'][j-1]),int(self.uff.read_sets(i)['nodes'][j])])
                l.append(ipv.plot_trisurf(x,y,z,lines=pairs))
                return l
            else:
                pass
        def ref():
            return ipv.scatter(x[list(ref_nodes_keys)], y[list(ref_nodes_keys)], z[list(ref_nodes_keys)], size=4, marker='circle_2d',color='blue')
        def rsp():
            return ipv.scatter(x[list(rsp_nodes_keys)], y[list(rsp_nodes_keys)], z[list(rsp_nodes_keys)], size=4, marker='circle_2d',color='green')
        def CS():
            I = np.diag([1,1,1])
            c=['red','green','blue']
            mcs = self.uff.read_sets(self.uffdict['2420'])['CS_matrices']
            disp_cs = self.uff.read_sets(self.uffdict['15'])['disp_cs']
            for i in range(3):
                u = []
                v = []
                w = []
                for p in self.uff.read_sets(self.uffdict['15'])['node_nums']:
                    u.append(np.matmul(np.transpose(mcs[int(disp_cs[int(p)])]),I[i])[0])
                    v.append(np.matmul(np.transpose(mcs[int(disp_cs[int(p)])]),I[i])[1])
                    w.append(np.matmul(np.transpose(mcs[int(disp_cs[int(p)])]),I[i])[2])
                u = np.asarray(u)
                v = np.asarray(v)
                w = np.asarray(w)
                ipv.quiver(x,y,z,u,v,w,size=5,color=c[i])
            ipv.xyzlim(min(np.array([x,y,z]).flatten()),max(np.array([x,y,z]).flatten()))
            
        pcb = widgets.Checkbox(value=False,description='Points')
        lcb = widgets.Checkbox(value=False,description='Lines')
        scb = widgets.Checkbox(value=False,description='Shadow',disabled=True)
        rfcb = widgets.Checkbox(value=False,description='Reference nodes')
        rscb = widgets.Checkbox(value=False,description='Response nodes')
        cscb = widgets.Checkbox(value=False,description='Coordinate systems')
        Hcb = widgets.Checkbox(value=False,description='Harmonic analysis')
        Mcb = widgets.Checkbox(value=False,description='Modal analysis')
        
        mfreq = widgets.Dropdown(options=[],description='Norma freq:')
        hfreq = widgets.BoundedIntText(min=0,description='Hz')
        drop = widgets.Dropdown(options=[],disabled=True)
        scale = widgets.IntText(value=10,description='Scale')
        
        title = widgets.VBox()
        analysis = widgets.VBox()
            
        def change_value(change):
            if change['new']:
                drop.disabled = False
                scb.disabled = False
                rfcb.value = False
                rscb.value = False
                cscb.value = False
                
                if change['owner'].description=='Harmonic analysis':
                    Mcb.value = False
                    hfreq.disabled = False
                    mfreq.disabled = True
                    drop.options = [names58[key] for key in self.indices['58'].keys()]
                    scale.value=1

                if change['owner'].description=='Modal analysis':
                    Hcb.value=False
                    hfreq.disabled = True
                    mfreq.disabled = False
                    drop.options = [names55[key] for key in self.indices['55'].keys()]
                    scale.value=10
    

            if Hcb.value==False and Mcb.value==False:
                drop.options = []
                drop.disabled = True
                scb.disabled = True

        Hcb.observe(change_value,names='value')
        Mcb.observe(change_value,names='value')
        def freq_ch(change):
            if Mcb.value:
                mfreq.options = self._dinfo55(drop)
            if Hcb.value:
                d,n = self._dinfo58(drop)
                hfreq.step = d
                hfreq.max = (n-1)*d
        drop.observe(freq_ch,'value')
        def figure(p=False,l=False,rf=False,rs=False,cs=False,s=False,M=False,H=False,sc=1,hfr=None,mfr=None):
            ipv.figure()
            if Hcb.value or Mcb.value:
                if s:
                    pos = points()
                    liness = lines()
                    pos.color = '#A1A1A1'
                    pos.size = 1
                    for lis in liness:
                        lis.color = '#A1A1A1'
                if Mcb.value:
                    data,dinfo= self._get_data55(drop)
                    analysis.children=[scb,drop,widgets.Label('Chose normal freqence in Hz'),mfreq,scale]
                    if mfr!=None:
                        f=dinfo['freq'].index(mfr)
                        title.children=[widgets.Label('Modal analysis'),
                                    widgets.Label('Mode shape: %i'%(f+1))]
                        X = np.transpose(np.array([x[i]+data[0,i,f,:]*sc for i in range(data.shape[1])]))
                        Y = np.transpose(np.array([y[i]+data[1,i,f,:]*sc for i in range(data.shape[1])]))
                        Z = np.transpose(np.array([z[i]+data[2,i,f,:]*sc for i in range(data.shape[1])]))
                        anim=[]
                        if p:
                            po = points(x=X,y=Y,z=Z)
                            anim.append(po)
                        if l:
                            li = lines(x=X,y=Y,z=Z)
                            for i in li:
                                anim.append(i)
                        try:
                            ipv.animation_control(anim)
                        except ValueError:
                            title.children=[widgets.Label('Select points or lines!')]
                if Hcb.value:
                    data,dinfo=self._get_data58(drop)
                    df=dinfo['df']
                    title.children=[widgets.Label('Harmonic analysis')]
                    analysis.children=[scb,drop,widgets.Label('Insert frequence by increment: %f Hz'%(df)),hfreq,scale]
                    if hfr!=None:
                        f=int(hfr/df-1)
                        X = np.transpose(np.array([x[i]+data[0,i,f,:]*sc for i in range(data.shape[1])]))
                        Y = np.transpose(np.array([y[i]+data[1,i,f,:]*sc for i in range(data.shape[1])]))
                        Z = np.transpose(np.array([z[i]+data[2,i,f,:]*sc for i in range(data.shape[1])]))
                        anim=[]
                        if p:
                            po = points(x=X,y=Y,z=Z)
                            anim.append(po)
                        if l:
                            li = lines(x=X,y=Y,z=Z)
                            for i in li:
                                anim.append(i)
                        try:
                            ipv.animation_control(anim)
                        except ValueError:
                            title.children=[widgets.Label('Select points or lines!')]
                    
            else:
                if p:
                    points()
                if l:
                    lines()
                if rf:
                    ref()
                if rs:
                    rsp()
                if cs:
                    CS()
                analysis.children=[]
                title.children=[]
            ipv.xyzlim(min(np.array([x,y,z]).flatten()),max(np.array([x,y,z]).flatten()))
            ipv.show()
        figure_out = widgets.interactive_output(figure,{'p':pcb,'l':lcb,'rf':rfcb,'rs':rscb,'cs':cscb,'s':scb,'M':Mcb,'H':Hcb,'mfr':mfreq,'hfr':hfreq,'sc':scale})
        display(widgets.HBox([widgets.VBox([title,figure_out],layout=widgets.Layout(width='60%')),widgets.VBox([pcb,lcb,rfcb,rscb,cscb,Hcb,Mcb,analysis])]))

    def show_frf(self):
        """show_frf 
        Method for easy chosing mesurment data from datasets 58 by
        reference and response node and index of dataset in UFF.
        Then simuntaneously ploting chosen mesurment
        """
        names58 ={'0': 'General or Unknown',
                '1': 'Time Response',
                '2': 'Auto Spectrum',
                '3': 'Cross Spectrum',
                '4': 'Frequency Response Function',
                '6': 'complex eigenvalue second order (velocity)'}

        ref = widgets.Dropdown(description='ref. node',options=self.ref_nodes.keys())
        rsp = widgets.Dropdown(description='rsp. node',options=self.rsp_nodes.keys())
        inter_drop =widgets.Dropdown(description='index in UFF:',options=set(self.ref_nodes[ref.value]) & set(self.rsp_nodes[rsp.value]))

        def ch_drop(change):
                inter = set(self.ref_nodes[ref.value]) & set(self.rsp_nodes[rsp.value])
                inter_drop.options=inter

        ref.observe(ch_drop,'value')
        rsp.observe(ch_drop,'value')
        display(ref,rsp,inter_drop)
        def show_frfi(i):
            direc = {0:'Unknown',
                    1:'X',
                    -1:'-X',
                    2:'Y',
                    -2:'-Y',
                    3:'Z',
                    -3:'-Z'}
            info = 'local reference direction: ' + direc[self.uff.read_sets(i)['ref_dir']] + '\n' +\
            'local response direction: ' + direc[self.uff.read_sets(i)['rsp_dir']] +'\n' +\
                'function type: %s'%(names58[str(self.uff.read_sets(i)['func_type'])])
            print(info)
            plt.figure()
            plt.semilogy(self.uff.read_sets(i)['x'],np.abs(self.uff.read_sets(i)['data']))
            plt.xlabel('Frequence [Hz]')
            plt.ylabel('Magnitude')
        frf = widgets.interactive_output(show_frfi,{'i':inter_drop})
        display(frf)

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