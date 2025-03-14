# # streamlit run app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime
import os
import base64
import sqlite3
import hashlib

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "message" not in st.session_state:
    st.session_state.message = ""
if "streak" not in st.session_state:
    st.session_state.streak = 0

# Database setup for user authentication
USER_DB = "users.db"
conn = sqlite3.connect(USER_DB, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)"""
)
conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to verify user credentials
def check_user(username, password):
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    return result and result[0] == hash_password(password)

# Function to register a new user
def register_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# User Authentication Page
def login_page():
    st.title("🔐 Welcome to JivaJournal")
    option = st.radio("Choose an option:", ["Login", "Sign Up"])

    if option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}! 🎉")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    elif option == "Sign Up":
        new_username = st.text_input("Create a Username")
        new_password = st.text_input("Create a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if new_password == confirm_password:
                if register_user(new_username, new_password):
                    st.success("Account created successfully! 🎉 Please log in.")
                else:
                    st.error("Username already exists. Try another one.")
            else:
                st.error("Passwords do not match. Please try again.")

# If user is not logged in, show login page
if not st.session_state.logged_in:
    login_page()
    st.stop()  # Stop execution here if user is not logged in

# Load sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# File path for storing journal entries (per user)
FILE_PATH = f"journal_entries_{st.session_state.username}.csv"

# Load or initialize journal data
if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Entry", "Sentiment", "Ayurveda Tip"])

# Streamlit Sidebar Navigation
st.sidebar.title(f"🌿 JivaJournal - {st.session_state.username}")
page = st.sidebar.radio("Go to", ["Journaling", "Dashboard", "Dosha Quiz", "Activities"])

# Logout Button
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# Function to set background image
def set_bg_image(image_file):
    with open(image_file, "rb") as f:
        base64_str = base64.b64encode(f.read()).decode()
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{base64_str}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Set background image
set_bg_image("assets/bg_img.jpg")

# Page 1: Journaling
if page == "Journaling":
    st.title("🧘‍♀️ JivaJournal - Mindfulness & Ayurveda Journal")
    st.subheader("Write your daily journal and get AI-powered insights!")

    # Journaling streak
    if not df.empty and df.iloc[-1]["Date"].date() == datetime.date.today():
        st.session_state.streak = len(df[df["Date"].dt.date == datetime.date.today()])
    else:
        st.session_state.streak = 0

    st.info(f"🔥 Journaling Streak: {st.session_state.streak} days in a row!")

    # Show success message if exists
    if st.session_state.message:
        st.success(st.session_state.message)
        st.session_state.message = ""

    # User journal input
    entry = st.text_area("📝 Write about your day:")

    if st.button("Analyze & Save"):
        if entry.strip():
            # Get sentiment
            sentiment_score = analyzer.polarity_scores(entry)["compound"]
            sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

            # Ayurveda tips based on sentiment
            ayurveda_tips = {
                "Positive": "🌿 Maintain balance with a warm herbal tea!",
                "Neutral": "🍵 Try deep breathing for better focus.",
                "Negative": "🛀 Relax with an oil massage or calming yoga."
            }
            tip = ayurveda_tips[sentiment]

            # Save entry with timestamp
            new_data = {
                "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Entry": entry,
                "Sentiment": sentiment,
                "Ayurveda Tip": tip
            }

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(FILE_PATH, index=False)

            # Reload DataFrame after saving
            df = pd.read_csv(FILE_PATH)
            df["Date"] = pd.to_datetime(df["Date"])

            # Update streak
            st.session_state.streak += 1

            # Show result
            st.session_state.message = f"Sentiment: **{sentiment}**\nAyurveda Tip: {tip}"
            st.rerun()
        else:
            st.warning("Please write something before analyzing.")


    # Show previous entries
    if not df.empty:
        st.subheader("📜 Your Journal History")

        for index, row in df.iterrows():
            with st.expander(f"🗓 {row['Date']} - {row['Sentiment']}"):
                st.write(f"**Entry:** {row['Entry']}")
                st.write(f"**Ayurveda Tip:** {row['Ayurveda Tip']}")

                # Edit feature
                updated_entry = st.text_area(f"Update Entry Here:", row["Entry"], key=f"edit_{index}")
                if st.button(f"Save Updated Entry", key=f"save_{index}"):
                    if updated_entry.strip():
                        sentiment_score = analyzer.polarity_scores(updated_entry)["compound"]
                        sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

                        # Ayurveda tips based on sentiment
                        ayurveda_tips = {
                            "Positive": "🌿 Maintain balance with a warm herbal tea!",
                            "Neutral": "🍵 Try deep breathing for better focus.",
                            "Negative": "🛀 Relax with an oil massage or calming yoga."
                        }
                        tip = ayurveda_tips[sentiment]

                        df.at[index, "Entry"] = updated_entry
                        df.at[index, "Sentiment"] = sentiment
                        df.at[index, "Ayurveda Tip"] = tip
                        df.at[index, "Date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        df.to_csv(FILE_PATH, index=False)
                        st.session_state.message = "Entry updated successfully!"
                        st.rerun()
                    else:
                        st.warning("Edited entry cannot be empty!")

                # Delete feature
                if st.button(f"Delete Entry", key=f"delete_{index}"):
                    df = df.drop(index).reset_index(drop=True)
                    df.to_csv(FILE_PATH, index=False)
                    st.session_state.message = "Entry deleted successfully!"
                    st.rerun()

# Page 2: Dashboard
elif page == "Dashboard":
    st.title("📊 Your Dashboard")
    st.subheader("Sentiment Analysis Over Time")

    if not df.empty:
        df["Sentiment_Numeric"] = df["Sentiment"].apply(lambda s: {"Positive": 1, "Neutral": 0, "Negative": -1}[s])
        
        # Line chart for sentiment trends
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=df, x="Date", y="Sentiment_Numeric", ax=ax, marker="o", color="blue")
        ax.set_ylabel("Sentiment Score")
        ax.set_xlabel("Date")
        st.pyplot(fig)

        # **Word Cloud for Journal Entries**
        st.subheader("🌟 Word Cloud from Your Journal Entries")
        
        all_text = " ".join(df["Entry"].dropna())  # Merge all entries into one string
        if all_text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No journal entries available to generate a word cloud.")

    else:
        st.info("No data available yet. Start journaling!")


# Page 3: Dosha Quiz
elif page == "Dosha Quiz":
    st.title("🧘 Discover Your Ayurveda Dosha")
    st.write("Answer a few questions to determine your Dosha type!")

    q1 = st.radio("How would you describe your body type?", ["Slim", "Medium", "Stocky"])
    q2 = st.radio("What is your usual body temperature?", ["Cold", "Neutral", "Warm"])
    q3 = st.radio("How is your digestion?", ["Irregular", "Moderate", "Strong"])

    if st.button("Determine Dosha"):
        if q1 == "Slim" and q2 == "Cold":
            st.session_state.dosha_type = "Vata"
        elif q1 == "Medium" and q2 == "Neutral":
            st.session_state.dosha_type = "Pitta"
        else:
            st.session_state.dosha_type = "Kapha"
        
        st.success(f"🌿 Your Dosha Type is: **{st.session_state.dosha_type}**")

# Page 4: Activities
elif page == "Activities":
    st.title("🏃‍♂️🎯 Activities for Well-being")
    
    category = st.selectbox("Choose a category:", ["Yoga", "Breathing", "Meditation", "Diet", "Lifestyle"])
    level = st.radio("Select difficulty level:", ["Beginner", "Intermediate", "Advanced"])

    st.subheader(f"📌 Recommended {category} Activities for {level} level")

    if category == "Yoga":
        if level == "Beginner":
            st.video("https://www.youtube.com/watch?v=v7AYKMP6rOE")  # Example Yoga video
        elif level == "Intermediate":
            st.video("https://www.youtube.com/watch?v=J6hD7k1UJD0")
        else:
            st.video("https://www.youtube.com/watch?v=4pKly2JojMw")

    elif category == "Breathing":
        if level == "Beginner":
            st.audio("https://example.com/breathing_exercise.mp3")  # Replace with actual audio link

    elif category == "Meditation":
        if level == "Beginner":
            st.video("https://www.youtube.com/watch?v=oVzTnS_IONU")

    elif category == "Diet":
        st.write("🍎 Eat fresh fruits, drink warm water, and balance your meals.")

    elif category == "Lifestyle":
        st.write("🛌 Maintain a regular sleep cycle and stay hydrated!")
