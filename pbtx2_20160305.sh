#!/bin/sh
# full region-to-region probabilistic tractography
# produces probtrackx2 scripts that are called in slurm for resource management
#  runs single seed region with full list of targets
# edited from _0717 based on meeting with Satra 8/13
# will stay in diffusion space by using parcellations made by tracula
# KRS 2014.08.14

tracdir=/om/user/ksitek/STUT/tracula/
fsdir=/om/user/ksitek/STUT/fsdata/

for subj in $fsdir/S*; do
#for subj in S24; do
  F=${subj:${#subj} - 3}

  tdiffdir=$tracdir/$F/dlabel/diff/
  tdvoldir=${tdiffdir}/aparc+aseg2mm/

  # use single seed regions, all regions as targets
  for lab in ${tdvoldir}*.nii.gz; do
  	labelname=${lab:${#tdvoldir}}
           #^^MUST ALTER IF CHANGE FOLDER NAMES--#a2009s=#a2aseg
          labelname=${labelname%.nii.gz}

      outdir=/om/user/ksitek/STUT/ptx2/$F/targlist20160305/$labelname/
  		mkdir $outdir --parents

   		# create a bash script and call with slurm for parallelization
  		echo '#!/bin/sh

  			' > $F.$labelname.sh
  		echo "probtrackx2 -s $tracdir$F/dmri.bedpostX/merged \
                   -m $tracdir$F/dmri.bedpostX/nodif_brain_mask.nii.gz \
                   -x $lab \
  		             --stop=${tdiffdir}cortex.bbr.nii.gz \
  		             --targetmasks=${tdiffdir}aparc+aseg_filelist.txt \
                   --omatrix1 --opd --pd --s2tastext --os2t \
                   --dir=$outdir \
                   --forcedir \
                   --seedref=$tracdir$F/dmri/brain_anat.nii.gz" >> $F.$labelname.sh
  		sbatch -n1 -c1 --mem=50000 $F.$labelname.sh
  done
done
