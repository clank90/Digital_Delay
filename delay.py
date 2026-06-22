import numpy as np
import scipy.io.wavfile as wavfile

# 1. Audio Parameters
SAMPLE_RATE = 44100
DURATION = 2.0

# 2. Generate a quick "beep" signal
n_idx = np.arange(int(SAMPLE_RATE * DURATION))
x = np.sin(2 * np.pi * 440.0 * (n_idx / SAMPLE_RATE))
envelope = np.exp(-n_idx / 44100)  # Fast decay for a percussive sound
beep = x * envelope


# 4. Save to WAV
def save_wav(filename, signal, fs=SAMPLE_RATE):
    signal_normalized = np.int16(signal * 32767)
    wavfile.write(filename, fs, signal_normalized)
    print(f"Saved {filename}")


def apply_delay(x, delay_ms, fs=SAMPLE_RATE, gain=0.6):

    # 1. Calculate M (delay in samples)
    delay_seconds = delay_ms / 1000.00
    M = int(delay_seconds * fs)

    # 2. Initialize the Output Array
    # We make the output exactly the same length as the input
    total_samples = len(x)
    y = np.zeros(total_samples)

    # 3. Initialize the Circular Buffer (The "State")
    # This array represents our fixed block of memory.
    circular_buffer = np.zeros(M)
    write_index = 0

    # 4. The Real-Time Audio Loop
    # We process the audio sample by sample, exactly as a C++ plugin would.
    for n in range(total_samples):
        # Step A: Read the delayed sample from the buffer
        # The value currently at write_index is the oldest sample in the buffer.
        delayed_samples = circular_buffer[write_index]

        # Step B: Calculate the output
        # y[n] = x[n] + g * x[n - M]
        y[n] = x[n] + (gain * delayed_samples)

        # Step C: Write the CURRENT input into the buffer
        # We overwrite the old sample with the new one.
        circular_buffer[write_index] = x[n]

        # Step D: Advance the index
        write_index += 1

        # Step E: The Wrap Around (Modulo arithmetic)
        # If the index goes out of bounds, snap it back to 0.
        if write_index >= M:
            write_index = 0
    # 5. Prevent clipping
    max_val = np.max(np.abs(y))
    if max_val > 1.0:
        y = y / max_val

    return y


# 3. Apply the Circular Delay
print("Processing circular delay (this may take a few seconds in Python)...")
y_circular_delay = apply_delay(beep, delay_ms=400)

save_wav("5_circular_delayed_beep.wav", y_circular_delay)
