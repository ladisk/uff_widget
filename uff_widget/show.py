import numpy as np
import ipywidgets as widgets
import ipyvolume as ipv
from IPython.display import display
import pyuff
from .get_data import ds58 as get_data58
from .get_data import ds55 as get_data55
from .get_data import dinfo55 as dinfo55
from .get_data import dinfo58 as dinfo58
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def show_3D(uff,uffdict,indices,ref_nodes_keys,rsp_nodes_keys):

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
              
    x = np.asarray(uff.read_sets(uffdict['15'])['x'])
    y = np.asarray(uff.read_sets(uffdict['15'])['y'])
    z = np.asarray(uff.read_sets(uffdict['15'])['z'])
    
    def points(x=x,y=y,z=z):
        return ipv.scatter(x, y, z, size=2, marker='sphere',color='red')
    def lines(x=x,y=y,z=z):
        l=[]
        if set(['82']).issubset(set(uffdict.keys())):
            pairs=[]
            for i in uffdict['82']:
                for j in range(1,uff.read_sets(i)['n_nodes']):
                    pairs.append([int(uff.read_sets(i)['nodes'][j-1]),int(uff.read_sets(i)['nodes'][j])])
            l.append(ipv.plot_trisurf(x,y,z,lines=pairs))
            return l
        else:
            pass
    def ref():
        return ipv.scatter(x[list(ref_nodes_keys)], y[list(ref_nodes_keys)], z[list(ref_nodes_keys)], size=3, marker='circle_2d',color='blue')
    def rsp():
        return ipv.scatter(x[list(rsp_nodes_keys)], y[list(rsp_nodes_keys)], z[list(rsp_nodes_keys)], size=3, marker='circle_2d',color='green')
    def CS():
        I = np.diag([1,1,1])
        c=['red','green','blue']
        mcs = uff.read_sets(uffdict['2420'])['CS_matrices']
        disp_cs = uff.read_sets(uffdict['15'])['disp_cs']
        for i in range(3):
            u = []
            v = []
            w = []
            for p in uff.read_sets(uffdict['15'])['node_nums']:
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
    cscb = widgets.Checkbox(value=False,description='Coordsinate systems')
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
                drop.options = [names58[key] for key in indices['58'].keys()]

            if change['owner'].description=='Modal analysis':
                Hcb.value=False
                hfreq.disabled = True
                mfreq.disabled = False
                drop.options = [names55[key] for key in indices['55'].keys()]
 

        if Hcb.value==False and Mcb.value==False:
            drop.options = []
            drop.disabled = True
            scb.disabled = True

    Hcb.observe(change_value,names='value')
    Mcb.observe(change_value,names='value')
    def freq_ch(change):
        if Mcb.value:
            mfreq.options = dinfo55(drop,uff,uffdict,indices['55'])
        if Hcb.value:
            d,n = dinfo58(drop,uff,uffdict,indices['58'])
            hfreq.step = d
            hfreq.max = (n-1)*d
    drop.observe(freq_ch,'value')
    def figure(p=False,l=False,rf=False,rs=False,cs=False,s=False,M=False,H=False,sc=10,hfr=None,mfr=None):
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
                data,dinfo=get_data55(uff,uffdict,indices['55'],drop)
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
                    ipv.animation_control(anim)
            if Hcb.value:
                data,dinfo=get_data58(uff,uffdict,indices['58'],drop)
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
                    ipv.animation_control(anim)
                
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
    display(widgets.HBox([widgets.VBox([title,figure_out]),widgets.VBox([pcb,lcb,rfcb,rscb,cscb,Hcb,Mcb,analysis])]))

def show_frf(uff,uffdict,ref_nodes,rsp_nodes):
    ref = widgets.Dropdown(description='ref. node',options=ref_nodes.keys())
    rsp = widgets.Dropdown(description='rsp. node',options=rsp_nodes.keys())
    inter_drop =widgets.Dropdown(description='index in UFF:',options=set(ref_nodes[ref.value]) & set(rsp_nodes[rsp.value]))

    def ch_drop(change):
            inter = set(ref_nodes[ref.value]) & set(rsp_nodes[rsp.value])
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
        info = 'local reference direction: ' + direc[uff.read_sets(i)['ref_dir']] + '\n' +\
        'local response direction: ' + direc[uff.read_sets(i)['rsp_dir']]
        print(info)
        plt.figure()
        plt.semilogy(uff.read_sets(i)['x'],np.abs(uff.read_sets(i)['data']))
    frf = widgets.interactive_output(show_frfi,{'i':inter_drop})
    display(frf)