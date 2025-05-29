
# Reddit Video Maker

A Flask-based web application that converts Reddit stories into engaging videos with text-to-speech narration and customizable backgrounds.

## Features

- **Text-to-Speech Generation**: Convert Reddit stories to audio using Google Text-to-Speech (gTTS)
- **Multiple Voice Options**: Support for English (5 variants) and Spanish voices
- **Speed Control**: Adjust speech speed from 0.5x to 2.0x
- **Custom Backgrounds**: Use images or videos as background
- **Aspect Ratio Support**: Create videos in 16:9 (YouTube) or 9:16 (Shorts/Reels) format
- **Real-time Preview**: Preview audio and video before downloading

## Installation

### Prerequisites

- Python 3.11+
- FFmpeg (included in Replit environment)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

The application will start on `http://0.0.0.0:8080`

## Usage

### 1. Enter Reddit Story
- Paste your Reddit story text in the text area
- The story will be converted to speech using TTS

### 2. Configure Audio Settings
- **Language**: Choose between English and Spanish
- **Voice**: Select from available voice variants:
  - English: Australian, British, American, Canadian, Indian
  - Spanish: Spanish
- **Speed**: Adjust speech speed using the slider (0.5x - 2.0x)

### 3. Generate Audio
- Click "Generate Audio" to create the TTS file
- Preview the audio using the built-in player

### 4. Add Background
- Choose between image or video background
- Upload your background file (supports: JPG, PNG, MP4, etc.)

### 5. Set Video Format
- **16:9**: Standard YouTube format (1920x1080)
- **9:16**: Vertical format for Shorts/Reels (1080x1920)

### 6. Create Video
- Click "Generate Video" to combine audio and background
- Preview the final video before downloading

## API Endpoints

### POST `/generate-tts`
Generate text-to-speech audio from text.

**Request Body:**
```json
{
    "text": "Your Reddit story text",
    "lang": "en",
    "voice": "us",
    "speed": 1.0
}
```

**Response:**
```json
{
    "audio": "/download/output_timestamp.mp3",
    "filename": "output_timestamp.mp3"
}
```

### POST `/create-video`
Create video by combining audio with background.

**Form Data:**
- `bg_file`: Background image/video file
- `aspect`: Aspect ratio ("16:9" or "9:16")
- `audio_filename`: Previously generated audio filename

**Response:**
```json
{
    "video": "/download/video_timestamp.mp4",
    "aspect": "16:9"
}
```

### GET `/download/<filename>`
Download generated audio or video files.

## File Structure

```
reddit-video-maker/
├── index/
│   └── index.html          # Main web interface
├── uploads/                # Generated files storage
│   ├── *.mp3              # Audio files
│   ├── *.mp4              # Video files
│   └── bg_*               # Temporary background files
├── main.py                # Flask application
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This documentation
```

## Technical Details

### Audio Processing
- Uses Google Text-to-Speech (gTTS) for voice generation
- Speed adjustment implemented with FFmpeg's `atempo` filter
- Supports speed changes from 0.5x to 2.0x with proper filter chaining

### Video Processing
- FFmpeg handles video/image processing and composition
- Automatic scaling and padding to maintain aspect ratios
- Background videos are looped to match audio duration
- Images are extended to full audio duration

### File Management
- Temporary files are automatically cleaned up after processing
- Unique timestamps prevent filename conflicts
- Secure filename handling prevents directory traversal

## Supported File Formats

### Background Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- WebP (.webp)

### Background Videos
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)

### Output Formats
- Audio: MP3 (44.1kHz, stereo, AAC)
- Video: MP4 (H.264, AAC audio)

## Configuration

### Environment Variables
The application uses these default settings:
- **Host**: 0.0.0.0 (accessible externally)
- **Port**: 8080
- **Upload Folder**: uploads/

### TTS Voice Options
```python
TTS_VOICES = {
    'en': [
        {'id': 'com.au', 'name': 'Australian'},
        {'id': 'co.uk', 'name': 'British'},
        {'id': 'us', 'name': 'American'},
        {'id': 'ca', 'name': 'Canadian'},
        {'id': 'ind', 'name': 'Indian'}
    ],
    'es': [
        {'id': 'es', 'name': 'Spanish'}
    ]
}
```

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid input files
- FFmpeg processing errors
- Audio duration detection failures
- File system operations
- Network timeouts

## Performance Considerations

- Audio generation: ~1-2 seconds per 100 words
- Video processing: ~5-10 seconds for typical Reddit story
- File cleanup: Automatic after each request
- Memory usage: Minimal (streaming file operations)

## Troubleshooting

### Common Issues

1. **"Port already in use" error**
   - Stop other Python processes or change port in main.py

2. **FFmpeg not found**
   - Ensure FFmpeg is installed (included in Replit)

3. **Audio generation fails**
   - Check internet connection (gTTS requires online access)
   - Verify text input is not empty

4. **Video processing errors**
   - Ensure background file is valid
   - Check FFmpeg error messages in response

### Debug Mode
Enable Flask debug mode for development:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Dependencies

- **Flask**: Web framework
- **gTTS**: Google Text-to-Speech
- **Werkzeug**: WSGI utilities
- **FFmpeg**: Audio/video processing (system dependency)

## Version History

- v1.0.0: Initial release with basic TTS and video generation
- Current: Enhanced UI, multiple voice options, speed control
