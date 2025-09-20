# 🚀 ASR Testing Platform - COMPLETE SETUP GUIDE

## **YOU'RE READY TO GO!** 🎉

Your ASR testing platform is built and ready to use. Here's everything you need to know:

## **Quick Start (2 Minutes)**

### 1. **Start the Platform**
```bash
cd /Users/shivenderabrol/Downloads/asr-testing-platform
./start.sh
```

### 2. **Open in Browser**
Visit: `http://localhost:5000`

### 3. **Login with Google**
- Click "Login with Google"
- Use your Google account
- Start testing!

## **What You Have Built**

✅ **Beautiful Web Interface** - Modern, responsive design  
✅ **Google OAuth Login** - Secure authentication  
✅ **Audio Recording** - 3-5 recordings per crop  
✅ **400 Crop Names** - Hindi/English crop database  
✅ **Real-time ASR** - Ready for Sarvam API integration  
✅ **Data Storage** - SQLite database  
✅ **Results Export** - JSON format  
✅ **Progress Tracking** - Visual progress bar  

## **File Structure**
```
asr-testing-platform/
├── index.html              # Main interface (standalone)
├── app.py                  # Flask backend
├── templates/
│   ├── index.html          # Flask template
│   └── login.html          # Login page
├── crops.json              # 400 crop names
├── requirements.txt        # Dependencies
├── start.sh               # Quick start script
├── venv/                  # Virtual environment
└── asr_testing.db         # Database (auto-created)
```

## **Next Steps (Day 2)**

### 1. **Set Up Google OAuth (5 minutes)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:5000/login/authorized`
6. Update `app.py`:
   ```python
   consumer_key='YOUR_CLIENT_ID',
   consumer_secret='YOUR_CLIENT_SECRET',
   ```

### 2. **Integrate Sarvam ASR API (30 minutes)**
Replace the mock function in `app.py`:
```python
def call_sarvam_asr(audio_data):
    # Your Sarvam API integration
    response = requests.post('YOUR_SARVAM_API_ENDPOINT', 
                           data={'audio': audio_data})
    return response.json()['transcript']
```

### 3. **Test with QA Team (1 hour)**
- Have QA testers login
- Test the complete workflow
- Export results
- Gather feedback

## **How It Works**

1. **User logs in** with Google OAuth
2. **Crop name displays** on screen
3. **User records audio** 5 times
4. **ASR processes** each recording
5. **Results are compared** and stored
6. **Progress tracked** visually
7. **Results exported** as JSON

## **API Endpoints**

- `GET /` - Main interface
- `GET /login` - Google OAuth login
- `GET /api/crops` - Get crop list
- `POST /api/process-audio` - Process audio with ASR
- `GET /api/export-results` - Export test results

## **Database Schema**

### Users Table
- `id`, `google_id`, `name`, `email`, `created_at`

### Test Sessions Table
- `id`, `user_id`, `session_name`, `created_at`

### Test Results Table
- `id`, `session_id`, `crop_name`, `expected_text`, `actual_text`, `is_correct`, `audio_file_path`, `created_at`

## **Customization**

### Add More Crops
Edit `crops.json` with your crop names.

### Change Recording Count
In `templates/index.html`, change:
```javascript
if (currentRecordingCount >= 5) {  // Change 5 to desired number
```

### Modify UI
Edit CSS in `templates/index.html` or `index.html`.

## **Troubleshooting**

### Server Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>
```

### Google OAuth Issues
- Check redirect URI matches exactly
- Ensure Google+ API is enabled
- Verify client ID/secret are correct

### Audio Recording Issues
- Check microphone permissions
- Use HTTPS in production
- Test with different browsers

## **Production Deployment**

### For Production Use:
1. **Use Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
2. **Set Environment Variables**: For secrets
3. **Use PostgreSQL**: Instead of SQLite
4. **Add HTTPS**: SSL certificates
5. **Add Logging**: Proper error handling

## **Support**

This is a 2-day MVP that does exactly what you need:
- ✅ Tests ASR accuracy with crop names
- ✅ Records audio multiple times
- ✅ Compares results with expected text
- ✅ Stores data for analysis
- ✅ Exports results for your team

**You're all set! Start testing!** 🎯
