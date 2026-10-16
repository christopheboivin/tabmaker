# 02 · Source separation: getting the guitar out of the mix

## 1. The problem
In a recording, all instruments end up in **one** waveform (two, in stereo). At every sample, the guitar's value, the bass's, the drums' and the voice's have simply been **added together**:

```
mix[t] = guitar[t] + bass[t] + drums[t] + vocals[t] + …
```

Going back is mathematically impossible on its own: for any mix there are infinitely many ways to split it into parts that add up. 5 = 2 + 3, but also 1 + 4. A separator works only because it **knows what instruments usually sound like**, and it learned that from examples. It makes an educated guess, so the result is always an approximation.

Why bother? Note detection on a full mix would pick up the bass, the vocal melody and the keyboard as "guitar notes". Isolating the guitar first removes most of that.

## 2. Core concepts

### Separation on a spectrogram: masks
On a spectrogram (see [01](01-digital-audio.md)), instruments overlap less than in the waveform: at a given moment, the bass owns the low frequencies, cymbals the very high ones, and the guitar sits in the middle. The classic approach:
1. compute the mix's spectrogram;
2. for every time × frequency cell, estimate **what fraction belongs to the guitar** (a number from 0 to 1): the **mask**;
3. multiply the mix by the mask and convert back to audio.

```
mix spectrogram      ×      guitar mask       =   guitar estimate
 ░▓█▓░░▓█▓░               0 1 1 1 0 ...          ░▓█▓░ ...
```

When two instruments use the same cell (a guitar and a keyboard playing the same note), the mask has to split it, and some of the keyboard **bleeds** into the guitar stem.

### Learning the mask: neural networks
Nobody writes mask rules by hand. A **neural network** is trained on thousands of songs for which the separate tracks (*stems*) exist:
1. give it the mix;
2. it outputs its guess for each stem;
3. compare the guess with the real stem, and nudge the network's millions of internal numbers (*weights*) to reduce the error;
4. repeat millions of times.

This is **supervised learning**. The network ends up recognizing what a snare hit, a sung vowel or a distorted guitar look like. It can only separate what it saw in training, which is why unusual instruments end up in "other".

### Demucs: waveform + spectrogram together
TabMaker uses **Demucs v4 ("Hybrid Transformer Demucs")** from Meta AI. Instead of choosing between the spectrogram (good for sustained, pitched sounds) and the raw waveform (good for sharp attacks and phase), it runs **two branches at once**, one on each representation. A *transformer* in the middle lets the two branches share what they found, and the outputs are added up. The variant `htdemucs_6s` outputs **six stems**: drums, bass, other, vocals, **guitar**, piano. The Demucs authors note that the extra stems (guitar and especially piano) are less reliable than the four classic ones, because far fewer training songs have separate guitar and piano tracks.

Two practical details:
- **Normalization**: the network was trained on audio scaled to a standard loudness, so the mix is scaled in before separation and the stems scaled back after.
- **Chunks**: a whole song doesn't fit in memory at once, so Demucs processes overlapping chunks of a few seconds and cross-fades them (TabMaker uses 25% overlap).

## 3. How TabMaker does it (`tabmaker/separate.py`)
1. Load the audio (trimmed to `--start/--end`), convert to 44.1 kHz stereo if needed.
2. Normalize, run `htdemucs_6s` in chunks, scale back.
3. Save the six stems in `work/<song>/stems/`: `guitar.wav` feeds the next stage, and the others are kept so you can listen to what went where.
4. Write a **cache key** (a fingerprint of the audio file + the time range + the model name). On the next run with the same input, the stems are reused and separation is skipped. On a CPU, separation is the slow stage, roughly as long as the audio itself.

## 4. Failure modes
| What you hear in `guitar.wav` | Why | What helps |
|---|---|---|
| Keyboards, organ or synth pads | They share the guitar's frequency range; the mask can't tell them apart | Check `piano.wav` and `other.wav`; M3's confidence filter drops weak notes |
| Two guitars at once (rhythm + lead) | There is only one guitar stem | `--guitar left/right/center` in M3: they're often panned apart |
| The guitar is quiet or missing, but it's in `other.wav` | Clean or acoustic guitar, or an unusual effect, looked "unknown" to the model. The decision is made moment by moment, so the guitar can vanish for a few seconds only (in *Come As You Are*, the chorus-effect guitar went to `other.wav` from 0:18 to 0:30) | Try another section; future model comparisons (M8); idea L.5 |
| "Underwater", phasey or swirly sound | Mask errors: cells half-assigned to the wrong stem | Normal artifact; note detection usually survives it |
| Bits of vocal melody | Voice and lead guitar overlap in range and phrasing | Shows up as stray notes; cleanup in M3 |
| Bass notes | Low guitar notes and bass overlap, worst when the bass doubles the guitar riff | The "notes below low E" warning often points to this, but check the tuning first: a tuned-down guitar (e.g. D standard) really does play below E2 |

## 5. Try it yourself
Process a 30-second excerpt of a song you know (fast, and cached for next time):
```bash
uv run tabmaker "path/to/song.mp3" --start 0:30 --end 1:00
```
Then listen to the files in `work/<song>/stems/`:
- `guitar.wav`: is it only guitar? What leaked in?
- `other.wav` and `piano.wav`: is some guitar hiding there?
- `mix.wav`: the exact excerpt that was processed.

Run it again: the "reusing the stems" message shows the cache at work.

## 6. Further reading
- Simon Rouard, Francisco Massa, Alexandre Défossez, "Hybrid Transformers for Music Source Separation" (ICASSP 2023): the Demucs v4 paper.
- Alexandre Défossez, "Hybrid Spectrogram and Waveform Source Separation" (2021): the hybrid idea (Demucs v3).
- The Demucs code and model list: github.com/facebookresearch/demucs.
- The SigSep tutorial "Open-Source Tools & Data for Music Source Separation" (sigsep.github.io/tutorials): masks, datasets (MUSDB18) and evaluation explained step by step.
