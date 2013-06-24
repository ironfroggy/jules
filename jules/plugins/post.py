from jules.plugins import ComponentPlugin

class PostComponent(ComponentPlugin):
    name = 'post'
    basenames = ['post']
    
    def maybe_load(self, post):
        (post_ext, post_f) = post
        with open(post_f) as f:
            return f.read() # FIXME: this is testing crap.