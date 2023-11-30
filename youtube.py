import os
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(youtube_link):
    # Extracting the video ID from the YouTube link
    video_id_match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_link)
    return video_id_match.group(1) if video_id_match else None

def get_youtube_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        return f"Error retrieving transcript: {e}"

def summarize_with_gpt(transcript):
    full_text = ' '.join([entry['text'] for entry in transcript])
    openai_api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    prompt_text = f"Create a summary with an introduction, key points, and a conclusion for the following transcript:\n\n{full_text}\n\nSummary:"

    data = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": prompt_text}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {'content': ''}).get('content', '').strip()
    else:
        print("Error in API response:", response.status_code, response.text)
        return "Error summarizing transcript."


def save_transcript(filename, text):
    with open(filename, 'w') as file:
        file.write(text)

# Main program
if __name__ == "__main__":
    youtube_link = input("Enter the YouTube video link: ")
    video_id = extract_video_id(youtube_link)

    if video_id:
        transcript = get_youtube_transcript(video_id)
        if isinstance(transcript, str):
            print(transcript)  # In case of an error message
        else:
            summary = summarize_with_gpt(transcript)
            print("Transcript Summary:\n", summary)

            # Ask user if they want to save the transcript
            if input("Do you want to save the transcript? (yes/no): ").lower() == 'yes':
                title = YouTubeTranscriptApi.list_transcripts(video_id).find_generated_transcript(['en']).video_title
                filename = f"{title.replace(' ', '_')}.txt"
                save_transcript(filename, summary)
                print(f"Transcript saved as {filename}")
    else:
        print("Invalid YouTube link.")
