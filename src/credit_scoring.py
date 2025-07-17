# Aave Wallet Credit Scoring System
# Calculates credit scores for Aave wallet addresses based on transaction history

# Standard library imports
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union

# Third-party imports
import pandas as pd
import numpy as np
from tqdm import tqdm

# Scoring parameters
BASE_SCORE = 500
MAX_SCORE = 1000
MIN_SCORE = 0
ACTIVITY_MAX_POINTS = 200
LONGEVITY_MAX_POINTS = 100
DIVERSITY_MAX_POINTS = 100
LIQUIDATION_PENALTY = 100
DEPOSIT_BONUS = 50

class AaveCreditScorer:
    # Handles credit score calculation for Aave wallets
    
    def __init__(self, data_path: Optional[str] = None) -> None:
        self.data_path = data_path
        self.transactions: Optional[pd.DataFrame] = None
        self.wallet_scores: Dict[str, float] = {}
    
    def _load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        # Load and parse JSON transaction data
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # Convert raw transaction data into proper types
        df = df.copy()
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
        if 'actionData.amount' in df.columns:
            # Convert amount to float, coerce errors to NaN
            df['amount'] = pd.to_numeric(df['actionData.amount'], errors='coerce')
            
        return df
    
    def load_data(self, data_path: Optional[str] = None) -> pd.DataFrame:
        # Load transaction data from JSON file and preprocess it
        data_path = data_path or self.data_path
        if not data_path:
            raise ValueError("No data path provided")
            
        print(f"Loading data from {data_path}...")
        try:
            raw_data = self._load_json_file(data_path)
            df = pd.json_normalize(raw_data)
            df = self._preprocess_dataframe(df)
            
            print(f"Loaded {len(df)} transactions for {df['userWallet'].nunique()} unique wallets")
            self.transactions = df
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load data: {str(e)}")
    
    def _calculate_time_features(self, wallet_txs: pd.DataFrame) -> Dict[str, float]:
        # Calculate time-based metrics for transaction patterns
        txs = wallet_txs.sort_values('timestamp')
        time_diffs = txs['timestamp'].diff().dt.total_seconds().dropna()
        
        return {
            # Average hours between transactions
            'tx_frequency_hrs': time_diffs.mean() / 3600 if not time_diffs.empty else 0,
            # Total days between first and last transaction
            'active_days': (txs['timestamp'].max() - txs['timestamp'].min()).days or 1,
            # Average transactions per day
            'tx_per_day': len(txs) / max(1, (txs['timestamp'].max() - txs['timestamp'].min()).days),
        }
    
    def _calculate_action_features(self, wallet_txs: pd.DataFrame) -> Dict[str, float]:
        # Calculate action distribution and diversity metrics
        action_counts = wallet_txs['action'].value_counts().to_dict()
        total_actions = len(wallet_txs)
        
        # Calculate action ratios and diversity index
        return {
            **action_counts,  # Raw counts per action type
            **{f"{action}_ratio": count / total_actions 
               for action, count in action_counts.items()},  # Action type ratios
            'action_diversity': len(action_counts) / total_actions if total_actions > 0 else 0  # 1.0 = all actions unique
        }
    
    def _calculate_amount_features(self, wallet_txs: pd.DataFrame) -> Dict[str, float]:
        # Calculate transaction amount statistics
        if 'amount' not in wallet_txs.columns:
            return {}
            
        amounts = wallet_txs['amount'].dropna()
        if amounts.empty:
            return {}
            
        return {
            'total_amount': amounts.sum(),  # Total volume
            'avg_amount': amounts.mean(),   # Average transaction size
            'max_amount': amounts.max(),    # Largest transaction
            'amount_std': amounts.std() if len(amounts) > 1 else 0,  # Transaction size volatility
        }
    
    def calculate_wallet_features(self, wallet_address: str) -> Dict[str, float]:
        # Extract all features for a given wallet
        if self.transactions is None:
            raise ValueError("No transaction data loaded. Call load_data() first.")
            
        wallet_txs = self.transactions[self.transactions['userWallet'] == wallet_address]
        if wallet_txs.empty:
            return {}
        
        # Initialize with basic transaction metrics
        features = {
            'total_transactions': len(wallet_txs),
            'unique_assets': wallet_txs['actionData.assetSymbol'].nunique(),
            'unique_actions': wallet_txs['action'].nunique(),
        }
        
        # Add time-based features if available
        if 'timestamp' in wallet_txs.columns:
            features.update(self._calculate_time_features(wallet_txs))
            
        # Add derived features
        features.update(self._calculate_action_features(wallet_txs))
        features.update(self._calculate_amount_features(wallet_txs))
        
        return features
    
    def _calculate_activity_score(self, features: Dict[str, float]) -> float:
        # Score based on transaction volume (capped at ACTIVITY_MAX_POINTS)
        return min(ACTIVITY_MAX_POINTS, features.get('total_transactions', 0) * 0.5)
    
    def _calculate_longevity_score(self, features: Dict[str, float]) -> float:
        # Reward long-term participation (2 points per active day, capped at 100)
        return min(LONGEVITY_MAX_POINTS, features.get('active_days', 0) * 2)
    
    def _calculate_diversity_score(self, features: Dict[str, float]) -> float:
        # Reward asset diversity (20 points per unique asset, capped at 100)
        return min(DIVERSITY_MAX_POINTS, features.get('unique_assets', 0) * 20)
    
    def _calculate_behavior_adjustment(self, features: Dict[str, float]) -> float:
        # Apply behavior-based score adjustments
        adjustment = 0.0
        
        # Reward conservative behavior (more deposits than borrows)
        if features.get('deposit_ratio', 0) > 0.5:
            adjustment += DEPOSIT_BONUS
            
        # Penalize liquidations
        if features.get('liquidationcall', 0) > 0:
            adjustment -= LIQUIDATION_PENALTY
            
        return adjustment
    
    def calculate_credit_score(self, wallet_address: str) -> float:
        # Calculate a credit score (0-1000) for a wallet address
        if wallet_address in self.wallet_scores:
            return self.wallet_scores[wallet_address]
            
        features = self.calculate_wallet_features(wallet_address)
        if not features:
            return MIN_SCORE
        
        # Start with base score and add components
        score = BASE_SCORE  # 500 points
        score += self._calculate_activity_score(features)     # Up to 200
        score += self._calculate_longevity_score(features)    # Up to 100
        score += self._calculate_diversity_score(features)    # Up to 100
        score += self._calculate_behavior_adjustment(features)  # Bonuses/penalties
        
        # Enforce score boundaries (0-1000)
        score = max(MIN_SCORE, min(MAX_SCORE, score))
        self.wallet_scores[wallet_address] = score
        return score
    
    def score_all_wallets(self, output_path: Optional[str] = None) -> pd.DataFrame:
        # Generate credit scores for all unique wallets
        if self.transactions is None:
            raise ValueError("No transaction data loaded. Call load_data() first.")
            
        wallets = self.transactions['userWallet'].unique()
        results = []
        
        print(f"Calculating scores for {len(wallets):,} wallets...")
        for wallet in tqdm(wallets, desc="Scoring wallets"):
            score = self.calculate_credit_score(wallet)
            results.append({'wallet': wallet, 'credit_score': score})
        
        results_df = pd.DataFrame(results)
        
        # Save results if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            results_df.to_csv(output_path, index=False)
            print(f"Saved results to {output_path}")
            
        return results_df


def parse_arguments() -> argparse.Namespace:
    # Set up and parse command line arguments
    parser = argparse.ArgumentParser(
        description='Calculate credit scores for Aave wallet addresses.'
    )
    parser.add_argument(
        'input_file', 
        type=str, 
        help='Path to the input JSON file containing transaction data'
    )
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        help='Path to save the output CSV file',
        default='results/wallet_scores.csv'
    )
    return parser.parse_args()


def print_score_summary(results_df: pd.DataFrame) -> None:
    # Display key statistics about the calculated scores
    print("\nScore Summary:")
    print(f"Total wallets scored: {len(results_df):,}")
    print(f"Average score: {results_df['credit_score'].mean():.2f}")
    print(f"Min score: {results_df['credit_score'].min():.2f}")
    print(f"Max score: {results_df['credit_score'].max():.2f}")
    print(f"Median score: {results_df['credit_score'].median():.2f}")


def main(input_file: str = None, output: str = None) -> None:
    # Main entry point for the credit scoring pipeline
    if input_file is None or output is None:
        # If no arguments provided, use command line arguments
        args = parse_arguments()
        input_file = args.input_file
        output = args.output
    
    try:
        scorer = AaveCreditScorer()
        scorer.load_data(input_file)
        results_df = scorer.score_all_wallets(output)
        print_score_summary(results_df)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
