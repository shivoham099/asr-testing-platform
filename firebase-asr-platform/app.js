// Main Application Logic
class ASRTestingPlatform {
    constructor() {
        this.currentUser = null;
        this.currentProject = null;
        this.currentLanguage = null;
        this.currentCrops = [];
        this.selectedCrops = [];
        this.testResults = [];
        this.currentCropIndex = 0;
        this.currentRecordingCount = 0;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAuthStateListener();
    }

    setupEventListeners() {
        // Login
        document.getElementById('googleLoginBtn').addEventListener('click', () => this.signInWithGoogle());
        document.getElementById('logoutBtn').addEventListener('click', () => this.signOut());

        // Project selection
        document.querySelectorAll('.project-card').forEach(card => {
            card.addEventListener('click', (e) => this.selectProject(e.currentTarget.dataset.project));
        });

        // Language selection
        document.getElementById('languageGrid').addEventListener('click', (e) => {
            if (e.target.closest('.language-card')) {
                this.selectLanguage(e.target.closest('.language-card').dataset.language);
            }
        });

        // Task management
        document.getElementById('startTestingBtn').addEventListener('click', () => this.startTesting());

        // Testing
        document.getElementById('recordBtn').addEventListener('click', () => this.toggleRecording());
        document.getElementById('nextCropBtn').addEventListener('click', () => this.nextCrop());
        document.getElementById('stopTestBtn').addEventListener('click', () => this.stopTesting());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportResults());
    }

    setupAuthStateListener() {
        firebase.auth().onAuthStateChanged((user) => {
            if (user) {
                this.currentUser = user;
                this.showScreen('projectScreen');
                document.getElementById('userName').textContent = user.displayName || user.email;
                document.getElementById('qaName').value = user.displayName || '';
            } else {
                this.currentUser = null;
                this.showScreen('loginScreen');
            }
        });
    }

    async signInWithGoogle() {
        try {
            const provider = new firebase.auth.GoogleAuthProvider();
            await firebase.auth().signInWithPopup(provider);
        } catch (error) {
            console.error('Sign in error:', error);
            alert('Sign in failed. Please try again.');
        }
    }

    async signOut() {
        try {
            await firebase.auth().signOut();
        } catch (error) {
            console.error('Sign out error:', error);
        }
    }

    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        document.getElementById(screenId).classList.add('active');
    }

    selectProject(projectId) {
        this.currentProject = projectId;
        document.getElementById('selectedProject').textContent = this.getProjectName(projectId);
        document.getElementById('selectedProject2').textContent = this.getProjectName(projectId);
        document.getElementById('currentProject').textContent = this.getProjectName(projectId);
        
        this.loadLanguages(projectId);
        this.showScreen('languageScreen');
    }

    getProjectName(projectId) {
        const names = {
            'dcs': 'DCS Project',
            'agriculture': 'Agriculture Project'
        };
        return names[projectId] || projectId;
    }

    async loadLanguages(projectId) {
        const languageGrid = document.getElementById('languageGrid');
        languageGrid.innerHTML = '<div class="loading">Loading languages...</div>';

        try {
            // Load languages from Firestore
            const languagesRef = firebase.db.collection('projects').doc(projectId).collection('languages');
            const snapshot = await languagesRef.get();
            
            if (snapshot.empty) {
                // Create default languages if none exist
                await this.createDefaultLanguages(projectId);
                this.loadLanguages(projectId); // Reload
                return;
            }

            languageGrid.innerHTML = '';
            snapshot.forEach(doc => {
                const language = doc.data();
                const languageCard = document.createElement('div');
                languageCard.className = 'language-card';
                languageCard.dataset.language = doc.id;
                languageCard.innerHTML = `
                    <h3>${language.name}</h3>
                    <p>${language.cropCount} crops available</p>
                `;
                languageGrid.appendChild(languageCard);
            });
        } catch (error) {
            console.error('Error loading languages:', error);
            languageGrid.innerHTML = '<div class="error">Error loading languages</div>';
        }
    }

    async createDefaultLanguages(projectId) {
        const languages = [
            { name: 'Hindi', cropCount: 400, file: 'hindi_crops.csv' },
            { name: 'English', cropCount: 400, file: 'english_crops.csv' },
            { name: 'Telugu', cropCount: 300, file: 'telugu_crops.csv' },
            { name: 'Tamil', cropCount: 250, file: 'tamil_crops.csv' },
            { name: 'Bengali', cropCount: 200, file: 'bengali_crops.csv' }
        ];

        const batch = firebase.db.batch();
        languages.forEach(lang => {
            const ref = firebase.db.collection('projects').doc(projectId).collection('languages').doc(lang.name.toLowerCase());
            batch.set(ref, lang);
        });
        await batch.commit();
    }

    async selectLanguage(languageId) {
        this.currentLanguage = languageId;
        document.getElementById('selectedLanguage').textContent = languageId;
        document.getElementById('currentLanguage').textContent = languageId;
        
        await this.loadCrops(languageId);
        this.showScreen('taskScreen');
    }

    async loadCrops(languageId) {
        try {
            // Load crops from Firestore
            const cropsRef = firebase.db.collection('projects').doc(this.currentProject).collection('languages').doc(languageId).collection('crops');
            const snapshot = await cropsRef.get();
            
            if (snapshot.empty) {
                // Create default crops if none exist
                await this.createDefaultCrops(languageId);
                this.loadCrops(languageId); // Reload
                return;
            }

            this.currentCrops = [];
            snapshot.forEach(doc => {
                this.currentCrops.push({
                    id: doc.id,
                    name: doc.data().name,
                    serial: doc.data().serial
                });
            });

            // Sort by serial number
            this.currentCrops.sort((a, b) => a.serial - b.serial);
            
            document.getElementById('totalCrops').textContent = this.currentCrops.length;
        } catch (error) {
            console.error('Error loading crops:', error);
        }
    }

    async createDefaultCrops(languageId) {
        const sampleCrops = [
            'ज्वार', 'चावल', 'मक्का', 'गेहूं', 'बाजरा', 'रागी', 'अरहर', 'चना',
            'मूंग', 'उड़द', 'सोयाबीन', 'मूंगफली', 'तिल', 'सरसों', 'सूरजमुखी',
            'कपास', 'गन्ना', 'आलू', 'प्याज', 'टमाटर', 'बैंगन', 'मिर्च', 'भिंडी'
        ];

        const batch = firebase.db.batch();
        sampleCrops.forEach((crop, index) => {
            const ref = firebase.db.collection('projects').doc(this.currentProject)
                .collection('languages').doc(languageId).collection('crops').doc(`crop_${index + 1}`);
            batch.set(ref, {
                name: crop,
                serial: index + 1
            });
        });
        await batch.commit();
    }

    startTesting() {
        const startSerial = parseInt(document.getElementById('startSerial').value);
        const cropCount = parseInt(document.getElementById('cropCount').value);
        const qaName = document.getElementById('qaName').value;

        if (!qaName.trim()) {
            alert('Please enter your QA name');
            return;
        }

        // Select crops based on serial numbers
        this.selectedCrops = this.currentCrops
            .filter(crop => crop.serial >= startSerial && crop.serial < startSerial + cropCount)
            .slice(0, cropCount);

        if (this.selectedCrops.length === 0) {
            alert('No crops found for the selected range');
            return;
        }

        // Initialize testing session
        this.currentCropIndex = 0;
        this.currentRecordingCount = 0;
        this.testResults = [];

        // Update UI
        document.getElementById('currentQAName').textContent = qaName;
        document.getElementById('totalSelectedCrops').textContent = this.selectedCrops.length;

        this.showScreen('testingScreen');
        this.updateDisplay();
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('status').textContent = 'Say the crop name 5 times clearly';
    }

    updateDisplay() {
        if (this.currentCropIndex < this.selectedCrops.length) {
            const currentCrop = this.selectedCrops[this.currentCropIndex];
            document.getElementById('wordDisplay').textContent = currentCrop.name;
            document.getElementById('currentCropIndex').textContent = this.currentCropIndex + 1;
            document.getElementById('currentRecording').textContent = this.currentRecordingCount + 1;
            
            const progress = ((this.currentCropIndex + 1) / this.selectedCrops.length) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        } else {
            document.getElementById('wordDisplay').textContent = '🎉 Test Complete!';
            document.getElementById('status').textContent = 'All selected crops tested. Export your results.';
            document.getElementById('recordBtn').disabled = true;
            document.getElementById('nextCropBtn').disabled = true;
        }
    }

    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = event => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.processAudio(audioBlob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            document.getElementById('recordBtn').classList.add('recording');
            document.getElementById('recordBtn').textContent = '⏹️ Stop Recording';
            document.getElementById('status').textContent = 'Recording... Speak clearly!';
        } catch (error) {
            console.error('Error accessing microphone:', error);
            document.getElementById('status').textContent = 'Error: Could not access microphone';
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            document.getElementById('recordBtn').classList.remove('recording');
            document.getElementById('status').textContent = 'Processing audio...';
        }
    }

    async processAudio(audioBlob) {
        try {
            // Upload audio to Firebase Storage
            const audioRef = firebase.storage.ref()
                .child(`audio/${this.currentUser.uid}/${Date.now()}.webm`);
            await audioRef.put(audioBlob);
            const audioUrl = await audioRef.getDownloadURL();

            // Call Sarvam ASR API (replace with your actual API)
            const recognizedText = await this.callSarvamASR(audioBlob);
            
            const currentCrop = this.selectedCrops[this.currentCropIndex];
            const isCorrect = recognizedText.toLowerCase().trim() === currentCrop.name.toLowerCase().trim();
            
            const result = {
                cropId: currentCrop.id,
                cropName: currentCrop.name,
                expected: currentCrop.name,
                actual: recognizedText,
                correct: isCorrect,
                audioUrl: audioUrl,
                timestamp: new Date().toISOString(),
                qaName: document.getElementById('qaName').value,
                project: this.currentProject,
                language: this.currentLanguage
            };

            this.testResults.push(result);
            await this.saveResult(result);

            this.currentRecordingCount++;
            this.updateDisplay();
            this.updateResults();
            this.updateStats();

            if (this.currentRecordingCount >= 5) {
                document.getElementById('recordBtn').disabled = true;
                document.getElementById('nextCropBtn').disabled = false;
                document.getElementById('status').textContent = '5 recordings complete. Click Next Crop.';
            } else {
                document.getElementById('status').textContent = `Recording ${this.currentRecordingCount + 1}/5. Say the word again.`;
            }
        } catch (error) {
            console.error('Error processing audio:', error);
            document.getElementById('status').textContent = 'Error processing audio';
        }
    }

    async callSarvamASR(audioBlob) {
        // Mock ASR processing (replace with actual Sarvam API call)
        const mockResponses = [
            this.selectedCrops[this.currentCropIndex].name, // Correct
            this.selectedCrops[this.currentCropIndex].name.toLowerCase(), // Correct but lowercase
            "wrong word", // Wrong
            this.selectedCrops[this.currentCropIndex].name, // Correct
            "another wrong" // Wrong
        ];
        
        const mockResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        return mockResponse;
    }

    async saveResult(result) {
        try {
            await firebase.db.collection('testResults').add(result);
        } catch (error) {
            console.error('Error saving result:', error);
        }
    }

    updateResults() {
        const resultsList = document.getElementById('resultsList');
        const latestResult = this.testResults[this.testResults.length - 1];
        
        const resultDiv = document.createElement('div');
        resultDiv.className = `result-item ${latestResult.correct ? 'correct' : 'incorrect'}`;
        resultDiv.innerHTML = `
            <h4>${latestResult.cropName}</h4>
            <p><strong>Expected:</strong> ${latestResult.expected}</p>
            <p><strong>Got:</strong> ${latestResult.actual}</p>
            <p><strong>Result:</strong> ${latestResult.correct ? '✅ Correct' : '❌ Incorrect'}</p>
        `;
        
        resultsList.appendChild(resultDiv);
        resultsList.scrollTop = resultsList.scrollHeight;
    }

    updateStats() {
        const totalRecordings = this.testResults.length;
        const correctRecordings = this.testResults.filter(r => r.correct).length;
        const accuracy = totalRecordings > 0 ? Math.round((correctRecordings / totalRecordings) * 100) : 0;
        
        document.getElementById('completedCrops').textContent = Math.ceil(totalRecordings / 5);
        document.getElementById('accuracyRate').textContent = accuracy + '%';
        document.getElementById('totalRecordings').textContent = totalRecordings;
    }

    nextCrop() {
        this.currentCropIndex++;
        this.currentRecordingCount = 0;
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('nextCropBtn').disabled = true;
        document.getElementById('status').textContent = 'Say the crop name 5 times clearly';
        this.updateDisplay();
    }

    stopTesting() {
        if (confirm('Are you sure you want to stop testing? Progress will be saved.')) {
            this.showScreen('projectScreen');
            document.getElementById('status').textContent = 'Testing stopped. You can export results or start a new test.';
        }
    }

    async exportResults() {
        if (this.testResults.length === 0) {
            alert('No test results to export');
            return;
        }

        const exportData = {
            qaName: document.getElementById('qaName').value,
            project: this.currentProject,
            language: this.currentLanguage,
            exportDate: new Date().toISOString(),
            totalCrops: this.selectedCrops.length,
            completedCrops: Math.ceil(this.testResults.length / 5),
            totalRecordings: this.testResults.length,
            accuracy: Math.round((this.testResults.filter(r => r.correct).length / this.testResults.length) * 100),
            results: this.testResults
        };

        // Export as JSON
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `sarvam-asr-results-${exportData.qaName.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);

        // Also save to Firestore
        try {
            await firebase.db.collection('exports').add(exportData);
        } catch (error) {
            console.error('Error saving export:', error);
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new ASRTestingPlatform();
});
