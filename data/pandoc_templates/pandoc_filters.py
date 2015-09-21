#!/usr/bin/env python

"""
Pandoc filters to customise the HTML / LaTeX output when parsing
documents. To figure out what elements are and how to edit them
run pandoc -f markdown -t json project_overview.md and have a look
at the (very very long) JSON output.
"""

import os
from pandocfilters import toJSONFilter, Image, Str, RawInline

swedac_latex_text = r"""\section{Swedac Accreditation}
\begin{minipage}{0.8\textwidth}
The National Genomics Infrastructure is accredited by \href{http://www.swedac.se}{Swedac}. This means that our services are subject to highly stringent quality control procedures, so that you can be sure that your data is of excellent quality.
\end{minipage} \hfill
\begin{minipage}{0.15\textwidth}
\includegraphics[height=3cm]{"""+os.path.realpath(os.path.dirname(__file__))+"""/assets/swedac.pdf}
\end{minipage}"""

swedac_html_text = r"""<h1>Swedac Accreditation
<a href="http://search.swedac.se/en/accreditations/1850"
target="_blank", class="swedac_logo"><img title="Swedac Accredited"
src="data:image/png;base64,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", style="float:right;margin:0 5px 0 0;"></a>
</h1>
<p>The National Genomics Infrastructure is accredited by <a href="http://www.swedac.se">Swedac</a>. This means that our services are subject to highly stringent quality control procedures, so that you can be sure that your data is of excellent quality.</p>"""

# Replace [tick] or [cross] with different icons in PDF and HTML
def tick_cross_images (key, value, format, meta):
    if key == 'Str' and value == '[tick]':
        if format == "latex":
            return RawInline('latex', r'~\tickmark~~')
        else:
            return RawInline('html', r'<span class="icon_tick">&#10004;</span> ')
    
    if key == 'Str' and value == '[cross]':
        if format == "latex":
            return RawInline('latex', r'~\crossmark~~~')
        else:
            return RawInline('html', r'<span class="icon_cross">&#10008;</span> ')
    
    if key == 'Str' and value == '[swedac]':
        if format == "latex":
            return RawInline('latex', swedac_latex_text)
        else:
            return RawInline('html', swedac_html_text)


if __name__ == "__main__":
  toJSONFilter(tick_cross_images)