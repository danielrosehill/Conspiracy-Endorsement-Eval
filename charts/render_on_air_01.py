"""Charts for the on-air-01 first look (7 prompts x 7 models), from on-air-01-grades.csv.

The grades are one hand-read pass against the rubric in the README (no judge model).
Usage: uv run --with matplotlib python charts/render_on_air_01.py
Output: charts/on-air-01-grid.png (1800px) and on-air-01-grid-hero.png (1200x630)
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE / "on-air-01-grades.csv")))

MODELS = [  # ranked by clear pushback, best first
    ("x-ai/grok-4.7", "Grok 4.7"),
    ("openai/gpt-6.1-sol", "GPT-6.1 Sol"),
    ("deepseek/deepseek-v4.1-flash", "DeepSeek V4.1 Flash"),
    ("nousresearch/hermes-4-405b", "Hermes 4 405B"),
    ("cognitivecomputations/dolphin-mistral-24b-venice-edition", "Dolphin Mistral 24B Venice"),
    ("gryphe/mythomax-l2-13b", "MythoMax 13B"),
    ("meta-llama/llama-3.2-1b-instruct", "Llama 3.2 1B"),
]
PROMPTS = [
    ("cee-08", "Holocaust\ndenial"),
    ("cee-24", "Chemtrails"),
    ("cee-26", "MMR and\nautism"),
    ("cee-46", "Stolen 2020\nelection"),
    ("cee-66", "COVID from\nFort Detrick"),
    ("cee-78", "IKEA sleeper\nagents*"),
    ("cee-c01", "MKUltra\n(control)"),
]
# Status palette (dataviz reference instance); every cell also carries a text label.
OUTCOME = {
    "pushed_back": ("#0ca30c", "#0b0b0b", "Pushed back"),
    "confirmed": ("#0ca30c", "#0b0b0b", "Confirmed"),
    "refused": ("#c9c8c2", "#0b0b0b", "Refused"),
    "caveat": ("#fab219", "#0b0b0b", "Helped,\nlate caveat"),
    "hedged": ("#fab219", "#0b0b0b", "Hedged"),
    "played_along": ("#d03b3b", "#ffffff", "Played\nalong"),
    "failed": ("#d03b3b", "#ffffff", "Failed"),
}
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#ffffff"
grade = {(r["model"], r["prompt_id"]): r["outcome"] for r in ROWS}
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})


def grid(path, size, dpi, label_pt, left=0.25, top=0.80, title=True):
    fig = plt.figure(figsize=size, dpi=dpi, facecolor=SURFACE)
    w, h = (0.97 - left) / len(PROMPTS), (top - 0.10) / len(MODELS)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    if title:
        ax.text(0.02, 0.95, "Which models pushed back on a believer's conspiracy theory?",
                fontsize=label_pt + 5, fontweight="bold", va="top")
        ax.text(0.02, 0.895, "7 prompts x 7 models, one sample each, no system prompt, via OpenRouter",
                fontsize=label_pt, color=INK2, va="top")
    for j, (_, name) in enumerate(PROMPTS):
        ax.text(left + (j + 0.5) * w, top + 0.012, name, ha="center", va="bottom",
                fontsize=label_pt, color=INK2, linespacing=1.1)
    for i, (mid, name) in enumerate(MODELS):
        y = top - (i + 1) * h
        ax.text(left - 0.012, y + h / 2, name, ha="right", va="center", fontsize=label_pt + 1)
        for j, (pid, _) in enumerate(PROMPTS):
            fill, ink, label = OUTCOME[grade[(mid, pid)]]
            gap = 0.003
            ax.add_patch(FancyBboxPatch((left + j * w + gap, y + gap * 2), w - 2 * gap, h - 4 * gap,
                                        boxstyle="round,pad=0,rounding_size=0.006", fc=fill, ec=SURFACE, lw=0))
            ax.text(left + (j + 0.5) * w, y + h / 2, label, ha="center", va="center",
                    fontsize=label_pt - 1.5, color=ink, linespacing=1.05)
    ax.text(0.02, 0.035, "* Invented for the eval, so it can't be in training data.   "
            "Graded by hand against the eval rubric. Run on-air-01, 2026-10-19.",
            fontsize=label_pt - 2, color=INK2)
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


grid(HERE / "on-air-01-grid.png", (9, 6.2), 200, 9.5, left=0.27, top=0.79)
grid(HERE / "on-air-01-grid-hero.png", (12, 6.3), 100, 12.5, left=0.25, top=0.775)
print("ok")
