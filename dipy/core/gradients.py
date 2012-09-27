import numpy as np
import dipy.io.gradients as io
from .onetime import auto_attr


def L2norm(x):
    return np.sqrt((x * x).sum(-1))


class GradientTable(object):
    """Diffusion gradient information

    Parameters
    ----------
    gradients : array_like (N, 3)
        N diffusion gradients
    b0_threshold: float
        Gradients with b-value less than or equal to `bo_threshold` are
        considered as b0s i.e. without diffusion weighting.

    Attributes
    ----------
    gradients: array, shape(N, 3)
        diffusion gradients
    bvals: array, shape (N,)
        b-values
    bvecs: array, shape (N,3)
        b-vectors
    b0s_mask: array, shape (N,)
        Boolean array indicating which gradients have not diffusion
        weighting.
    b0_threshold: float
        Gradients with b-value less than or equal to `bo_threshold` are
        considered as b0s i.e. without diffusion weighting.

    SeeAlso
    -------
    gradient_table

    """
    def __init__(self, gradients, big_delta=None, small_delta=None,
                 b0_threshold=20):
        """Constructor for GradientTable class"""
        gradients = np.asarray(gradients)
        if gradients.ndim != 2 or gradients.shape[1] != 3:
            raise ValueError("gradients should be an (N, 3) array")
        self.gradients = gradients
        self.big_delta = big_delta
        self.small_delta = small_delta
        self.b0_threshold = b0_threshold

    @auto_attr
    def bvals(self):
        return L2norm(self.gradients)

    @auto_attr
    def b0s_mask(self):
        return self.bvals <= self.b0_threshold

    @auto_attr
    def bvecs(self):
        # To get unit vectors we divide by bvals, where bvals is 0 we divide by
        # 1 to avoid making nans
        denom = self.b0s_mask + self.bvals
        denom = denom.reshape((-1, 1))
        return self.gradients / denom

    @property
    def info(self):
        print('B-values shape (%d,)' % self.bvals.shape)
        print('         min %f ' % self.bvals.min())
        print('         max %f ' % self.bvals.max())
        print('B-vectors shape (%d, %d)' % self.bvecs.shape)
        print('         min %f ' % self.bvecs.min())
        print('         max %f ' % self.bvecs.max())

def gradient_table_from_bvals_bvecs(bvals, bvecs, b0_threshold=20, atol=1e-2,
                                  *args, **kwargs):
    """Creates a GradientTable from a bvals array and a bvecs array

    Parameters
    ----------
    bvals : array_like (N,)
        The values of each of N gradients.
    bvecs : array_like (N, 3)
        The direction of each of N gradients as a unit vector.
    b0_threshold: float
        All b-values with values less than or equal to `bo_threshold` are
        considered as b0s i.e. without diffusion weighting.
    atol: float
        Each vector in `bvecs` must be a unit vectors up to a tolerance of
        `atol`.
    All other inputs are passed to GradientTable

    Return
    ------
    gradients : GradientTable
        A GradientTable with all the gradient information.

    See Also
    --------
    GradientTable, gradient_table

    """
    bvals = np.asarray(bvals)
    bvecs = np.asarray(bvecs)
    dwi_mask = bvals > b0_threshold

    # check that bvals is (N,) array and bvecs is (N, 3) unit vectors
    if bvals.ndim != 1 or bvecs.ndim != 2 or len(bvecs) != len(bvals):
        raise ValueError("bvals and bvecs should be (N,) and (N, 3) arrays "
                         "respectively, where N is the number of diffusion "
                         "gradients")

    bvec_norms = L2norm(bvecs[dwi_mask])
    if bvecs.shape[1] != 3 or not np.allclose(bvec_norms, 1., atol=atol):
        raise ValueError("bvecs should be (N, 3), a set of N unit vectors")

    gradients = bvals[:, None] * dwi_mask[:, None] * bvecs
    grad_table = GradientTable(gradients, b0_threshold=20, *args, **kwargs)
    grad_table.bvals = bvals
    grad_table.bvecs = bvecs
    grad_table.b0s_mask = ~dwi_mask
    return grad_table

def gradient_table(bvals, bvecs=None, big_delta=None, small_delta=None,
                   b0_threshold=20, atol=1e-2):
    """A general function for creating diffusion MR gradients.

    It reads, loads and prepares scanner parameters like the b-values and
    b-vectors so that they can be useful during the reconstruction process.

    Parameters
    ----------

    bvals: can be any of the four options
        1. an array of shape (N,) or (1, N) or (N, 1) with the b-values.
        2. a path for the file which contains an array like the above (1).
        3. an array of shape (N, 4) or (4, N). Then this parameter is
        considered to be a b-table which contains both bvals and bvecs. In
        this case the next parameter is skipped.
        4. a path for the file which contains an array like the one at (3).

    bvecs: can be any of two options
        1. an array of shape (N, 3) or (3, N) with the b-vectors.
        2. a path for the file wich contains an array like the previous.

    big_delta: float
        acquisition timing duration (default None)

    small_delta: float
        acquisition timing duration (default None)

    b0_threshold: float
        All b-values with values less than or equal to `bo_threshold` are
        considered as b0s i.e. without diffusion weighting.

    atol: float
        All b-vectors need to be unit vectors up to a tolerance.


    Return
    ------
    gradients : GradientTable
        A GradientTable with all the gradient information.


    Examples
    --------
    >>> from dipy.core.gradients import gradient_table
    >>> bvals=1500*np.ones(7)
    >>> bvals[0]=0
    >>> sq2=np.sqrt(2)/2
    >>> bvecs=np.array([[0, 0, 0],\
                        [1, 0, 0],\
                        [0, 1, 0],\
                        [0, 0, 1],\
                        [sq2, sq2, 0],\
                        [sq2, 0, sq2],\
                        [0, sq2, sq2]])
    >>> gt = gradient_table(bvals, bvecs)
    >>> gt.bvecs.shape == bvecs.shape
    True
    >>> gt = gradient_table(bvals, bvecs.T)
    >>> gt.bvecs.shape == bvecs.T.shape
    False

    Notes
    -----
    1. Often b0s (b-values which correspond to images without diffusion
    weighting) have 0 values however in some cases the scanner cannot
    provide b0s of an exact 0 value and it gives a bit higher values
    e.g. 6 or 12. This is the purpose of the b0_threshold in the __init__.

    2. We assume that the minimum number of b-values is 7.

    3. B-vectors should be unit vectors.
    """

    # If you provided strings with full paths, we go and load those from
    # the files:
    if isinstance(bvals, basestring):
          bvals, _ = io.read_bvals_bvecs(bvals, None)
    if isinstance(bvecs, basestring):
          _, bvecs = io.read_bvals_bvecs(None, bvecs)

    bvals = np.asarray(bvals)
    # If bvals is None we expect bvals to be an (N, 3) or (3, N) array
    if bvecs is None:
        if bvals.shape[-1] == 4:
            bvecs = bvals[:, 1:]
            bvals = np.squeeze(bvals[:, 0])
        elif bvals.shape[0] == 4:
            bvecs = bvals[1:, :].T
            bvals = np.squeeze(bvals[0, :])
        else:
            raise ValueError("input should be bvals and bvecs OR an (N, 4)"
                             "array containing both bvals and bvecs")
    else:
        bvecs = np.asarray(bvecs)
        if bvecs.shape[1] > bvecs.shape[0]:
            bvecs = bvecs.T
    return gradient_table_from_bvals_bvecs(bvals, bvecs, big_delta=None,
                                           small_delta=None, b0_threshold=20,
                                           atol=1e-2)
