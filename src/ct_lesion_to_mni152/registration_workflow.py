import os
from subprocess import call
import sys
import argparse
import numpy as np
import itk
import ct_lesion_to_mni152.data as data

HELP_MESSAGE = (
    "Usage:\n"
    "ct_lesion_to_mni152 -p <CT_SCAN_PATH> "
    "-o <OUTPUT_PATH> "
    "-l <LESION_MASK_PATH> "
)


def arg_setup() -> argparse.Namespace:
    # Argument parser
    arg_parser = argparse.ArgumentParser(
        description="CT lesion to MNI152 Registration",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Add arguments
    arg_parser.add_argument(
        "-p",
        "--ct_scan_path",
        metavar="DIR",
        required=True,
        help="Path to the CT scan.",
    )
    arg_parser.add_argument(
        "-o",
        "--output_path",
        metavar="DIR",
        help="Path to save the results folder.",
        required=True,
    )
    arg_parser.add_argument(
        "-l",
        "--lesion_mask_path",
        metavar="DIR",
        help="Path to the lesion mask.",
        required=True,
    )
    # Parse arguments
    args = arg_parser.parse_args()

    # Check that arguments are correct
    if not os.path.exists(args.ct_scan_path):
        raise ValueError(
            f"CT scan path does not exist. (Could not find: {args.ct_scan_path})"
        )
    if not os.path.exists(args.output_path):
        raise ValueError(
            f"Output path does not exist. (Could not find: {args.output_path})"
        )

    return args


def register_ct_and_lesion_to_mni152() -> None:
    # Print CLI help message if no arguments are provided or if "-h" or "--help" is provided
    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        print(HELP_MESSAGE)
        sys.exit(1)

    # Global Variable Definition
    MNI152_BONE_PATH = data.MNI152_BONE_PATH
    MNI152_T1_PATH = data.MNI152_T1_PATH
    MNI152_BRAIN_PATH = data.MNI152_BRAIN_PATH
    BSPLINE_PATH = data.BSPLINE_PATH
    print(("Location of MNI152 bone image:", MNI152_BONE_PATH))

    # Get CLI input arguments
    args = arg_setup()

    # Define CT scan, affine matrix, and lesion mask paths.
    ct_scan_path = args.ct_scan_path
    ct_scan_name = os.path.basename(ct_scan_path[: ct_scan_path.find(".nii.gz")])
    lesion_mask_path = args.lesion_mask_path
    lesion_name = os.path.basename(lesion_mask_path[: lesion_mask_path.find(".nii.gz")])
    affine_matrix_path = os.path.join(
        args.output_path,
        os.path.basename(ct_scan_name + "_affine.mat"),
    )
    print(ct_scan_path)
    call(
        [
        "fsl-cluster",
        "--in=" + ct_scan_path,
        "--thresh=100",
        "--no_table",
        "--minextent=100000",
        "--oindex=" + os.path.join(args.output_path, ct_scan_name + "_skull_clusters.nii.gz"),
        "--osize=" + os.path.join(args.output_path, ct_scan_name + "_skull_cluster_sizes.nii.gz"),
        ]
    )
    skull_cluster_size = np.max(itk.array_from_image(itk.imread(os.path.join(args.output_path, ct_scan_name + "_skull_cluster_sizes.nii.gz"), itk.F)).flatten())
    call([
        "fslmaths",
        os.path.join(args.output_path, ct_scan_name + "_skull_cluster_sizes.nii.gz"),
        "-thr",
        str(skull_cluster_size),
        "-uthr",
        str(skull_cluster_size),
        "-bin",
        os.path.join(args.output_path, ct_scan_name + "_skull_mask.nii.gz"),
    ])
    call([
        "fslmaths",
        ct_scan_path,
        "-mas",
        os.path.join(args.output_path, ct_scan_name + "_skull_mask.nii.gz"),
        os.path.join(args.output_path, ct_scan_name + "_skull.nii.gz"),
    ])
    call([
        "fslmaths",
        ct_scan_path,
        "-thr",
        str(0),
        "-uthr",
        str(100),
        os.path.join(args.output_path, ct_scan_name + "_HU.nii.gz"),
    ])
    # Register bone from CT scan to MNI152-bone.
    # Compute registration Affine
    call(
        [
            "flirt",
            "-in",
            os.path.join(args.output_path, ct_scan_name + "_skull.nii.gz"),
            "-ref",
            MNI152_BONE_PATH,
            "-omat",
            affine_matrix_path,
            "-bins",
            "256",
            "-searchrx",
            "-180",
            "180",
            "-searchry",
            "-180",
            "180",
            "-searchrz",
            "-180",
            "180",
            "-dof",
            "12",
            "-interp",
            "trilinear",
        ]
    )

    ct_HU = os.path.join(
        args.output_path, f"{ct_scan_name}_HU.nii.gz"
    )

    call(
        [
            "fslmaths",
            ct_scan_path,
            "-thr",
            "0", 
            "-uthr", 
            "100",
            ct_HU,
        ]
    )
    
    # Deformable Registration (output path)
    ct_pre_mni = os.path.join(
        args.output_path, f"{ct_scan_name}_pre_mni.nii.gz"
    )

    call(
        [
            "flirt",
            "-in",
            ct_HU,
            "-ref",
            MNI152_T1_PATH,
            "-applyxfm",
            "-init",
            affine_matrix_path,
            "-out",
            ct_pre_mni,
        ]
    )

    # Applies affine transform generated between subject space skull and MNI152 skull to the lesion mask
    lesion_pre_mni = os.path.join(
        args.output_path, f"{lesion_name}_pre_mni.nii.gz"
    )
    call(
        [
            "flirt",
            "-in",
            lesion_mask_path,
            "-ref",
            MNI152_T1_PATH,
            "-applyxfm",
            "-init",
            affine_matrix_path,
            "-interp",
            "nearestneighbour",
            "-out",
            lesion_pre_mni,
        ]
    )
    nolesion_pre_mni = os.path.join(
        args.output_path, f"no_{lesion_name}_pre_mni.nii.gz"
    )
    call(
        [
            "fslmaths",
            ct_pre_mni,
            "-bin",
            "-sub",
            lesion_pre_mni,
            nolesion_pre_mni,
        ]
    )
    # Load images with ITK
    no_lesion_mask_im = itk.imread(nolesion_pre_mni, itk.UC)
    ct_pre_mni_im = itk.imread(ct_pre_mni, itk.F)
    mni_template_im = itk.imread(MNI152_BRAIN_PATH, itk.F)
    lesion_mask_pre_mni_im = itk.imread(lesion_pre_mni, itk.F)

    # Load BSpline parameter object
    transform_param_object = itk.ParameterObject.New()
    transform_param_object.ReadParameterFile(BSPLINE_PATH)

    # Compute registration between preMNI and MNI152 of the CT, with elastix
    _, pre_mni_2_mni_transform = itk.elastix_registration_method(
        mni_template_im,
        ct_pre_mni_im,
        moving_mask=no_lesion_mask_im,
        parameter_object=transform_param_object,
        output_directory=args.output_path,
        log_to_console=True,
    )

    # Apply the transform to the CT scan that is in the preMNI space and save it.
    ct_registered_mni152 = itk.transformix_filter(
        ct_pre_mni_im, pre_mni_2_mni_transform
    )
    ct_mni152_fname = os.path.join(
        args.output_path,
        ct_scan_name + "_MNI152.nii.gz",
    )
    itk.imwrite(ct_registered_mni152, ct_mni152_fname)

    # Modify parameters in BSpline transform to perform NearestNeighbor interpolation
    pre_mni_2_mni_transform.SetParameter("FinalBSplineInterpolationOrder", "0")

    # Apply the transform to the lesion mask that is in the preMNI space and save it.
    lesion_registered_mni152 = itk.transformix_filter(
        lesion_mask_pre_mni_im, pre_mni_2_mni_transform
    )
    lesion_mni15_fname = os.path.join(
        args.output_path,
        lesion_name + "_MNI152.nii.gz",
    )
    itk.imwrite(lesion_registered_mni152, lesion_mni15_fname)

def main() -> None:
    register_ct_and_lesion_to_mni152()


if __name__ == "__main__":
    main()
