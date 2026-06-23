import sqlite3
import csv
import os

# Define paths
DB_PATH = '../data/support_database.db'
CSV_PATH = '../data/incoming_tickets.csv'

def setup_database():
    """Creates the SQLite database and the support_tickets table."""
    print("Connecting to database...")
    
    # This will create the file if it doesn't exist
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the table schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY,
            original_text TEXT,
            sentiment TEXT,
            category TEXT,
            priority TEXT,
            agent_draft TEXT,
            status TEXT
        )
    ''')
    
    conn.commit()
    print("Table 'support_tickets' created successfully.")
    return conn

def load_initial_data(conn):
    """Reads the CSV and loads the tickets into the database."""
    cursor = conn.cursor()
    
    # Check if the CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find {CSV_PATH}. Make sure it is in the data folder.")
        return

    print("Reading CSV and loading tickets into database...")
    with open(CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            ticket_id = row['ticket_id']
            text = row['customer_text']
            
            # Insert the raw ticket, leaving ML/Agent columns blank (NULL) for now.
            # We set the initial status to 'New'.
            cursor.execute('''
                INSERT OR IGNORE INTO support_tickets 
                (id, original_text, status) 
                VALUES (?, ?, ?)
            ''', (ticket_id, text, 'New'))
            
    conn.commit()
    print("Data loaded successfully!")

if __name__ == "__main__":
    # Ensure the data directory exists
    os.makedirs('../data', exist_ok=True)
    
    # Run the setup
    db_connection = setup_database()
    load_initial_data(db_connection)
    db_connection.close()
    
    print("Phase 1 Complete: Database is ready.")