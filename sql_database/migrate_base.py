import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
csv_file = r'C:\Users\Administrateur\OneDrive\Documents\GitHub\reparatorAI\data\OpenRepairData_v0.3_aggregate_202309.csv'
df = pd.read_csv(csv_file)

# Database credentials
db_name = 'reparatorAI'
db_user = 'postgres'
db_pass = 'charlie'
db_host = 'localhost'  # or IP address of your PostgreSQL server
db_port = '5432'       # Default port for PostgreSQL

# Create an SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')

# Write the DataFrame to a PostgreSQL table (this will create a new table or replace if exists)
table_name = 'reparatorai_repairs'
df.to_sql(table_name, engine, index=False, if_exists='replace')

print("CSV data loaded into PostgreSQL successfully!")
