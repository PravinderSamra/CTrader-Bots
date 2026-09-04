#!/usr/bin/env python3
"""Convert a YouTube auto-caption VTT into clean, de-duplicated timestamped text.

YouTube's auto-captions use a rolling two-line window, so naive extraction
repeats nearly every word. This keeps only newly-appearing tokens and
re-flows them into timestamped paragraphs.
"""
import re, sys, html

def parse(path):
    cues = []
    for block in re.split(r'\n\n+', open(path, encoding='utf-8').read()):
        lines = [l for l in block.strip().split('\n') if l.strip()]
        if not lines:
            continue
        ts = next((l for l in lines if '-->' in l), None)
        if not ts:
            continue
        start = ts.split('-->')[0].strip().split(' ')[0]
        text_lines = lines[lines.index(ts) + 1:]
        txt = ' '.join(text_lines)
        txt = re.sub(r'<[^>]+>', '', txt)          # inline timing/karaoke tags
        txt = html.unescape(txt)
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt:
            cues.append((start, txt))
    return cues

def dedupe(cues):
    """Emit only the tail of each cue that wasn't already in the previous one."""
    out, prev = [], ''
    for start, txt in cues:
        if txt == prev:
            continue
        # find longest suffix-of-prev that prefixes txt
        new = txt
        pw, cw = prev.split(), txt.split()
        best = 0
        for k in range(min(len(pw), len(cw)), 0, -1):
            if pw[-k:] == cw[:k]:
                best = k
                break
        if best:
            new = ' '.join(cw[best:])
        if new.strip():
            out.append((start, new.strip()))
        prev = txt
    return out

def hhmm(t):
    return t.split('.')[0]

def main(src, dst, para_secs=30):
    cues = dedupe(parse(src))
    chunks, buf, anchor = [], [], None
    def secs(t):
        p = [float(x) for x in t.split(':')]
        return p[0]*3600 + p[1]*60 + p[2]
    for start, txt in cues:
        if anchor is None:
            anchor = start
        buf.append(txt)
        if secs(start) - secs(anchor) >= para_secs:
            chunks.append((anchor, ' '.join(buf)))
            buf, anchor = [], None
    if buf:
        chunks.append((anchor or cues[0][0], ' '.join(buf)))
    with open(dst, 'w', encoding='utf-8') as f:
        for start, txt in chunks:
            txt = re.sub(r'\s+', ' ', txt).strip()
            f.write(f'[{hhmm(start)}] {txt}\n\n')
    words = sum(len(c[1].split()) for c in chunks)
    print(f'{dst}: {len(chunks)} paragraphs, ~{words} words')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
