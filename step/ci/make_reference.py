"""Build the reference case from the pinned stroke-server fixture generator.

The committed-by-reference fixture CT (76x92x60 voxels, 2.5x2.5x3 mm) holds only ~29k voxels
above 100 HU, whereas the unchanged workflow needs a skull cluster of >= 100000 voxels
(`fsl-cluster --minextent=100000`). This script runs the same generator code, seed, lesion and
random transform (case-01) on a 1 mm isotropic native grid, which gives a skull cluster the
workflow accepts. The MNI ground-truth mask is the generator's own (2 mm working grid).

    python step/ci/make_reference.py FETCHED_DIR OUT_DIR
Output: ct.nii.gz, lesion_mask_native.nii.gz, lesion_mask_mni.nii.gz
"""

import sys
from pathlib import Path

import numpy as np

fetched, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(fetched))
from fixtures import generate, phantom  # noqa: E402
from fixtures.io import MNI2_AFFINE, write_nifti_gz  # noqa: E402

phantom.CT_SHAPE = (190, 230, 180)
phantom.CT_VOX = np.array([1.0, 1.0, 1.0])

case = "case-01"
i = sorted(generate.CASES).index(case)
rng = np.random.default_rng([generate.SEED, 1, i])
p = phantom.make_patient(rng, generate.CASES[case])
out.mkdir(parents=True, exist_ok=True)
write_nifti_gz(out / "ct.nii.gz", p["ct"], p["affine"], mni=False)
write_nifti_gz(out / "lesion_mask_native.nii.gz", p["mask"], p["affine"], mni=False)
write_nifti_gz(out / "lesion_mask_mni.nii.gz", p["mni_mask"], MNI2_AFFINE, mni=True)
print("skull-range voxels:", int((p["ct"] > 100).sum()), "lesion voxels (native):", int(p["mask"].sum()))
