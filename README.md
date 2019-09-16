# uff_widget
Package for visualizing a UFF file used in vibration testing.

It is constructed from 4 basic methodes:

read_uff

get_info

show_frf

show_3D

A UFF file is required to use the package

## Initialization
uff_1=uff_widget.widgetuff(path)

uff_1.read_uff()

## Overview of information about considered model/structure
uff_1.get_info()

## Viewing writen function data like FRF-s
uff_1.show_frf()

## Viewing geometry, harmonic an modal analysis in 3D
uff_1.show_3D()

## Preparation of an UFF file
For help with preparation of the UFF file, check files in the folder `test_data` and
documentation of the package `pyuff` (https://github.com/openmodal/pyuff) and
documentation of Universal File Format (http://sdrl.uc.edu/sdrl/referenceinfo/universalfileformats)
