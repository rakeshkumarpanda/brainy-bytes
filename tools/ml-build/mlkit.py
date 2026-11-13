"""Small boxes the Machine Learning topic files use on top of cvkit, coreaikit and pykit.

    link(sid, title, why, label)   a card that links to another subject on the site, for example the Complete
                                   Python subject (all of Python, Django, Flask and API handling) or Maths for ML
"""


def link(sid, title, why, label='Open the subject'):
    return (f'<div class="ml-link"><div><b>{title}</b><span>{why}</span></div>'
            f'<a class="ck-nb-a" href="../../subject.html?s={sid}" target="_top">{label}</a></div>')
