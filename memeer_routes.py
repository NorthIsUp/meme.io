line_re = '[\w\s!@#$%^&*()?<>."\':;+=[\]{}\\~`|-]+'
serve_meme_thread = "^/memeer/disqus/(?P<name>{0})/(?P<line_a>{0})//(?P<line_b>{0})[/]?$".format(line_re)
serve_meme_image = "^/memeer/(?P<name>{0})/(?P<line_a>{0})//(?P<line_b>{0})[/]?$".format(line_re)
