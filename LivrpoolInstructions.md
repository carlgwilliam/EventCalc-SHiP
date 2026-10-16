# Logon to Liverpool HEP macines
ssh <username>@phi.ph.liv.ac.uk

# First time only, checkout package
git clone https://github.com/carlgwilliam/EventCalc-SHiP

# Change to that dir 
cd EventCalc-SHiP

# Run setup
source setup.sh

# 1. Try to run one point of a given model e.g. ALP-photon

## Run example mass / coupling point and look at output
`python simulate.py --model ALP-photon --events 100000 --masses 0.02 --couplings 1e-5 --alp-production-mode primary`

# 2. Run full mass-coupling scan for that model

## Edit examples/coupling_scan.py to update events to 100000 then run
`python examples/coupling_scan.py > ALPPhoton.json`

## Look at scan card to understand

## Run Simulate
`python simulate.py --card ALPPhoton.json`

## Plot the result and reproduce the scan in Fig 50 (d) of CERN-SPSC-2023-033

# 3. Start to add in a small number of background events

# 4. Investigate at other models

# 5. Move on to looking at kinematics of events 
