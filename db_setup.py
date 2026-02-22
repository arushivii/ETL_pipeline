import psycopg2
from psycopg2 import sql

# Connection parameters
conn = psycopg2.connect(
    host="localhost",
    database="postgres",  # We'll connect to default database first
    user="postgres",
    password="Reddit00#",  # Replace with your password!
    port=5432  # Your port
)

# Important: Set autocommit to create database
conn.autocommit = True
cursor = conn.cursor()

# Create our database
try:
    cursor.execute("CREATE DATABASE news_pipeline")
    print("Database 'news_pipeline' created successfully!")
except psycopg2.errors.DuplicateDatabase:
    print("Database 'news_pipeline' already exists")

cursor.close()
conn.close()

print("Database setup complete!")