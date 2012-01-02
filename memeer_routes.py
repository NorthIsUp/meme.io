line_re = r"[\w\s!@#$%^&*()?<>.\"':;+=\[\]{}\\~`|-]+"
serve_meme_thread = r"^/memeer/disqus/(?P<name>{0})@@(?P<line_a>{0})@@(?P<line_b>{0})[/]?$".format(line_re)
serve_meme_image = r"^/memeer/(?P<name>{0})@@(?P<line_a>{0})@@(?P<line_b>{0})(?P<ext>(\.jpeg|\.jpg))?$".format(line_re)
