import os
import posixpath
import shutil

from jules.plugins import ComponentPlugin
from jules.plugins.rendering import RenderingPlugin
from jules import writer, utils

# FIXME: depend on meta field to determine where the static content goes.
#        (needs implementation of meta dependencies first.)
class StaticComponent(ComponentPlugin, RenderingPlugin):
    name = None # only loaded for side-effects (for now)
    basenames = ['static']
    config = utils.named_keywords('static_directories')
    
    def init(self):
        self.render_actions = []
        self.config.static_directories = [
            os.path.join(self.engine.src_path, d)
            for d in getattr(self.config, 'static_directories', ['static'])]
        
        for d in self.config.static_directories:
            self.maybe_load(('', d))
    
    def maybe_load(self, static):
        ext, path = static
        # ignore ext, we don't really care (bleh.)
        
        for root, dirs, files in os.walk(path):
            # subpath is the path to it if root was /
            subpath = os.path.normpath(os.path.join(
                '/',
                os.path.relpath(root, path)))
            for filename in files:
                filepath = os.path.join(root, filename)
                filesubpath = os.path.join(subpath, filename)
                url = posixpath.join('/', *writer.split_path(filesubpath))
                self.render_actions.append((
                    url,
                    None,
                    FileCopyRenderer(filepath),
                    ()))
    
    def get_render_actions(self):
        return self.render_actions

class FileCopyRenderer(object):
    def __init__(self, path):
        self.path = path

    def render(self, f):
        with open(self.path) as origin:
            shutil.copyfileobj(origin, f)
