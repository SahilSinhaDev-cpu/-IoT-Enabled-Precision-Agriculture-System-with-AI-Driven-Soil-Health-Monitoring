import sqlite3
import pandas as pd
import argparse
import os

# Assume the script is in the same directory as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'agri_data.db')

def execute_query(query):
    """
    Connects to the SQLite database, executes a given query,
    and prints the results using pandas for nice formatting.
    """
    if not os.path.exists(DATABASE_FILE):
        print(f"Error: Database file not found at '{DATABASE_FILE}'")
        print("Please make sure you have run the Flask app (app.py) at least once to create the database.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_FILE)
        
        # Use pandas to read the SQL query into a DataFrame
        df = pd.read_sql_query(query, conn)

        # Close the connection
        conn.close()

        # Print the results
        if not df.empty:
            print("\n--- Query Results ---")
            print(df.to_string())
            print("---------------------\n")
        else:
            print("\nQuery executed successfully, but it returned no results.\n")

    except sqlite3.Error as e:
        print(f"\nDatabase error: {e}\n")
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
        A command-line tool to query the agri_data.db SQLite database.
        You can provide a query directly using the -q flag.
        If no query is provided, it will run a default query to show the 10 most recent entries.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help="The SQL query to execute. Example: 'SELECT * FROM sensor_history WHERE N > 100'"
    )

    parser.add_argument(
        '--examples',
        action='store_true',
        help="Show some example queries you can run."
    )

    args = parser.parse_args()

    if args.examples:
        print("""
--- Example Queries ---

1. Get the 10 most recent sensor readings:
   python query_db.py -q "SELECT * FROM sensor_history ORDER BY timestamp DESC LIMIT 10;"

2. Get average values for all numeric columns:
   python query_db.py -q "SELECT AVG(N) as avg_N, AVG(P) as avg_P, AVG(K) as avg_K, AVG(temperature) as avg_temp FROM sensor_history;"

3. Count how many times each crop has been predicted:
   python query_db.py -q "SELECT predicted_crop, COUNT(*) as count FROM sensor_history GROUP BY predicted_crop;"

4. Find all readings where the temperature was above 35 degrees:
   python query_db.py -q "SELECT id, timestamp, temperature, predicted_crop FROM sensor_history WHERE temperature > 35;"
        """)
    elif args.query:
        print(f"Executing custom query: {args.query}")
        execute_query(args.query)
    else:
        print("No query provided. Running default query to get the 10 most recent records.")
        default_query = "SELECT * FROM sensor_history ORDER BY timestamp DESC LIMIT 10;"
        execute_query(default_query)