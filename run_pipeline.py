#!/usr/bin/env python3
# Aave Wallet Credit Scoring Pipeline
# Orchestrates the complete workflow from raw transactions to analysis

import argparse
from pathlib import Path
import sys

# Ensure src directory is in the path
sys.path.append(str(Path(__file__).parent / 'src'))

import credit_scoring
import analyze_scores

def main():
    # Set up command line interface
    parser = argparse.ArgumentParser(description='Run the complete Aave wallet credit scoring pipeline.')
    parser.add_argument('input', help='Path to the input JSON file with transaction data')
    parser.add_argument('-o', '--output-dir', default='results',
                      help='Directory to save output files (default: results/)')
    
    args = parser.parse_args()
    
    # Prepare output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scores_path = output_dir / 'wallet_scores.csv'
    
    print("=== Starting Aave Wallet Credit Scoring Pipeline ===\n")
    
    # 1. Calculate credit scores for all wallets
    print("=== Step 1: Calculating credit scores ===")
    credit_scoring.main(input_file=args.input, output=str(scores_path))
    
    # 2. Generate analysis and visualizations
    print("\n=== Step 2: Analyzing score distribution ===")
    analyze_scores.main(input_file=str(scores_path), output_dir=str(output_dir))
    
    print("\n=== Pipeline completed successfully! ===")
    print(f"Results saved to: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
