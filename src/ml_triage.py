import sqlite3
from transformers import pipeline

# Define database path
DB_PATH = '../data/support_database.db'

print("Loading ML Models (this may take a minute the first time as it downloads them)...")
# 1. Load standard Sentiment Analysis model
sentiment_analyzer = pipeline("sentiment-analysis")

# 2. Load Zero-Shot Classification model for categories
category_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the categories we want the model to sort tickets into
CATEGORIES = ["Billing", "Technical Support", "Shipping"]

def process_tickets():
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch only tickets that haven't been processed yet
    cursor.execute("SELECT id, original_text FROM support_tickets WHERE status = 'New'")
    new_tickets = cursor.fetchall()

    if not new_tickets:
        print("No new tickets to process.")
        return

    print(f"Found {len(new_tickets)} new tickets. Processing...")

    for ticket in new_tickets:
        ticket_id = ticket[0]
        text = ticket[1]

        print(f"\n--- Analyzing Ticket {ticket_id} ---")

        # --- 1. Predict Sentiment ---
        sent_result = sentiment_analyzer(text)[0]
        sentiment = sent_result['label'] # Usually 'POSITIVE' or 'NEGATIVE'

        # --- 2. Predict Category ---
        cat_result = category_classifier(text, candidate_labels=CATEGORIES)
        # The model returns a list of labels sorted by probability. We take the top one.
        category = cat_result['labels'][0]

        # --- 3. Determine Priority ---
        # Simple logic: If it's a negative ticket, flag it as High Priority. Otherwise, Low.
        priority = "High" if sentiment == "NEGATIVE" else "Low"

        print(f"Sentiment: {sentiment}")
        print(f"Category: {category}")
        print(f"Priority: {priority}")

        # --- 4. Update the Database ---
        cursor.execute('''
            UPDATE support_tickets
            SET sentiment = ?, category = ?, priority = ?, status = 'Triaged'
            WHERE id = ?
        ''', (sentiment, category, priority, ticket_id))

    # Commit changes and close
    conn.commit()
    conn.close()
    print("\nAll tickets processed and database updated!")

if __name__ == "__main__":
    process_tickets()