# 🎤 Sarvam ASR Testing Platform

A comprehensive Firebase-based platform for testing Speech Recognition accuracy with crop names across multiple languages.

## 🚀 Features

### ✅ **Complete Implementation**
- **Google OAuth Authentication** - Secure login with Google accounts
- **Project Selection** - Multiple projects (DCS, Agriculture, etc.)
- **Language & Dataset Management** - Support for multiple languages
- **Task Management** - Divide and conquer with serial numbers
- **Audio Recording** - High-quality 16kHz mono recording
- **Real-time ASR Testing** - 5 recordings per crop
- **Cloud Storage** - Firebase Storage for audio files
- **Database** - Firestore for results and metadata
- **Export System** - JSON/CSV export capabilities

### 🎯 **Key Capabilities**
- **Multi-tester Support** - QA teams can work on different crop ranges
- **Progress Tracking** - Real-time progress and accuracy metrics
- **Cloud Integration** - All data stored in Firebase
- **Responsive Design** - Works on desktop and mobile
- **Sarvam Styling** - Professional UI matching Sarvam's design

## 📁 Project Structure

```
firebase-asr-platform/
├── index.html              # Main application
├── styles.css              # Sarvam-style CSS
├── app.js                  # Application logic
├── firebase-config.js      # Firebase configuration
├── firebase.json           # Firebase hosting config
├── firestore.rules         # Database security rules
├── storage.rules           # Storage security rules
└── README.md               # This file
```

## 🛠️ Setup Instructions

### 1. **Create Firebase Project**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication, Firestore, and Storage
4. Set up Google Authentication provider

### 2. **Configure Firebase**
1. Copy your Firebase config from Project Settings
2. Update `firebase-config.js` with your credentials:
```javascript
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};
```

### 3. **Deploy to Firebase**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize project
firebase init

# Deploy
firebase deploy
```

### 4. **Set up Data Structure**
The platform will automatically create the following Firestore structure:
```
projects/
├── dcs/
│   └── languages/
│       ├── hindi/
│       │   └── crops/
│       │       ├── crop_1: {name: "ज्वार", serial: 1}
│       │       └── crop_2: {name: "चावल", serial: 2}
│       └── english/
│           └── crops/
├── agriculture/
│   └── languages/
testResults/
├── result_1: {cropName, expected, actual, correct, audioUrl, timestamp, qaName, project, language}
exports/
├── export_1: {qaName, project, language, results, accuracy, exportDate}
```

## 🎮 Usage

### **For QA Testers:**
1. **Login** with Google account
2. **Select Project** (e.g., DCS Project)
3. **Choose Language** (e.g., Hindi)
4. **Set Task Range** (starting serial number, number of crops)
5. **Start Testing** - Record each crop 5 times
6. **Export Results** when done

### **For Admins:**
1. **Upload CSV files** with crop names
2. **Manage projects** and languages
3. **View aggregated results**
4. **Export team results**

## 🔧 Customization

### **Add New Projects:**
Update the project selection in `app.js`:
```javascript
const names = {
    'dcs': 'DCS Project',
    'agriculture': 'Agriculture Project',
    'newproject': 'New Project'  // Add here
};
```

### **Integrate Sarvam ASR API:**
Replace the mock function in `app.js`:
```javascript
async callSarvamASR(audioBlob) {
    // Your Sarvam API integration
    const response = await fetch('your-sarvam-api-endpoint', {
        method: 'POST',
        body: audioBlob,
        headers: {
            'Authorization': 'Bearer your-api-key'
        }
    });
    const result = await response.json();
    return result.transcript;
}
```

### **Add New Languages:**
The platform automatically creates languages when first accessed. You can also manually add them to Firestore.

## 📊 Data Export

Results are exported in JSON format with:
- QA tester information
- Project and language details
- Individual test results
- Overall accuracy metrics
- Audio file URLs

## 🔒 Security

- **Authentication required** for all operations
- **User-specific data** access controls
- **Secure file uploads** to Firebase Storage
- **Database rules** prevent unauthorized access

## 🚀 Deployment

The platform is ready for production deployment on Firebase Hosting with:
- **Automatic HTTPS**
- **Global CDN**
- **Scalable infrastructure**
- **Real-time database**

## 📱 Mobile Support

Fully responsive design works on:
- Desktop browsers
- Mobile devices
- Tablets
- Progressive Web App ready

## 🎯 Next Steps

1. **Set up Firebase project**
2. **Configure authentication**
3. **Deploy to Firebase Hosting**
4. **Integrate Sarvam ASR API**
5. **Upload your crop datasets**
6. **Start testing!**

**Your complete ASR testing platform is ready!** 🎉
