import nibabel as nib
import numpy as np
from nibabel.cifti2 import Cifti2BrainModel


def load_parc(parcel_file):
    '''Loads parcel from either numpy or nifti format'''

    if parcel_file.endswith('.npy'):
        return np.load(parcel_file)
    
    return np.array(nib.load(parcel_file).get_fdata())


def remove_medial_wall(fill_cifti, parcel, index_map):

    for index in index_map:
        if isinstance(index, Cifti2BrainModel):
            if index.surface_number_of_vertices is not None:
                inds = index.index_offset + np.array(index.vertex_indices._indices)
                fill_cifti[index.index_offset: index.index_offset+index.index_count] = parcel[inds]

    return fill_cifti

def add_subcortical(fill_cifti, index_map):
    '''Assumes base parcel already added'''

    # Start at 1 plus last
    cnt = np.max(np.unique(fill_cifti)) + 1

    for index in index_map:
        if isinstance(index, Cifti2BrainModel):
            
            # If subcort volume
            if index.surface_number_of_vertices is None:
                
                start = index.index_offset 
                end = start + index.index_count
                fill_cifti[start:end] = cnt
                cnt += 1

    return fill_cifti

def static_parc_to_cifti(parcel, index_map):

    # Init empty cifti with zeros
    fill_cifti = np.zeros(91282)

    # Apply cifti medial wall reduction to parcellation
    fill_cifti = remove_medial_wall(fill_cifti, parcel, index_map)
    
    # Add subcortical structures as unique parcels next
    fill_cifti = add_subcortical(fill_cifti, index_map)

    return fill_cifti


def get_cort_slabs(parcel, index_map):
    '''Prob. case'''
    
    cort_slabs = []
    for i in range(parcel.shape[1]):
        slab = np.zeros(91282)
        slab = remove_medial_wall(slab, parcel[:, i], index_map)
        cort_slabs.append(slab)
        
    return cort_slabs
        

def get_subcort_slabs(index_map):
    'Prob. case'
    
    subcort_slabs = []

    for index in index_map:
        if isinstance(index, Cifti2BrainModel):
            if index.surface_number_of_vertices is None:

                slab = np.zeros(91282)
                
                start = index.index_offset 
                end = start + index.index_count
                slab[start:end] = 1
                
                subcort_slabs.append(slab)
                
    return subcort_slabs


def prob_parc_to_cifti(parcel, index_map):
    'Prob. case'

    cort_slabs = get_cort_slabs(parcel, index_map)
    subcort_slabs = get_subcort_slabs(index_map)
    
    return np.stack(cort_slabs + subcort_slabs, axis=1)


def surf_parc_to_cifti(cifti_file, parcel_file):
    '''For now just works when parcel file is a parcellation
    in combined fs_LR_32k lh+rh space with medial wall included.
    Works for static or prob.'''

    # Get index map from example cifti file
    index_map = nib.load(cifti_file).header.get_index_map(1)

    # Load parcel
    parcel = load_parc(parcel_file)
    
    # Probabilistic case
    if len(parcel.shape) > 1:
        return prob_parc_to_cifti(parcel, index_map)

    # Static case
    return static_parc_to_cifti(parcel, index_map)
