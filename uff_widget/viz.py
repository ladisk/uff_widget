import numpy as np
import ipywidgets as widgets
import ipyvolume as ipv
from IPython.display import display
import pyuff

def viz (file,uffdict,data,disp_typ='freq'):
    
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
            
        out = widgets.interactive_output(f,{'buttons':buttons,'drop':drop})
        display(widgets.HBox([ipv.gcf(),widgets.VBox([buttons,drop])]))
    
    if type(data)==np.ndarray:
        if data.ndim==3:#problems for more than 100 animating points
            if disp_typ=='time':
                dt=file.read_sets(uffdict['58'][0])['abscissa_spacing']
                X = np.array([x+data[0,:,i] for i in range(data.shape[2])])
                Y = np.array([y+data[1,:,i] for i in range(data.shape[2])])
                Z = np.array([z+data[2,:,i] for i in range(data.shape[2])])
                anim = s(X,Y,Z)
                ipv.animation_control(anim)
                ipv.show()
            if disp_typ=='freq':
                print('TODO')
            else:
                print('error')
        else:
            print('error')
