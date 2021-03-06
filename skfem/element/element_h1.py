import numpy as np
from numpy import ndarray

from .element import Element
from .discrete_field import DiscreteField


class ElementH1(Element):
    """A global element defined through identity mapping."""

    def gbasis(self, mapping, X, i, tind=None):
        phi, dphi = self.lbasis(X, i)
        invDF = mapping.invDF(X, tind)
        if len(X.shape) == 2:
            return (DiscreteField(
                value = np.broadcast_to(phi, (invDF.shape[2], invDF.shape[3])),
                grad = np.einsum('ijkl,il->jkl', invDF, dphi)
            ),)
        elif len(X.shape) == 3:
            return (DiscreteField(
                value = np.broadcast_to(phi, (invDF.shape[2], invDF.shape[3])),
                grad = np.einsum('ijkl,ikl->jkl', invDF, dphi)
            ),)

    def lbasis(self, X, i):
        raise Exception("ElementH1.lbasis method not found.")
