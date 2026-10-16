# Setup recent python and associated packages 
source /cvmfs/sft.cern.ch/lcg/views/LCG_110/x86_64-el9-gcc16-opt/setup.sh
export PYTHIA8_LIB=/user/software/Pythia8/pythia8317/lib

# Make output dir outside user dir
if [[ ! -z outputs ]]
then
    outdir=/hepstore/${USER}/SHIP/outputs
    mkdir -p $outdir
    ln -s $outdir outputs
fi 
