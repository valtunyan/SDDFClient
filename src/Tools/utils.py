from psikit import Psikit

import numpy as np

from src.constants import *

def get_argument_suggestion(pool_processes=1):
    return {
        'threads' : max(1, AVAILABLE_CPU_COUNT // pool_processes), 
        'memory' : AVAILABLE_MEMORY_IN_GB / pool_processes
    }

def create_runner(pool_processes=1):
    return Psikit(**get_argument_suggestion(pool_processes))

def read_coordinates(mol_block: str):
    lines = mol_block.split("\n")
    counts_line = lines[3]

    if counts_line.strip().endswith("V3000"):
        coordinate_lines = []
        atoms_block = False

        for line in lines:
            if line.strip() == "M  V30 BEGIN ATOM":
                atoms_block = True
            elif line.strip() == "M  V30 END ATOM":
                atoms_block = False
            elif atoms_block:
                coordinate_lines.append(line)
        
        coordinates = np.array([
            list(map(float, line.split()[4:7]))
            for line in coordinate_lines
        ])

    else:
        atom_count = int(counts_line.strip()[:3])
        
        coordinate_lines = lines[4:4 + atom_count]
        coordinates = np.array([
            list(map(float, line.split()[:3]))
            for line in coordinate_lines
        ])

    return coordinates

def get_obj_to_block_mapping(mol, mol_block):
    mol_block_coords = read_coordinates(mol_block)
    mol_obj_coords = mol.GetConformer().GetPositions()

    mapping = sorted(list(zip(*np.where(np.linalg.norm(mol_block_coords[:, None, :] - mol_obj_coords[None, :, :], axis=-1) == 0))))
    return np.array([pair[1] for pair in mapping])
