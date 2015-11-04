# -*- coding: utf-8 -*-
"This module defines the UFL finite element classes."

# Copyright (C) 2008-2015 Martin Sandve Alnæs
#
# This file is part of UFL.
#
# UFL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with UFL. If not, see <http://www.gnu.org/licenses/>.
#
# Modified by Kristian B. Oelgaard
# Modified by Marie E. Rognes 2010, 2012
# Modified by Anders Logg 2014

from ufl.assertions import ufl_assert
from ufl.utils.formatting import istr
from ufl.cell import as_cell
from ufl.log import info_blue, warning, warning_blue, error

from ufl.cell import OuterProductCell
from ufl.finiteelement.elementlist import canonical_element_description, simplices
from ufl.finiteelement.finiteelementbase import FiniteElementBase

class FiniteElement(FiniteElementBase):
    "The basic finite element class for all simple finite elements"
    # TODO: Move these to base?
    __slots__ = ("_short_name",
                 "_sobolev_space",
                 "_mapping",
                )

    def __new__(cls,
                family,
                domain=None,
                degree=None,
                form_degree=None,
                quad_scheme=None):
        """Intercepts construction to expand CG, DG, RTCE and RTCF spaces
        on OuterProductCells.
        """
        if domain is None:
            cell = None
        else:
            domain = as_domain(domain)
            cell = domain.cell()
            ufl_assert(cell is not None, "Missing cell in given domain.")

        family, short_name, degree, value_shape, reference_value_shape, sobolev_space, mapping = \
          canonical_element_description(family, cell, degree, form_degree)

        if isinstance(cell, OuterProductCell):
            # Delay import to avoid circular dependency at module load time
            from ufl.finiteelement.outerproductelement import OuterProductElement
            from ufl.finiteelement.enrichedelement import EnrichedElement
            from ufl.finiteelement.hdivcurl import HDiv, HCurl

            if family in ["RTCF", "RTCE"]:
                ufl_assert(cell._A.cellname() == "interval", "%s is available on OuterProductCell(interval, interval) only." % family)
                ufl_assert(cell._B.cellname() == "interval", "%s is available on OuterProductCell(interval, interval) only." % family)

                C_elt = FiniteElement("CG", "interval", degree, 0, quad_scheme)
                D_elt = FiniteElement("DG", "interval", degree - 1, 1, quad_scheme)

                CxD_elt = OuterProductElement(C_elt, D_elt, domain, form_degree, quad_scheme)
                DxC_elt = OuterProductElement(D_elt, C_elt, domain, form_degree, quad_scheme)

                if family == "RTCF":
                    return EnrichedElement(HDiv(CxD_elt), HDiv(DxC_elt))
                if family == "RTCE":
                    return EnrichedElement(HCurl(CxD_elt), HCurl(DxC_elt))

            elif family == "NCF":
                ufl_assert(cell._A.cellname() == "quadrilateral", "%s is available on OuterProductCell(quadrilateral, interval) only." % family)
                ufl_assert(cell._B.cellname() == "interval", "%s is available on OuterProductCell(quadrilateral, interval) only." % family)

                Qc_elt = FiniteElement("RTCF", "quadrilateral", degree, 1, quad_scheme)
                Qd_elt = FiniteElement("DQ", "quadrilateral", degree - 1, 2, quad_scheme)

                Id_elt = FiniteElement("DG", "interval", degree - 1, 1, quad_scheme)
                Ic_elt = FiniteElement("CG", "interval", degree, 0, quad_scheme)

                return EnrichedElement(HDiv(OuterProductElement(Qc_elt, Id_elt, domain, form_degree, quad_scheme)),
                                       HDiv(OuterProductElement(Qd_elt, Ic_elt, domain, form_degree, quad_scheme)))

            elif family == "NCE":
                ufl_assert(cell._A.cellname() == "quadrilateral", "%s is available on OuterProductCell(quadrilateral, interval) only." % family)
                ufl_assert(cell._B.cellname() == "interval", "%s is available on OuterProductCell(quadrilateral, interval) only." % family)

                Qc_elt = FiniteElement("Q", "quadrilateral", degree, 0, quad_scheme)
                Qd_elt = FiniteElement("RTCE", "quadrilateral", degree, 1, quad_scheme)

                Id_elt = FiniteElement("DG", "interval", degree - 1, 1, quad_scheme)
                Ic_elt = FiniteElement("CG", "interval", degree, 0, quad_scheme)

                return EnrichedElement(HCurl(OuterProductElement(Qc_elt, Id_elt, domain, form_degree, quad_scheme)),
                                       HCurl(OuterProductElement(Qd_elt, Ic_elt, domain, form_degree, quad_scheme)))

            elif family == "Q":
                return OuterProductElement(FiniteElement("CG", cell._A, degree, 0, quad_scheme),
                                           FiniteElement("CG", cell._B, degree, 0, quad_scheme),
                                           domain, form_degree, quad_scheme)

            elif family == "DQ":
                family_A = "DG" if cell._A.cellname() in simplices else "DQ"
                family_B = "DG" if cell._B.cellname() in simplices else "DQ"
                return OuterProductElement(FiniteElement(family_A, cell._A, degree, cell._A.topological_dimension(), quad_scheme),
                                           FiniteElement(family_B, cell._B, degree, cell._B.topological_dimension(), quad_scheme),
                                           domain, form_degree, quad_scheme)

        return super(FiniteElement, cls).__new__(cls,
                                                 family,
                                                 domain,
                                                 degree,
                                                 form_degree,
                                                 quad_scheme)

    def __init__(self,
                 family,
                 cell=None,
                 degree=None,
                 form_degree=None,
                 quad_scheme=None):
        """Create finite element.

        *Arguments*
            family (string)
               The finite element family
            cell
               The geometric cell
            degree (int)
               The polynomial degree (optional)
            form_degree (int)
               The form degree (FEEC notation, used when field is
               viewed as k-form)
            quad_scheme
               The quadrature scheme (optional)
        """
        # Note: Unfortunately, dolfin sometimes passes None for cell. Until this is fixed, allow it:
        if cell is not None:
            cell = as_cell(cell)

        family, short_name, degree, value_shape, reference_value_shape, sobolev_space, mapping = \
          canonical_element_description(family, cell, degree, form_degree)

        # TODO: Move these to base? Might be better to instead simplify base though.
        self._sobolev_space = sobolev_space
        self._mapping = mapping
        self._short_name = short_name

        # Finite elements on quadrilaterals have an IrreducibleInt as degree
        if domain is not None:
            if cell.cellname() == "quadrilateral":
                from ufl.algorithms.estimate_degrees import IrreducibleInt
                degree = IrreducibleInt(degree)

        # Initialize element data
        FiniteElementBase.__init__(self, family, cell, degree,
                                   quad_scheme, value_shape, reference_value_shape)

        # Cache repr string
        qs = self.quadrature_scheme()
        quad_str = "" if qs is None else ", quad_scheme=%r" % (qs,)
        self._repr = "FiniteElement(%r, %r, %r%s)" % (self.family(), self.cell(), self.degree(), quad_str)
        assert '"' not in self._repr

    def mapping(self):
        return self._mapping

    def sobolev_space(self):
        return self._sobolev_space

    def __str__(self):
        "Format as string for pretty printing."
        qs = self.quadrature_scheme()
        qs = "" if qs is None else "(%s)" % qs
        return "<%s%s%s on a %s>" % (self._short_name, istr(self.degree()),
                                           qs, self.cell())

    def shortstr(self):
        "Format as string for pretty printing."
        return "%s%s(%s)" % (self._short_name, istr(self.degree()),
                             istr(self.quadrature_scheme()))
