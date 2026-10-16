# Installation and setup

## Logon to Liverpool HEP macines
`ssh <username>@theta.ph.liv.ac.uk`

## First time only, checkout package
`git clone https://github.com/carlgwilliam/EventCalc-SHiP`

## Each time logon, change to that dir and run setup
```
cd EventCalc-SHiP
source setup.sh
```

# Outline of work

## 1. Try to run one point of a given model e.g. ALP-photon

### Run example mass / coupling point and look at output
`python simulate.py --model ALP-photon --events 100000 --masses 0.02 --couplings 1e-5 --alp-production-mode primary`

## 2. Run full mass-coupling scan for that model

Edit examples/coupling_scan.py to update events to 100000 then run

`python examples/coupling_scan.py > ALPPhoton.json`

Look at scan card and try to understand

Run Simulation

`python simulate.py --card ALPPhoton.json`

Look at total outputs in `outputs/<model>/total/`

Plot the number of events vs mass and coupling, then try reproduce the exclusion limit in Fig 50 (d) of CERN-SPSC-2023-033

## 3. Start to add in a small number of background events by hand

## 4. Investigate at other models as above

## 5. Move on to looking at kinematics of events
These can be found in `output/<model>/eventData`
