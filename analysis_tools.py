
import re
import numpy as np
import uproot as up
import awkward as ak
import vector
vector.register_awkward()
from dataclasses import dataclass

from typing import Any, Iterable

@dataclass(frozen=True)
class Metadata:
    polar_acceptance : float 
    azimuthal_acceptance : float 
    visible_BR : float 
    n_LLP : float 
    n_events_processed : float 
    n_events_scaled : float 
    coupling_squared : float 
    ctau : float 
    mass : float 
    scale_factor : float 

@dataclass(frozen=True)
class SampleRecord:
    mass: float
    coupling: float
    num: float
    hists: dict[str, Any]
    
def load_file(filename, treename = "LLP_tree;1", metaname = "Metadata;1", build = True):
    with up.open(filename) as f:
        data = f[treename].arrays()
        if metaname:
            meta = f[metaname].arrays()
        else:
            meta = None    
    if build: 
        return build_events(data), Metadata(**ak.to_list(meta)[0])
    else:
        return data, meta

def build_events(data):
    llp_p4 = ak.zip(
        {
            "px": data["px_llp"],
            "py": data["py_llp"],
            "pz": data["pz_llp"],
            "E":  data["e_llp"],
        },
        with_name="Momentum4D",
    )
    
    llp_vtx = ak.zip(
        {
            "x": data["vx"],
            "y": data["vy"],
            "z": data["vz"],
        },
        with_name="Position3D",
    )
    
    # --- daughters ---
    # infer how many daughter slots exist from branch names like px_prod1, px_prod2, ...
    prod_ids = sorted(
        int(m.group(1))
        for name in data.fields
        if (m := re.fullmatch(r"px_prod(\d+)", name))
    )
    max_dau = max(prod_ids)
    
    def stack(prefix):
        return np.stack([ak.to_numpy(data[f"{prefix}{i}"]) for i in range(1, max_dau + 1)], axis=1)
    
    px  = stack("px_prod")
    py  = stack("py_prod")
    pz  = stack("pz_prod")
    E   = stack("e_prod")
    pdg = stack("pdg_prod")
    
    ndau = ak.to_numpy(data["ndau"]).astype(np.int64)
    mask = np.arange(max_dau)[None, :] < ndau[:, None]   # True for valid daughters
    
    # flatten only valid daughter slots, then unflatten back to variable-length per event
    flat_daughters = ak.zip(
        {
            "p4": ak.zip(
                {
                    "px": ak.Array(px.reshape(-1)[mask.reshape(-1)]),
                    "py": ak.Array(py.reshape(-1)[mask.reshape(-1)]),
                    "pz": ak.Array(pz.reshape(-1)[mask.reshape(-1)]),
                    "E":  ak.Array(E.reshape(-1)[mask.reshape(-1)]),
                },
                with_name="Momentum4D",
            ),
            "pdg": ak.Array(pdg.reshape(-1)[mask.reshape(-1)]),
        },
        depth_limit=1,
    )
    
    daughters = ak.unflatten(flat_daughters, ndau)
    
    # --- full event record ---
    events = ak.zip(
        {
            "llp": llp_p4,
            "vtx": llp_vtx,
            "daughters": daughters,
            "ndau": data["ndau"],
            "decay_prob": data["decay_prob"],
        },
        depth_limit=1,
    )

    return events

