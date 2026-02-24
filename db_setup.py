import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    database="postgres",  
    user="postgres",
    password=os.getenv('POSTGRES_PASSWORD'),  
    port=5432
)

conn.autocommit = True
cursor = conn.cursor()

try:
    cursor.execute("CREATE DATABASE news_pipeline")
    print("Database 'news_pipeline' created successfully!")
except psycopg2.errors.DuplicateDatabase:
    print("Database 'news_pipeline' already exists")

cursor.close()
conn.close()

print("Database setup complete!")