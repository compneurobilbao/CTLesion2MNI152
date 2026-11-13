"""Dice of a step output mask against the fixture ground truth (both on the 2 mm grid).

    python step/tests/report_dice.py OUT_DIR TRUTH_MASK
Prints one JSON line; used by CI to report the real value.
"""

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np


def dice(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a > 0, b > 0
    total = int(a.sum()) + int(b.sum())
    return 1.0 if total == 0 else 2.0 * int((a & b).sum()) / total


if __name__ == "__main__":
    out = nib.load(str(Path(sys.argv[1]) / "lesion_mask_mni.nii.gz"))
    truth = nib.load(sys.argv[2])
    a, b = np.asanyarray(out.dataobj), np.asanyarray(truth.dataobj)
    print(json.dumps({"dice": round(dice(a, b), 4), "voxels_out": int((a > 0).sum()), "voxels_truth": int((b > 0).sum())}))
