// Main Application Logic - POC Version
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
        
        // Default crop data with proper structure
        this.cropData = {
            hindi: [
                { serial: 1, code: '700100', name: 'पेठा', language: 'hindi', project: 'dcs' },
                { serial: 2, code: '700500', name: 'बैंगन', language: 'hindi', project: 'dcs' },
                { serial: 3, code: '700600', name: 'ब्रसेल्स स्प्राउट', language: 'hindi', project: 'dcs' },
                { serial: 4, code: '700700', name: 'ब्रोकली', language: 'hindi', project: 'dcs' },
                { serial: 5, code: '700800', name: 'चुकंदर', language: 'hindi', project: 'dcs' },
                { serial: 6, code: '700900', name: 'करेला', language: 'hindi', project: 'dcs' },
                { serial: 7, code: '701000', name: 'पत्ता गोभी', language: 'hindi', project: 'dcs' },
                { serial: 8, code: '701100', name: 'फूल गोभी', language: 'hindi', project: 'dcs' },
                { serial: 9, code: '701200', name: 'गाजर', language: 'hindi', project: 'dcs' },
                { serial: 10, code: '701300', name: 'चीनी मेलो', language: 'hindi', project: 'dcs' },
                { serial: 11, code: '701400', name: 'गवार फली', language: 'hindi', project: 'dcs' },
                { serial: 12, code: '701500', name: 'अजवाइन', language: 'hindi', project: 'dcs' },
                { serial: 13, code: '701600', name: 'गिल्की', language: 'hindi', project: 'dcs' },
                { serial: 14, code: '701700', name: 'गांठ गोभी', language: 'hindi', project: 'dcs' },
                { serial: 15, code: '701800', name: 'कुंदरू', language: 'hindi', project: 'dcs' },
                { serial: 16, code: '701900', name: 'खीरा', language: 'hindi', project: 'dcs' },
                { serial: 17, code: '702000', name: 'लौकी', language: 'hindi', project: 'dcs' },
                { serial: 18, code: '702100', name: 'भिंडी', language: 'hindi', project: 'dcs' }
            ],
            english: [
                { serial: 1, code: '700100', name: 'Ash Gourd', language: 'english', project: 'dcs' },
                { serial: 2, code: '700500', name: 'Brinjal', language: 'english', project: 'dcs' },
                { serial: 3, code: '700600', name: 'Brussels Sprout', language: 'english', project: 'dcs' },
                { serial: 4, code: '700700', name: 'Broccoli', language: 'english', project: 'dcs' },
                { serial: 5, code: '700800', name: 'Beetroot', language: 'english', project: 'dcs' },
                { serial: 6, code: '700900', name: 'Bitter Gourd', language: 'english', project: 'dcs' },
                { serial: 7, code: '701000', name: 'Cabbage', language: 'english', project: 'dcs' },
                { serial: 8, code: '701100', name: 'Cauliflower', language: 'english', project: 'dcs' },
                { serial: 9, code: '701200', name: 'Carrot', language: 'english', project: 'dcs' },
                { serial: 10, code: '701300', name: 'Chinese Mellow', language: 'english', project: 'dcs' },
                { serial: 11, code: '701400', name: 'Cluster Bean', language: 'english', project: 'dcs' },
                { serial: 12, code: '701500', name: 'Celery', language: 'english', project: 'dcs' },
                { serial: 13, code: '701600', name: 'Gilky', language: 'english', project: 'dcs' },
                { serial: 14, code: '701700', name: 'Kohlrabi', language: 'english', project: 'dcs' },
                { serial: 15, code: '701800', name: 'Ivy Gourd', language: 'english', project: 'dcs' },
                { serial: 16, code: '701900', name: 'Cucumber', language: 'english', project: 'dcs' },
                { serial: 17, code: '702000', name: 'Bottle Gourd', language: 'english', project: 'dcs' },
                { serial: 18, code: '702100', name: 'Okra', language: 'english', project: 'dcs' }
            ]
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login
        document.getElementById('loginBtn').addEventListener('click', () => this.login());

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

        // CSV upload
        document.getElementById('csvFile').addEventListener('change', (e) => this.handleFileUpload(e));
        document.getElementById('uploadArea').addEventListener('click', () => document.getElementById('csvFile').click());
        document.getElementById('uploadArea').addEventListener('dragover', (e) => this.handleDragOver(e));
        document.getElementById('uploadArea').addEventListener('drop', (e) => this.handleDrop(e));

        // Task management
        document.getElementById('startTestingBtn').addEventListener('click', () => this.startTesting());

        // Testing
        document.getElementById('recordBtn').addEventListener('click', () => this.toggleRecording());
        document.getElementById('nextCropBtn').addEventListener('click', () => this.nextCrop());
        document.getElementById('stopTestBtn').addEventListener('click', () => this.stopTesting());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportResults());
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
    }

    login() {
        const qaName = document.getElementById('qaName').value.trim();
        if (!qaName) {
            alert('Please enter your QA name');
            return;
        }

        this.currentUser = { name: qaName };
        document.getElementById('userName').textContent = qaName;
        document.getElementById('qaNameDisplay').value = qaName;
        this.showScreen('projectScreen');
    }

    logout() {
        this.currentUser = null;
        this.showScreen('loginScreen');
        document.getElementById('qaName').value = '';
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
        this.showScreen('languageScreen');
    }

    getProjectName(projectId) {
        const names = {
            'dcs': 'DCS Project',
            'agriculture': 'Agriculture Project'
        };
        return names[projectId] || projectId;
    }

    selectLanguage(languageId) {
        this.currentLanguage = languageId;
        document.getElementById('selectedLanguage').textContent = languageId;
        document.getElementById('currentLanguage').textContent = languageId;
        
        // Load crops for selected language (prioritize uploaded crops)
        if (this.uploadedCrops && this.uploadedCrops.length > 0) {
            this.currentCrops = this.uploadedCrops
                .filter(crop => crop.language === languageId && crop.project === this.currentProject)
                .sort((a, b) => a.serial - b.serial);
        } else {
            this.currentCrops = this.cropData[languageId] || [];
        }
        
        // Check if crops are available for this language
        if (this.currentCrops.length === 0) {
            alert(`No crops found for ${languageId} language. Please upload a CSV with ${languageId} crops or select a different language.`);
            return;
        }
        
        document.getElementById('totalCrops').textContent = this.currentCrops.length;
        
        // Show success message
        console.log(`✅ Loaded ${this.currentCrops.length} ${languageId} crops for testing`);
        
        this.showScreen('taskScreen');
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            this.processCSVFile(file);
        } else {
            alert('Please select a valid CSV file');
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        const file = event.dataTransfer.files[0];
        if (file && file.type === 'text/csv') {
            this.processCSVFile(file);
        } else {
            alert('Please drop a valid CSV file');
        }
    }

    processCSVFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const text = e.target.result;
                const lines = text.split('\n').filter(line => line.trim());
                
                if (lines.length < 2) {
                    alert('CSV file must have at least a header and one data row');
                    return;
                }

                // Parse header and normalize column names
                const header = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/[^a-z0-9_]/g, ''));
                const requiredColumns = ['serialnumber', 'cropcode', 'cropname', 'language', 'project'];
                
                // Map common variations to standard names
                const columnMapping = {
                    'serialnumber': ['serial_number', 'serialnumber', 'serial'],
                    'cropcode': ['crop_code', 'cropcode', 'cropcode'],
                    'cropname': ['crop_name', 'cropname', 'crop_name'],
                    'language': ['language', 'lang'],
                    'project': ['project', 'proj']
                };
                
                // Check if all required columns are present (with variations)
                const missingColumns = [];
                const foundColumns = {};
                
                requiredColumns.forEach(requiredCol => {
                    const variations = columnMapping[requiredCol];
                    const found = variations.some(variation => header.includes(variation));
                    if (!found) {
                        missingColumns.push(requiredCol);
                    } else {
                        // Find the actual column name used
                        const actualCol = variations.find(variation => header.includes(variation));
                        foundColumns[requiredCol] = header.indexOf(actualCol);
                    }
                });
                
                if (missingColumns.length > 0) {
                    alert(`Missing required columns: ${missingColumns.join(', ')}\n\nFound columns: ${header.join(', ')}`);
                    return;
                }

                // Parse data
                const crops = [];
                const languageCounts = {};
                
                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(',').map(v => v.trim());
                    if (values.length >= 5) {
                        const crop = {
                            serial: parseInt(values[foundColumns.serialnumber]) || i,
                            code: values[foundColumns.cropcode],
                            name: values[foundColumns.cropname],
                            language: values[foundColumns.language].toLowerCase(),
                            project: values[foundColumns.project].toLowerCase()
                        };
                        
                        crops.push(crop);
                        
                        // Count by language
                        if (!languageCounts[crop.language]) {
                            languageCounts[crop.language] = 0;
                        }
                        languageCounts[crop.language]++;
                    }
                }

                // Update crop data
                this.uploadedCrops = crops;
                
                // Update language counts in UI and show/hide language cards
                Object.keys(languageCounts).forEach(lang => {
                    const countElement = document.getElementById(`${lang}-count`);
                    if (countElement) {
                        countElement.textContent = `${languageCounts[lang]} crops available`;
                    }
                    
                    // Show language card if it has crops
                    const languageCard = document.querySelector(`[data-language="${lang}"]`);
                    if (languageCard) {
                        languageCard.style.display = 'block';
                    }
                });
                
                // Hide language cards that have no crops
                const allLanguageCards = document.querySelectorAll('.language-card');
                allLanguageCards.forEach(card => {
                    const lang = card.dataset.language;
                    if (!languageCounts[lang]) {
                        card.style.display = 'none';
                    }
                });

                // Show success message
                document.getElementById('fileInfo').classList.remove('hidden');
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('cropCount').textContent = crops.length;

                alert(`✅ Successfully loaded ${crops.length} crops from CSV file!`);

            } catch (error) {
                console.error('Error processing CSV:', error);
                alert('Error processing CSV file. Please check the format.');
            }
        };
        reader.readAsText(file);
    }

    startTesting() {
        const startSerial = parseInt(document.getElementById('startSerial').value);
        const cropCount = parseInt(document.getElementById('cropCount').value);

        console.log('Debug - currentCrops:', this.currentCrops);
        console.log('Debug - currentLanguage:', this.currentLanguage);
        console.log('Debug - cropData:', this.cropData);

        // Ensure we have crops loaded
        if (!this.currentCrops || this.currentCrops.length === 0) {
            // Reload crops for current language
            if (this.currentLanguage) {
                this.currentCrops = this.cropData[this.currentLanguage] || [];
                console.log('Reloaded crops:', this.currentCrops);
            }
        }

        if (startSerial < 1 || startSerial > this.currentCrops.length) {
            alert(`Invalid starting serial number. Available range: 1-${this.currentCrops.length}`);
            return;
        }

        // Select crops based on serial numbers
        this.selectedCrops = this.currentCrops
            .slice(startSerial - 1, startSerial - 1 + cropCount)
            .map((crop, index) => ({
                id: `crop_${startSerial + index}`,
                name: crop.name,
                code: crop.code,
                serial: startSerial + index,
                language: crop.language,
                project: crop.project
            }));

        if (this.selectedCrops.length === 0) {
            alert('No crops found for the selected range');
            return;
        }

        // Initialize testing session
        this.currentCropIndex = 0;
        this.currentRecordingCount = 0;
        this.testResults = [];

        // Update UI
        document.getElementById('currentQAName').textContent = this.currentUser.name;
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
            // Mock ASR processing (replace with Sarvam API)
            const recognizedText = await this.callSarvamASR(audioBlob);
            
            const currentCrop = this.selectedCrops[this.currentCropIndex];
            const isCorrect = recognizedText.toLowerCase().trim() === currentCrop.name.toLowerCase().trim();
            
            const result = {
                cropId: currentCrop.id,
                cropCode: currentCrop.code,
                cropName: currentCrop.name,
                expected: currentCrop.name,
                actual: recognizedText,
                correct: isCorrect,
                timestamp: new Date().toISOString(),
                qaName: this.currentUser.name,
                project: this.currentProject,
                language: this.currentLanguage,
                recordingNumber: this.currentRecordingCount + 1
            };

            this.testResults.push(result);
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
        // TODO: Replace with actual Sarvam ASR API call
        try {
            // Example Sarvam API integration:
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('language', this.currentLanguage); // hindi, english, etc.
            formData.append('model', 'crop_survey'); // or your specific model
            
            const response = await fetch('YOUR_SARVAM_API_ENDPOINT', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer YOUR_SARVAM_API_KEY'
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            const result = await response.json();
            return result.transcript || result.text || '';
            
        } catch (error) {
            console.error('Sarvam ASR Error:', error);
            
            // Fallback to mock for now
            const mockResponses = [
                this.selectedCrops[this.currentCropIndex].name, // Correct
                this.selectedCrops[this.currentCropIndex].name.toLowerCase(), // Correct but lowercase
                "wrong word", // Wrong
                this.selectedCrops[this.currentCropIndex].name, // Correct
                "another wrong" // Wrong
            ];
            
            const mockResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
            await new Promise(resolve => setTimeout(resolve, 1000));
            return mockResponse;
        }
    }

    updateResults() {
        const resultsList = document.getElementById('resultsList');
        const latestResult = this.testResults[this.testResults.length - 1];
        
        const resultDiv = document.createElement('div');
        resultDiv.className = `result-item ${latestResult.correct ? 'correct' : 'incorrect'}`;
        resultDiv.innerHTML = `
            <h4>${latestResult.cropName} (${latestResult.cropCode}) - Recording ${latestResult.recordingNumber}</h4>
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

    exportResults() {
        if (this.testResults.length === 0) {
            alert('No test results to export');
            return;
        }

        const exportData = {
            qaName: this.currentUser.name,
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

        alert('Results exported successfully!');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new ASRTestingPlatform();
});
