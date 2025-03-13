# # cd C:\Users\bharg\OneDrive\Desktop\DP
# # streamlit run app.py

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from wordcloud import WordCloud
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# import datetime
# import os
# import base64

# # Load sentiment analyzer
# analyzer = SentimentIntensityAnalyzer()

# # File path for storing journal entries
# FILE_PATH = "journal_entries.csv"

# # Initialize session state
# if "message" not in st.session_state:
#     st.session_state.message = ""
# if "streak" not in st.session_state:
#     st.session_state.streak = 0

# #Load or initialize journal data
# if os.path.exists(FILE_PATH):
#     df = pd.read_csv(FILE_PATH)
#     df["Date"] = pd.to_datetime(df["Date"])
# else:
#     df = pd.DataFrame(columns=["Date", "Entry", "Sentiment", "Ayurveda Tip"])



# import streamlit as st
# import base64

# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# def set_bg_image(image_file):
#     base64_str = get_base64_of_bin_file(image_file)
#     bg_css = f"""
#     <style>
#     .stApp {{
#         background-image: url("data:image/jpg;base64,{base64_str}");
#         background-repeat: no-repeat;
#         background-position: center center;
#         background-size: cover;
#         background-attachment: fixed;
#     }}

#     /* Transparent overlay ABOVE content */
#     .overlay {{
#         position: fixed;
#         top: 0;
#         left: 0;
#         width: 100%;
#         height: 100%;
#         background: rgba(0, 0, 0, 0.3);  /* Adjust transparency */
#         z-index: 0;  /* Ensures it stays above background but below content */
#     }}

#     /* Moves Streamlit content above the overlay */
#     .block-container {{
#         position: relative;
#         z-index: 1;
#     }}
#     </style>

#     <div class="overlay"></div>
#     """
#     st.markdown(bg_css, unsafe_allow_html=True)

# # Set background image with transparent overlay
# set_bg_image("assets/bgi2.jpg")

# # Set background image with transparent overlay
# set_bg_image("assets/bgi2.jpg")

# # Streak Logic
# if not df.empty and df.iloc[-1]["Date"].date() == datetime.date.today():
#     st.session_state.streak = len(df[df["Date"].dt.date == datetime.date.today()])
# else:
#     st.session_state.streak = 0

# # Streamlit UI
# st.title("🧘‍♀️ JivaJournal - Mindfulness & Ayurveda Journal")
# st.subheader("Write your daily journal and get AI-powered insights!")

# # Show streak
# st.info(f"🔥 Journaling Streak: {st.session_state.streak} days in a row!")

# # Show success message if exists
# if st.session_state.message:
#     st.success(st.session_state.message)
#     st.session_state.message = ""

# # User journal input
# entry = st.text_area("📝 Write about your day:")

# if st.button("Analyze & Save"):
#     if entry.strip():
#         # Get sentiment
#         sentiment_score = analyzer.polarity_scores(entry)["compound"]
#         sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

#         # Ayurveda tips based on sentiment
#         ayurveda_tips = {
#             "Positive": "🌿 Maintain balance with a warm herbal tea!",
#             "Neutral": "🍵 Try deep breathing for better focus.",
#             "Negative": "🛀 Relax with an oil massage or calming yoga."
#         }
#         tip = ayurveda_tips[sentiment]

#         # Personalized Affirmations
#         affirmations = {
#             "Positive": "🌞 You are radiating positivity! Keep shining!",
#             "Neutral": "🌱 Growth happens in stillness. Reflect and thrive.",
#             "Negative": "💖 Challenges build strength. You're doing great!"
#         }
#         affirmation = affirmations[sentiment]

#         # Save entry with timestamp
#         new_data = {
#             "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "Entry": entry,
#             "Sentiment": sentiment,
#             "Ayurveda Tip": tip
#         }
#         df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
#         df.to_csv(FILE_PATH, index=False)

#         # Update streak
#         st.session_state.streak += 1

#         # Show result
#         st.session_state.message = f"Sentiment: **{sentiment}**\nAyurveda Tip: {tip}\n💬 Affirmation: {affirmation}"
#         st.rerun()
#     else:
#         st.warning("Please write something before analyzing.")

# # Show previous entries with edit & delete functionality
# if not df.empty:
#     st.subheader("📜 Your Journal History")

#     for index, row in df.iterrows():
#         with st.expander(f"🗓 {row['Date']} - {row['Sentiment']}"):
#             st.write(f"**Entry:** {row['Entry']}")
#             st.write(f"**Ayurveda Tip:** {row['Ayurveda Tip']}")

#             # Edit feature
#             updated_entry = st.text_area(f"Update Entry Here:", row["Entry"], key=f"edit_{index}")
#             if st.button(f"Save Updated Entry", key=f"save_{index}"):
#                 if updated_entry.strip():
#                     sentiment_score = analyzer.polarity_scores(updated_entry)["compound"]
#                     sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

                   
#                     # Get updated Ayurveda Tip
#                     ayurveda_tips = {
#                         "Positive": "🌿 Maintain balance with a warm herbal tea!",
#                         "Neutral": "🍵 Try deep breathing for better focus.",
#                         "Negative": "🛀 Relax with an oil massage or calming yoga."
#                     }
#                     tip = ayurveda_tips[sentiment]

#                     df.at[index, "Entry"] = updated_entry
#                     df.at[index, "Sentiment"] = sentiment
#                     df.at[index, "Ayurveda Tip"] = tip
#                     df.at[index, "Date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#                     df.to_csv(FILE_PATH, index=False)
#                     st.session_state.message = "Entry updated successfully! Sentiment & Tip recalculated."
#                     st.rerun()
#                 else:
#                     st.session_state.message = "Edited entry cannot be empty!"
#                     st.rerun()

#             # Delete feature
#             if st.button(f"Delete Entry", key=f"delete_{index}"):
#                 df = df.drop(index).reset_index(drop=True)
#                 df.to_csv(FILE_PATH, index=False)
#                 st.session_state.message = "Entry deleted successfully!"
#                 st.rerun()

# # Insights Dashboard
# st.subheader("📊 Journaling Insights")

# # Sentiment Distribution
# st.write("### Sentiment Analysis Over Time")
# fig, ax = plt.subplots(figsize=(10, 4))
# df["Sentiment_Numeric"] = df["Sentiment"].apply(lambda s: {"Positive": 1, "Neutral": 0, "Negative": -1}[s])

# sns.lineplot(data=df, x="Date", y="Sentiment_Numeric", ax=ax, marker="o", color="blue")

# #sns.lineplot(data=df, x="Date", y=df["Sentiment"].apply(lambda s: {"Positive": 1, "Neutral": 0, "Negative": -1}[s]), ax=ax, marker="o", color="blue")
# ax.set_ylabel("Sentiment Score")
# ax.set_xlabel("Date")
# st.pyplot(fig)

# # Word Cloud
# st.write("### Word Cloud of Your Journal Entries")
# text = " ".join(df["Entry"]) if not df.empty else "Start writing to see insights!"
# wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
# fig, ax = plt.subplots(figsize=(10, 5))
# ax.imshow(wordcloud, interpolation="bilinear")
# ax.axis("off")
# st.pyplot(fig)

# st.subheader("💡 Tips for Consistent Journaling")
# st.markdown("""
# - ⏳ **Set a daily reminder** to write for 5 minutes.
# - 🖊 **Be honest** in your reflections, no judgment.
# - 🎯 **Set goals** and track patterns in your mood.
# """)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime
import os
import base64

# Load sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# File path for storing journal entries
FILE_PATH = "journal_entries.csv"

# Initialize session state
if "message" not in st.session_state:
    st.session_state.message = ""
if "streak" not in st.session_state:
    st.session_state.streak = 0

# Load or initialize journal data
if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Entry", "Sentiment", "Ayurveda Tip"])

# Streamlit Sidebar Navigation
st.sidebar.title("🌿 JivaJournal Navigation")
page = st.sidebar.radio("Go to", ["Journaling", "Dashboard", "Dosha Quiz", "Activities"])

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