# Background voice talks

Each chapter page's "Listen to this lesson" bar starts with a spoken background talk: the story behind the lesson,
why it matters, where it shows up in real life, and how the parts fit together. The talk is heard, not shown.

The Cybersecurity builder writes its talks into the page (`div.vt-talk`). Every other subject keeps them here, one
file per page, so a rebuild of a page never loses them:

    data/talk/<subject>/<page>.js      for content/<subject>/<page>.html

    VT_TALK('<subject>/<page>', {
      '<lesson id>': 'The talk, plain sentences, no markup.',
      ...
    });

The lesson id is the `id` of the `article.cv-lesson` or `section.jsec` that holds the lesson.
`assets/voiceteach.js` loads the file and places each talk inside its lesson.
`tools/voice/digest.py <page>` prints the lessons of a page with their ids, to write or check talks against.
`tools/voice/check.py` reports lessons that have no talk and talk ids that match no lesson.
