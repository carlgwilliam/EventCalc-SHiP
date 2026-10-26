# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright CERN for the benefit of the SHiP Collaboration

"""Convert files from EventCalc to ROOT format."""

import re
import os
import sys
from argparse import ArgumentParser

import numpy as np
import ROOT as r


def parse_file(infile: str, add_metadata: bool):
    """
    Parse the given text file and extracts process type, sample points, and variables.

    Parameters:
    infile (str): Path to the input text file.

    Returns:
    tuple: A tuple containing process type (str), sample points (int), and a list of numpy arrays for each variable.
    """

    try:
        with open(infile) as file:
            lines = file.readlines()
            meta   = lines[0]
            lines = lines[2:]
            
        parsed_data = []
        current_block = []
        process_type = None
        sampled_points = None

        for line in lines:
            if line.startswith("#<"):
                if current_block:
                    data = np.loadtxt(current_block)
                    variables = [data[:, i] for i in range(data.shape[1])]
                    current_block = []
                    header = line.strip()
                    process_type = header.split(";")[0].split("=")[1]
                    # print(f'Process type: {process_type}')
                    sampled_points = int(header.split(";")[1].split("=")[1][:-1])
                    # print(f'Sampled points: {sampled_points}')
                    parsed_data.append((process_type, sampled_points, variables))
            else:
                current_block.append(line.strip())

        if current_block:
            if process_type is None or sampled_points is None:
                raise ValueError("bin data encountered before any header")
            data = np.loadtxt(current_block)
            variables = [data[:, i] for i in range(data.shape[1])]
            parsed_data.append((process_type, sampled_points, variables))

        if add_metadata:
            pattern = (
                r'Sampled\s+(?P<finalEvents>[\d\.\+\-eE]+)\s+events inside SHiP volume\. '
                r'Squared coupling:\s+(?P<coupling_squared>[\d\.\+\-eE]+)\. '
                r'Total number of produced LLPs:\s+(?P<N_LLP_tot>[\d\.\+\-eE]+)\. '
                r'Polar acceptance:\s+(?P<epsilon_polar>[\d\.\+\-eE]+)\. '
                r'Azimuthal acceptance:\s+(?P<epsilon_azimuthal>[\d\.\+\-eE]+)\. '
                r'Averaged decay probability:\s+(?P<P_decay_averaged>[\d\.\+\-eE]+)\. '
                r'Visible Br Ratio:\s+(?P<br_visible_val>[\d\.\+\-eE]+)\. '
                r'Total number of events:\s+(?P<N_ev_tot>[\d\.\+\-eE]+)'
            )
            match = re.match(pattern, meta)
            # print(match)
            if match:
                finalEvents = float(match.group('finalEvents'))
                coupling_squared = float(match.group('coupling_squared'))
                N_LLP_tot = float(match.group('N_LLP_tot'))
                epsilon_polar = float(match.group('epsilon_polar'))
                epsilon_azimuthal = float(match.group('epsilon_azimuthal'))
                P_decay_averaged = float(match.group('P_decay_averaged'))
                br_visible_val = float(match.group('br_visible_val'))
                N_ev_tot = float(match.group('N_ev_tot'))
                print(f"finalEvents: {finalEvents}, coupling_squared: {coupling_squared}, N_LLP_tot: {N_LLP_tot}, epsilon_polar: {epsilon_polar}, "
                      f"epsilon_azimuthal: {epsilon_azimuthal}, P_decay_averaged: {P_decay_averaged}, "
                      f"br_visible_val: {br_visible_val}, N_ev_tot: {N_ev_tot}")

                mass, ctau = [float(x) for x in infile.split("/")[-1].split("_")[1:3]]
                
                metadata = {
                    "polar_acceptance" : epsilon_polar,
                    "azimuthal_acceptance" : epsilon_azimuthal,
                    "visible_BR" : br_visible_val,
                    "n_LLP"  : N_LLP_tot,
                    "n_events_processed" : finalEvents,
                    "n_events_scaled" : N_ev_tot,                    
                    "coupling_squared" : coupling_squared,
                    "ctau" : ctau,
                    "mass" : mass,
                    "scale_factor" : N_LLP_tot * epsilon_polar * epsilon_azimuthal / finalEvents
                    }

                return parsed_data, metadata
                
        return parsed_data

    except FileNotFoundError:
        print(f"- convertEvtCalc - Error: The file {infile} was not found.")
        return None
    except (ValueError, IndexError) as e:
        print(f"- convertEvtCalc - An error occurred: {e}")
        return None


def check_consistency_infile(nvars, ncols) -> None:
    """
    Check the consistency between number of columns in the input file (ncols) and variables (nvars).

    Parameters:
    nvars, ncols (int or float): The value to be checked. Must be equal.

    """
    if nvars != ncols:
        raise ValueError("Nr of variables does not match input file.")
    return


def convert_file(infile, outdir, add_metadata) -> str | None:
    """
    Create a ROOT file with a TTree containing the variables from the parsed input text file.

    Parameters:
    infile (str): Path to the input text file.
    outdir (str): Name of the output directory, the filename will be the same
                  as inputfile with the .dat replaced with .root.
    """
    vars_names = [
        "px_llp",
        "py_llp",
        "pz_llp",
        "e_llp",
        "mass_llp",
        "pdg_llp",
        "decay_prob",
        "vx",
        "vy",
        "vz",
    ]
    daughter_vars = [
        "px_prod",
        "py_prod",
        "pz_prod",
        "e_prod",
        "mass_prod",
        "pdg_prod",
    ]
    fname = infile.split("/")[-1]
    command = f"cp {infile} {outdir}/{fname}"

    if os.path.isfile(f"{outdir}/{fname}"):
        print(f"Warning: The file {outdir}/{fname} already exists.")
    else:
        os.system(command)

    infile = f"{outdir}/{fname}"
    parsed_data = parse_file(infile, add_metadata)

    if len(parsed_data) == 2:
        eventdata = parsed_data[0] 
        metadata = parsed_data[1]    
    else:
        eventdata = parsed_data
        metadata = None 
        
    if eventdata is None:
        # parse_file already reported the failure
        sys.exit(1)
    if not eventdata:
        print(f"- convertEvtCalc - Error: no completed blocks found in {infile}.")
        sys.exit(1)
    outfile = infile.split(".dat")[0] + ".root"
    ncols = len(eventdata[0][2])
    nvardau = 6  # qualifiers for each daughter
    remaining_vars = ncols - len(vars_names)

    if (remaining_vars % nvardau) != 0:
        raise ValueError("- convertEvtCalc - Error: number of daughters is not exact.")

    ndau = remaining_vars // nvardau
    print(f"- convertEvtCalc - Max multiplicity of daughters: {ndau}")

    vars_names.extend(f"{var}{i}" for i in range(1, ndau + 1) for var in daughter_vars)

    try:
        check_consistency_infile(nvars=len(vars_names), ncols=ncols)
    except ValueError as e:
        print(f"- convertEvtCalc - Error: {e}")
        sys.exit(1)

    vars_names += ["ndau"]

    root_file = r.TFile.Open(outfile, "RECREATE")
    
    if eventdata:
        tree = r.TTree("LLP_tree", "LLP_tree")

        branch_f = {}
        for var in vars_names:
            branch_f[var] = np.zeros(1, dtype=float)
            tree.Branch(var, branch_f[var], f"{var}/D")

        for pt, sp, vars in eventdata:
            for row in zip(*vars):
                for i, value in enumerate(row):
                    if i < len(vars_names) - 1:
                        branch_f[vars_names[i]][0] = value
                branch_f["ndau"][0] = ndau / 1.0
                tree.Fill()

        tree.Write()

    if metadata:
        metatree = r.TTree("Metadata", "Metadata")

        metabranch_f = {}
        for var, val in metadata.items():
            metabranch_f[var] = np.zeros(1, dtype=float)
            metatree.Branch(var, metabranch_f[var], f"{var}/D")
            metabranch_f[var][0] = val

        metatree.Fill()
        metatree.Write()
                    
    root_file.Close()
    print(f"- convertEvtCalc - ROOT file '{outfile}' created successfully.")
    return outfile


def main() -> None:
    """Convert files from EventCalc to ROOT format."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "-f",
        "--inputfile",
        help="""Simulation results to use as input."""
        """Supports retrieving file from EOS via the XRootD protocol.""",
        required=True,
    )
    parser.add_argument("-o", "--outputdir", help="""Output directory, must exist.""", default=".")
    parser.add_argument("-m", "--metadata", action="store_true", help="""Add metadata information to file.""", default=False)    
    args = parser.parse_args()
    print(f"Opening input file for conversion: {args.inputfile}")
    if not os.path.isfile(args.inputfile):
        raise FileNotFoundError("EvtCalc: input .dat file does not exist")
    if not os.path.isdir(args.outputdir):
        print(f"Warning: The specified directory {args.outputdir} does not exist. Creating it now.")
        command = f"mkdir {args.outputdir}"
        os.system(command)
    outputfile = convert_file(infile=args.inputfile, outdir=args.outputdir, add_metadata=args.metadata)
    print(f"{args.inputfile} successfully converted to {outputfile}.")


if __name__ == "__main__":
    main()
