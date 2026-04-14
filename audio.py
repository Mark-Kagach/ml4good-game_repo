"""
audio.py - Procedural chiptune + SFX for Alignment Adventure.

All sounds are synthesized at import/build time using numpy + pygame.mixer.
No external assets. 8-bit NES-ish flavor: square leads, triangle bass,
noise-based drums. Music loops via pygame.mixer.Channel(0).play(sound, -1).
"""

from __future__ import annotations

import math

import numpy as np
import pygame


SAMPLE_RATE = 22050


# ---------------------------------------------------------------------------
# Low-level synth helpers
# ---------------------------------------------------------------------------
_SEMITONES = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def note_freq(name):
    """Convert a note name like 'C4', 'F#5', 'Bb3' to Hz. 'R' = rest."""
    if name == "R":
        return 0.0
    i = 0
    while i < len(name) and not name[i].isdigit() and name[i] != "-":
        i += 1
    note_part = name[:i]
    octave = int(name[i:])
    semitone = _SEMITONES[note_part] + (octave - 4) * 12 - 9  # A4 = 0
    return 440.0 * (2 ** (semitone / 12.0))


def gen_tone(freq, duration_s, wave="square", volume=0.2,
             attack=0.006, release=0.04):
    """Generate a mono float32 waveform for a single note."""
    n = int(duration_s * SAMPLE_RATE)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    if freq <= 0:
        return np.zeros(n, dtype=np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    phase = (freq * t) % 1.0
    if wave == "square":
        s = np.where(phase < 0.5, 1.0, -1.0)
    elif wave == "pulse12":
        s = np.where(phase < 0.125, 1.0, -1.0)
    elif wave == "pulse25":
        s = np.where(phase < 0.25, 1.0, -1.0)
    elif wave == "triangle":
        s = 4.0 * np.abs(phase - 0.5) - 1.0
    elif wave == "saw":
        s = 2.0 * phase - 1.0
    else:  # sine
        s = np.sin(2 * np.pi * freq * t)

    env = np.ones(n, dtype=np.float32)
    attack_n = min(int(attack * SAMPLE_RATE), n // 4)
    release_n = min(int(release * SAMPLE_RATE), n // 2)
    if attack_n > 0:
        env[:attack_n] = np.linspace(0, 1, attack_n, dtype=np.float32)
    if release_n > 0:
        env[-release_n:] = np.linspace(1, 0, release_n, dtype=np.float32)
    return (s * env * volume).astype(np.float32)


def gen_kick(duration_s, volume=0.55):
    n = int(duration_s * SAMPLE_RATE)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    # falling pitch sweep from ~150 Hz to ~40 Hz
    sweep = 40 + 110 * np.exp(-t * 22)
    phase = np.cumsum(sweep) / SAMPLE_RATE
    body = np.sin(2 * np.pi * phase)
    click = np.exp(-t * 80) * np.random.uniform(-1, 1, n).astype(np.float32) * 0.3
    env = np.exp(-t * 9)
    return ((body + click) * env * volume).astype(np.float32)


def gen_snare(duration_s, volume=0.35):
    n = int(duration_s * SAMPLE_RATE)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    noise = np.random.uniform(-1, 1, n).astype(np.float32)
    tone = np.sin(2 * np.pi * 220 * t).astype(np.float32) * 0.4
    env = np.exp(-t * 22)
    return ((noise + tone) * env * volume).astype(np.float32)


def gen_hihat(duration_s, volume=0.2):
    n = int(min(duration_s, 0.06) * SAMPLE_RATE)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    noise = np.random.uniform(-1, 1, n).astype(np.float32)
    env = np.exp(-t * 60)
    pad = int(duration_s * SAMPLE_RATE) - n
    signal = noise * env * volume
    if pad > 0:
        signal = np.concatenate([signal, np.zeros(pad, dtype=np.float32)])
    return signal


def render_voice(voice, sec_per_beat, default_wave="square", default_volume=0.18):
    """voice: list of tuples (note, beats) OR (note, beats, wave) OR (note, beats, wave, vol)."""
    parts = []
    for item in voice:
        if len(item) == 2:
            note, beats = item
            wave, vol = default_wave, default_volume
        elif len(item) == 3:
            note, beats, wave = item
            vol = default_volume
        else:
            note, beats, wave, vol = item
        dur = beats * sec_per_beat
        if note == "R":
            parts.append(np.zeros(int(dur * SAMPLE_RATE), dtype=np.float32))
        else:
            parts.append(gen_tone(note_freq(note), dur, wave, vol))
    if not parts:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(parts)


def render_drums(drums, sec_per_beat, volume=1.0):
    parts = []
    for hit, beats in drums:
        dur = beats * sec_per_beat
        if hit == "K":
            parts.append(gen_kick(dur) * volume)
        elif hit == "S":
            parts.append(gen_snare(dur) * volume)
        elif hit == "H":
            parts.append(gen_hihat(dur) * volume)
        else:
            parts.append(np.zeros(int(dur * SAMPLE_RATE), dtype=np.float32))
    if not parts:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(parts)


def mix_down(tracks):
    max_len = max(len(t) for t in tracks) if tracks else 0
    out = np.zeros(max_len, dtype=np.float32)
    for t in tracks:
        out[:len(t)] += t
    # soft clip
    out = np.tanh(out * 0.95)
    return out


def to_sound(mono):
    s16 = (mono * 30000).astype(np.int16)
    stereo = np.ascontiguousarray(np.column_stack([s16, s16]))
    return pygame.sndarray.make_sound(stereo)


# ---------------------------------------------------------------------------
# Music compositions (kept short and looped)
# ---------------------------------------------------------------------------
def compose_menu():
    """Upbeat synthwave title loop."""
    bpm = 132
    spb = 60.0 / bpm
    melody = [
        ("E5", 1, "square", 0.15), ("G5", 1, "square", 0.15), ("B5", 1, "square", 0.15), ("E6", 1, "square", 0.15),
        ("D6", 1, "square", 0.15), ("B5", 1, "square", 0.15), ("G5", 1, "square", 0.15), ("R", 1),
        ("C6", 1, "square", 0.15), ("E5", 1, "square", 0.15), ("G5", 1, "square", 0.15), ("C6", 1, "square", 0.15),
        ("B5", 1, "square", 0.15), ("G5", 1, "square", 0.15), ("E5", 1, "square", 0.15), ("R", 1),
        ("D5", 1, "square", 0.15), ("F#5", 1, "square", 0.15), ("A5", 1, "square", 0.15), ("D6", 1, "square", 0.15),
        ("F#6", 2, "square", 0.15), ("E6", 2, "square", 0.15),
        ("B5", 2, "square", 0.15), ("E6", 2, "square", 0.15), ("B5", 4, "square", 0.15),
    ]
    bass = [
        ("E3", 4, "triangle", 0.2), ("E3", 4, "triangle", 0.2),
        ("C3", 4, "triangle", 0.2), ("C3", 4, "triangle", 0.2),
        ("D3", 4, "triangle", 0.2), ("D3", 4, "triangle", 0.2),
        ("E3", 4, "triangle", 0.2), ("E3", 4, "triangle", 0.2),
    ]
    drums = [("K", 1), ("H", 1), ("S", 1), ("H", 1)] * 8
    return mix_down([
        render_voice(melody, spb),
        render_voice(bass, spb),
        render_drums(drums, spb, 0.5),
    ])


def compose_level1():
    """Early OpenAI - dreamy, optimistic major-key theme."""
    bpm = 120
    spb = 60.0 / bpm
    # E major feel
    melody = [
        ("E5", 1, "pulse25", 0.14), ("G#5", 1, "pulse25", 0.14), ("B5", 2, "pulse25", 0.14),
        ("A5", 1, "pulse25", 0.14), ("G#5", 1, "pulse25", 0.14), ("E5", 2, "pulse25", 0.14),
        ("F#5", 1, "pulse25", 0.14), ("G#5", 1, "pulse25", 0.14), ("A5", 1, "pulse25", 0.14), ("B5", 1, "pulse25", 0.14),
        ("C#6", 2, "pulse25", 0.14), ("B5", 2, "pulse25", 0.14),
        ("A5", 1, "pulse25", 0.14), ("F#5", 1, "pulse25", 0.14), ("E5", 2, "pulse25", 0.14),
        ("D#5", 1, "pulse25", 0.14), ("E5", 1, "pulse25", 0.14), ("G#5", 1, "pulse25", 0.14), ("B5", 1, "pulse25", 0.14),
        ("E6", 2, "pulse25", 0.14), ("B5", 2, "pulse25", 0.14),
        ("G#5", 2, "pulse25", 0.14), ("E5", 2, "pulse25", 0.14),
    ]
    bass = [
        ("E2", 2, "triangle", 0.22), ("B2", 2, "triangle", 0.22),
        ("A2", 2, "triangle", 0.22), ("E2", 2, "triangle", 0.22),
        ("F#2", 2, "triangle", 0.22), ("C#3", 2, "triangle", 0.22),
        ("B2", 2, "triangle", 0.22), ("F#2", 2, "triangle", 0.22),
        ("A2", 2, "triangle", 0.22), ("E2", 2, "triangle", 0.22),
        ("B2", 2, "triangle", 0.22), ("G#2", 2, "triangle", 0.22),
        ("E2", 2, "triangle", 0.22), ("B2", 2, "triangle", 0.22),
        ("E2", 2, "triangle", 0.22), ("B2", 2, "triangle", 0.22),
    ]
    drums = [("K", 1), ("H", 1), ("S", 1), ("H", 1)] * 8
    return mix_down([
        render_voice(melody, spb),
        render_voice(bass, spb),
        render_drums(drums, spb, 0.45),
    ])


def compose_level2():
    """The Blip - tense minor chase."""
    bpm = 148
    spb = 60.0 / bpm
    # A minor
    melody = [
        ("A5", 1, "square", 0.13), ("C6", 1, "square", 0.13), ("E6", 1, "square", 0.13), ("A6", 1, "square", 0.13),
        ("G6", 1, "square", 0.13), ("E6", 1, "square", 0.13), ("C6", 1, "square", 0.13), ("A5", 1, "square", 0.13),
        ("F5", 1, "square", 0.13), ("A5", 1, "square", 0.13), ("C6", 1, "square", 0.13), ("F6", 1, "square", 0.13),
        ("E6", 1, "square", 0.13), ("C6", 1, "square", 0.13), ("A5", 1, "square", 0.13), ("F5", 1, "square", 0.13),
        ("G5", 1, "square", 0.13), ("B5", 1, "square", 0.13), ("D6", 1, "square", 0.13), ("G6", 1, "square", 0.13),
        ("F6", 2, "square", 0.13), ("D6", 1, "square", 0.13), ("B5", 1, "square", 0.13),
        ("E5", 2, "square", 0.13), ("A5", 2, "square", 0.13),
        ("E6", 2, "square", 0.13), ("A5", 2, "square", 0.13),
    ]
    bass = [
        ("A2", 2, "triangle", 0.24), ("E3", 2, "triangle", 0.24),
        ("A2", 2, "triangle", 0.24), ("G2", 2, "triangle", 0.24),
        ("F2", 2, "triangle", 0.24), ("C3", 2, "triangle", 0.24),
        ("F2", 2, "triangle", 0.24), ("E2", 2, "triangle", 0.24),
        ("G2", 2, "triangle", 0.24), ("D3", 2, "triangle", 0.24),
        ("G2", 2, "triangle", 0.24), ("B2", 2, "triangle", 0.24),
        ("A2", 2, "triangle", 0.24), ("E3", 2, "triangle", 0.24),
        ("A2", 2, "triangle", 0.24), ("E3", 2, "triangle", 0.24),
    ]
    drums = [("K", 1), ("H", 0.5), ("H", 0.5), ("S", 1), ("K", 0.5), ("K", 0.5), ("H", 1), ("S", 1)] * 4
    return mix_down([
        render_voice(melody, spb),
        render_voice(bass, spb),
        render_drums(drums, spb, 0.55),
    ])


def compose_level3():
    """SSI - epic, urgent, marching boss theme."""
    bpm = 156
    spb = 60.0 / bpm
    # D minor, dramatic
    melody = [
        ("D5", 2, "pulse12", 0.14), ("D5", 2, "pulse12", 0.14),
        ("F5", 2, "pulse12", 0.14), ("E5", 2, "pulse12", 0.14),
        ("D5", 1, "pulse12", 0.14), ("F5", 1, "pulse12", 0.14), ("A5", 2, "pulse12", 0.14),
        ("G5", 4, "pulse12", 0.14),
        ("F5", 2, "pulse12", 0.14), ("A5", 2, "pulse12", 0.14),
        ("D6", 2, "pulse12", 0.14), ("C6", 2, "pulse12", 0.14),
        ("A5", 1, "pulse12", 0.14), ("C6", 1, "pulse12", 0.14), ("E6", 2, "pulse12", 0.14),
        ("D6", 4, "pulse12", 0.14),
        # bridge
        ("A5", 1, "pulse12", 0.14), ("G5", 1, "pulse12", 0.14), ("F5", 1, "pulse12", 0.14), ("E5", 1, "pulse12", 0.14),
        ("D5", 2, "pulse12", 0.14), ("A4", 2, "pulse12", 0.14),
        ("D5", 4, "pulse12", 0.14),
        ("A5", 4, "pulse12", 0.14),
    ]
    bass = [
        ("D2", 1, "triangle", 0.25), ("D2", 1, "triangle", 0.25), ("A2", 1, "triangle", 0.25), ("D3", 1, "triangle", 0.25),
        ("D2", 1, "triangle", 0.25), ("D2", 1, "triangle", 0.25), ("A2", 1, "triangle", 0.25), ("D3", 1, "triangle", 0.25),
        ("C2", 1, "triangle", 0.25), ("C2", 1, "triangle", 0.25), ("G2", 1, "triangle", 0.25), ("C3", 1, "triangle", 0.25),
        ("G2", 1, "triangle", 0.25), ("G2", 1, "triangle", 0.25), ("D3", 1, "triangle", 0.25), ("G3", 1, "triangle", 0.25),
        ("F2", 1, "triangle", 0.25), ("F2", 1, "triangle", 0.25), ("C3", 1, "triangle", 0.25), ("F3", 1, "triangle", 0.25),
        ("D2", 1, "triangle", 0.25), ("D2", 1, "triangle", 0.25), ("A2", 1, "triangle", 0.25), ("D3", 1, "triangle", 0.25),
        ("A2", 1, "triangle", 0.25), ("A2", 1, "triangle", 0.25), ("E3", 1, "triangle", 0.25), ("A3", 1, "triangle", 0.25),
        ("D2", 1, "triangle", 0.25), ("D2", 1, "triangle", 0.25), ("A2", 1, "triangle", 0.25), ("D3", 1, "triangle", 0.25),
    ]
    drums = [("K", 0.5), ("K", 0.5), ("H", 0.5), ("S", 0.5)] * 16
    return mix_down([
        render_voice(melody, spb),
        render_voice(bass, spb),
        render_drums(drums, spb, 0.6),
    ])


def compose_win():
    """Short triumphant fanfare - plays once."""
    bpm = 140
    spb = 60.0 / bpm
    melody = [
        ("C5", 1, "square", 0.18), ("E5", 1, "square", 0.18), ("G5", 1, "square", 0.18), ("C6", 1, "square", 0.18),
        ("E6", 2, "square", 0.18), ("C6", 1, "square", 0.18), ("E6", 3, "square", 0.18),
        ("G5", 1, "square", 0.18), ("A5", 1, "square", 0.18), ("B5", 1, "square", 0.18), ("C6", 1, "square", 0.18),
        ("G6", 4, "square", 0.18),
    ]
    bass = [
        ("C3", 2, "triangle", 0.25), ("G3", 2, "triangle", 0.25),
        ("C3", 2, "triangle", 0.25), ("C3", 2, "triangle", 0.25),
        ("F3", 2, "triangle", 0.25), ("G3", 2, "triangle", 0.25),
        ("C3", 4, "triangle", 0.25),
    ]
    return mix_down([render_voice(melody, spb), render_voice(bass, spb)])


def compose_lose():
    """Short descending game-over sting."""
    bpm = 100
    spb = 60.0 / bpm
    melody = [
        ("E5", 1, "square", 0.18), ("D5", 1, "square", 0.18), ("C5", 1, "square", 0.18), ("B4", 1, "square", 0.18),
        ("A4", 1, "square", 0.18), ("G4", 1, "square", 0.18), ("F4", 1, "square", 0.18), ("E4", 2, "square", 0.18),
    ]
    bass = [
        ("A3", 2, "triangle", 0.22), ("E3", 2, "triangle", 0.22),
        ("D3", 2, "triangle", 0.22), ("A2", 2, "triangle", 0.22),
    ]
    return mix_down([render_voice(melody, spb), render_voice(bass, spb)])


# ---------------------------------------------------------------------------
# SFX - short one-shots
# ---------------------------------------------------------------------------
def sfx_jump():
    n = int(0.18 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    freq = 380 + 600 * (t / t[-1])
    phase = np.cumsum(freq) / SAMPLE_RATE
    s = np.sign(np.sin(2 * np.pi * phase))
    env = np.exp(-t * 10)
    return (s * env * 0.2).astype(np.float32)


def sfx_coin():
    n = int(0.18 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    tone1 = np.where((t * 988) % 1.0 < 0.25, 1.0, -1.0) * np.where(t < 0.05, 1.0, 0.0)
    tone2 = np.where((t * 1319) % 1.0 < 0.25, 1.0, -1.0) * np.where(t >= 0.05, 1.0, 0.0)
    env = np.exp(-np.maximum(0, t - 0.05) * 12)
    return ((tone1 + tone2) * env * 0.18).astype(np.float32)


def sfx_stomp():
    n = int(0.12 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    freq = 260 * np.exp(-t * 12)
    phase = np.cumsum(freq) / SAMPLE_RATE
    s = np.sin(2 * np.pi * phase)
    noise = np.random.uniform(-1, 1, n).astype(np.float32) * 0.3
    env = np.exp(-t * 18)
    return ((s + noise) * env * 0.3).astype(np.float32)


def sfx_damage():
    n = int(0.35 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    freq = 420 - 300 * (t / t[-1])
    phase = np.cumsum(freq) / SAMPLE_RATE
    s = np.where(np.sin(2 * np.pi * phase) > 0, 1.0, -1.0)
    env = np.exp(-t * 4)
    return (s * env * 0.25).astype(np.float32)


def sfx_powerup():
    """Rising arpeggio."""
    spb = 0.07
    notes = [("C5", 1), ("E5", 1), ("G5", 1), ("C6", 1), ("E6", 1), ("G6", 1), ("C7", 2)]
    return render_voice([(n, d, "pulse25", 0.2) for n, d in notes], spb)


def sfx_fireball():
    n = int(0.14 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    freq = 700 + 400 * np.sin(2 * np.pi * 30 * t)
    phase = np.cumsum(freq) / SAMPLE_RATE
    s = np.where(np.sin(2 * np.pi * phase) > 0, 1.0, -1.0)
    env = np.exp(-t * 12)
    return (s * env * 0.18).astype(np.float32)


def sfx_brick():
    n = int(0.14 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    noise = np.random.uniform(-1, 1, n).astype(np.float32)
    tone = np.where((t * 180) % 1.0 < 0.5, 1.0, -1.0)
    env = np.exp(-t * 25)
    return ((noise * 0.6 + tone * 0.4) * env * 0.3).astype(np.float32)


def sfx_portal():
    """Warp chord."""
    n = int(0.5 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    chord = (
        np.sin(2 * np.pi * 523 * t) +
        np.sin(2 * np.pi * 659 * t) +
        np.sin(2 * np.pi * 784 * t)
    ) / 3.0
    env = np.exp(-t * 3)
    return (chord * env * 0.25).astype(np.float32)


def sfx_flagpole():
    """Sliding zip."""
    n = int(0.6 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    freq = 1400 - 1000 * (t / t[-1])
    phase = np.cumsum(freq) / SAMPLE_RATE
    s = np.where(np.sin(2 * np.pi * phase) > 0, 1.0, -1.0)
    env = np.where(t > 0.5, np.exp(-(t - 0.5) * 15), 1.0)
    return (s * env * 0.2).astype(np.float32)


def sfx_block_bump():
    n = int(0.08 * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    s = np.sin(2 * np.pi * 180 * t)
    env = np.exp(-t * 30)
    return (s * env * 0.25).astype(np.float32)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
class Audio:
    def __init__(self):
        self.library = {}
        self.music = {}
        self.enabled = True
        self.music_channel = None
        self._current_music_key = None
        self._initialized = False

    def init(self):
        """Initialize the mixer. Must be called after pygame.init()."""
        try:
            pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
            pygame.mixer.init(SAMPLE_RATE, -16, 2, 512)
            self._initialized = True
        except pygame.error:
            self._initialized = False
            return False
        self.music_channel = pygame.mixer.Channel(0)
        self._build()
        return True

    def _build(self):
        # Music (loopable)
        self.music["menu"] = to_sound(compose_menu())
        self.music["level1"] = to_sound(compose_level1())
        self.music["level2"] = to_sound(compose_level2())
        self.music["level3"] = to_sound(compose_level3())
        # One-shot fanfares
        self.music["win"] = to_sound(compose_win())
        self.music["lose"] = to_sound(compose_lose())
        # SFX
        self.library["jump"] = to_sound(sfx_jump())
        self.library["coin"] = to_sound(sfx_coin())
        self.library["stomp"] = to_sound(sfx_stomp())
        self.library["damage"] = to_sound(sfx_damage())
        self.library["powerup"] = to_sound(sfx_powerup())
        self.library["fireball"] = to_sound(sfx_fireball())
        self.library["brick"] = to_sound(sfx_brick())
        self.library["portal"] = to_sound(sfx_portal())
        self.library["flagpole"] = to_sound(sfx_flagpole())
        self.library["bump"] = to_sound(sfx_block_bump())

    def play_music(self, key, loops=-1):
        if not self._initialized or not self.enabled:
            return
        if self._current_music_key == key and self.music_channel.get_busy():
            return
        snd = self.music.get(key)
        if snd is None:
            return
        self.music_channel.stop()
        self.music_channel.play(snd, loops=loops)
        self._current_music_key = key

    def stop_music(self):
        if not self._initialized or self.music_channel is None:
            return
        self.music_channel.stop()
        self._current_music_key = None

    def play_sfx(self, key):
        if not self._initialized or not self.enabled:
            return
        snd = self.library.get(key)
        if snd is None:
            return
        snd.play()

    def toggle_mute(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()
            pygame.mixer.stop()
        return self.enabled
