# L'effet Pompeux v2.0 — Technical Documentation

## 1. Project Description
"L'effet Pompeux" is a web-based audio mastering application designed to recreate the aggressive sidechain compression effect ("pumping") famously used in electronic music (EDM, French Touch, House). Originally built for local network (LAN) use, it is now fully adapted for Cloud deployment (e.g., Render.com) with multi-user isolation.

## 2. Technical Features
- **Framework:** Gradio (Python)
- **DSP Engine:** 100% Vectorized processing via pure NumPy and SciPy for minimal latency and maximum cloud compatibility (No AVX instructions required).
- **Output Standard:** Forced export to WAV 48 kHz / 24-bit.
- **Precision:** Internal 32-bit float calculations to preserve dynamic range.
- **Cloud-Ready:** Dynamic port binding (`PORT` env variable, defaults to `7861`), secure file management with UUIDs, and safe cache clearing.

## 3. Installation & Launch

### Prerequisites
- Python 3.9 or higher
- pip
- Linux (for Cloud deployment): `libsndfile1` and `ffmpeg` (see `build.sh`)

### Cloud Deployment (e.g., Render.com)
Use the included `build.sh` script to install system dependencies before installing Python requirements:
```bash
bash build.sh
python leffet_pompeux.py
```

### Local Deployment (Windows)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the application
python leffet_pompeux.py

# Note: You can also use `start.bat` for an easy launch, or `effetpompeuxstart_hidden.vbs` to run it silently in the background on startup.
```

## 4. Signal Flow (Architecture)

The tool follows a strict 11-step processing chain:

```
[Audio File]
      │
      ▼
  1. Load & Resample → 48 kHz / float32
      │
      ├──[Sidechain Source]──────────────────────────────────────────────┐
      │  (External file OR main audio if no SC provided)                 │
      │                                                           3. LP Filter
      │                                                           4. × Bass Gain
      │                                                           5. Envelope Follower
      │◄─────────────────────────────────────────────────────────────────┘
      │
      ▼
  6. Ducking (Linked stereo gain reduction, depth = Compression Amount)
      │
      ▼
  7. Sidechain Re-injection (Adds SC signal back into the mix if desired)
      │
      ▼
  8. Wet/Dry Mix with the original un-ducked signal
      │
      ▼
  9. Auto-Leveling (Normalization if peak > 0 dBFS before mastering)
      │
      ▼
 10. Glue Compressor (NumPy Mathematical Soft Clipper/Saturator — optional)
      │
      ▼
 11. Brickwall Limiter at -0.1 dBFS (NumPy — optional)
      │
      ▼
[WAV 48 kHz / 24-bit]
```

## 5. Interface Parameters

| Parameter | Range | Default (French Touch) | Description |
|---|---|---|---|
| Low-Pass Cutoff | 20–500 Hz | 90 Hz | Cutoff frequency for the sidechain trigger filter |
| Bass Gain | 0.5×–4.0× | 2.5× | Amplification of the trigger signal |
| Compression Amount | 0–100 % | 90 % | Depth of the ducking effect |
| Attack | 0.1–50 ms | 1.5 ms | Speed of gain reduction onset |
| Release | 10–500 ms | 130 ms | Gain recovery speed (Tip: use the Tap Tempo tool) |
| Wet/Dry Mix | 0–100 % | 100 % | Parallel processing mix |
| Sidechain Volume | 0–150 % | 100 % | Volume of the external kick re-injected into the final mix |
| Preview Start | 0–(duration-15) s | 0 | Starting point for the 15-second fast preview |

## 6. Advanced Features

### Tap Tempo & Release Calculator
The UI includes a "🎵 Tap Tempo" button. Tapping it to the rhythm of your track calculates the exact BPM and the millisecond value of a 1/16th note in real-time (using client-side Javascript for zero latency). The "⬇️ Paste to Release" button instantly applies this value to the Release slider for perfectly timed pumping grooves.

### Multi-User Safety (Cloud)
Temporary audio files are saved in the `fichiers_audio/` folder using cryptographically secure UUIDs. The "Clear Cache" button has been smart-coded to only delete files older than 1 hour, ensuring that active users do not interrupt each other's processing sessions.

## 7. Technical Notes
- The envelope follower uses independent exponential coefficients (attack/release) for organic behavior.
- The trigger signal is always mixed to mono before filtering and envelope following.
- Auto-leveling (Step 9) guarantees headroom before the master chain.
- Float64 precision is maintained during envelope calculation, then converted back to float32.
