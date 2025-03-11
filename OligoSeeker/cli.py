"""Command-line interface for OligoSeeker"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_cli.ipynb.

# %% auto 0
__all__ = ['create_parser', 'validate_args', 'args_to_config', 'run_cli', 'main']

# %% ../nbs/04_cli.ipynb 4
import argparse
import sys
import logging
import os
from typing import List, Optional

from .pipeline import PipelineConfig, OligoCodonPipeline

# %% ../nbs/04_cli.ipynb 6
def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="OligoSeeker: Process FASTQ files to count oligo codons",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument('--f1', '--fastq_1', dest='fastq_path_1', required=True,
                        default="../test_fastq_files/test_1.fq.gz",
                        help="Path to FASTQ 1 file")
    
    parser.add_argument('--f2', '--fastq_2', dest='fastq_path_2', required=True,
                        default="../test_fastq_files/test_2.fq.gz",
                        help="Path to FASTQ 2 file")   
    
    # Oligo source (at least one required)
    oligo_group = parser.add_argument_group("Oligo Source Options (one required)")
    
    oligo_group.add_argument('--oligos-file', dest='oligos_file',
                           help="File containing oligo sequences (one per line)")
    
    oligo_group.add_argument('--oligos', dest='oligos_string',
                             default="GCGGATTACATTNNNAAATAACATCGT,TGTGGTAAGCGGNNNGAAAGCATTTGT,GTCGTAGAAAATNNNTGGGTGATGAGC",
                           help="Comma-separated list of oligo sequences")
    
    # Output options
    parser.add_argument('-o', '--output', dest='output_path', default="./results",
                        help="Output directory for results")
    
    parser.add_argument('--prefix', dest='output_prefix', default="",
                        help="Prefix for output files")
    
    parser.add_argument('--offset', dest='offset_oligo', type=int, default=1,
                        help="Value to add to oligo index in output")
    
    # Logging options
    parser.add_argument('--log-file', dest='log_file',
                        help="Path to log file (if not specified, logs to console only)")
    
    parser.add_argument('--log-level', dest='log_level', default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    
    return parser

# %% ../nbs/04_cli.ipynb 8
def validate_args(args: argparse.Namespace) -> bool:
    """Validate command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        True if arguments are valid, False otherwise
    """
    if not (args.oligos_file or args.oligos_string):
        print("Error: You must specify either --oligos-file or --oligos")
        return False
        
    if args.oligos_file and not os.path.exists(args.oligos_file):
        print(f"Error: Oligos file does not exist: {args.oligos_file}")
        return False
        
    if not os.path.exists(args.fastq_path_1):
        print(f"Error: FASTQ file 1 does not exist: {args.fastq_path_1}")
        return False
    
    if not os.path.exists(args.fastq_path_2):
        print(f"Error: FASTQ file 2 does not exist: {args.fastq_path_2}")
        return False        
    
    return True

# %% ../nbs/04_cli.ipynb 9
def args_to_config(args: argparse.Namespace) -> PipelineConfig:
    """Convert command-line arguments to pipeline configuration.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Pipeline configuration object
    """
    # Convert log level string to int
    log_level = getattr(logging, args.log_level)
    
    return PipelineConfig(
        fastq_1=args.fastq_path_1,
        fastq_2=args.fastq_path_2,
        oligos_file=args.oligos_file,
        oligos_string=args.oligos_string,
        oligos_list=None,  # Not used in CLI
        output_path=args.output_path,
        output_prefix=args.output_prefix,
        offset_oligo=args.offset_oligo,
        log_file=args.log_file,
        log_level=log_level
    )

# %% ../nbs/04_cli.ipynb 10
def run_cli(args: Optional[List[str]] = None) -> int:
    """Run the command-line interface.
    
    Args:
        args: Command-line arguments (if None, uses sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    
    # When testing, avoid sys.exit() errors by just returning the error code
    is_testing = 'ipykernel' in sys.modules or os.environ.get('NBDEV_TEST') == '1'
    
    try:
        parsed_args = parser.parse_args(args)
        
        if not validate_args(parsed_args):
            parser.print_help()
            return 1
        
        # Convert args to config
        config = args_to_config(parsed_args)
        
        # When testing, we might want to mock the pipeline run
        if is_testing and os.environ.get('MOCK_PIPELINE') == '1':
            print("Mock pipeline run (for testing)")
            return 0
            
        # Run pipeline
        pipeline = OligoCodonPipeline(config)
        results = pipeline.run()
        
        # Print summary information
        print("\nResults saved to:")
        print(f"  CSV: {results['csv_path']}")
        if 'excel_path' in results:
            print(f"  Excel: {results['excel_path']}")
        if 'json_path' in results:
            print(f"  Summary JSON: {results['json_path']}")
        
        print(f"\nProcessed {results['oligos_processed']} oligos in {results['elapsed_time']:.2f} seconds")
        
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    except SystemExit as e:
        # Catch SystemExit and just return the code instead of exiting
        if is_testing:
            print(f"Caught SystemExit: {e.code}")
            return e.code
        else:
            raise

# %% ../nbs/04_cli.ipynb 11
def main():
    """Main entry point for command-line execution."""
    # Only actually call sys.exit() when running as a script, not in tests or notebooks
    is_notebook_or_test = 'ipykernel' in sys.modules or 'pytest' in sys.modules or 'NBDEV_TEST' in os.environ
    
    # Use test arguments when in test/notebook environment
    if is_notebook_or_test:
        test_args = [
            '--f1', '../test_files/test_1.fq.gz',
            '--f2', '../test_files/test_2.fq.gz',
            '--oligos', 'GCGGATTACATTNNNAAATAACATCGT,TGTGGTAAGCGGNNNGAAAGCATTTGT,GTCGTAGAAAATNNNTGGGTGATGAGC',
            '--output', '../test_files/test_outs',
            '--prefix', 'test_cm1'
        ]
        run_cli(test_args)

        test_args = [
            '--f1', '../test_files/test_1.fq.gz',
            '--f2', '../test_files/test_2.fq.gz',
            '--oligos-file', '../test_files/oligos.txt',
            '--output', '../test_files/test_outs',
            '--prefix', 'test_cm2'
        ]
        run_cli(test_args)
        
        return 0
    else:
        return run_cli()

# %% ../nbs/04_cli.ipynb 12
#| eval: false
if __name__ == "__main__":
    # For safety, wrap in try/except to catch any SystemExit
    try:
        exit_code = main()
        is_notebook_or_test = 'ipykernel' in sys.modules or 'pytest' in sys.modules or 'NBDEV_TEST' in os.environ
        if is_notebook_or_test:
            print(f"\nCLI completed with exit code: {exit_code}")
    except SystemExit as e:
        # Just in case, catch any SystemExit and print instead
        print(f"\nSystemExit caught with code: {e.code}")
