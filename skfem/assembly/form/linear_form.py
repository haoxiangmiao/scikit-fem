from typing import Any, Callable, Optional, Dict

import numpy as np
from numpy import ndarray

from .form import Form, FormDict
from ..basis import Basis
from ...element import DiscreteField


class LinearForm(Form):

    def assemble(self,
                 u: Basis,
                 v: Optional[Basis] = None,
                 w: Dict[str, DiscreteField] = {}) -> ndarray:

        assert v is None
        v = u

        nt = v.nelems
        dx = v.dx
        w = FormDict({**v.default_parameters(), **self.dictify(w)})

        # initialize COO data structures
        sz = v.Nbfun * nt
        data = np.zeros(sz)
        rows = np.zeros(sz)
        cols = np.zeros(sz)

        for i in range(v.Nbfun):
            ixs = slice(nt * i, nt * (i + 1))
            rows[ixs] = v.element_dofs[i]
            cols[ixs] = np.zeros(nt)
            data[ixs] = self._kernel(v.basis[i], w, dx)

        return self._assemble_numpy_vector(data, rows, cols, (v.N, 1))

    def _kernel(self, v, w, dx):
        return np.sum(self.form(*v, w) * dx, axis=1)


def linear_form(form: Callable) -> LinearForm:

    # for backwards compatibility
    from .form_parameters import FormParameters

    # TODO: deprecate
    class ClassicLinearForm(LinearForm):

        def _kernel(self, v, w, dx):
            v = v[0]
            W = {k: w[k].f for k in w}
            if 'w' in w:
                W['dw'] = w['w'].df
            if v.ddf is not None:
                return np.sum(self.form(v=v.f, dv=v.df, ddv=v.ddf,
                                        w=FormParameters(**W)) * dx, axis=1)
            else:
                return np.sum(self.form(v=v.f, dv=v.df,
                                        w=FormParameters(**W)) * dx, axis=1)

    return ClassicLinearForm(form)
