# 01 · Digital audio: what the computer actually "hears"

## 1. The problem
You hear a song as a guitar, a voice and drums. The computer gets a long list of numbers. Every later stage has to turn those numbers back into musical things: pitches, notes, beats. To understand how that can work (and why it sometimes fails), you need to know what the numbers are.

## 2. Core concepts

### Sound is air pressure over time
A vibrating string pushes the air back and forth. A microphone turns that pressure into a voltage, and a converter **measures the voltage many times per second**. Each measurement is a **sample**: a number between -1 (full push one way) and +1 (full push the other way).

```
pressure
  +1 |      .-.           .-.
     |    .'   '.       .'   '.
   0 |---'-------'-----'-------'-----  time →
     |            '.-.'
  -1 |
         ↑ ↑ ↑ ↑ ↑ samples: one measurement every 1/44100 s
```

- **Sample rate**: how many samples per second. CDs and most MP3s use **44,100 Hz**. TabMaker's guitar isolation (Demucs) works at 44.1 kHz; note detection (basic-pitch) converts to 22,050 Hz internally.
- **Channels**: stereo files have two lists, left and right. Mixing engineers often pan guitars left or right, which TabMaker uses from M3.
- **Bit depth**: how precisely each sample is stored (16-bit = 65,536 levels). Not important for us.

A 4-minute stereo song is 4 × 60 × 44,100 × 2 ≈ **21 million numbers**.

### Frequency is pitch
A string vibrating back and forth 110 times per second produces a 110 Hz wave. You hear that as the note **A2**: the open A string.

| Open string (standard tuning) | Note | Frequency |
|---|---|---|
| 6th (low E) | E2 | 82.41 Hz |
| 5th | A2 | 110.00 Hz |
| 4th | D3 | 146.83 Hz |
| 3rd | G3 | 196.00 Hz |
| 2nd | B3 | 246.94 Hz |
| 1st (high e) | E4 | 329.63 Hz |

**Each fret multiplies the frequency by 2^(1/12) ≈ 1.0595** (about +6%). Twelve frets multiply it by exactly 2, which is why the 12th fret is the octave. This is *equal temperament*, the system frets are built for.

### MIDI note numbers: pitch as a simple count
Instead of Hz, software counts semitones: **MIDI note numbers**. A4 (440 Hz) is 69, middle C (C4) is 60, the open low E (E2) is 40. One fret = +1.

```
frequency = 440 × 2^((midi − 69) / 12)
E2 = 40 → 440 × 2^(−29/12) = 82.41 Hz
```

This is why TabMaker's fretboard math is easy: the open A string is 45, so its 7th fret is 45 + 7 = 52 = E3, the same pitch as the D string's 2nd fret (50 + 2). One pitch can be played in several places, which is the whole topic of [05 Fingering](README.md).

### Harmonics: why one note is many frequencies
A plucked string doesn't vibrate at one frequency. It vibrates at the **fundamental** f *and* at 2f, 3f, 4f… all at once (the **harmonics** or overtones). Their mix is the instrument's tone (timbre): the reason a guitar and a flute playing A2 sound different.

```
A2 played on guitar:
 110 Hz  ████████████  fundamental (the note you name)
 220 Hz  ████████      2nd harmonic (= A3, one octave up)
 330 Hz  ██████        3rd harmonic (≈ E4, an octave + a fifth)
 440 Hz  ████          4th harmonic (= A4, two octaves)
   …
```

This is the main headache for note detection: the 2nd harmonic *is* the octave above, so a detector can easily report A3 (or E4) when you played A2. Distortion makes it worse by adding even more harmonics. The `21` and `22` frets you'll see in early M1 sheets are exactly that: harmonics reported as notes. M3 filters them.

### Spectrograms: seeing frequencies over time
Waveforms are hard to read. A **spectrogram** shows which frequencies are present at each moment:
1. cut the audio into short overlapping windows (e.g. 2048 samples ≈ 46 ms);
2. for each window, measure how strong every frequency is (a **Fourier transform**, FFT);
3. stack the results side by side: time →, frequency ↑, brightness = strength.

This is the **STFT** (short-time Fourier transform). A held note shows up as a horizontal line plus fainter lines at its harmonics. A drum hit shows up as a vertical smear across all frequencies.

**The trade-off you can't escape:** a longer window gives finer frequency detail but blurrier timing. With a 46 ms window at 44.1 kHz, frequency bins are 21.5 Hz apart. Low E (82.4 Hz) and F (87.3 Hz) differ by only 5 Hz, so they land in the same bin. That's why music tools often use a **constant-Q transform (CQT)**: bins spaced like frets (a fixed number per octave), so low notes get finer frequency resolution. basic-pitch uses a harmonic version of this (see 03).

## 3. How TabMaker does it
- `tabmaker/audio.py` reads the file with **libsndfile** (via `soundfile`) into an array of shape (channels, samples) with values between -1 and 1. WAV, FLAC, OGG and MP3 are read directly; other formats (M4A…) go through ffmpeg.
- `--start/--end` cut the array before anything else runs, so a 30-second excerpt is processed 8 times faster than a 4-minute song.
- The excerpt is saved as `work/<song>/mix.wav`, so later stages (and you) can listen to exactly what was processed.
- Pitches are handled as MIDI numbers everywhere (`tabmaker/fretboard.py`), and the tuning is the list of open-string numbers: standard = 40 45 50 55 59 64.

## 4. Failure modes
| Symptom | Cause |
|---|---|
| Every note is off by one fret | The recording isn't at standard pitch (tuned down a half step, or a tape-speed change). Tunings arrive in M5. |
| Notes jump an octave | Harmonics: the detector picked the 2nd harmonic instead of the fundamental. |
| Many short wrong notes | A low-bitrate MP3 (≤128 kbps) adds "swirly" artifacts and removes high frequencies. Use the best file you have. |
| Distorted sound | Clipping: the recording was pushed past ±1 and the tops of the waves are cut flat, which adds fake harmonics. |

## 5. Try it yourself
Print the frequency of every fret of the low E string:
```bash
uv run python -c "from tabmaker.synth import midi_to_hz; print([round(midi_to_hz(40 + f), 1) for f in range(13)])"
```
Check that the 12th fret is double the open string (82.4 → 164.8).

Hear what a synthetic plucked string sounds like (TabMaker uses it for its self-test):
```bash
uv run tabmaker dev selftest --keep selftest_out
```
Then open `selftest_out/selftest_guitar.wav` (the clean riff) and `selftest_out/selftest_mix.wav` (riff + drums) in any audio player. To see spectrograms, open the files in [Audacity](https://www.audacityteam.org/) and choose *Spectrogram* from the track menu: held notes show as horizontal lines stacked at their harmonics.

## 6. Further reading
- Meinard Müller, *Fundamentals of Music Processing* (Springer, 2nd ed. 2021), chapters 1–2: the standard textbook, very readable.
- Steven W. Smith, *The Scientist and Engineer's Guide to Digital Signal Processing*, free at dspguide.com: sampling and the Fourier transform without heavy math.
- Wikipedia: "Equal temperament", "Harmonic series (music)", "Constant-Q transform".
