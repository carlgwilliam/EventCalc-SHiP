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

The first thing is to conver these to root files.  Each file can be converted with

`python convertEvtCalc.py -f <filename>.dat -m`

The output can be viewed with root or with the root plugin for VSCode and includes a tree of events, containing 4 vectors of the particles etc, and a tree of metadata.

To avoid having to learn root to process these, we can use the pure-python [uproot](https://githib.com/scikit-hep/uproot5) package, which behaves a bit like NumPy.  You can do this using e.g.

```
import analysis_tools as tools
events, meta = load_files(<filename>.root)

# 4 vector of ALP etc 
llps = events.llp

# 4 vectors of decay daughters (maybe more than 2)
daughter0 = events.daugthers[0] 
daughter1 = events.daugthers[1] 

# 3 vector of production vertices
vertices = events.vtx
```

To histogram the results, you pay also find the [uproot](https://githib.com/scikit-hep/hist) package useful.

