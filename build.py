"""Copies the small icon sets into this site folder and rebuilds the gallery (index.html).

Every folder next to this one that has a 100x100 folder counts as a character.
Run publish.cmd to build and push to GitHub in one go.
"""
import json
import os
import re
import shutil

SITE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.dirname(SITE)
SIZES = ['100x100', '150x150']


def natural(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', name)]


def emotion_order(char_dir):
    """Emotion order from the sorter's emotions.md, so the gallery matches the sorter buttons."""
    path = os.path.join(char_dir, 'emotions.md')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return [m.group(1) for m in (re.match(r'^## (.*?)(?: \(\d+\))?$', l.strip()) for l in f) if m]


data = {}
for char in sorted(os.listdir(ICONS), key=natural):
    char_dir = os.path.join(ICONS, char)
    if char_dir == SITE or not os.path.isdir(os.path.join(char_dir, SIZES[0])):
        continue
    for size in SIZES:
        src, dst = os.path.join(char_dir, size), os.path.join(SITE, char, size)
        shutil.rmtree(dst, ignore_errors=True)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=lambda d, fs: [f for f in fs if not f.lower().endswith('.png')
                                                            and not os.path.isdir(os.path.join(d, f))])
    base = os.path.join(char_dir, SIZES[0])
    order = emotion_order(char_dir)
    groups = {}
    for emotion in os.listdir(base):
        if os.path.isdir(os.path.join(base, emotion)):
            icons = sorted((os.path.splitext(f)[0] for f in os.listdir(os.path.join(base, emotion))
                            if f.lower().endswith('.png')), key=natural)
            if icons:
                groups[emotion] = icons
    loose = sorted((os.path.splitext(f)[0] for f in os.listdir(base) if f.lower().endswith('.png')), key=natural)
    ordered = [e for e in order if e in groups] + sorted((e for e in groups if e not in order), key=natural)
    data[char] = [[e, groups[e]] for e in ordered] + ([['', loose]] if loose else [])
    print(f'{char}: {sum(len(g[1]) for g in data[char])} icons in {len(data[char])} groups')

# drop characters whose source folder is gone
for entry in os.listdir(SITE):
    if os.path.isdir(os.path.join(SITE, entry)) and not entry.startswith('.') and entry not in data:
        shutil.rmtree(os.path.join(SITE, entry))

with open(os.path.join(SITE, 'template.html'), encoding='utf-8') as f:
    page = f.read().replace('/*DATA*/null', json.dumps(data, separators=(',', ':')))
    page = page.replace('/*SIZES*/null', json.dumps(SIZES))
with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(page)
print('index.html written')
