# ASR Testing Platform

A web-based platform for QA testing of ASR (Automatic Speech Recognition) systems, specifically designed for testing crop name recognition using the Sarvam API.

## Features

- **QA Login**: Simple name-based login (Google login integration planned)
- **Multi-language Support**: Hindi, Odia, English, Gujarati, Malayalam
- **CSV Upload**: Upload crop names in CSV format
- **Audio Recording**: Web-based audio recording (5 attempts per crop)
- **ASR Integration**: Uses Sarvam API for speech-to-text conversion
- **Keyword Matching**: Automatic detection of crop names in transcribed text
- **Results Export**: Download detailed results as CSV
- **Database Storage**: SQLite database for storing all test results

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 3. CSV Format

Create a CSV file with crop names (one per row, no header):

```
गेहूं
चावल
मक्का
बाजरा
ज्वार
```

## Usage Flow

1. **Login**: Enter your QA name
2. **Language Selection**: Choose from supported languages
3. **CSV Upload**: Upload your crop names CSV file
4. **Testing**: For each crop name:
   - Record 5 audio samples using the crop name in sentences
   - Each recording is automatically transcribed using Sarvam API
   - Keyword matching determines if the crop name was detected
5. **Results**: View detailed results and download CSV

## API Configuration

The platform uses the Sarvam API with the following configuration:
- **API URL**: `https://api.sarvam.ai/speech-to-text`
- **API Key**: Configured in the application
- **Supported Languages**: Hindi, Odia, English, Gujarati, Malayalam

## Database Schema

The SQLite database includes:
- `qa_users`: Store QA user information
- `test_sessions`: Track testing sessions
- `test_results`: Store detailed test results with all 5 recording logs

## File Structure

```
asr-testing-platform/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── sample_crops.csv      # Sample crop names
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── language_selection.html
│   ├── upload_csv.html
│   ├── testing.html
│   └── results.html
└── uploads/              # Temporary file storage
```

## Testing the ASR API

The platform includes sample crop names for testing. You can also upload your own CSV file with crop names in the supported languages.

## Future Enhancements

- Google Login integration
- Additional language support
- Batch processing capabilities
- Advanced analytics and reporting
- User management system