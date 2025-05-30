# main.py
from flask import Flask, request, jsonify, send_from_directory, render_template
from gtts import gTTS
import os
import subprocess
from werkzeug.utils import secure_filename
import time
import speech_recognition as sr
from pydub import AudioSegment
import json

app = Flask(__name__, template_folder='index')

# Replit-specific setup
os.environ["PATH"] += os.pathsep + "/usr/bin"
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Available TTS voices and speeds
TTS_VOICES = {
    'en': [{
        'id': 'com.au',
        'name': 'Australian'
    }, {
        'id': 'co.uk',
        'name': 'British'
    }, {
        'id': 'us',
        'name': 'American'
    }, {
        'id': 'ca',
        'name': 'Canadian'
    }, {
        'id': 'ind',
        'name': 'Indian'
    }],
    'es': [{
        'id': 'es',
        'name': 'Spanish'
    }]
}


@app.route('/')
def home():
    return render_template('index.html', tts_voices=TTS_VOICES)


@app.route('/generate-tts', methods=['POST'])
def generate_tts():
    data = request.json
    text = data.get('text')
    lang = data.get('lang', 'en')
    voice = data.get('voice', 'us')
    speed = float(data.get('speed', 1.0))

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        tts = gTTS(
            text=text,
            lang=lang,
            tld=voice,
            slow=False  # Always generate at normal speed
        )

        timestamp = str(int(time.time()))
        audio_filename = f'output_{timestamp}.mp3'
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        tts.save(audio_path)

        # Adjust speed using FFmpeg if needed
        if abs(speed - 1.0) > 0.01:
            temp_audio = os.path.join(UPLOAD_FOLDER, f'temp_{timestamp}.mp3')
            os.rename(audio_path, temp_audio)
            # atempo only supports 0.5-2.0 per filter, chain if needed
            atempo_filters = []
            s = speed
            while s > 2.0:
                atempo_filters.append('atempo=2.0')
                s /= 2.0
            while s < 0.5:
                atempo_filters.append('atempo=0.5')
                s /= 0.5
            atempo_filters.append(f'atempo={s:.2f}')
            atempo_str = ','.join(atempo_filters)
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_audio, '-filter:a', atempo_str,
                audio_path
            ],
                           check=True)
            os.remove(temp_audio)

        return jsonify({
            'audio': f'/download/{audio_filename}',
            'filename': audio_filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_captions_from_text(text, audio_duration):
    """Generate captions from original text with proper timing"""
    try:
        # Split text into words for better timing calculation
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return None, "No text to generate captions"
        
        # Calculate words per second based on audio duration
        words_per_second = total_words / audio_duration
        
        # Create segments of 3-6 words for TikTok-style captions
        segments = []
        current_segment = []
        
        for i, word in enumerate(words):
            current_segment.append(word)
            
            # Create shorter segments for better readability (3-6 words)
            if (len(current_segment) >= 4 and 
                (word.endswith(('.', '!', '?', ',')) or len(current_segment) >= 6)):
                segments.append(' '.join(current_segment))
                current_segment = []
            # Force break every 6 words to keep segments short
            elif len(current_segment) >= 6:
                segments.append(' '.join(current_segment))
                current_segment = []
        
        # Add remaining words
        if current_segment:
            segments.append(' '.join(current_segment))
        
        # Calculate timing for each segment based on word count
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        # Create SRT content with proper timing
        srt_content = ""
        current_word_index = 0
        
        for i, segment in enumerate(segments):
            segment_words = segment.split()
            words_in_segment = len(segment_words)
            
            # Calculate start and end times based on word position
            start_time = current_word_index / words_per_second
            end_time = (current_word_index + words_in_segment) / words_per_second
            
            # Ensure we don't exceed audio duration
            end_time = min(end_time, audio_duration)
            
            srt_content += f"{i + 1}\n"
            srt_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
            srt_content += f"{segment.upper()}\n\n"  # Uppercase for TikTok style
            
            current_word_index += words_in_segment
        
        return srt_content, f"Generated {len(segments)} caption segments"
        
    except Exception as e:
        return None, f"Caption generation error: {e}"

@app.route('/create-video', methods=['POST'])
def create_video():
    if 'bg_file' not in request.files:
        return jsonify({'error': 'No background file uploaded'}), 400

    bg_file = request.files['bg_file']
    aspect_ratio = request.form.get('aspect', '16:9')
    audio_filename = request.form.get('audio_filename')
    original_text = request.form.get('text', '')  # Get original text for captions

    if not audio_filename:
        return jsonify({'error': 'No audio reference provided'}), 400

    # Create unique filenames
    timestamp = str(int(time.time()))
    bg_filename = f"bg_{timestamp}_{secure_filename(bg_file.filename)}"
    bg_path = os.path.join(UPLOAD_FOLDER, bg_filename)
    output_filename = f"video_{timestamp}.mp4"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # Save background file
    bg_file.save(bg_path)

    try:
        # Step 1: Convert audio to ensure compatibility
        temp_audio = os.path.join(UPLOAD_FOLDER, f'converted_{timestamp}.aac')
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        subprocess.run([
            'ffmpeg', '-y', '-i', audio_path, '-ar', '44100', '-ac', '2',
            '-c:a', 'aac', temp_audio
        ],
                       check=True)

        # Step 2: Get audio duration
        import json as _json
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'json', temp_audio
        ],
                                capture_output=True,
                                text=True)
        duration = None
        if result.returncode == 0:
            info = _json.loads(result.stdout)
            duration = float(info['format']['duration'])
        if not duration:
            return jsonify({'error':
                            'Could not determine audio duration'}), 500

        # Step 3: Generate captions from original text
        srt_content = None
        caption_text = None
        srt_path = None
        
        if original_text.strip():
            srt_content, caption_text = generate_captions_from_text(original_text, duration)
            if srt_content:
                srt_path = os.path.join(UPLOAD_FOLDER, f'captions_{timestamp}.srt')
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
        
        # Step 4: Create video with proper audio mapping and captions
        ext = os.path.splitext(bg_filename)[1].lower()
        is_image = ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        scale_filter = (
            'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2'
            if aspect_ratio == '9:16' else 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2')
        
        # Create video with or without captions
        if srt_path and os.path.exists(srt_path):
            # Font settings for TikTok-style captions
            if aspect_ratio == '16:9':
                font_size = 32
                margin_v = 40
            else:
                font_size = 36
                margin_v = 80
                
            # Escape the SRT path for FFmpeg
            srt_path_escaped = srt_path.replace('\\', '\\\\').replace(':', '\\:')
            subtitle_filter = f"subtitles='{srt_path_escaped}':force_style='Fontsize={font_size},PrimaryColour=&Hffffff,OutlineColour=&H000000,BackColour=&H80000000,Outline=3,Shadow=2,Alignment=2,MarginV={margin_v},Bold=1'"
            
            if is_image:
                cmd = [
                    'ffmpeg', '-y', '-loop', '1', '-framerate', '30', '-t',
                    str(duration), '-i', bg_path, '-i', temp_audio,
                    '-filter_complex', f'[0:v]{scale_filter},{subtitle_filter}[v]', 
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 
                    'fast', '-c:a', 'copy', '-movflags', '+faststart', '-shortest', output_path
                ]
            else:
                cmd = [
                    'ffmpeg', '-y', '-stream_loop', '-1', '-i', bg_path, '-i',
                    temp_audio, '-t', str(duration), '-filter_complex', 
                    f'[0:v]{scale_filter},{subtitle_filter}[v]',
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset',
                    'fast', '-c:a', 'copy', '-movflags', '+faststart', '-shortest',
                    output_path
                ]
        else:
            # Create video without captions
            if is_image:
                cmd = [
                    'ffmpeg', '-y', '-loop', '1', '-framerate', '30', '-t',
                    str(duration), '-i', bg_path, '-i', temp_audio,
                    '-filter_complex', f'[0:v]{scale_filter}[v]', 
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 
                    'fast', '-c:a', 'copy', '-movflags', '+faststart', '-shortest', output_path
                ]
            else:
                cmd = [
                    'ffmpeg', '-y', '-stream_loop', '-1', '-i', bg_path, '-i',
                    temp_audio, '-t', str(duration), '-filter_complex', 
                    f'[0:v]{scale_filter}[v]',
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset',
                    'fast', '-c:a', 'copy', '-movflags', '+faststart', '-shortest',
                    output_path
                ]

        # Run FFmpeg and capture output for debugging
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({
                'error': 'Video creation failed',
                'ffmpeg_error': result.stderr
            }), 500

        # Verify output file exists
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output video not generated'}), 500

        return jsonify({
            'video': f'/download/{output_filename}',
            'aspect': aspect_ratio,
            'captions': caption_text if srt_path else None,
            'srt_file': f'/download/{os.path.basename(srt_path)}' if srt_path else None
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            'error': 'FFmpeg processing failed',
            'details': str(e),
            'cmd': ' '.join(e.cmd) if e.cmd else None
        }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary files
        if 'temp_audio' in locals() and os.path.exists(temp_audio):
            os.remove(temp_audio)
        if os.path.exists(bg_path):
            os.remove(bg_path)


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
