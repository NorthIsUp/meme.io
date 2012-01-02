THREAD = """
<html>
<body>
    <div>
        <img src="{meme_link}" alt="{meme_name} says\n{line_a}\n{line_b}" style="margin-left: auto; margin-right: auto; display: block;"/>
    </div>
    <div style="margin-left: auto; margin-right: auto; width: 600px">
        <div id="disqus_thread"></div>
        <script type="text/javascript">
            /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
            var disqus_shortname = 'northisup'; // required: replace example with your forum shortname
            var disqus_identifier= '{meme_name}/{line_a}/{line_b}';
            var disqus_developer = 1;

            /* * * DON'T EDIT BELOW THIS LINE * * */
            (function() {{
                var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
            }})();
        </script>
        <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
        <a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
    </div>
</body>
</html>
"""
