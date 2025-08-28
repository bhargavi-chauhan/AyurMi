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
import feedparser
import nltk
from textblob import TextBlob
from collections import Counter
import plotly.express as px
import pytz
import streamlit.components.v1 as components

nltk.download('punkt')

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
    

# Function to fetch latest wellness & Ayurveda articles
def get_latest_articles():
    feed_url = "https://news.google.com/rss/search?q=ayurveda+mindfulness+wellness&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(feed_url)

    articles = []
    for entry in feed.entries[:5]:  # Fetch top 5 articles
        articles.append({"title": entry.title, "link": entry.link})
    
    return articles

# Function to analyze journal entries and extract keywords
def analyze_journal_entries():
    try:
        df = pd.read_csv("journal_entries.csv")
        all_entries = " ".join(df["Entry"].dropna())  # Combine all journal entries
        blob = TextBlob(all_entries)

        common_words = [word.lower() for word in blob.words if len(word) > 3]  # Ignore short words
        word_counts = Counter(common_words)
        top_keywords = [word for word, _ in word_counts.most_common(3)]  # Top 3 keywords

        return top_keywords
    except FileNotFoundError:
        return []

# Function to save journal entries
def save_entry(date, entry):
    try:
        df = pd.read_csv("journal_entries.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Entry"])

    new_entry = pd.DataFrame([[date, entry]], columns=["Date", "Entry"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv("journal_entries.csv", index=False)

# Function for sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "😊 Positive"
    elif analysis.sentiment.polarity < 0:
        return "😟 Negative"
    else:
        return "😐 Neutral"

# User Authentication Page
def login_page():
    st.title("Welcome to AyurMi")
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

# # Custom CSS for Sidebar
# Function to convert image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

image_path = "assets/sd.jpg"  # Update the correct path to your image
base64_img = get_base64_image(image_path)  # Convert image to Base64 string

# Inject custom CSS for sidebar styling
sidebar_css = f"""
<style>
    /*Set Sidebar Background */
    [data-testid="stSidebar"] {{
        background-image: url("data:image/jpg;base64,{base64_img}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}

    /* Sidebar Title Styling */
    [data-testid="stSidebar"] h1 {{
        color: white !important;
        text-align: left;
        font-weight: bold;
    }}


    /* Make Sidebar Radio Button Labels White */
    .stRadio label {{
        color: white !important;
        font-size: 16px;
    }}

    /* Streamlit Button Styling (Logout Button) */
    div.stButton > button {{
        background-color: brown !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        width: 100%;
        transition: background-color 0.3s ease;
        border: none;
    }}

    div.stButton > button:hover {{
        background-color: darkred !important;
    }}

    /* Ensure Other Sidebar Text is White Except Buttons */
    [data-testid="stSidebar"] *:not(.stButton > button):not(.logout-button) {{
        color: white !important;
    }}

    /* 🌟 Ensure Sidebar Starts Below Navbar */
    [data-testid="stSidebar"] {{
        margin-top: 3.6rem; /* Adjust as needed to match the navbar height */
    }}

    # /* 🌟 Make Navbar Background White */
    # header[data-testid="stHeader"] {{
    #     background-color: white !important;
    #     height: 3.5rem; /* Adjust based on your navbar size */
    #     position: fixed;
    #     width: 100%;
    #     top: 0;
    #     z-index: 100;
    #     box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); /* Optional: Adds slight shadow */
    # }}
</style>
"""

st.markdown(sidebar_css, unsafe_allow_html=True)


# Streamlit Sidebar Navigation
# st.sidebar.title(f"AyurMi")
# st.sidebar.markdown(f"Hey there, **{st.session_state.username}**!")
# page = st.sidebar.radio("Go to", ["Journaling", "Dashboard", "Dosha Quiz", "Activities", "Mood & Mind Chat", "Recommendations"])

st.sidebar.markdown(
    "<h1 style='text-align: center; margin-bottom: 0.2em; color:#4B8A5D;'>AyurMi</h1>",
    unsafe_allow_html=True
)

st.sidebar.markdown(
    f"<p style='text-align: center; font-size: 0.9em; color: gray;'>Hey there, <strong>{st.session_state.username}</strong>!</p>",
    unsafe_allow_html=True
)

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigate",
    ["Journaling", "Dashboard", "Dosha Quiz", "Activities", "Mood & Mind Chat", "Recommendations"]
)


# Logout Button 
logout_clicked = st.sidebar.button("Logout", key="logout_button")
if logout_clicked:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()  # Refresh the page

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
set_bg_image("assets/bg-copy.jpg")

# # Page 1: Journaling
if page == "Journaling":
    st.title("AyurMi - Ayurveda Journal & Mindfulness")
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
    entry = st.text_area("Write about your day:")

    if st.button("Analyze & Save"):
        if entry.strip():
            # Get sentiment
            sentiment_score = analyzer.polarity_scores(entry)["compound"]
            sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

            # Ayurveda tips based on sentiment
            ayurveda_tips = {
                "Positive": "🌿 Stay hydrated and eat fresh fruits",
                "Neutral": "🍵 Take a short walk or do deep breathing.",
                "Negative": "🛀 Unwind with a warm bath and rest well."
            }
            tip = ayurveda_tips[sentiment]

            # # Save entry with timestamp
            # new_data = {
            #     "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            #     "Entry": entry,
            #     "Sentiment": sentiment,
            #     "Ayurveda Tip": tip
            # }

            # Get current UTC time
            utc_now = datetime.datetime.utcnow()

            # Convert UTC to IST (Indian Standard Time)
            ist = pytz.timezone("Asia/Kolkata")
            local_time = utc_now.astimezone(ist)

            # Save entry with corrected timestamp
            new_data = {
                "Date": local_time.strftime("%Y-%m-%d %H:%M:%S"),  # Stores in IST
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
            st.session_state.message = f"Sentiment: **{sentiment}**\n; Ayurveda Tip: {tip}"
            st.rerun()
        else:
            st.warning("Please write something before analyzing.")

    # Show previous entries
    if not df.empty:
        st.subheader("Your Journal History")

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
                            "Positive": "🌿 Stay hydrated and eat fresh fruits",
                            "Neutral": "🍵 Take a short walk or do deep breathing.",
                            "Negative": "🛀 Unwind with a warm bath and rest well."
                        }
                        tip = ayurveda_tips[sentiment]

                        ist = pytz.timezone("Asia/Kolkata")
                        current_time = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

                        df.at[index, "Entry"] = updated_entry
                        df.at[index, "Sentiment"] = sentiment
                        df.at[index, "Ayurveda Tip"] = tip
                        # df.at[index, "Date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        df.at[index, "Date"] = current_time

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
    # Apply Custom Styling
    st.markdown("""
        <style>
            .css-18e3th9 { padding-top: 1rem; }
            .stApp { background-color: #FAF3E0; }
            .title { text-align: center; font-size: 32px; font-weight: bold; color: #4F4A45; }
            .subtitle { text-align: center; font-size: 24px; font-weight: bold; color: #6D676E; }
            .metric-box { background: #F5F5F5; padding: 10px; border-radius: 10px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

    # File where journal entries are stored dynamically
    # FILE_PATH = "journal_entries.csv"

    # Load Data (If File Exists)
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df["Month"] = df["Date"].dt.strftime("%Y-%m")  # Extract Year-Month for grouping
    else:
        df = pd.DataFrame(columns=["Date", "Entry", "Sentiment", "Ayurveda Tip"])

    # Sentiment Mapping
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    df["Sentiment_Numeric"] = df["Sentiment"].map(sentiment_map)

    # --- 📊 PAGE: DASHBOARD ---
    st.title("Your Mindfulness Dashboard")
    st.markdown("🌿 Get insights into your journaling habits and emotional well-being!")

    if not df.empty:
        # --- 🌟 Sentiment Summary ---
        st.subheader("Mood Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positive Entries", df[df["Sentiment"] == "Positive"].shape[0])
        with col2:
            st.metric("😐 Neutral Entries", df[df["Sentiment"] == "Neutral"].shape[0])
        with col3:
            st.metric("😢 Negative Entries", df[df["Sentiment"] == "Negative"].shape[0])

        # --- 📈 Sentiment Trends Over Time ---
        st.subheader("Sentiment Analysis Over Time")
        fig = px.line(df, x="Date", y="Sentiment_Numeric", 
                    markers=True, line_shape="spline", 
                    title="Your Mood Journey", 
                    labels={"Sentiment_Numeric": "Sentiment Score", "Date": "Journal Date"},
                    color_discrete_sequence=["#1f77b4"])
        st.plotly_chart(fig, use_container_width=True)

        # --- ☁️ Word Cloud for Journal Entries ---
        st.subheader("Most Frequent Words in Your Journal")
        all_text = " ".join(df["Entry"].dropna())
        if all_text.strip():
            wordcloud = WordCloud(width=1000, height=500, background_color="white", colormap="viridis").generate(all_text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No journal entries available yet to generate a word cloud.")

        # --- 📅 Monthly Mood Trends ---
        st.subheader("Monthly Mood Tracker")
        mood_trends = df.groupby(["Month", "Sentiment"]).size().unstack().fillna(0).reset_index()
        mood_trends_long = mood_trends.melt(id_vars="Month", var_name="Sentiment", value_name="Count")
        
        fig = px.bar(mood_trends_long, x="Month", y="Count", color="Sentiment",
                    barmode="stack", text="Count",
                    title="Mood Trends Over Months",
                    color_discrete_map={"Positive": "green", "Neutral": "gray", "Negative": "red"})
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("📌 No journal entries yet. Start writing to see your progress!")

# Page 3: Dosha Quiz
elif page == "Dosha Quiz":
# Function to calculate dosha scores
    def calculate_dosha_scores(responses):
        scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
        for response in responses:
            for dosha in response:
                scores[dosha] += 1
        return scores

    # Define the questions and options based on the SDL India Prakriti Quiz
    questions = [
        {"question": "My body is:", "options": [
            {"text": "Small", "dosha": "Vata"},
            {"text": "Rough", "dosha": "Vata"},
            {"text": "Medium", "dosha": "Pitta"},
            {"text": "Strong", "dosha": "Pitta"},
            {"text": "Smooth", "dosha": "Kapha"},
            {"text": "Oily", "dosha": "Kapha"},
            {"text": "Gentle", "dosha": "Kapha"}
        ]},
        {"question": "My physique is:", "options": [
            {"text": "Thin", "dosha": "Vata"},
            {"text": "Weak", "dosha": "Vata"},
            {"text": "Medium", "dosha": "Pitta"},
            {"text": "Tender", "dosha": "Pitta"},
            {"text": "Heavy", "dosha": "Kapha"},
            {"text": "Attractive", "dosha": "Kapha"}
        ]},
        {"question": "My skin is:", "options": [
            {"text": "Dry", "dosha": "Vata"},
            {"text": "Rough", "dosha": "Vata"},
            {"text": "Thin", "dosha": "Vata"},
            {"text": "Scaly", "dosha": "Vata"},
            {"text": "Soft", "dosha": "Pitta"},
            {"text": "Reddish", "dosha": "Pitta"},
            {"text": "Oily", "dosha": "Kapha"},
            {"text": "Thick", "dosha": "Kapha"}
        ]},
        {"question": "My complexion is:", "options": [
            {"text": "Dark", "dosha": "Vata"},
            {"text": "Reddish", "dosha": "Pitta"},
            {"text": "With spots", "dosha": "Pitta"},
            {"text": "Moles and pimples", "dosha": "Pitta"},
            {"text": "Fair", "dosha": "Kapha"}
        ]},
        {"question": "My hair is:", "options": [
            {"text": "Rough", "dosha": "Vata"},
            {"text": "Dry", "dosha": "Vata"},
            {"text": "Soft", "dosha": "Pitta"},
            {"text": "Brownish", "dosha": "Pitta"},
            {"text": "Thin", "dosha": "Pitta"},
            {"text": "Oily", "dosha": "Kapha"},
            {"text": "Thick", "dosha": "Kapha"}
        ]},
        {"question": "My nails are:", "options": [
            {"text": "Cracked", "dosha": "Vata"},
            {"text": "Dark", "dosha": "Vata"},
            {"text": "Reddish", "dosha": "Pitta"},
            {"text": "Sharp", "dosha": "Pitta"},
            {"text": "Whitish", "dosha": "Kapha"},
            {"text": "Soft", "dosha": "Kapha"},
            {"text": "Shining", "dosha": "Kapha"}
        ]},
        {"question": "My teeth are:", "options": [
            {"text": "Small size", "dosha": "Vata"},
            {"text": "Irregular", "dosha": "Vata"},
            {"text": "Cracked", "dosha": "Vata"},
            {"text": "With Gaps", "dosha": "Vata"},
            {"text": "Medium size", "dosha": "Pitta"},
            {"text": "Sometimes with discoloration", "dosha": "Pitta"},
            {"text": "Large size", "dosha": "Kapha"},
            {"text": "White", "dosha": "Kapha"},
            {"text": "Regular", "dosha": "Kapha"}
        ]},
        {"question": "My gums are:", "options": [
            {"text": "Dry", "dosha": "Vata"},
            {"text": "Weak", "dosha": "Vata"},
            {"text": "Soft", "dosha": "Pitta"},
            {"text": "Tender", "dosha": "Pitta"},
            {"text": "Strong", "dosha": "Kapha"}
        ]},
        {"question": "My joints are:", "options": [
            {"text": "Weak", "dosha": "Vata"},
            {"text": "Make cracking sound on movement", "dosha": "Vata"},
            {"text": "Flaccid", "dosha": "Pitta"},
            {"text": "Lax", "dosha": "Pitta"},
            {"text": "Strong", "dosha": "Kapha"},
            {"text": "Stable", "dosha": "Kapha"}
        ]},
        {"question": "My activities are:", "options": [
            {"text": "Hyperactive", "dosha": "Vata"},
            {"text": "Moderate", "dosha": "Pitta"},
            {"text": "Slow", "dosha": "Kapha"},
            {"text": "Measured", "dosha": "Kapha"}
        ]},
        {"question": "My sleep is:", "options": [
            {"text": "Irregular", "dosha": "Vata"},
            {"text": "Uncontrollable", "dosha": "Pitta"},
            {"text": "Low", "dosha": "Kapha"},
            {"text": "Steady", "dosha": "Kapha"}
        ]},
        {"question": "My digestion is:", "options": [
            {"text": "Irregular", "dosha": "Vata"},
            {"text": "Sensitive", "dosha": "Vata"},
            {"text": "Strong", "dosha": "Pitta"},
            {"text": "Fast", "dosha": "Pitta"},
            {"text": "Slow", "dosha": "Kapha"},
            {"text": "Steady", "dosha": "Kapha"}
        ]},
        {"question": "My thirst is:", "options": [
            {"text": "Variable", "dosha": "Vata"},
            {"text": "High", "dosha": "Pitta"},
            {"text": "Low", "dosha": "Kapha"},
            {"text": "Moderate", "dosha": "Kapha"}
        ]},
        {"question": "My bowel movements are:", "options": [
            {"text": "Dry", "dosha": "Vata"},
            {"text": "Hard", "dosha": "Vata"},
            {"text": "Soft", "dosha": "Pitta"},
            {"text": "Loose", "dosha": "Pitta"},
            {"text": "Regular", "dosha": "Kapha"},
            {"text": "Well-formed", "dosha": "Kapha"}
        ]},
        {"question": "My speech is:", "options": [
            {"text": "Fast", "dosha": "Vata"},
            {"text": "Talkative", "dosha": "Vata"},
            {"text": "Sharp", "dosha": "Pitta"},
            {"text": "Clear", "dosha": "Pitta"},
            {"text": "Slow", "dosha": "Kapha"},
            {"text": "Measured", "dosha": "Kapha"}
        ]}
    ]

    st.title("Discover Your Ayurveda Dosha")
    st.write("Answer the following questions to determine your Dosha type!")


    responses = []

    for q in questions:
        st.subheader(q["question"])
        
    
        # Create columns dynamically based on the number of options
        cols = st.columns(4)  # Adjust number of columns

        selected_options = []
        for i, option in enumerate(q["options"]):
            col_index = i % 4  # Cycle through 4 columns
            with cols[col_index]:  
                if st.checkbox(option["text"], key=f"{q['question']}_{option['text']}"):
                    selected_options.append(option["dosha"])
        
        responses.append(selected_options)

    if st.button("Determine Dosha"):
        dosha_scores = calculate_dosha_scores(responses)
        # dominant_dosha = max(dosha_scores, key=dosha_scores.get)
        # st.success(f"🌿 Your dominant Dosha Type is: **{dominant_dosha}**")
        st.success(f"🌿The Dosha with the highest number of points signifies your dominant Dosha.")
        st.write(f"Vata: {dosha_scores['Vata']}, Pitta: {dosha_scores['Pitta']}, Kapha: {dosha_scores['Kapha']}")

         # Add a link to a diet recommendation webpage
        st.markdown("[🍽️ Click here to see diet recommendations based on your Dosha](https://sdlindia.com/diet-according-to-dosha/)", unsafe_allow_html=True)

# Page 4: Activities
elif page == "Activities":
    st.title("Activities for Well-being")

    category = st.selectbox("Choose a category:", ["Yoga", "Breathing", "Meditation", "Diet", "Lifestyle"])
    level = st.radio("Select difficulty level:", ["Beginner", "Intermediate", "Advanced"])

    st.subheader(f"📌 Recommended {category} Activities for {level} level")

    # Yoga Activities
    if category == "Yoga":
        if level == "Beginner":
            st.video("https://youtu.be/bJJWArRfKa0")
            st.video("https://www.youtube.com/watch?v=v7AYKMP6rOE")  # 
        elif level == "Intermediate":
            st.video("https://youtu.be/LphBXB0KfxU")  # 15 Minute Energizing Yoga Flow (Morning Routine)
            st.video("https://youtu.be/KPG1tJW8dwQ") 
        else:
            st.video("https://youtu.be/iWUaZfR-gWU")  # 10 MIN EASY HAPPY CARDIO
            

    # Breathing Exercises
    elif category == "Breathing":
        if level == "Beginner":
            st.video("https://www.youtube.com/watch?v=395ZloN4Rr8")  # 5-Minute Meditation (includes breathwork)
            st.video("https://www.youtube.com/watch?v=blbv5UTBCGg")  # Relaxing Music with Nature Sounds
        elif level == "Intermediate":
            st.video("https://www.youtube.com/watch?v=LMS3K8_5KFA")  # Meditation for Anxiety (also includes breathwork)
        else:
            st.video("https://www.youtube.com/watch?v=-7-CAFhJn78")  # Relaxing Music with Nature Sounds

    # Meditation Sessions
    elif category == "Meditation":
        if level == "Beginner":
            st.video("https://youtu.be/inpok4MKVLM")
            st.video("https://youtu.be/ZToicYcHIOU")  # 10 Minute Mindfulness Meditation
        elif level == "Intermediate":
            st.video("https://youtu.be/4pLUleLdwY4")  # 5-Minute Meditation Anywhere
            st.video("https://www.youtube.com/watch?v=1ZYbU82GVz4")
        else:
            st.video("https://youtu.be/1ZYbU82GVz4")  # Waterfall Relaxation Music

    # Diet Suggestions
    elif category == "Diet":
        if level == "Beginner":
            st.video("https://www.youtube.com/watch?v=b5TVaoN5wM4") 
        elif level == "Intermediate":
            st.video("https://www.youtube.com/watch?v=6ZUFT0CwU1w") 
        else:
            st.video("https://www.youtube.com/watch?v=Ni0-KXa2V28")
    

    # Lifestyle Recommendations
    elif category == "Lifestyle":
        if level == "Beginner":
            st.video("https://www.youtube.com/watch?v=7-1Y6IbAxdM")
            st.video("https://www.youtube.com/watch?v=CYr7qJq7bJk") 
        elif level == "Intermediate":
            st.video("https://www.youtube.com/watch?v=SN6U0Z-eBzY")
            st.video("https://www.youtube.com/watch?v=cMwSxrkSX3E&t=375s") 
        else:
            st.video("https://www.youtube.com/watch?v=1nP5oedmzkM")

# PAGE 5: Chat-bot
elif page == "Mood & Mind Chat":
    st.title("Talk to your Mate...")

    #  Place chatbot HTML right here
    chatbot_html = """
    <script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
    <style>
    /* Ensure the chatbot floats at the bottom-right corner */
    df-messenger {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 10000 !important; /* Ensures it stays on top of all other elements */
    }
    </style>
    <df-messenger
    intent="WELCOME"
    chat-title="AyurMi Bot"
    agent-id="61d9d626-beb0-4e6e-ae47-c8cad607c4b8"
    language-code="en">
    </df-messenger>
    """
    st.components.v1.html(chatbot_html, height=600, width=800)

    st.markdown("Drop your journal entry from chatbot below to log it in your journal:")

    journal_text = st.text_area("Start writing...")

    if st.button("Save to Journal"):
        if journal_text.strip():
            # Analyze sentiment
            sentiment_score = analyzer.polarity_scores(journal_text)["compound"]
            sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

            ayurveda_tips = {
                "Positive": "🌿 Stay hydrated and eat fresh fruits",
                "Neutral": "🍵 Take a short walk or do deep breathing.",
                "Negative": "🛀 Unwind with a warm bath and rest well."
            }
            tip = ayurveda_tips[sentiment]

            ist = pytz.timezone("Asia/Kolkata")
            timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

            FILE_PATH = f"journal_entries_{st.session_state.username}.csv"
            if os.path.exists(FILE_PATH):
                df = pd.read_csv(FILE_PATH)
            else:
                df = pd.DataFrame(columns=["Date", "Entry", "Sentiment", "Ayurveda Tip"])

            new_data = {
                "Date": timestamp,
                "Entry": journal_text,
                "Sentiment": sentiment,
                "Ayurveda Tip": tip
            }

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(FILE_PATH, index=False)

            st.success("Your entry has been saved!")
        else:
            st.warning("Please paste or type your journal entry before saving.")

# PAGE 6: AI-Powered Recommendations
elif page == "Recommendations":
    st.title("AI-Powered Health & Wellness Recommendations")

    # Fetch AI-based personalized suggestions
    user_keywords = analyze_journal_entries()
    if user_keywords:
        st.subheader("Personalized Suggestions")
        st.write(f"Based on your journal, you seem interested in: **{', '.join(user_keywords)}**")
        
        ai_articles = {
            "Meditation for Mental Clarity": "https://www.headspace.com/meditation",
            "Balancing Ayurvedic Diet": "https://www.ayurveda.com/resources/articles",
            "How to Reduce Stress with Ayurveda": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573577/"
        }
        
        for title, link in ai_articles.items():
            if any(keyword in title.lower() for keyword in user_keywords):
                st.markdown(f"🔗 [{title}]({link})")

    # Fetch Latest Articles
    st.subheader("Latest Wellness Articles")
    latest_articles = get_latest_articles()
    for article in latest_articles:
        st.markdown(f"📌 [{article['title']}]({article['link']})")

    # Specialist Connections
    st.subheader("Connect with Wellness Experts")
    specialists = {
        "Find Ayurvedic Doctors": "https://www.nama-ayurveda.org/Find-a-Practitioner",
        "Yoga & Mindfulness Coaches": "https://www.yogaalliance.org/",
        "Mental Well-being Support": "https://www.betterhelp.com/"
    }
    for title, link in specialists.items():
        st.markdown(f"🌟 [{title}]({link})")

    st.success("Stay informed and take care of your well-being! 💙")

# else:
#     st.warning("Page not found!")

