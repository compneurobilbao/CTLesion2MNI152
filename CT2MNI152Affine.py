import os
import CTtools
from subprocess import call
import sys
import argparse


def setup():
    # Argument parser
    arg_parser = argparse.ArgumentParser(
        description="CT to MNI152 Registration",
        formatter_class=argparse.RawTextHelpFormatter)

    # Add arguments
    arg_parser.add_argument("-p", "--ct_scan_path",
                            metavar="DIR",
                            required=True,
                            help="Path to the CT scan.")
    arg_parser.add_argument("-sdr", "--scan_device_removal",
                            default=False,
                            help="Whether CT scan device removal is desired. Default is False.")
    arg_parser.add_argument("-o", "--output_path",
                            metavar="DIR",
                            help="Path to save the results folder.",
                            required=True)
    # Parse arguments
    args = arg_parser.parse_args()
    
    # Check that arguments are correct
    if not os.path.exists(args.ct_scan_path):
        raise ValueError("CT scan path does not exist.")
    if not os.path.exists(args.output_path):
        raise ValueError("Output path does not exist.")
    if not isinstance(args.scan_device_removal, bool):
        raise ValueError("Scan device removal must be a boolean. Write 'True' or 'False'.")
    
    return args


def main():
    # Global Variable Definition
    SCRIPT_PATH = os.path.abspath(__file__)
    DATA_PATH = os.path.join(SCRIPT_PATH, "data")
    MNI_152_BONE = os.path.join(DATA_PATH, "MNI152_T1_1mm_bone.nii.gz")
    MNI_152_T1 = os.path.join(DATA_PATH, "MNI152_T1_1mm.nii.gz")
    BSPLINE_PATH = os.path.join(DATA_PATH, "Par0000bspline.txt")
    print(("Location of MNI152 bone image:" , MNI_152_BONE))
    
    # Argument parser configuration
    args = setup()

    ct_scan_path = args.ct_scan_path
    affine_matrix_name = ct_scan_path[:ct_scan_path.find(".nii.gz")]+"_affine.mat"

    # if you want to do ct scan removal 
    if "scan_device_removal" in vars(args):
        ct_scan_wodevice = CTtools.remove_ct_scan_device(ct_scan_path)
    else:
        ct_scan_wodevice = ct_scan_path
    
    # Extract bone from CT scan
    ct_scan_wodevice_bone = CTtools.bone_extracted(ct_scan_wodevice)

    # Register bone from CT scan to MNI152-bone. RIGID REGISTRATION
    call(["flirt",
          "-in", ct_scan_wodevice_bone,
          "-ref", MNI_152_BONE,
          "-omat", affine_matrix_name,
          "-bins", "256",
          "-searchrx", "-180", "180",
          "-searchry", "-180", "180",
          "-searchrz", "-180", "180",
          "-dof", "12",
          "-interp", "trilinear"])

    call(["flirt",
    "-in", ct_scan_wodevice,
    "-ref", MNI_152_T1,
    "-applyxfm",
    "-init", affine_matrix_name,
    "-out", ct_scan_wodevice[:ct_scan_wodevice.find(".nii.gz")]+"_MNI152.nii.gz"])

    # Perform contrast stretching in the ct scan without device
    ct_scan_wodevice_contrast_stretching = CTtools.contrast_stretch(ct_scan_wodevice)

    # Deformable Registration
    call(["flirt",
    "-in", ct_scan_wodevice_contrast_stretching,
    "-ref", MNI_152_T1,
    "-applyxfm",
    "-init", affine_matrix_name,
    "-out", ct_scan_wodevice_contrast_stretching[:ct_scan_wodevice_contrast_stretching.find(".nii.gz")]+"_MNI152.nii.gz"])

    call(["elastix",
          "-m", ct_scan_wodevice_contrast_stretching[:ct_scan_wodevice_contrast_stretching.find(".nii.gz")]+"_MNI152.nii.gz",
          "-f", MNI_152_T1,
          "-out", os.path.dirname(ct_scan_path),
          "-p", BSPLINE_PATH])
