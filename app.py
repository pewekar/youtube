from flask import Flask, request, jsonify, render_template
import youtube  # Replace with the name of your Python script

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_transcript():
    youtube_link = request.json.get('youtube_link')
    print("Received YouTube link:", youtube_link)  # Debug print
    video_id = youtube.extract_video_id(youtube_link)
    print("Video ID:", video_id)  # Debug print
    if video_id:
        transcript = youtube.get_youtube_transcript(video_id)
        if isinstance(transcript, list):  # Ensure transcript is a list
            summary = youtube.summarize_with_gpt(transcript)
            return jsonify({'summary': summary})
        else:
            return jsonify({'error': 'Error in fetching transcript'})
    else:
        return jsonify({'error': 'Invalid YouTube link.'})

if __name__ == '__main__':
    app.run(debug=True)
