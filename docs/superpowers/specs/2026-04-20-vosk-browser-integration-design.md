# Design: vosk-browser A-Z Recognition Integration

**Date:** 2026-04-20  
**Project:** Edukultur AI Demos — English Alphabet Spelling  
**Status:** Approved

---

## Problem

Web Speech API (Chrome) is unreliable for single-letter recognition:
- Designed for sentences, not individual letters
- Rapid open/close causes dirty audio pipeline on Chrome Android (~30-40% failure rate)
- No grammar control — guesses words not letters

## Solution

Replace Web Speech API with **vosk-browser** (WASM port of VOSK) using a letter-only grammar constraint.

---

## Architecture

```
Page load
  → fetch vosk.js from jsDelivr CDN (5.7MB)
  → Vosk.createModel('./models/vosk-model-small-en-us-0.15.tar.gz')
      → 40MB download on first visit, cached in IndexedDB forever after
  → KaldiRecognizer created with A-Z grammar

Round start (user presses "Start Round")
  → getUserMedia({ audio: true })
  → AudioContext at 16kHz
  → ScriptProcessorNode captures Float32Array chunks
  → chunks fed to recognizer.acceptWaveform()
  → result event fires → processVoiceInput(text)

Round end (user presses "End Round" or all letters complete)
  → audioContext.close()
  → stream.getTracks().forEach(t => t.stop())
```

### Layers

1. **VoskEngine** — thin wrapper object inside english-spelling.html
   - `init(onProgress)` — load model, report progress
   - `startListening(onResult, onError)` — open mic + AudioContext, start feeding recognizer
   - `stopListening()` — close AudioContext + mic stream
   - `isReady` — boolean, false until model loaded
   - `isListeningActive` — boolean, true while round running

2. **State machine** — unchanged (idle → starting → listening → processing → stopping → cooldown → error)

3. **processVoiceInput()** — unchanged, handles letter matching via existing phoneticMap

---

## Model

- File: `vosk-model-small-en-us-0.15.tar.gz` (~40MB)
- Location: `english alphabet spelling/models/`
- Committed directly to repo, served by GitHub Pages
- Loaded at page load; IndexedDB cache skips download on repeat visits
- If load fails: silent fallback to Web Speech API

---

## Grammar

KaldiRecognizer initialized with constrained grammar — A-Z letters + phonetic aliases only:

```json
[
  "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
  "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
  "bee", "see", "dee", "ef", "gee", "aitch", "eye", "jay", "kay",
  "el", "em", "en", "oh", "pee", "cue", "are", "es", "tee", "you",
  "vee", "why", "zed", "double u", "[unk]"
]
```

Existing `phoneticMap` already maps these aliases to letters — zero changes to letter matching logic.

---

## Audio Pipeline Detail

```javascript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const audioContext = new AudioContext({ sampleRate: 16000 });
const source = audioContext.createMediaStreamSource(stream);
const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
    const float32 = e.inputBuffer.getChannelData(0);
    recognizer.acceptWaveform(float32);
};

source.connect(processor);
processor.connect(audioContext.destination);

recognizer.on('result', ({ result }) => {
    if (result.text && result.text !== '[unk]') {
        onResult(result.text.toUpperCase());
    }
});
```

---

## State Machine Integration

| State | VoskEngine action |
|---|---|
| `STARTING` | `VoskEngine.startListening()` — open mic + AudioContext |
| `LISTENING` | recognizer running, audio flowing |
| `PROCESSING` | `processVoiceInput()` called with result text |
| back to `LISTENING` | resume audio feed (mic stays open — no restart) |
| `STOPPING` | `VoskEngine.stopListening()` — close AudioContext + stream |
| `COOLDOWN` | 400ms → IDLE |

**Key improvement:** mic stays open entire round. No open/close between letters. No dirty pipeline.

---

## Loading UX

- On page load: status shows "⏳ Loading speech engine… X%" with progress bar
- "Start Round" button disabled until model ready
- On cached load (IndexedDB hit): status shows "✅ Ready!" almost instantly
- On model load failure: status shows Web Speech API fallback message

---

## Files Changed

| File | Change |
|---|---|
| `english alphabet spelling/english-spelling.html` | Add VoskEngine object, swap `startListeningSession`/`stopListening` internals, add model loading UI/progress |
| `english alphabet spelling/models/vosk-model-small-en-us-0.15.tar.gz` | New — 40MB model file downloaded and committed |

No other files changed. Hanzi demo untouched.

---

## Fallback

If vosk-browser script or model fails to load:
- `VoskEngine.isReady` remains false
- App silently initializes Web Speech API instead
- User sees same "Start Round" button, same UX
- No error shown unless both fail
