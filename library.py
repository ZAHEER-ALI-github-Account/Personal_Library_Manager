import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Database setup
def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            status TEXT CHECK(status IN ('Read', 'Unread'))
        )
    """)
    conn.commit()
    conn.close()

# Function to add book
def add_book(title, author, genre, status):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, genre, status) VALUES (?, ?, ?, ?)",
                   (title, author, genre, status))
    conn.commit()
    conn.close()

# Function to get books
def get_books():
    conn = sqlite3.connect("library.db")
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df

# Function to delete book
def delete_book(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

# Initialize Database
init_db()

# Streamlit UI
st.set_page_config(page_title="Personal Library Manager", layout="wide", initial_sidebar_state="expanded")
st.title("📚 Personal Library Manager")

# Sidebar for adding a book
with st.sidebar:
    st.header("➕ Add a New Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy", "Biography", "Self-Help", "Other"])
    status = st.selectbox("Status", ["Read", "Unread"])
    if st.button("Add Book", use_container_width=True):
        if title and author:
            add_book(title, author, genre, status)
            st.success("Book added successfully!")
            st.rerun()
        else:
            st.error("Title and Author are required!")

# Search and Filter Books
st.subheader("🔎 Search & Filter Books")
search_query = st.text_input("Search by Title or Author")
filter_genre = st.selectbox("Filter by Genre", ["All"] + ["Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy", "Biography", "Self-Help", "Other"])
filter_status = st.selectbox("Filter by Status", ["All", "Read", "Unread"])

# Get books and apply filters
df = get_books()
if not df.empty:
    if search_query:
        df = df[df["title"].str.contains(search_query, case=False, na=False) | df["author"].str.contains(search_query, case=False, na=False)]
    if filter_genre != "All":
        df = df[df["genre"] == filter_genre]
    if filter_status != "All":
        df = df[df["status"] == filter_status]
    
    st.dataframe(df, use_container_width=True)
    
    # Delete option
    book_id_to_delete = st.number_input("Enter Book ID to delete", min_value=1, step=1)
    if st.button("Delete Book", use_container_width=True):
        delete_book(book_id_to_delete)
        st.warning("Book deleted!")
        st.rerun()
else:
    st.info("No books found. Add some to your library!")

# Statistics
st.subheader("📊 Library Stats")
if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        status_counts = df["status"].value_counts()
        fig1 = px.pie(names=status_counts.index, values=status_counts.values, title="Read vs Unread Books")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        genre_counts = df["genre"].value_counts()
        fig2 = px.bar(x=genre_counts.index, y=genre_counts.values, title="Books by Genre")
        st.plotly_chart(fig2, use_container_width=True)
