#!/usr/bin/env python

"""
The Form class.
"""

__authors__ = "Martin Sandve Alnes"
__date__    = "2008-03-14 -- 2008-04-03"

class Form:
    """Description of a weak form consisting of a sum of integrals over subdomains."""
    def __init__(self, integrals):
        self._integrals = integrals
    
    def integrals(self, domain_type):
        return tuple([itg for itg in self._integrals if itg._domain_type == domain_type])
    
    def cell_integrals(self):
        return self.integrals("cell")
    
    def exterior_facet_integrals(self):
        return self.integrals("exterior_facet")
    
    def interior_facet_integrals(self):
        return self.integrals("interior_facet")

    def __contains__(self, item):
        """Return wether item is in the UFL expression tree. If item is a str, it is assumed to be a repr."""
        return any((item in itg) for itg in self._integrals)
    
    def __add__(self, other):
        return Form(self._integrals + other._integrals)
    
    def __str__(self):
        return "  +  ".join(str(itg) for itg in self._integrals)
    
    def __repr__(self):
        return "Form([%s])" % ", ".join(repr(itg) for itg in self._integrals)
