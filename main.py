import streamlit as st
import librosa
import numpy as np
import matplotlib.pyplot as plt
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tempfile
import soundfile as sf
from pydub import AudioSegment
import os


def plot_sentiment_scale(sentiment_score):
    fig, ax = plt.subplots(figsize=(7, 1))
    ax.set_xlim(-1, 1)
    ax.set_xticks(np.arange(-1, 1.1, 0.5))
    ax.set_xticklabels(np.arange(-1, 1.1, 0.5))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_visible(False)

    # Make the background transparent
    ax.set_facecolor("none")

    cmap = plt.get_cmap("RdYlGn")
    color = cmap((sentiment_score + 1) / 2)

    # Draw the gradient background
    gradient = np.linspace(-1, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect="auto", cmap="RdYlGn", extent=[-1, 1, -0.1, 0.1], alpha=0.5)

    # Draw the black triangle marker for the sentiment score
    ax.scatter(sentiment_score, 0, marker="v", color="black", s=100, zorder=10)

    # Label the sentiment score
    ax.annotate(f"Sentiment: {sentiment_score:.2f}", (sentiment_score, 0.05), xytext=(0, 10),
                textcoords='offset points', ha='center', fontsize=10, color="black")

    # Hide ticks and tick labels to make the scale cleaner
    ax.set_xticks([])
    ax.set_yticks([])

    st.pyplot(fig)


# Create the VADER Sentiment Analyzer object
sentiment_analyzer = SentimentIntensityAnalyzer()

def text_sentiment_analysis(text):
    sentiment_score = sentiment_analyzer.polarity_scores(text)['compound']
    if sentiment_score > 0:
        val = 'positive'
    elif sentiment_score == 0:
        val = 'neutral'
    else: val = 'negative'

    return val, sentiment_score


def audio_sentiment_analysis(audio_data):
    # Convert the audio file to WAV format using pydub
    audio = AudioSegment.from_file(audio_data)
    wav_path = audio_data.replace(".m4a", ".wav")  # Create a new temporary WAV file

    # Export the audio as WAV
    audio.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_text = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_text)
        result = text_sentiment_analysis(text)
    except sr.UnknownValueError:
        result = "unknown", 0.0
    except sr.RequestError:
        st.warning("Speech recognition service is unavailable.")
        result = "error", 0.0

    # Delete the temporary WAV file
    os.remove(wav_path)

    return result

def delete_temp_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        st.warning(f"Error deleting temporary file: {e}")


def main():
    # Set the background color
    st.set_page_config( page_title="Sentiment Analyzer", page_icon=":smiley:") 
    
    st.title("Sentiment Analyzer")

    option = st.selectbox("Select Input Type", ("Text", "Audio"))

    if option == "Text":
        text_input = st.text_area("Enter your text here:")
        if st.button("Analyze Text"):
            if text_input:
                sentiment_label, sentiment_score = text_sentiment_analysis(text_input)
                st.write(f"Sentiment: {sentiment_label}, Score: {sentiment_score}")
            else:
                st.warning("Please enter some text to analyze.")

            # Custom sentiment visualization
            plot_sentiment_scale(sentiment_score)

    elif option == "Audio":
        audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
        if audio_file:
            st.audio(audio_file)

            # Save the uploaded audio data to a temporary file
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.read())

                if st.button("Analyze Audio"):
                    sentiment_label, sentiment_score = audio_sentiment_analysis(temp_audio_path)
                    st.write(f"Sentiment: {sentiment_label}, Score: {sentiment_score}")



                    # Custom sentiment visualization
                    plot_sentiment_scale(sentiment_score)

if __name__ == "__main__":
    main()
