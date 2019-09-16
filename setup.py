import setuptools

setuptools.setup(
     name='uff_widget',  
     version='0.2',
     author='Lovro Trilar,Janko Slavič',
     author_email='Lovro.3lar@gmail.com, janko.slavic@fs.uni-lj.si',
     description='Visualization of uff file',
     url='https://github.com/ladisk/uff_widget',
     py_modules=['uff_widget'],
     install_requires=['numpy>=1.16.1', 'pyuff>=1.20', 'ipywidgets>=7.4.2',
     'ipyvolume>=0.5.1', 'ipython>=6.2.1'],
     classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
     ],
 )