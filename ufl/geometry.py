#!/usr/bin/env python

"""
Types for quantities computed from cell geometry.
"""

__authors__ = "Martin Sandve Alnes"
__date__ = "2008-03-14 -- 2008-04-01"

from base import *


class GeometricQuantity(Terminal):
    def __init__(self):
        pass
    

class FacetNormal(GeometricQuantity):
    def __init__(self):
        pass
    
    def free_indices(self):
        return ()
    
    def rank(self):
        return 1
    
    def __str__(self):
        return "n"
    
    def __repr__(self):
        return "FacetNormal()"


class MeshSize(GeometricQuantity):
    def __init__(self):
        pass
    
    def free_indices(self):
        return ()
    
    def rank(self):
        return 0
    
    def __str__(self):
        return "h"
    
    def __repr__(self):
        return "MeshSize()"


# TODO: More mesh quantities? Local measures of mesh quality should be easy to add, if we just define what's interesting.
