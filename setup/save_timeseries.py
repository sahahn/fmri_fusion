import nibabel as nib
import numpy as np
import os
import sys
import glob
from conv import surf_parc_to_cifti
from nilearn.signal import clean
from BPt.extensions import SurfLabels, SurfMaps
import random

def proc_file(file, mapper, save_dr):

     # Get subject name
    name = file.split('/')[-1].split('_')[0].replace('sub-', '')

    # Gen save loc
    save_loc = os.path.join(save_dr, name + '.npy')

    # Check if already exists - if so skip
    if os.path.exists(save_loc):
        return

    # Load data
    data = nib.load(file).get_fdata()

    # Apply mapper
    data = mapper.fit_transform(data)

    # Run clean
    data = clean(signals=data,
                 detrend=True,
                 standardize='zscore')

    # Cast to float32
    data = data.astype('float32')
    
    # Save
    np.save(save_loc, data)


def save_modality(glob_path, mapper, save_dr):

    # Make sure directory exists
    os.makedirs(save_dr, exist_ok=True)
    
    # Get file then randomize
    files = glob.glob(glob_path)
    random.shuffle(files)
    
    # Proc. all files
    for file in files:
        proc_file(file, mapper, save_dr)

def get_parcel_loc(parcel_name):

    parcel_dr = '../parcels/'

    existing_parcels = os.listdir(parcel_dr)
    if parcel_name + '.npy' not in existing_parcels:
        os.system(f'wget https://raw.githubusercontent.com/sahahn/Parcs_Project/main/parcels/{parcel_name}.npy')
        os.system(f'mv {parcel_name}.npy ../parcels/')
    parcel_loc = os.path.join(parcel_dr, parcel_name + '.npy')

    return parcel_loc

def main():

    # Grab parcel loc from input
    parcel_name = str(sys.argv[1])
    parcel_loc = get_parcel_loc(parcel_name)
    
    # Define globbing path
    data_dr = '/home/sage/fmri_fusion/data/'
    base_glob1 = data_dr + 'derivatives/abcd-hcp-pipeline/sub-*/*/func/'
    base_glob = base_glob1 + 'sub-*_ses-baselineYear1Arm1_task-TASK_*.dtseries.nii'

    save_dr = '../data/timeseries/'
    
    # The different tasks
    tasks = ['MID', 'nback', 'rest', 'SST']
    
    # Grab example cifti file
    ex_cifti_file = glob.glob(base_glob.replace('TASK', tasks[0]))[0]

    # Load parcel into cifti space
    parc = surf_parc_to_cifti(ex_cifti_file, parcel_loc)

    # If static
    if len(parc.shape) == 1:
        mapper = SurfLabels(labels=parc, strategy='mean', vectorize=False)

    # If prob.
    else:
        mapper = SurfMaps(maps=parc, strategy='auto', vectorize=False)
    
    # Proc. each task
    for task in tasks:
        glob_path = base_glob.replace('TASK', task)
        save_modality(glob_path, mapper, os.path.join(save_dr, task.lower()))

if __name__ == '__main__':
    main()





