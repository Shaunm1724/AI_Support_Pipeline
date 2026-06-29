import sqlite3
import os
from dotenv import load_dotenv
import time

# LlamaIndex Imports
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
# --- NEW: Using the updated Google GenAI package ---
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables from the .env file
load_dotenv()

# Verify the API key was loaded
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("Error: GOOGLE_API_KEY not found. Please check your .env file.")

# Define paths
DB_PATH = '../data/support_database.db'
KNOWLEDGE_BASE_DIR = '../knowledge_base'

def setup_rag_engine():
    print("Initializing AI Agent and loading Knowledge Base...")
    
    # --- NEW: Updated LLM configuration ---
    Settings.llm = GoogleGenAI(model="gemini-3.1-flash-lite")
    
    # Set the Embedding model
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Load the text documents from the knowledge base directory
    documents = SimpleDirectoryReader(KNOWLEDGE_BASE_DIR).load_data()
    
    # Create the Vector Database
    index = VectorStoreIndex.from_documents(documents)
    
    # Create the query engine
    query_engine = index.as_query_engine()
    
    return query_engine

def process_high_priority_tickets(query_engine):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch ONLY Triaged tickets that are High Priority (Negative sentiment)
    cursor.execute("SELECT id, original_text, category FROM support_tickets WHERE status = 'Triaged' AND priority = 'High'")
    action_tickets = cursor.fetchall()

    if not action_tickets:
        print("No High Priority tickets need processing right now.")
        return

    print(f"\nFound {len(action_tickets)} High Priority tickets. AI Agent is drafting responses...\n")

    for ticket in action_tickets:
        ticket_id = ticket[0]
        text = ticket[1]
        category = ticket[2]

        print(f"--- Drafting response for Ticket {ticket_id} ({category}) ---")
        
        prompt = f"""
        You are an expert customer support agent. 
        A customer has submitted a complaint regarding: {category}.
        
        Customer's message: "{text}"
        
        Search the provided company policy document for the correct procedure regarding this issue.
        Draft a polite, professional, and empathetic response to the customer. 
        Offer the EXACT solution, timeframe, or compensation dictated by the company policy.
        Do not make up policies. Keep the response concise (under 4 sentences).
        """

        print("Thinking...")
        
        # --- NEW: Error Handling and Rate Limiting ---
        try:
            response = query_engine.query(prompt)
            drafted_reply = str(response)
            
            print("Drafted Reply:")
            print(f"\033[92m{drafted_reply}\033[0m")
            print("-" * 40)

            # Update the database
            cursor.execute('''
                UPDATE support_tickets
                SET agent_draft = ?, status = 'Ready for Review'
                WHERE id = ?
            ''', (drafted_reply, ticket_id))
            
            # Pause for 4.5 seconds to respect the 15 requests/minute limit
            time.sleep(4.5) 
            
        except Exception as e:
            print(f"API Error encountered: {e}")
            print("Pausing for 10 seconds before continuing to avoid rate limits...")
            time.sleep(10)

    # Update low priority tickets
    cursor.execute("UPDATE support_tickets SET status = 'Closed - No Action Needed' WHERE status = 'Triaged' AND priority = 'Low'")

    conn.commit()
    conn.close()
    print("Database updated. Pipeline complete!")

if __name__ == "__main__":
    engine = setup_rag_engine()
    process_high_priority_tickets(engine)