# Aave Wallet Credit Scoring

A comprehensive system for calculating and analyzing credit scores for Aave wallet addresses based on their on-chain transaction history. This project helps assess the creditworthiness of wallets interacting with the Aave protocol.

## 📊 Features

- **Data Processing**: Efficiently load and process raw Aave transaction data
- **Feature Engineering**: Extract meaningful features from transaction history
- **Credit Scoring**: Calculate credit scores (0-1000) based on transaction behavior
- **Analysis & Visualization**: Generate detailed reports and visualizations
- **Modular Design**: Easy to extend with custom scoring models
- **Rule-based System**: Transparent and explainable scoring methodology

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Reproduction

1. Clone the repository:
   ```bash
   git clone https://github.com/pragyajhaa/wallet_credit_scoring.git
   cd wallet_credit_scoring
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the pipeline:
   ```bash
   python src/run_pipeline.py data/raw/user-wallet-transactions.json -o results
   ```

## Scoring Methodology

The credit scoring system (0-1000) evaluates wallet behavior using these key factors:

- **Base Score (500 points)**: Starting point for all wallets
- **Activity (up to 200 points)**: Rewards consistent transaction history (0.5 points per transaction, capped at 200)
- **Longevity (up to 100 points)**: Values long-term participation (2 points per active day, capped at 100)
- **Diversity (up to 100 points)**: Encourages multiple asset interactions (20 points per unique asset, capped at 100)
- **Behavior Adjustments**:
  - **+50 points** for maintaining a deposit ratio >50%
  - **-100 points** for any liquidation events

Scores are bounded between 0 and 1000, with higher scores indicating more reliable borrowing behavior.

## 🛠 Usage

### Run the Complete Pipeline

To process the data, calculate scores, and generate analysis:

```bash
python run_pipeline.py data/raw/user-wallet-transactions.json -o results
```

### Individual Components

1. **Calculate Credit Scores**:
   ```bash
   python src/credit_scoring.py data/raw/user-wallet-transactions.json -o results/wallet_scores.csv
   ```

2. **Analyze Results**:
   ```bash
   python src/analyze_scores.py results/wallet_scores.csv -o results/
   ```

## 📈 Methodology

### Feature Engineering

For each wallet, we calculate comprehensive features including:

- **Activity Metrics**:
  - Total transactions
  - Unique assets interacted with
  - Transaction frequency
  - Active days (longevity)
  - Time between transactions

- **Action Analysis**:
  - Count of each action type (deposit, borrow, repay, etc.)
  - Action diversity (Shannon entropy)
  - Action ratios and patterns
  - Liquidation history

- **Financial Behavior**:
  - Total/avg/max transaction amounts
  - Deposit-to-borrow ratios
  - Collateralization patterns
  - Asset concentration

### Scoring Model

The credit score (0-1000) is calculated using a transparent, rule-based approach:

| Component            | Points | Description                                                                 |
|----------------------|--------|-----------------------------------------------------------------------------|
| Base Score           | 500    | Starting point for all wallets                                             |
| Activity Score       | 0-200  | Based on transaction volume and frequency                                  |
| Longevity Score      | 0-100  | Rewards long-term participation (150+ days = max points)                   |
| Diversity Score      | 0-100  | Based on number of unique assets and protocols used                        |
| Behavior Adjustments | ±100   | Bonuses for good behavior (e.g., consistent repayments), penalties for risks |

### Key Factors Affecting Scores

- **Positive Factors**:
  - Long account history
  - Diverse asset allocation
  - Consistent repayment patterns
  - Conservative borrowing
  - Active participation

- **Negative Factors**:
  - Liquidations (-100 points each)
  - Short-term activity
  - High concentration in single assets
  - Risky borrowing behavior

## 📂 Project Structure

```
aave-wallet-credit-scoring/
├── data/
│   ├── raw/                   # Raw transaction data
│   └── processed/             # Processed datasets
├── results/                   # Output files (scores, visualizations)
│   ├── wallet_scores.csv      # Generated credit scores
│   ├── score_distribution.png # Score distribution plot
│   └── analysis.md            # Detailed analysis report
├── src/
│   ├── credit_scoring.py      # Core scoring logic
│   ├── analyze_scores.py      # Analysis and visualization
│   └── 1_data_processing.py   # Data processing utilities
├── requirements.txt           # Python dependencies
├── run_pipeline.py            # Complete pipeline script
└── README.md                  # This file
```

## 📊 Results

After running the analysis, you'll find these files in the `results` directory:

1. `wallet_scores.csv`: Complete list of wallet addresses with their credit scores
2. `score_distribution.png`: Visualization of score distribution
3. `analysis.md`: Comprehensive report with:
   - Score distribution statistics
   - Behavioral insights
   - High vs. low scoring wallet comparisons
   - Risk factors and recommendations

```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For questions or support, please open an issue in the GitHub repository.
