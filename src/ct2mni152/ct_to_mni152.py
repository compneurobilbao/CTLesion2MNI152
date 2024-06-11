import os
from subprocess import call
import sys
import argparse

import ct2mni152.ct_tools as ct_tools
import ct2mni152.data as data

HELP_MESSAGE = ("Usage:\n"
               "ct2mni152 -p <CT_SCAN_PATH> "
               "-o <OUTPUT_PATH> "
               "[-sdr <SCAN_DEVICE_REMOVAL>(Default: True)]")


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
    arg_parser.add_argument("-nL", "--no_lesion_path",
                            metavar="DIR",
                            help="Path to the no lesion mask.",
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
    if len(sys.argv) == 1:
        print(HELP_MESSAGE)
        sys.exit(1)

    # Global Variable Definition
    MNI152_BONE_PATH = data.MNI152_BONE_PATH 
    MNI152_T1_PATH = data.MNI152_T1_PATH
    BSPLINE_PATH = data.BSPLINE_PATH
    print(("Location of MNI152 bone image:" , MNI152_BONE_PATH))
    
    # Argument parser configuration
    args = setup()

    ct_scan_path = args.ct_scan_path
    no_lesion_path = args.no_lesion_path
    affine_matrix_name = ct_scan_path[:ct_scan_path.find(".nii.gz")]+"_affine.mat"

    # if you want to do ct scan removal 
    if "scan_device_removal" in vars(args):
        ct_scan_wodevice = ct_tools.remove_ct_scan_device(ct_scan_path)
    else:
        ct_scan_wodevice = ct_scan_path
    
    # Extract bone from CT scan
    ct_scan_wodevice_bone = ct_tools.bone_extracted(ct_scan_wodevice)

    # Register bone from CT scan to MNI152-bone. RIGID REGISTRATION
    call(["flirt",
          "-in", ct_scan_wodevice_bone,
          "-ref", MNI152_BONE_PATH,
          "-omat", affine_matrix_name,
          "-bins", "256",
          "-searchrx", "-180", "180",
          "-searchry", "-180", "180",
          "-searchrz", "-180", "180",
          "-dof", "12",
          "-interp", "trilinear"])

    call(["flirt",
    "-in", ct_scan_wodevice,
    "-ref", MNI152_T1_PATH,
    "-applyxfm",
    "-init", affine_matrix_name,
    "-out", ct_scan_wodevice[:ct_scan_wodevice.find(".nii.gz")]+"_MNI152.nii.gz"])

    # Perform contrast stretching in the ct scan without device
    ct_scan_wodevice_contrast_stretching = ct_tools.contrast_stretch(ct_scan_wodevice)

    # Deformable Registration
    call(["flirt",
    "-in", ct_scan_wodevice_contrast_stretching,
    "-ref", MNI152_T1_PATH,
    "-applyxfm",
    "-init", affine_matrix_name,
    "-out", ct_scan_wodevice_contrast_stretching[:ct_scan_wodevice_contrast_stretching.find(".nii.gz")]+"_MNI152.nii.gz"])

    call(["elastix",
          "-m", ct_scan_wodevice_contrast_stretching[:ct_scan_wodevice_contrast_stretching.find(".nii.gz")]+"_MNI152.nii.gz",
          "-f", MNI152_T1_PATH,
          "-mMask", no_lesion_path,
          "-out", os.path.dirname(ct_scan_path),
          "-p", BSPLINE_PATH])


if __name__ == "__main__":
    main()
