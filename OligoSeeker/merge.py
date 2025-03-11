"""Functions for merging multiple count CSV files"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_merge.ipynb.

# %% auto 0
__all__ = ['merge_count_csvs']

# %% ../nbs/05_merge.ipynb 3
import os
import pandas as pd
import glob
from pathlib import Path
from typing import List, Optional

# %% ../nbs/05_merge.ipynb 5
def merge_count_csvs(input_dir: str, output_file: str = None, output_dir: str = None, 
                     pattern: str = "*count*.csv") -> pd.DataFrame:
    """Merge multiple count CSV files by summing values.
    
    Args:
        input_dir: Directory containing count CSV files
        output_file: Path to save the merged CSV (if full path provided)
        output_dir: Directory to save the output (if output_file is just a filename)
        pattern: Glob pattern to match count files (default: "*count*.csv")
        
    Returns:
        DataFrame with merged counts
    """
    # Find all matching CSV files
    csv_files = glob.glob(os.path.join(input_dir, pattern))
    
    if not csv_files:
        raise ValueError(f"No CSV files matching pattern '{pattern}' found in {input_dir}")
    
    print(f"Found {len(csv_files)} CSV files to merge")
    
    # Read all CSVs
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file, index_col=0)
        print(f"  Loaded {file} with {len(df)} rows and {len(df.columns)} columns")
        dfs.append(df)
    
    # Merge by summing values for each codon and oligo
    merged_df = pd.concat(dfs).groupby(level=0).sum()
    
    # Determine output location
    if output_file:
        if output_dir:
            # Both output_dir and output_file provided - combine them
            final_output_path = os.path.join(output_dir, output_file)
        else:
            # Just output_file - might be a full path or just a filename
            if os.path.dirname(output_file):
                # It's a full path
                final_output_path = output_file
            else:
                # Just a filename - save to input_dir
                final_output_path = os.path.join(input_dir, output_file)
    else:
        # No output_file specified - use default filename
        if output_dir:
            # Use output_dir with default filename
            final_output_path = os.path.join(output_dir, "merged_counts.csv")
        else:
            # Use input_dir with default filename
            final_output_path = os.path.join(input_dir, "merged_counts.csv")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(final_output_path)), exist_ok=True)
    
    # Save merged data
    merged_df.to_csv(final_output_path)
    print(f"Merged data saved to {final_output_path}")
    
    return merged_df
