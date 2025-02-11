## Background
Lesion Network Mapping (LNM) is a technique used to infer brain network disconnectivity after a brain injury. For running LNM it is necessary a lesion seed from the participant suffering a brain injury and functional/anatomical MRI normative data. It is usual, when using assistencial data, that the only brain image available from the patient is a computed tomography (CT). Furthermore, for running analyses on normative data, all the normative participants have to be in the same space and dimensions, usually following the MNI152 standard. The objective of this tool is to transform the lesion mask segmented on a CT scan, to the MNI152 standard.

## Description

We used the tool [CT2MNI152](https://github.com/pykao/CT2MNI152) as reference code, but modifying some features for simplifying and boosting the registration of the lesion segmented. Additionally, we added a second tool for removing the ventricles based on the age of the participant, because participants could be elder and the MNI152 is based on young participants, who have smaller ventricles.

## How to install `CTLesion2MNI152`

For running the code is recommended to use [docker](https://www.docker.com/) and it is not necessary to install the anything else. 

But it is possible to install the package if [fsl](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/) is already installed in your computer. For doing this, run in your terminal `git clone https://github.com/compneurobilbao/CTLesion2MNI152.git` Then `cd` into the `CTLesion2MNI152` folder, and `pip install .`

## How to use `CTLesion2MNI152`

Data should be stored in [BIDS format](https://bids.neuroimaging.io/), as follows:

```
/path/to/your/project/
participants.tsv
├──sub-XXX
│   ├── ct
│   │   ├── sub-XXX_ct.nii.gz
│   │   ├── sub-XXX_ct_lesion_mask.nii.gz
```

There are two main CLIs:

* **ct_lesion_to_mni152**: perform the registration of the CT lesion mask, to the MNI152 template. For running it execute:
```
docker run -v /path/to/your/project/:/project -it compneurobilbaolab/ct_lesion_to_mni152:1.1 ct_lesion_to_mni152 -p /project/sub-XXX/ct/sub-XXX_ct.nii.gz -l /project/sub-XXX/ct/sub-XXX_ct_lesion_mask.nii.gz -o /project/sub-XXX/ct

```

* **ventricle_removal** (*optional*): remove the overlap with the ventricles depending on the age of the participant. Is optional, but recommended if the lesion is near the ventricles. For running it execute:

```
docker run -v /path/to/your/project/:/project -it compneurobilbaolab/ct_lesion_to_mni152:1.1 ventricle_removal -p /project/ -s sub-XXX
```

## Outputs

* `sub-XXX_ct_MNI152.nii.gz` to check if the ct seems to be correctly registered to the MNI152 template.
* `sub-XXX_ct_lesion_mask_MNI152.nii.gz` the lesion mask in MNI152 template.
* `sub-XXX_ct_lesion_mask_MNI152_novent.nii.gz` the lesion mask in MNI152 template after ventricle removal.

## Reference paper: 

Kuijf, Hugo J., et al. "[Registration of brain CT images to an MRI template for the purpose of lesion-symptom mapping.](https://link.springer.com/content/pdf/10.1007%2F978-3-319-02126-3_12.pdf)" International Workshop on Multimodal Brain Image Analysis. Springer, Cham, 2013.


# LICENSE

MIT LICENSE


