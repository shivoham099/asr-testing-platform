# 🎤 ASR Testing Platform - DCS

A comprehensive platform for testing Automatic Speech Recognition (ASR) accuracy for crop names in multiple languages.

## 🌟 Features

- **Multi-language Support**: Hindi and English crop testing
- **CSV Upload**: Upload custom crop datasets
- **Progress Tracking**: Real-time testing progress
- **Results Export**: Download test results as CSV
- **Modern UI**: Clean, responsive interface
- **Session Management**: Persistent testing sessions

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Run locally
streamlit run streamlit_app.py
```

### Deployment
This app is designed to run on Streamlit Cloud with zero configuration.

## 📋 Usage

1. **Enter QA Name**: Input your name to start
2. **Select Language**: Choose Hindi or English
3. **Upload CSV**: Upload crop data or use defaults
4. **Start Testing**: Record 5 sentences per crop
5. **Download Results**: Get CSV with test results

## 📊 CSV Format

Expected format: `serial_number,crop_code,crop_name,language,project`

Example:
```csv
1,H001,पेठा,hindi,DCS
2,H002,बैंगन,hindi,DCS
3,E001,Ash Gourd,english,DCS
```

## 🔧 Configuration

- **Port**: 8501 (default)
- **Theme**: Custom Sarvam-style design
- **Session State**: Persistent across page refreshes

## 📝 License

Built for DCS crop survey testing.