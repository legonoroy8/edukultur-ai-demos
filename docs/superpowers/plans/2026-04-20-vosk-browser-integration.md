# vosk-browser A-Z Recognition Integration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Chrome Web Speech API with vosk-browser (WASM) for reliable offline letter recognition on all devices.

**Architecture:** VoskEngine wrapper object inside `english-spelling.html` handles model loading, mic stream, and continuous recognition. Existing state machine and `processVoiceInput()` are unchanged. Web Speech API kept as fallback if VOSK fails to load.

**Tech Stack:** vosk-browser@0.0.5 (jsDelivr CDN), vosk-model-small-en-us-0.15.tar.gz (~40MB, committed to repo), Web Audio API (ScriptProcessorNode), getUserMedia

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `english alphabet spelling/models/vosk-model-small-en-us-0.15.tar.gz` | Create | VOSK model, served by GitHub Pages, cached by vosk-browser in IndexedDB |
| `english alphabet spelling/english-spelling.html` | Modify | Add VoskEngine, loading UI, swap recognition internals, add ignore-flag |

---

### Task 1: Download and commit the model file

**Files:**
- Create: `english alphabet spelling/models/vosk-model-small-en-us-0.15.tar.gz`

- [ ] **Step 1: Create models directory**

```bash
mkdir "C:/Users/legon/Documents/Taktis/Client/Edukultur/demo/english alphabet spelling/models"
```

- [ ] **Step 2: Download model zip from alphacephei and repack as tar.gz**

Run these commands from `english alphabet spelling/models/` directory:

```powershell
cd "C:/Users/legon/Documents/Taktis/Client/Edukultur/demo/english alphabet spelling/models"

# Download (~40MB — takes a minute)
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -OutFile "vosk-model-small-en-us-0.15.zip"

# Extract
Expand-Archive -Path "vosk-model-small-en-us-0.15.zip" -DestinationPath "."

# Repack as tar.gz (tar is built into Windows 10+)
tar -czf "vosk-model-small-en-us-0.15.tar.gz" "vosk-model-small-en-us-0.15"

# Cleanup
Remove-Item "vosk-model-small-en-us-0.15.zip"
Remove-Item -Recurse -Force "vosk-model-small-en-us-0.15"
```

Expected: `vosk-model-small-en-us-0.15.tar.gz` exists, size ~40MB.

- [ ] **Step 3: Verify file exists and is non-zero**

```powershell
Get-Item "C:/Users/legon/Documents/Taktis/Client/Edukultur/demo/english alphabet spelling/models/vosk-model-small-en-us-0.15.tar.gz" | Select-Object Name, Length
```

Expected output: Name `vosk-model-small-en-us-0.15.tar.gz`, Length ~40000000+

- [ ] **Step 4: Commit model file**

```bash
cd "C:/Users/legon/Documents/Taktis/Client/Edukultur/demo"
git add "english alphabet spelling/models/vosk-model-small-en-us-0.15.tar.gz"
git commit -m "feat: add vosk-model-small-en-us-0.15 model for offline speech recognition"
```

> Note: 40MB binary push will be slower than usual — this is expected.

---

### Task 2: Add VoskEngine object to english-spelling.html

**Files:**
- Modify: `english alphabet spelling/english-spelling.html` — insert VoskEngine after the `MIC_STATE` / state variable block (~line 870)

- [ ] **Step 1: Add `voskIgnoreResults` flag to variable declarations**

Find this block (around line 870):
```javascript
        let lastHeardInput = '';
```

Replace with:
```javascript
        let lastHeardInput = '';
        let voskIgnoreResults = false; // true during feedback delays — prevents double-recognition
```

- [ ] **Step 2: Add VoskEngine object after the variable declarations block**

Find this line (around line 872):
```javascript
        // Statistics
        let stats = {
```

Insert the entire VoskEngine object immediately before it:

```javascript
        // ── VoskEngine ────────────────────────────────────────────────────────────
        const VoskEngine = {
            _model: null,
            _recognizer: null,
            _audioContext: null,
            _processor: null,
            _stream: null,
            isReady: false,
            isListeningActive: false,

            async init() {
                try {
                    if (typeof Vosk === 'undefined') {
                        console.warn('VoskEngine: vosk-browser script not loaded');
                        return false;
                    }
                    Vosk.setLogLevel(-1);
                    this._model = await Vosk.createModel('./models/vosk-model-small-en-us-0.15.tar.gz');
                    this.isReady = true;
                    console.log('VoskEngine: model loaded successfully');
                    return true;
                } catch (e) {
                    console.error('VoskEngine init failed:', e);
                    return false;
                }
            },

            async startListening(onResult, onError) {
                if (!this.isReady || this.isListeningActive) return;
                try {
                    this._stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this._audioContext = new AudioContext({ sampleRate: 16000 });

                    const grammar = JSON.stringify([
                        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                        'bee', 'see', 'dee', 'ef', 'gee', 'aitch', 'eye', 'jay', 'kay',
                        'el', 'em', 'en', 'oh', 'pee', 'cue', 'are', 'es', 'tee', 'you',
                        'vee', 'why', 'zed', 'double u', '[unk]'
                    ]);
                    this._recognizer = new this._model.KaldiRecognizer(16000, grammar);

                    this._recognizer.on('result', (message) => {
                        const text = message.result && message.result.text;
                        if (text && text !== '[unk]' && text.trim() !== '') {
                            onResult(text.trim().toUpperCase());
                        }
                    });

                    const source = this._audioContext.createMediaStreamSource(this._stream);
                    this._processor = this._audioContext.createScriptProcessor(4096, 1, 1);
                    this._processor.onaudioprocess = (e) => {
                        if (this._recognizer) {
                            this._recognizer.acceptWaveform(e.inputBuffer.getChannelData(0));
                        }
                    };
                    source.connect(this._processor);
                    this._processor.connect(this._audioContext.destination);

                    this.isListeningActive = true;
                } catch (e) {
                    console.error('VoskEngine startListening failed:', e);
                    if (onError) onError(e);
                }
            },

            stopListening() {
                this.isListeningActive = false;
                if (this._processor) { this._processor.disconnect(); this._processor = null; }
                if (this._audioContext) { this._audioContext.close(); this._audioContext = null; }
                if (this._stream) { this._stream.getTracks().forEach(t => t.stop()); this._stream = null; }
                if (this._recognizer) { this._recognizer.free(); this._recognizer = null; }
            }
        };

```

- [ ] **Step 3: Add vosk-browser CDN script tag in the `<head>` section**

Find the closing `</head>` tag (around line 20-30). Insert before it:

```html
    <!-- vosk-browser: WASM speech recognition engine -->
    <script src="https://cdn.jsdelivr.net/npm/vosk-browser@0.0.5/dist/vosk.js"></script>
```

- [ ] **Step 4: Verify VoskEngine object is syntactically valid**

Open browser console after saving. No JS parse errors should appear. Type `VoskEngine.isReady` — should return `false` (model not yet loaded).

---

### Task 3: Wire model loading in window.onload

**Files:**
- Modify: `english alphabet spelling/english-spelling.html` — update `window.onload`

- [ ] **Step 1: Make `window.onload` async and add VoskEngine.init() call**

Find:
```javascript
        window.onload = function() {
```

Replace with:
```javascript
        window.onload = async function() {
```

- [ ] **Step 2: Add model loading UI and init call at the top of window.onload**

Find this block at the start of window.onload (around line 1590):
```javascript
            // Restore saved theme
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.body.setAttribute('data-theme', savedTheme);

            loadStats();
            updateProgress();
            updateStatsDisplay();
            updateDebugInfo();
```

Replace with:
```javascript
            // Restore saved theme
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.body.setAttribute('data-theme', savedTheme);

            loadStats();
            updateProgress();
            updateStatsDisplay();
            updateDebugInfo();

            // Disable Start Round until engine is ready
            document.getElementById('startBtn').disabled = true;
            updateStatus('not-listening', '⏳ Loading speech engine… (first visit downloads ~40MB, cached after)');

            const voskLoaded = await VoskEngine.init();
            if (voskLoaded) {
                document.getElementById('startBtn').disabled = false;
                updateStatus('not-listening', '✅ Speech engine ready! Press "Start Round" to begin.');
            } else {
                // Fall back to Web Speech API
                console.warn('VoskEngine failed — falling back to Web Speech API');
                initializeSpeechRecognition();
            }
```

- [ ] **Step 3: Verify in browser**

Load `https://localhost:8443/english-spelling.html`. On first load:
- Status shows "⏳ Loading speech engine…"
- Start Round button disabled
- After model loads (may take 30-60s first visit): status shows "✅ Speech engine ready!"
- On second load: "✅ Speech engine ready!" appears almost instantly (IndexedDB cache)

---

### Task 4: Add VOSK-based startListeningSession and rename WSAPI version

**Files:**
- Modify: `english alphabet spelling/english-spelling.html`

- [ ] **Step 1: Rename existing startListeningSession to startListeningSessionWSAPI**

Find:
```javascript
        // Start a fresh recognition session (called each loop iteration)
        function startListeningSession() {
```

Replace with:
```javascript
        // Web Speech API fallback — used only when VoskEngine is not ready
        function startListeningSessionWSAPI() {
```

- [ ] **Step 2: Add new VOSK-based startListeningSession after the watchdog functions**

Find this comment (after `startWatchdog`):
```javascript
        // Public: start a round (mic stays on for all letters)
        function startListening() {
```

Insert immediately before it:

```javascript
        // VOSK-based session — mic stays open entire round, no restart between letters
        async function startListeningSession() {
            if (micState !== MIC_STATE.IDLE) return;
            setMicState(MIC_STATE.STARTING);

            await VoskEngine.startListening(
                function onResult(text) {
                    if (voskIgnoreResults) return; // During feedback delay — ignore
                    if (!roundActive) return;
                    setMicState(MIC_STATE.PROCESSING);
                    processVoiceInput(text);
                    if (roundActive) {
                        setMicState(MIC_STATE.LISTENING);
                    }
                },
                function onError(e) {
                    roundActive = false;
                    setMicState(MIC_STATE.ERROR);
                    if (e && (e.name === 'NotAllowedError' || e.name === 'PermissionDeniedError')) {
                        document.getElementById('permissionDenied').style.display = 'block';
                        updateStatus('error', '❌ Microphone access denied.');
                    } else {
                        updateStatus('error', `❌ Mic error: ${e ? e.message || e : 'unknown'}`);
                    }
                }
            );

            if (VoskEngine.isListeningActive) {
                setMicState(MIC_STATE.LISTENING);
            } else if (micState !== MIC_STATE.ERROR) {
                setMicState(MIC_STATE.ERROR);
                updateStatus('error', '❌ Failed to open microphone.');
            }
        }

```

---

### Task 5: Update stopListening and startListening to route by engine

**Files:**
- Modify: `english alphabet spelling/english-spelling.html`

- [ ] **Step 1: Replace stopListening with dual-path version**

Find:
```javascript
        // Public: end the round
        function stopListening() {
            roundActive = false;
            setMicState(MIC_STATE.STOPPING);
            clearWatchdog();
            if (recognition) {
                try { recognition.stop(); } catch(e) {}
            }
            updateStatus('not-listening', '🛑 Round ended. Press "Start Round" to begin again.');
        }
```

Replace with:
```javascript
        // Public: end the round (works for both VOSK and WSAPI paths)
        function stopListening() {
            roundActive = false;
            setMicState(MIC_STATE.STOPPING);
            clearWatchdog();
            if (VoskEngine.isListeningActive) {
                VoskEngine.stopListening();
                // VOSK stop is synchronous — go straight to cooldown
                setMicState(MIC_STATE.COOLDOWN);
                setTimeout(() => setMicState(MIC_STATE.IDLE), 400);
            } else if (recognition) {
                try { recognition.stop(); } catch(e) {}
                // WSAPI stop is async — onend fires and handles COOLDOWN → IDLE
            }
            updateStatus('not-listening', '🛑 Round ended. Press "Start Round" to begin again.');
        }
```

- [ ] **Step 2: Replace startListening with routing version**

Find:
```javascript
        // Public: start a round (mic stays on for all letters)
        function startListening() {
            if (!microphonePermissionGranted) {
                requestMicrophonePermission();
                return;
            }
            if (micState !== MIC_STATE.IDLE) return; // Busy — ignore spam clicks
            roundActive = true;
            startListeningSession();
        }
```

Replace with:
```javascript
        // Public: start a round — routes to VOSK or WSAPI fallback
        function startListening() {
            if (micState !== MIC_STATE.IDLE) return; // Busy — ignore spam clicks
            roundActive = true;
            if (VoskEngine.isReady) {
                startListeningSession(); // VOSK path — handles mic permission internally
            } else {
                // WSAPI fallback path
                if (!microphonePermissionGranted) {
                    requestMicrophonePermission();
                    return;
                }
                startListeningSessionWSAPI();
            }
        }
```

---

### Task 6: Add voskIgnoreResults guard to checkLetterPronunciation

**Files:**
- Modify: `english alphabet spelling/english-spelling.html`

With VOSK's continuous recognition, audio keeps flowing during the 1500ms success animation and the 800ms wrong-answer feedback. Without a guard, the user might inadvertently trigger another result during that window.

- [ ] **Step 1: Update checkLetterPronunciation to set voskIgnoreResults**

Find:
```javascript
            if (isCorrect) {
                stats.correctPronunciations++;
                stats.currentStreak++;
                attemptCount = 0;
                hideSkipSuggestion();
                updateStatus('success', `✅ Perfect! "${spokenLetter}" is correct.`);
                setTimeout(() => { nextLetter(); }, 1500);
            } else {
                stats.currentStreak = 0;
                attemptCount++;
                updateStatus('error', `❌ Heard "${spokenLetter}" — expected "${expectedLetter}". Try again!`);
                if (attemptCount >= 3) {
                    setTimeout(() => showSkipSuggestion(), 800);
                }
            }
```

Replace with:
```javascript
            if (isCorrect) {
                stats.correctPronunciations++;
                stats.currentStreak++;
                attemptCount = 0;
                hideSkipSuggestion();
                updateStatus('success', `✅ Perfect! "${spokenLetter}" is correct.`);
                voskIgnoreResults = true;
                setTimeout(() => { voskIgnoreResults = false; nextLetter(); }, 1500);
            } else {
                stats.currentStreak = 0;
                attemptCount++;
                updateStatus('error', `❌ Heard "${spokenLetter}" — expected "${expectedLetter}". Try again!`);
                voskIgnoreResults = true;
                setTimeout(() => { voskIgnoreResults = false; }, 800);
                if (attemptCount >= 3) {
                    setTimeout(() => showSkipSuggestion(), 800);
                }
            }
```

---

### Task 7: Manual end-to-end verification and commit

- [ ] **Step 1: Start HTTPS dev server**

```bash
cd "C:/Users/legon/Documents/Taktis/Client/Edukultur/demo/english alphabet spelling"
python https_server.py
```

- [ ] **Step 2: Verify model loading (first visit)**

Open `https://localhost:8443/english-spelling.html` in Chrome.
Expected:
- Status: "⏳ Loading speech engine… (first visit downloads ~40MB, cached after)"
- Start Round disabled
- Browser console: no JS errors, vosk-browser worker logs visible
- After load completes: "✅ Speech engine ready!"

- [ ] **Step 3: Verify model caching (second visit)**

Reload the page.
Expected:
- "✅ Speech engine ready!" appears within 1-2 seconds (IndexedDB cache)
- No 40MB download in Network tab

- [ ] **Step 4: Verify round-based recognition**

Click Start Round. Say "B" clearly.
Expected:
- Button switches to "⏹️ End Round"
- Status shows "🎤 Listening… Say: [current letter]"
- Browser console logs "Heard: B" (or "BEE")
- Letter processed correctly
- Mic stays open — status shows next letter without pressing Start again

- [ ] **Step 5: Verify End Round**

Click End Round during active listening.
Expected:
- Status: "🛑 Round ended. Press 'Start Round' to begin again."
- Start Round button reappears
- Mic stream stopped (no mic indicator in browser tab)

- [ ] **Step 6: Verify WSAPI fallback (optional — simulate by blocking CDN)**

In DevTools → Network → block `cdn.jsdelivr.net`. Reload page.
Expected:
- VoskEngine.init() fails silently
- App falls through to Web Speech API path
- "✅ Ready! Press 'Start Round' to begin." message (WSAPI ready)
- Mic works via Chrome STT as before

- [ ] **Step 7: Commit**

```bash
cd "C:/Users/legon/Documents/Taktis/Client/Edukultur/demo"
git add "english alphabet spelling/english-spelling.html"
git commit -m "feat: integrate vosk-browser WASM for offline A-Z letter recognition

- VoskEngine wrapper: init/startListening/stopListening
- Letter-only grammar constraint (A-Z + phonetic aliases)
- Round-based: mic stays open entire round, no restart between letters
- voskIgnoreResults flag prevents double-detection during feedback delays
- Web Speech API kept as silent fallback if VOSK fails to load"
```

- [ ] **Step 8: Push to GitHub**

```bash
git push origin main
```

> Note: first push after committing the 40MB model will be slow.

---

## Self-Review

**Spec coverage check:**
- ✅ VoskEngine with init/startListening/stopListening/isReady/isListeningActive — Task 2
- ✅ Model at `models/vosk-model-small-en-us-0.15.tar.gz` — Task 1
- ✅ Loading UX (disabled button + status message) — Task 3
- ✅ IndexedDB caching — handled automatically by vosk-browser, verified in Task 7 Step 3
- ✅ Grammar constraint A-Z + phonetic aliases — Task 2 Step 2
- ✅ Audio pipeline (ScriptProcessorNode → acceptWaveform) — Task 2 Step 2
- ✅ State machine integration (STARTING→LISTENING→PROCESSING→LISTENING) — Task 4
- ✅ stopListening dual-path — Task 5 Step 1
- ✅ startListening routing — Task 5 Step 2
- ✅ WSAPI fallback — Task 5 Step 2 + Task 3 Step 2
- ✅ voskIgnoreResults guard — Task 6
- ✅ Manual test coverage — Task 7

**Placeholder scan:** None found.

**Type consistency:**
- `VoskEngine.startListening(onResult, onError)` defined Task 2 Step 2, called Task 4 Step 2 ✅
- `VoskEngine.stopListening()` defined Task 2 Step 2, called Task 5 Step 1 ✅
- `VoskEngine.isReady` defined Task 2 Step 2, checked Task 5 Step 2 ✅
- `VoskEngine.isListeningActive` defined Task 2 Step 2, checked Task 5 Step 1 ✅
- `voskIgnoreResults` declared Task 2 Step 1, set Task 6 Step 1, checked Task 4 Step 2 ✅
- `startListeningSessionWSAPI` renamed Task 4 Step 1, called Task 5 Step 2 ✅
