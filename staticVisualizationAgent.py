import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.dates as mdates
from utils.DriveJSONRetriever import retrieve_data_from_gdrive


# Use a Seaborn style for a polished look
sns.set(style="whitegrid")
plt.rcParams.update({'figure.figsize': (12, 6), 'axes.titlesize': 16, 'axes.labelsize': 14})

def load_data(json_file):
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"File not found: {json_file}. Please check the file path and name.")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    # data = retrieve_data_from_gdrive('processed_output.json')
    
    records = []
    for file_name, transactions in data.items():
        for tx in transactions:
            tx['file'] = file_name  # add source file info
            records.append(tx)
    
    df = pd.DataFrame(records)
    # Convert dates (adjust format if time details are added later)
    df['Date'] = pd.to_datetime(df['Date'], format="%d-%m-%Y", errors='coerce')
    # Ensure numeric values
    df['Deposit'] = pd.to_numeric(df['Deposit'], errors='coerce')
    df['Withdrawal'] = pd.to_numeric(df['Withdrawal'], errors='coerce')
    df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
    
    # Create a Net column (Deposit - Withdrawal, treating null withdrawal as 0)
    df['Net'] = df['Deposit'].fillna(0) - df['Withdrawal'].fillna(0)
    return df

def adjust_xticks(ax):
    """Dynamically adjust date ticks to reduce clutter."""
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

def plot_balance_over_time(df):
    df_sorted = df.sort_values('Date')
    fig, ax = plt.subplots()
    sns.lineplot(data=df_sorted, x='Date', y='Balance', marker='o', label="Balance", ax=ax)
    ax.set_title("Account Balance Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")
    adjust_xticks(ax)
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/balance_over_time.png")

def plot_deposits_over_time(df):
    df_deposits = df.dropna(subset=['Deposit']).sort_values('Date')
    fig, ax = plt.subplots()
    sns.barplot(data=df_deposits, x='Date', y='Deposit', color='green', ax=ax)
    ax.set_title("Deposits Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Deposit Amount")
    adjust_xticks(ax)
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/deposits_over_time.png")

def plot_transactions_per_day(df):
    df['TransactionCount'] = 1
    daily_counts = df.groupby('Date')['TransactionCount'].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(data=daily_counts.sort_values('Date'), x='Date', y='TransactionCount', palette='Blues_d', ax=ax)
    ax.set_title("Number of Transactions Per Day")
    ax.set_xlabel("Date")
    ax.set_ylabel("Transaction Count")
    adjust_xticks(ax)
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/transactions_per_day.png")

def plot_deposit_distribution(df):
    fig, ax = plt.subplots()
    sns.histplot(df['Deposit'].dropna(), kde=True, color='blue', bins=20, ax=ax)
    ax.set_title("Deposit Distribution")
    ax.set_xlabel("Deposit Amount")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/deposit_distribution.png")

def plot_withdrawal_distribution(df):
    fig, ax = plt.subplots()
    sns.histplot(df['Withdrawal'].dropna(), kde=True, color='red', bins=20, ax=ax)
    ax.set_title("Withdrawal Distribution")
    ax.set_xlabel("Withdrawal Amount")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/withdrawal_distribution.png")

def plot_deposit_vs_withdrawal(df):
    filtered_df = df.dropna(subset=['Deposit', 'Withdrawal'])
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='Deposit', y='Withdrawal', ax=ax)
    ax.set_title("Deposit vs. Withdrawal")
    ax.set_xlabel("Deposit")
    ax.set_ylabel("Withdrawal")
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/deposit_vs_withdrawal.png")

def plot_cumulative_net(df):
    df_sorted = df.sort_values('Date')
    df_sorted['CumulativeNet'] = df_sorted['Net'].cumsum()
    fig, ax = plt.subplots()
    sns.lineplot(data=df_sorted, x='Date', y='CumulativeNet', marker='o', color='purple', ax=ax)
    ax.set_title("Cumulative Net Deposits Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Net Amount")
    adjust_xticks(ax)
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/cumulative_net.png")

def plot_balance_moving_average(df, window=3):
    df_sorted = df.sort_values('Date')
    df_sorted['Balance_MA'] = df_sorted['Balance'].rolling(window=window).mean()
    fig, ax = plt.subplots()
    sns.lineplot(data=df_sorted, x='Date', y='Balance', marker='o', label="Balance", ax=ax)
    sns.lineplot(data=df_sorted, x='Date', y='Balance_MA', marker='o', color='orange', label=f'{window}-Day MA', ax=ax)
    ax.set_title("Balance with Moving Average")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")
    adjust_xticks(ax)
    ax.legend()
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/balance_moving_average.png")

def plot_deposits_withdrawals_time_series(df):
    df_sorted = df.sort_values('Date')
    fig, ax = plt.subplots()
    sns.lineplot(data=df_sorted, x='Date', y='Deposit', marker='o', label="Deposits", color='green', ax=ax)
    sns.lineplot(data=df_sorted, x='Date', y='Withdrawal', marker='o', label="Withdrawals", color='red', ax=ax)
    ax.set_title("Deposits & Withdrawals Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount")
    adjust_xticks(ax)
    ax.legend()
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/deposits_withdrawals_time_series.png")

def plot_transactions_by_file(df):
    file_counts = df['file'].value_counts().reset_index()
    file_counts.columns = ['file', 'TransactionCount']
    fig, ax = plt.subplots()
    sns.barplot(data=file_counts, x='file', y='TransactionCount', palette='viridis', ax=ax)
    ax.set_title("Transactions Per Source File")
    ax.set_xlabel("Source File")
    ax.set_ylabel("Number of Transactions")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/transactions_by_file.png")

def plot_boxplot_deposit_by_weekday(df):
    df['Weekday'] = df['Date'].dt.day_name()
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x='Weekday', y='Deposit', palette='Set3', ax=ax)
    ax.set_title("Deposit Amount Distribution by Weekday")
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Deposit Amount")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/boxplot_deposit_by_weekday.png")

def plot_daily_net_transactions(df):
    daily_net = df.groupby('Date')['Net'].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(data=daily_net.sort_values('Date'), x='Date', y='Net', palette='coolwarm', ax=ax)
    ax.set_title("Daily Net Transactions")
    ax.set_xlabel("Date")
    ax.set_ylabel("Net Amount (Deposit - Withdrawal)")
    adjust_xticks(ax)
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/daily_net_transactions.png")

def plot_numeric_correlation_heatmap(df):
    numeric_df = df[['Deposit', 'Withdrawal', 'Balance', 'Net']].copy()
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap of Financial Variables")
    fig.tight_layout()
    fig.savefig("INFO/staticPlots/correlation_heatmap.png")

def main():
    json_file = "./INFO/processed_output.json"  # Ensure this file exists!
    df = load_data(json_file)
    
    # Original plots
    plot_balance_over_time(df)
    plot_deposits_over_time(df)
    plot_transactions_per_day(df)
    plot_deposit_distribution(df)
    plot_withdrawal_distribution(df)
    plot_deposit_vs_withdrawal(df)
    plot_cumulative_net(df)
    
    # Additional plots
    plot_balance_moving_average(df, window=3)
    plot_deposits_withdrawals_time_series(df)
    plot_transactions_by_file(df)
    plot_boxplot_deposit_by_weekday(df)
    plot_daily_net_transactions(df)
    plot_numeric_correlation_heatmap(df)

if __name__ == '__main__':
    main()
