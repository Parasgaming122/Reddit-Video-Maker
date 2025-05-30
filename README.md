
# Reddit Video Maker

A Flask-based web application that converts Reddit stories into engaging videos with text-to-speech narration, customizable backgrounds, and automatic caption generation.

## Features

- **Text-to-Speech Generation**: Convert Reddit stories to audio using Google Text-to-Speech (gTTS)
- **Multiple Voice Options**: Support for English (5 variants) and Spanish voices
- **Speed Control**: Adjust speech speed from 0.5x to 2.0x
- **Custom Backgrounds**: Use images or videos as background
- **Auto Caption Generation**: Automatically generate and embed TikTok-style captions synced with voiceover
- **SRT Export**: Download caption files in SRT format
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
- The story will be converted to speech using TTS and used for caption generation

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

### 6. Create Video with Auto Captions
- Click "Generate Video" to combine audio, background, and captions
- Captions are automatically generated from your original text
- TikTok-style captions (uppercase, bold, centered) are embedded in the video
- Preview the final video with captions before downloading
- Download SRT caption files separately if needed

## Caption Features

### Auto Caption Generation
- Captions are automatically generated from the original Reddit story text
- Text is intelligently segmented into 3-6 word chunks for optimal readability
- Timing is calculated based on audio duration for perfect synchronization
- TikTok-style formatting: uppercase text with bold styling

### Caption Styling
- **Font**: Bold, uppercase text for maximum readability
- **Position**: Centered on screen with proper margins
- **Colors**: White text with black outline and semi-transparent background
- **Timing**: Precisely synced with voiceover audio

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
Create video by combining audio with background and auto-generated captions.

**Form Data:**
- `bg_file`: Background image/video file
- `aspect`: Aspect ratio ("16:9" or "9:16")
- `audio_filename`: Previously generated audio filename
- `text`: Original text for caption generation

**Response:**
```json
{
    "video": "/download/video_timestamp.mp4",
    "aspect": "16:9",
    "captions": "Generated X caption segments",
    "srt_file": "/download/captions_timestamp.srt"
}
```

### GET `/download/<filename>`
Download generated audio, video, or SRT caption files.

## File Structure

```
reddit-video-maker/
├── index/
│   └── index.html          # Main web interface
├── uploads/                # Generated files storage
│   ├── *.mp3              # Audio files
│   ├── *.mp4              # Video files with embedded captions
│   ├── *.srt              # Caption files
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

### Caption Processing
- Intelligent text segmentation for optimal readability
- Word-count based timing calculation for precise synchronization
- SRT format generation with proper timestamp formatting
- FFmpeg subtitle filter integration for embedded captions

### Video Processing
- FFmpeg handles video/image processing and composition
- Automatic scaling and padding to maintain aspect ratios
- Background videos are looped to match audio duration
- Images are extended to full audio duration
- Subtitle overlay with customizable styling

### File Management
- Temporary files are automatically cleaned up after processing
- Unique timestamps prevent filename conflicts
- Secure filename handling prevents directory traversal
- SRT files available for separate download

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
- Video: MP4 (H.264, AAC audio) with embedded captions
- Captions: SRT (SubRip Subtitle format)

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

### Caption Settings
- **Segment Length**: 3-6 words per caption for optimal readability
- **Font Size**: 32px (16:9) / 36px (9:16) for clear visibility
- **Styling**: Bold, uppercase, white text with black outline
- **Position**: Bottom-centered with proper margins

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid input files
- FFmpeg processing errors
- Audio duration detection failures
- Caption generation failures
- File system operations
- Network timeouts

## Performance Considerations

- Audio generation: ~1-2 seconds per 100 words
- Caption generation: Near-instantaneous text processing
- Video processing: ~5-15 seconds for typical Reddit story (including captions)
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

5. **Caption sync issues**
   - Ensure original text matches the generated audio
   - Check that text segmentation is working properly

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
- **SpeechRecognition**: Audio processing utilities
- **pydub**: Audio manipulation library
- **FFmpeg**: Audio/video processing (system dependency)

## Version History

- v1.0.0: Initial release with basic TTS and video generation
- v1.1.0: Added auto caption generation and SRT export
- Current: Enhanced UI, multiple voice options, speed control, TikTok-style captions
