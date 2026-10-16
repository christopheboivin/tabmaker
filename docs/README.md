# How TabMaker works: the tutorials

These docs explain the **ideas** behind each stage (sound, signal processing, machine learning, guitar) for a guitarist with no DSP or ML background. They're not Python docs; for the code, see [DEV-GUIDE.md](DEV-GUIDE.md).

```
song.mp3 ─→ [02] separate ─→ guitar stem ─┬─→ [03] transcribe notes ─┐
    └────→ full mix ─→ [04] beats & bars ─┤                          ├─→ tab or chords?
                                          └─→ chroma per beat ───────┘
  tab bars   ─→ [05] fingering            ─┐
  chord bars ─→ [06] chords + voicings    ─┴─→ [07] text sheet  ([08] Guitar Pro later)
  [09] measuring quality · [10] making it better
```

## Reading order
| # | Tutorial | Status |
|---|---|---|
| 01 | [Digital audio](01-digital-audio.md): samples, pitch, MIDI numbers, spectrograms | ✅ written (M1) |
| 02 | [Source separation](02-source-separation.md): getting the guitar out of the mix | ✅ written (M1) |
| 03 | Transcription: from sound to notes | arrives in M3 |
| 04 | Rhythm: beats, bars, quantization, strums | arrives in M4 |
| 05 | Fingering: choosing strings and frets with Viterbi | arrives in M5 |
| 06 | Chords: chroma, templates, voicings | arrives in M6 |
| 07 | Tab notation in plain text | arrives in M5 |
| 08 | The Guitar Pro format | arrives in M9 |
| 09 | Evaluation: measuring how good a tab is | arrives in M2 |
| 10 | Improving: tuning, learning from your fixes | arrives in M7–M8 |

Start with 01: everything else builds on it.

## The format of each tutorial
1. **The problem**: what this stage solves and why it's hard.
2. **Core concepts**: the theory, with diagrams and worked examples.
3. **How TabMaker does it**: what the tool actually runs.
4. **Failure modes**: what goes wrong, and what it looks or sounds like.
5. **Try it yourself**: commands to see or hear this stage's output.
6. **Further reading**.
