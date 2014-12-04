#!/usr/bin/env python

"""
Pandoc filters to customise the HTML / LaTeX output when parsing
documents. To figure out what elements are and how to edit them
run pandoc -f markdown -t json project_overview.md and have a look
at the (very very long) JSON output.
"""

from pandocfilters import toJSONFilter, Image, Str, RawInline


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


if __name__ == "__main__":
  toJSONFilter(tick_cross_images)