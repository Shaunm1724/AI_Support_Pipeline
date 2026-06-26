import streamlit as st
import sqlite3
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="AI Support Agent Dashboard", page_icon="🤖", layout="wide")

# Define database path
DB_PATH = '../data/support_database.db'

def load_data():
    """Connects to SQLite and loads the tickets into a Pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    # Read the whole table into a pandas dataframe
    df = pd.read_sql_query("SELECT * FROM support_tickets", conn)
    conn.close()
    return df

# --- UI Setup ---
st.title("🤖 AI Customer Support Dashboard")
st.markdown("Enterprise pipeline for automated ticket triage and AI response generation.")

# Load the data
df = load_data()

if df.empty:
    st.warning("No data found in the database. Please run the pipeline scripts first.")
else:
    # --- Top Metrics Row ---
    # Calculate some quick stats
    total_tickets = len(df)
    high_priority = len(df[df['priority'] == 'High'])
    ready_review = len(df[df['status'] == 'Ready for Review'])

    # Display stats in 3 columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets Processed", total_tickets)
    col2.metric("High Priority (Action Needed)", high_priority)
    col3.metric("Drafts Ready for Human Review", ready_review)

    st.divider()

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Tickets")
    selected_status = st.sidebar.multiselect(
        "Status",
        options=df['status'].unique(),
        default=df['status'].unique()
    )
    
    selected_priority = st.sidebar.multiselect(
        "Priority",
        options=df['priority'].unique(),
        default=df['priority'].unique()
    )

    # Apply filters to dataframe
    filtered_df = df[(df['status'].isin(selected_status)) & (df['priority'].isin(selected_priority))]

    # --- Main Data Table ---
    st.subheader("Ticket Overview")
    # Display the dataframe nicely, hiding the long text columns for the main view
    st.dataframe(
        filtered_df[['id', 'category', 'sentiment', 'priority', 'status']],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --- AI Draft Review Section ---
    st.subheader("📝 Review AI Drafted Responses")
    st.markdown("Review the responses drafted by the RAG Agent for High Priority tickets.")

    # Filter only tickets that have a draft
    draft_df = filtered_df[filtered_df['status'] == 'Ready for Review']

    if draft_df.empty:
        st.info("No drafted responses match your current filters.")
    else:
        # Create an expandable section for each ticket
        for index, row in draft_df.iterrows():
            with st.expander(f"Ticket #{row['id']} - {row['category']} Issue"):
                st.markdown("**😠 Customer Complaint:**")
                st.info(row['original_text'])
                
                st.markdown("**🤖 AI Drafted Response:**")
                st.success(row['agent_draft'])
                
                # A mock button to simulate a human approving the AI response
                if st.button(f"Approve & Send Ticket {row['id']}", key=f"btn_{row['id']}"):
                    st.toast(f"Ticket {row['id']} approved and sent to customer!", icon="✅")