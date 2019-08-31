# uff_widget
Package for visualizing a UFF file used in vibration testing.

It is constructed from 4 basic methodes:

read_uff

get_info

show_frf

show_3D

A UFF file is required to use the package

## initialization
uff_1=uff_widget.widgetuff(path)

uff_1.read_uff()

## owerview of information about considered model/structure
uff_1.get_info()

## Viewing writen function data like FRF-s
uff_1.show_frf()

## Viewing geometry and oscilatin in 3D
uff_1.show3D()

## Constructing a UFF file
For help with preparation of the UFF file, check files in the folder `test_data` and
documentation of the package `pyuff` (https://github.com/openmodal/pyuff) and
documentation of Universal File Format (http://sdrl.uc.edu/sdrl/referenceinfo/universalfileformats)
