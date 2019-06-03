import numpy as np
import ipywidgets as widgets
import ipyvolume as ipv
from IPython.display import display
import pyuff

def viz (file,uffdict,data,dinfo=None):
    """viz Function for vizualizating points from dataset 15 with
    information from input data and difno. If data is dictionary
    with indices of nodes separately for dataset type (55 and 58)
    and stored data type, points are marked regarding to choice in
    buttons and dropdown menu. If data is numpy array, movement of
    points in animated regarding to input data and dinfo.

    
    Parameters
    ----------
    file : UFF class variable
        variable for access to data stored in uff
    uffdict : dictionary
        dictionary wirt all in file existing dataset types as keys
    data : numpy array 
        numpy array with size (three directions,,number of all points, 
        length of mesurment) for time response 
        numpy array with size (three directions,,number of all points, 
        length of mesurment,two extremes) for frequence response
    dinfo : ditionary, optional
        By default None. Dictionary with keys 'dset'(value 58 or 55) and 
        'dt' or 'df' of 'freq'. Frst two are abscissa spaceing for 
        dataset 58, freq is list of frequences for dataset 55. 
    
    Returns
    -------
    buttons : widget
        ipython buttons widget with options 'Function data', 'Analysis'. Only when data is dictionary
    drop : widget
        ipython drodown widget with options according to the value of buttons. Only when data is dictionary
    widget output
        output with figure and control witgets
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
    in_names55 = {'normal mode':'2',
              'complex eigenvalue first order (displacement)':'3',
              'frequency response':'5',
              'complex eigenvalue second order (velocity)':'7'}
    in_names58 ={'General or Unknown':'0',
              'Time Response':'1',
              'Auto Spectrum':'2',
              'Cross Spectrum':'3',
              'Frequency Response Function':'4',
              'complex eigenvalue second order (velocity)':'6'}    
    
    x = np.asarray(file.read_sets(uffdict['15'])['x'])
    y = np.asarray(file.read_sets(uffdict['15'])['y'])
    z = np.asarray(file.read_sets(uffdict['15'])['z'])
    
    def s(x,y,z):
        ipv.figure()
        f = [ipv.scatter(x, y, z, size=2, marker='sphere',color='red')]
        if set(['82']).issubset(set(uffdict.keys())):
            pairs=[]
            for i in uffdict['82']:
                for j in range(1,file.read_sets(i)['n_nodes']):
                    pairs.append([int(file.read_sets(i)['nodes'][j-1]),int(file.read_sets(i)['nodes'][j])])
        f.append(ipv.plot_trisurf(x,y,z,lines=pairs))
        ipv.xyzlim(min(np.array([x,y,z]).flatten()),max(np.array([x,y,z]).flatten()))
        return f
    
    if type(data)==dict:
        buttons = widgets.RadioButtons(options=['Function data', 'Analysis'],description='Results type:')
        drop = widgets.Dropdown(options=[names58[key] for key in data['58'].keys()])
        s(x,y,z)
        def drop_data(*args):
            if buttons.value == 'Analysis':
                drop.options = [names55[key] for key in data['55'].keys()]
            if buttons.value=='Function data':
                drop.options = [names58[key] for key in data['58'].keys()]
        buttons.observe(drop_data,'value')
        a = ipv.scatter(np.array([0.]),np.array([0.]),np.array([0.]),size=3, marker='circle_2d',color='blue')
        def f(buttons,drop):
            if buttons=='Analysis':
                dset='55'
                a.x=x[data[dset][in_names55[drop]]]
                a.y=y[data[dset][in_names55[drop]]]
                a.z=z[data[dset][in_names55[drop]]]
                a.color='blue'
            if buttons=='Function data':
                dset='58'
                a.x=x[data[dset][in_names58[drop]]]
                a.y=y[data[dset][in_names58[drop]]]
                a.z=z[data[dset][in_names58[drop]]]
                a.color='green'
        widgets.interactive_output(f,{'buttons':buttons,'drop':drop})
        display(widgets.HBox([ipv.gcf(),widgets.VBox([buttons,drop])]))
        return buttons,drop
    
    if type(data)==np.ndarray:
        if data.ndim==3:#problems for more than 100 animating points
            if set(['dt']).issubset(list(dinfo.keys())):
                X = np.array([x+data[0,:,i] for i in range(data.shape[2])])
                Y = np.array([y+data[1,:,i] for i in range(data.shape[2])])
                Z = np.array([z+data[2,:,i] for i in range(data.shape[2])])
                anim = s(X,Y,Z)
                ipv.animation_control(anim,interval=dinfo['dt']*1000)
                ipv.show()

        if data.ndim==4:
            if dinfo['dset']==58:
                df=dinfo['df']
                def show_freq(freq,scale=1):
                    f=int(freq/df-1)
                    X = np.transpose(np.array([x[i]+data[0,i,f,:]*scale for i in range(data.shape[1])]))
                    Y = np.transpose(np.array([y[i]+data[1,i,f,:]*scale for i in range(data.shape[1])]))
                    Z = np.transpose(np.array([z[i]+data[2,i,f,:]*scale for i in range(data.shape[1])]))
                    anim = s(X,Y,Z)
                    ipv.animation_control(anim)
                    ipv.show()
                scale = widgets.BoundedIntText(step=1,value=1,min=1,max=1000,description='scale by:')
                freq = widgets.BoundedIntText(min=0*df,max=(len(data[0,0,:,0])-1)*df,step=df,description='Hz')
                out1 = widgets.interactive_output(show_freq, {'freq':freq,'scale':scale})
                display(widgets.HBox([out1,widgets.VBox([widgets.Label('Insert frequence by increment: %f Hz'%(df)),freq,scale])]))
            
            if dinfo['dset']==55:
                mfreq=dinfo['freq']
                def norm_freq(freq,scale=1):
                    f=mfreq.index(freq)
                    X = np.transpose(np.array([x[i]+data[0,i,f,:]*scale for i in range(data.shape[1])]))
                    Y = np.transpose(np.array([y[i]+data[1,i,f,:]*scale for i in range(data.shape[1])]))
                    Z = np.transpose(np.array([z[i]+data[2,i,f,:]*scale for i in range(data.shape[1])]))
                    anim = s(X,Y,Z)
                    ipv.animation_control(anim)
                    ipv.show()
                def mshape(freq):
                    m=mfreq.index(freq)+1
                    display(widgets.Label('Mode shape: %i'%(m)))
                freq = widgets.Dropdown(options=mfreq)
                scale = widgets.BoundedIntText(step=1,value=1,min=1,max=1000,description='scale by:')
                out1 = widgets.interactive_output(mshape, {'freq':freq})
                out2 = widgets.interactive_output(norm_freq, {'freq':freq,'scale':scale})
                display(widgets.HBox([widgets.VBox([out1,out2]),widgets.VBox([widgets.Label('Chose normal freqence'),widgets.HBox([freq,widgets.Label('Hz')]),scale])]))
        else:
            print('error')