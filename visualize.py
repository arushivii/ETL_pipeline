import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="news_pipeline",
        user="postgres",
        password=os.getenv('POSTGRES_PASSWORD'),
        port=5432
    )

def fetch_data():
    """Fetch all data from cleaned_articles"""
    conn = get_connection()
    query = """
        SELECT source_name, title, word_count, published_at, pulled_at
        FROM cleaned_articles
        ORDER BY published_at
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_summary():
    """Fetch daily summary data"""
    conn = get_connection()
    query = """
        SELECT date, source_name, article_count, avg_word_count
        FROM daily_summary
        ORDER BY date
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Visualization 1: Articles over time
def plot_articles_over_time(df):
    """Line chart: number of articles published per day"""
    df['date'] = pd.to_datetime(df['published_at']).dt.date
    daily_counts = df.groupby('date').size()
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=8)
    plt.title('Articles Published Per Day', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Articles', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('articles_over_time.png', dpi=300, bbox_inches='tight')
    print("Saved: articles_over_time.png")
    plt.close()

# Visualization 2: Top news sources
def plot_top_sources(df):
    """Bar chart: most active news sources"""
    source_counts = df['source_name'].value_counts().head(10)
    
    plt.figure(figsize=(12, 6))
    colors = plt.cm.viridis(range(len(source_counts)))
    plt.barh(source_counts.index, source_counts.values, color=colors)
    plt.title('Top 10 News Sources by Article Count', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Articles', fontsize=12)
    plt.ylabel('News Source', fontsize=12)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('top_sources.png', dpi=300, bbox_inches='tight')
    print("Saved: top_sources.png")
    plt.close()

# Visualization 3: Word count distribution
def plot_word_count_distribution(df):
    """Histogram: distribution of article lengths"""
    df_clean = df[df['word_count'] > 0]  # Remove zeros
    
    plt.figure(figsize=(12, 6))
    plt.hist(df_clean['word_count'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title('Article Length Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Word Count', fontsize=12)
    plt.ylabel('Number of Articles', fontsize=12)
    plt.axvline(df_clean['word_count'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {df_clean["word_count"].mean():.0f} words')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('word_count_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: word_count_distribution.png")
    plt.close()

# Visualization 4: Source activity heatmap
def plot_source_activity_heatmap(summary_df):
    """Heatmap: which sources publish most on which days"""
  
    pivot = summary_df.pivot(index='source_name', columns='date', values='article_count')
    pivot = pivot.fillna(0)
    
    
    top_sources = summary_df.groupby('source_name')['article_count'].sum().nlargest(10).index
    pivot = pivot.loc[pivot.index.isin(top_sources)]
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', cbar_kws={'label': 'Article Count'})
    plt.title('Daily Article Count by Source (Heatmap)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('News Source', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('source_activity_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: source_activity_heatmap.png")
    plt.close()


if __name__ == "__main__":
    print("="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    
    print("\nFetching data from database...")
    df = fetch_data()
    summary_df = fetch_summary()
    
    print(f"Loaded {len(df)} articles")
    print(f"Loaded {len(summary_df)} summary records")
    
    print("\nCreating visualizations...")
    print("-"*60)
    
    plot_articles_over_time(df)
    plot_top_sources(df)
    plot_word_count_distribution(df)
    plot_source_activity_heatmap(summary_df)
    
    print("\n" + "="*60)
    print("ALL VISUALIZATIONS CREATED!")
    print("="*60)
    print("\nGenerated files:")
    print("  - articles_over_time.png")
    print("  - top_sources.png")
    print("  - word_count_distribution.png")
    print("  - source_activity_heatmap.png")