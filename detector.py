import librosa
import numpy as np

def analyze_voice(audio_path: str):
    # Load audio
    y, sr = librosa.load(audio_path, sr=16000)

    # Feature extraction
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    zero_crossing = librosa.feature.zero_crossing_rate(y)
    pitch = librosa.yin(y, fmin=50, fmax=300)

    # Aggregate statistics
    mfcc_mean = np.mean(mfcc)
    pitch_std = np.std(pitch)
    zcr_mean = np.mean(zero_crossing)
    spec_centroid_mean = np.mean(spectral_centroid)

    # Decision logic based on acoustic behavior
    ai_score = 0

    if pitch_std < 18:
        ai_score += 0.3
    if mfcc_mean < -120:
        ai_score += 0.3
    if zcr_mean < 0.04:
        ai_score += 0.2
    if spec_centroid_mean < 1800:
        ai_score += 0.2

    confidence = round(min(0.99, max(0.60, ai_score + 0.5)), 2)

    if ai_score >= 0.6:
        return "AI_GENERATED", confidence
    else:
        return "HUMAN", confidence
