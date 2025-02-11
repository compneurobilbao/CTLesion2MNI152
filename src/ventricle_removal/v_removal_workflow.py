import os
import sys
import matplotlib.pyplot as plt
import nibabel as nib
import nilearn.plotting as nip
import argparse
import numpy as np
import pandas as pd
import ventricle_removal.data as data

HELP_MESSAGE = (
    "Usage:\n"
    "ventricle_removal -p <PROJECT_PATH> "
    "-s <SUB_NAME> "
)

def arg_setup() -> argparse.Namespace:
    # Argument parser
    arg_parser = argparse.ArgumentParser(
        description="Ventricle removal of MNI152 Lesion Masks",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Add arguments
    arg_parser.add_argument(
        "-p",
        "--project_path",
        metavar="DIR",
        required=True,
        help="Path to project (in BIDS format).",
    )

    arg_parser.add_argument(
        "-s",
        "--sub_name",
        metavar="S",
        required=True,
        help="Name of the subject",
    )

    args = arg_parser.parse_args()

    # Check that arguments are correct
    if not os.path.exists(args.project_path):
        raise ValueError(
            f"Project path does not exist. (Could not find: {args.project_path})"
        )

    if not os.path.exists(os.path.join(args.project_path, args.sub_name)):
        raise ValueError(
            f"Folder for {args.sub_name} does not exist."
        )

    return args
    

def main() -> None:
    args = arg_setup()
    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        print(HELP_MESSAGE)
        sys.exit(1)
    ventricle_mask_ranges = ["35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89"]
    participants_tsv = pd.read_csv(os.path.join(args.project_path, "participants.tsv"), sep="\t")
    age = participants_tsv[participants_tsv["BIDS"] == args.sub_name]["AGE"].values[0]
    age_range_selected = None
    for ventricle_mask_range in ventricle_mask_ranges:
        if age >= int(ventricle_mask_range.split("-")[0]) and age <= int(ventricle_mask_range.split("-")[1]):
            age_range_selected = ventricle_mask_range
            break
        elif age < 35:
            age_range_selected = "35-39"
            break
        elif age > 89:
            age_range_selected = "85-89"
            break
    ventricle_mask = nib.load(os.path.join(data.VENTRICLES_PATH, f"{age_range_selected}_ventricles_MNI152.nii.gz"))
    les_mask_mni = nib.load(os.path.join(args.project_path, args.sub_name, "ct", "lesion_mask_MNI152.nii.gz"))
    les_mask_mni_novent = les_mask_mni.get_fdata() - ventricle_mask.get_fdata()
    les_mask_mni_novent_bin = nib.Nifti1Image((les_mask_mni_novent > 0).astype(np.int16), les_mask_mni.affine)
    nib.save(les_mask_mni_novent_bin, os.path.join(args.project_path, args.sub_name, "ct", "lesion_mask_mni_novent.nii.gz"))



if __name__ == "__main__":
    main()
