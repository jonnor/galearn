import numpy as np
import soundfile as sf

def generate_test_tone(
    duration_sec=5,
    sample_rate=44100,
    freqs=[440, 1000, 3000],
    noise_level=0.05,
    amplitude=0.5,
):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    signal = np.zeros_like(t)

    # Add multiple sine waves
    for freq in freqs:
        signal += amplitude * np.sin(2 * np.pi * freq * t)

    # Normalize to avoid clipping if multiple frequencies are added
    signal /= len(freqs)

    # Add white noise
    noise = noise_level * np.random.normal(0, 1, signal.shape)
    signal += noise

    return signal

if __name__ == "__main__":

    filename="test_tone.wav"
    # Save to WAV file
    
    sample_rate = 16000

    signal = generate_test_tone(sample_rate=sample_rate, freqs=[1000.0, 440.0], noise_level=0.01)

    sf.write(filename, signal, sample_rate)
    print(f"Saved test tone to '{filename}'.")
