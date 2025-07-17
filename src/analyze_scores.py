# Script to analyze and visualize credit score distributions

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def load_scores(filepath: str) -> pd.DataFrame:
    # Load credit scores from CSV file
    return pd.read_csv(filepath)

def plot_score_distribution(scores: pd.Series, output_path: str = None):
    # Create a 2-panel figure showing score distribution
    plt.figure(figsize=(12, 6))
    
    # Left panel: Histogram with KDE
    plt.subplot(1, 2, 1)
    sns.histplot(scores, bins=20, kde=True)
    plt.title('Credit Score Distribution')
    plt.xlabel('Credit Score')
    plt.ylabel('Number of Wallets')
    
    # Right panel: Box plot
    plt.subplot(1, 2, 2)
    sns.boxplot(x=scores)
    plt.title('Credit Score Box Plot')
    plt.xlabel('Credit Score')
    
    plt.tight_layout()
    
    # Save or display the plot
    if output_path:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        plot_file = output_path / 'score_distribution.png'
        plt.savefig(plot_file)
        plt.close()
        return str(plot_file)
    else:
        plt.show()
        return None

def analyze_score_ranges(scores: pd.Series) -> str:
    # Categorize scores into ranges and calculate distribution
    bins = [0, 300, 500, 700, 850, 1000]
    labels = ['Very Poor (0-300)', 'Fair (301-500)', 'Good (501-700)', 
              'Very Good (701-850)', 'Excellent (851-1000)']
    
    # Bin the scores and count occurrences
    score_ranges = pd.cut(scores, bins=bins, labels=labels, right=False)
    range_counts = score_ranges.value_counts().sort_index()
    range_pct = (range_counts / len(scores) * 100).round(1)
    
    # Format results as markdown table
    analysis = "## Score Distribution by Range\n\n"
    analysis += "| Score Range | Wallets | Percentage |\n"
    analysis += "|-------------|---------|------------|\n"
    
    for (r, count), pct in zip(range_counts.items(), range_pct):
        analysis += f"| {r} | {count:,} | {pct}% |\n"
    
    return analysis

def main(input_file: str = None, output_dir: str = None):
    # If no arguments provided, use command line arguments
    if input_file is None or output_dir is None:
        parser = argparse.ArgumentParser(description='Analyze credit score distribution.')
        parser.add_argument('input', help='Path to the input CSV file with credit scores')
        parser.add_argument('-o', '--output', help='Directory to save analysis results')
        args = parser.parse_args()
        input_file = args.input
        output_dir = args.output
    
    # Create output directory if it doesn't exist
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the data
    print(f"Loading scores from {input_file}...")
    df = load_scores(input_file)
    
    # Basic info
    num_wallets = len(df)
    avg_score = df['credit_score'].mean()
    
    print(f"Analyzed {num_wallets:,} wallets")
    print(f"Average score: {avg_score:.2f}")
    
    # Analyze score ranges
    print("\nScore Range Analysis:")
    range_analysis = analyze_score_ranges(df['credit_score'])
    print(range_analysis)
    
    # Plot distribution
    plot_path = plot_score_distribution(df['credit_score'], str(output_dir) if output_dir else None)
    
    # Save analysis report if output directory is provided
    if output_dir:
        report_path = output_dir / 'analysis.md'
        with open(report_path, 'w') as f:
            f.write(f"# Credit Score Analysis\n\n")
            f.write(f"- **Total Wallets Analyzed**: {num_wallets:,}\n")
            f.write(f"- **Average Score**: {avg_score:.2f}\n")
            f.write("\n## Statistics\n")
            f.write(df['credit_score'].describe().to_markdown())
            f.write("\n\n## Score Ranges\n")
            f.write(range_analysis)
            f.write("\n\n## Visualization\n")
            f.write(f"![Score Distribution]({plot_path})\n")
        
        print(f"\nAnalysis report saved to {report_path}")
        return str(report_path)
    
    return None

if __name__ == "__main__":
    main()
