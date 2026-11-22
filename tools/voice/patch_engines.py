"""Patches the shared engines that also live as inline copies inside older pages.

1. voice.js (the floating Listen narrator): English only for now. The Hindi, Kannada, Odia, Arabic and German
   text stays inside the pages, so a language comes back by putting its row into LANGS again.
2. viz.js (the step player of the DSA, TestNG, Java and other older pages): while "Voice on" is reading the
   current step aloud, Play waits for the voice to finish before it moves to the next step.

Run from the repository root: python3 tools/voice/patch_engines.py
It patches assets/voice.js, assets/viz.js and every inline copy in content/ and tools/, and reports counts.
Running it twice changes nothing.
"""
import glob

PATCHES = [
    ("""    { k: 'en', native: 'English', bcp: 'en-US', listen: 'Listen' },
    { k: 'hi', native: 'हिन्दी', bcp: 'hi-IN', listen: 'सुनिए' },
    { k: 'kn', native: 'ಕನ್ನಡ', bcp: 'kn-IN', listen: 'ಆಲಿಸಿ' },
    { k: 'or', native: 'ଓଡ଼ିଆ', bcp: 'or-IN', listen: 'ଶୁଣନ୍ତୁ' },
    { k: 'ar', native: 'العربية', bcp: 'ar-SA', listen: 'استمع', rtl: true },
    { k: 'de', native: 'Deutsch', bcp: 'de-DE', listen: 'Anhören' }
  ];""",
     """    /* English only for now. The other languages' text stays in the pages, so a language comes back by adding its
       row here again: { k: 'hi', native: 'हिन्दी', bcp: 'hi-IN', listen: 'सुनिए' } (also kn-IN, or-IN, ar-SA with rtl: true, de-DE) */
    { k: 'en', native: 'English', bcp: 'en-US', listen: 'Listen' }
  ];"""),
    ("""      <div class="vx-langs" role="radiogroup" aria-label="Language">""",
     """      <div class="vx-langs" role="radiogroup" aria-label="Language"${LANGS.length < 2 ? ' style="display:none"' : ''}>"""),
    ("""    const tick = () => { if (i >= n - 1) { pause(); return; } go(i + 1); timer = setTimeout(tick, ms / +sp.value); };""",
     """    /* with "Voice on", wait until the voice has finished explaining this step (assets/voiceteach.js) */
    const tick = () => { if (i >= n - 1) { pause(); return; } if (window.__vtHold && window.__vtHold(host)) { timer = setTimeout(tick, 150); return; } go(i + 1); timer = setTimeout(tick, ms / +sp.value); };"""),
]

files = ['assets/voice.js', 'assets/viz.js'] + glob.glob('content/**/*.html', recursive=True) + glob.glob('tools/**/*.html', recursive=True) + glob.glob('tools/**/*.js', recursive=True)
counts = [0] * len(PATCHES)
for f in sorted(set(files)):
    s = open(f, encoding='utf-8').read()
    t = s
    for k, (a, b) in enumerate(PATCHES):
        if a in t:
            t = t.replace(a, b)
            counts[k] += 1
    if t != s:
        open(f, 'w', encoding='utf-8').write(t)
print('voice.js languages:', counts[0], 'language row:', counts[1], 'viz.js player:', counts[2])
