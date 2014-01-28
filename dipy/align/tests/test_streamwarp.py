import numpy as np
from numpy.testing import (run_module_suite,
                           assert_equal,
                           assert_array_equal,
                           assert_array_almost_equal)
from dipy.align.streamwarp import (LinearRegistration,
                                   transform_streamlines,
                                   matrix44,
                                   mdf_optimization_sum,
                                   mdf_optimization_min,
                                   center_streamlines)
from dipy.tracking.metrics import downsample
from dipy.data import get_data
from dipy.bundle.descriptors import midpoints
from nibabel import trackvis as tv
from dipy.align.streamwarp import StreamlineRigidRegistration, compose_transformations


def simulated_bundle(no_streamlines=10, waves=False, no_pts=12):
    t = np.linspace(-10, 10, 200)
    # parallel waves or parallel lines
    bundle = []
    for i in np.linspace(-5, 5, no_streamlines):
        if waves:
            pts = np.vstack((np.cos(t), t, i * np.ones(t.shape))).T
        else:
             pts = np.vstack((np.zeros(t.shape), t, i * np.ones(t.shape))).T
        pts = downsample(pts, no_pts)
        bundle.append(pts)

    return bundle


def fornix_streamlines(no_pts=12):
    fname = get_data('fornix')
    streams, hdr = tv.read(fname)
    streamlines = [downsample(i[0], no_pts) for i in streams]
    return streamlines


def evaluate_convergence(bundle, new_bundle2):
    pts_static = np.concatenate(bundle, axis=0)
    pts_moved = np.concatenate(new_bundle2, axis=0)
    assert_array_almost_equal(pts_static, pts_moved, 3)


def test_rigid():

    bundle_initial = simulated_bundle()
    bundle, shift = center_streamlines(bundle_initial)
    mat = matrix44([20, 0, 10, 0, 40, 0])
    bundle2 = transform_streamlines(bundle, mat)

    lin = LinearRegistration(mdf_optimization_sum, 'rigid')
    new_bundle2 = lin.transform(bundle, bundle2)

    evaluate_convergence(bundle, new_bundle2)

    cx, cy, cz = shift
    shift_mat = matrix44([cx, cy, cz, 0, 0, 0])

    new_bundle2_initial = transform_streamlines(new_bundle2, shift_mat)

    evaluate_convergence(bundle_initial, new_bundle2_initial)


def test_rigid_real_bundles():

    bundle_initial = fornix_streamlines()[:20]
    bundle, shift = center_streamlines(bundle_initial)
    mat = matrix44([0, 0, 20, 45, 0, 0])
    bundle2 = transform_streamlines(bundle, mat)


    lin = LinearRegistration(mdf_optimization_sum, 'rigid')
    new_bundle2 = lin.transform(bundle, bundle2)

    evaluate_convergence(bundle, new_bundle2)

    cx, cy, cz = shift
    new_bundle2_initial = transform_streamlines(new_bundle2, matrix44([cx, cy, cz, 0, 0, 0]))

    evaluate_convergence(bundle_initial, new_bundle2_initial)


def test_rigid_partial():

    static = fornix_streamlines()[:20]
    moving = fornix_streamlines()[20:40]
    static_center, shift = center_streamlines(static)

    mat = matrix44([0, 0, 0, 0, 40, 0])
    moving = transform_streamlines(moving, mat)

    lin = LinearRegistration(mdf_optimization_min, 'rigid')

    moving_center = lin.transform(static_center, moving)

    static_center = [downsample(s, 100) for s in static_center]
    moving_center = [downsample(s, 100) for s in moving_center]
    vol = np.zeros((100, 100, 100))
    spts = np.concatenate(static_center, axis=0)
    spts = np.round(spts).astype(np.int) + np.array([50, 50, 50])

    mpts = np.concatenate(moving_center, axis=0)
    mpts = np.round(mpts).astype(np.int) + np.array([50, 50, 50])

    for index in spts:
        i, j, k = index
        vol[i, j, k] = 1

    vol2 = np.zeros((100, 100, 100))
    for index in mpts:
        i, j, k = index
        vol2[i, j, k] = 1

    overlap = np.sum(np.logical_and(vol,vol2)) / float(np.sum(vol2))
    print(overlap)

    assert_equal(overlap * 100 > 40, True )


def test_stream_rigid():

    static = fornix_streamlines()[:20]
    moving = fornix_streamlines()[20:40]
    static_center, shift = center_streamlines(static)

    mat = matrix44([0, 0, 0, 0, 40, 0])
    moving = transform_streamlines(moving, mat)

    srr = StreamlineRigidRegistration(mdf_optimization_min, full_output=True)

    sr_params = srr.optimize(static, moving)

    moved = transform_streamlines(moving, sr_params.matrix)

    srr = StreamlineRigidRegistration(mdf_optimization_min, full_output=False)

    srp = srr.optimize(static, moving)

    moved2 = transform_streamlines(moving, srp.matrix)

    moved3 = srp.transform(moving)

    assert_array_equal(moved[0], moved2[0])
    assert_array_equal(moved2[0], moved3[0])


def test_compose_transformations():

    A = np.eye(4)
    A[0, -1] = 10

    B = np.eye(4)    
    B[0, -1] = -20    

    C = np.eye(4)
    C[0, -1] = 10    

    CBA = compose_transformations(A, B, C)

    assert_array_equal(CBA, np.eye(4))


if __name__ == '__main__':

    run_module_suite()
    
