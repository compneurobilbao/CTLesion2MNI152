import os

DATA_PATH = os.path.abspath(os.path.dirname(__file__))

MNI152_BONE_PATH = os.path.join(DATA_PATH, "ct_skull_MNI152.nii.gz")
MNI152_T1_PATH = os.path.join(DATA_PATH, "ct_in_MNI152.nii.gz")
MNI152_BRAIN_PATH = os.path.join(DATA_PATH, "ct_brain_MNI152.nii.gz")
BSPLINE_PATH = os.path.join(DATA_PATH, "Par0000bspline.txt")
