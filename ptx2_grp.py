#!/cm/shared/openmind/anaconda/1.9.2
import numpy as np
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#plt = mpl.pyplot
#import nibabel
import os
import scipy.stats

def collapse_probtrack_results(waytotal_file, matrix_file):
    with open(waytotal_file) as f:
        waytotal = int(f.read())
    #data = nibabel.load(matrix_file).get_data()
    data = np.loadtxt(matrix_file)
    collapsed = data.sum(axis=0) / waytotal * 100.
    return collapsed

lvdir_template = "/om/user/ksitek/STUT/fsdata/{subj}/label2vol/"
tddir_template = '/om/user/ksitek/STUT/tracula/{subj}/dlabel/diff/'
#ptdir_template = "/om/user/ksitek/STUT/ptx2/{subj}/targlist0814/"
ptdir_template = "/om/user/ksitek/STUT/ptx2/{subj}/targlist20160305/"

num_list = range(1,10)
num_str_list = map(str,num_list)
subj_list_1d = ['S0' + n for n in num_str_list]

num_list = range(10,40)
num_str_list = map(str,num_list)
subj_list_2d = ['S' + n for n in num_str_list]

outdir = '/om/user/ksitek/STUT/scripts/ptx2/conn_out_roi/'

# rh-inferiortemporal wasn't run by 0814 analysis,
# unknown why as of 8/23, but needs to be skipped:
# 2016-03-03: missing a line break at end of roi_list_reorder.
# Reran ptx2 with just rh-inferiortemporal as target
missing_target = [] #'wm-rh-inferiortemporal'

# added 9/4 to account for reordered data at the base level:
roi_num_reorder = np.loadtxt(outdir+'roi_num_reorder.txt')
roi_num_reorder = map(int,roi_num_reorder)
roi_list_reorder_txt = [line.rstrip() for line in open(outdir+'roi_list_reorder.txt')]
roi_list_reorder = []
for r in roi_list_reorder_txt:
    if r.startswith('wm-'):
        roi_list_reorder.append(r[3:])
    else:
        roi_list_reorder.append(r)

subjx = 0
for subj in subj_list_1d+subj_list_2d:
    lvdir = lvdir_template.format(subj=subj)
    tddir = tddir_template.format(subj=subj)
    ptdir = ptdir_template.format(subj=subj)

    #matrix_template = 'results/{roi}.nii.gz.probtrackx2/matrix_seeds_to_all_targets.nii.gz'
    matrix_template = ptdir+'{roi}/matrix_seeds_to_all_targets'
    processed_seed_list = [s.replace('.nii.gz','').replace('label/', '')
        #for s in open(lvdir+'seeds.txt').read().split('\n')
        for s in open(tddir+'aparc+aseg_filelist.txt').read().split('\n')
        if s]
    N = len(processed_seed_list) - len(missing_target) # -1 corrects for missing rh-inferiortemporal
    conn = np.zeros((N, N))
    rois=[]
    idx = 0

    if subjx == 0:
        conn_all = np.zeros((len(subj_list_1d+subj_list_2d), N, N))

    # per ROI - using the reordered list:
    for roi in roi_list_reorder_txt:
        #roi=xpath+r
        #roi=os.path.basename(roi)
        if roi != missing_target:
            matrix_file = matrix_template.format(roi=roi)
            seed_directory = os.path.dirname(matrix_file)
            #seed_directory = ptdir
            #roi = os.path.basename(seed_directory).replace('.nii.gz.probtrackx2', '')
            #roi = os.path.basename(seed_directory)
            waytotal_file = os.path.join(seed_directory, 'waytotal')
            rois.append(roi)
            try:
                # if this particular seed hasn't finished processing, you can still
                # build the matrix by catching OSErrors that pop up from trying
                # to open the non-existent files
                conn[idx, :] = collapse_probtrack_results(waytotal_file, matrix_file)
            except IOError:
                conn[idx, :] = np.nan
                pass
            idx += 1

    new_order = rois

    # save into group matrix USING REORDERED DATA
    conn_all[subjx,:,:] = conn[:,roi_num_reorder]
    subjx += 1
"""
with open(outdir+'roi_list.csv','wb') as file:
  for s in new_order:
    file.write(s + '\n')
"""

rx = 0
for r in rois:
    roi_dat = np.squeeze(conn_all[:,rx,:])
    np.savetxt(outdir+r+'.txt',roi_dat)
    rx += 1

pfs = [ 1,  2,  4, 10, 12, 13, 17, 18, 21, 22, 23, 24, 26, 29, 30, 31, 34, 37, 38]
pws = [ 0,  3,  5,  6,  7,  8,  9, 11, 14, 15, 16, 19, 20, 25, 27, 28, 32, 33, 35, 36]

pfs_dat = conn_all[pfs,:,:]
pfs_mat = scipy.stats.nanmean(pfs_dat)
np.savetxt(outdir+'pfs_mean.txt',pfs_mat)

pws_dat = conn_all[pws,:,:]
pws_mat = scipy.stats.nanmean(pws_dat)
np.savetxt(outdir+'pws_mean.txt',pws_mat)
