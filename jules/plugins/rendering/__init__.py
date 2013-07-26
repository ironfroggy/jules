import os
import tempfile
import shutil
import posixpath

import genshi
import jinja2

import jules
from jules.query import cache, unwrapping_kwargs, method_registrar
from jules import writer, utils

from .postprocessing import MutatingPostProcessingPlugin

jules.add_namespace(__package__)

class CanonConflictError(Exception): pass

class Renderer(jules.plugins.EnginePlugin):
    """Query operatings for rendering results to disk.
    
    A basic problem is that posts need to know canonical URLs, but canonical
    URLs are generated after posts. To solve this, we look at the URLs first,
    and only then do we render the templates and write out the actual data.
    
    Steps:
     * Collect URL information
       This is done during the pipeline/query phase. To be precise, we collect:
        
        - what URLs get rendered with what templates, data.
        - what URLs are canonical for what names.
     * Create canonical URL database
       This is done during the finalization phase of the EnginePlugin,
       using the collect_urls() method.
     * Render to disk.
       This is done during the finalization phase of the EnginePlugin,
       using the render_urls() method.
     * Put rendered data into final location.
       This is also done during finalization, but in final_move()
    """
    
    def init(self):
        self.config.output_dir = os.path.join(
            self.engine.src_path,
            getattr(self.config, 'output_dir', '_build'))

        self.url_canon = {} # map names -> (url, title)
        self.name_canon = {} # map urls -> (name, title)

        self.tempdir = tempfile.mkdtemp(suffix='-jules')
    
    def init_postprocessors(self):
        postprocessors = self.engine.plugins.produce_instances(
            MutatingPostProcessingPlugin)
        self.postprocessors = list(utils.topsort(
            {p: p.processing_dependencies
            for p in postprocessors}))
    
    def finalize(self):
        self.init_postprocessors() # FIXME: circular dependencies are disgusting man.
        self.collect_urls()
        self.render_urls()
        self.final_move()
    
    def collect_urls(self):
        self.renders = []
        
        for url, canon, data in self.get_render_actions():
            if canon is not None:
                name, title = canon
                self.update_canon(name, title, url)
            self.renders.append((url, data))
    
    def render_urls(self):
        urlwriter = writer.URLWriter(self.tempdir)
        for url, data in self.renders:
            data = self.postprocess_render(url, data)
            with urlwriter.urlopen(url) as f:
                f.write(data)
        
        self.renders = []
    
    def postprocess_render(self, url, data):
        # FIXME: MIME types instead, perhaps?
        if url.endswith("/") or url.endswith(".htm"):
            extension = '.html'
        else:
            extension = posixpath.splitext(url)[-1]
        
        while True:
            # Need to restart the processor pipeline if the extension changes.
            for postprocessor in self.postprocessors:
                if postprocessor.input_extension == extension:
                    data = postprocessor.process_data(data)
                    
                    if (postprocessor.output_extension is not None
                    and postprocessor.output_extension != extension):
                        extension = postprocessor.output_extension
                        break # reset loop
            else:
                # don't need to reset. Don't hate the coder, hate the code.
                break
        
        return data

    def final_move(self):
        out = self.config.output_dir

        # race conditions ahoy, unavoidable, don't care.
        # should I even bother with this?
        old_out = None
        if os.path.isdir(out):
            temp_storage = tempfile.mkdtemp(suffix='-jules')
            old_out = os.path.join(temp_storage, os.path.basename(out))
            shutil.move(out, old_out)
        try:
            shutil.move(self.tempdir, out)
        except:
            if old_out is not None:
                shutil.move(old_out, out)
            raise

    def get_render_actions(self):
        plugins = self.engine.plugins.produce_instances(RenderingPlugin)
        for plugin in plugins:
            for action in plugin.get_render_actions():
                yield action

    def update_canon(self, name, title, url):
        try:
            old_url, old_title = self.url_canon[name]
        except KeyError:
            pass
        else:
            if old_url == url:
                raise CanonConflictError(
                    "Resources want identical names and URL: "
                    "name %r and URL %r (%s and %s)"
                    % (name, url, old_title, title))
            raise CanonConflictError(
                "The resources at URL %r (%s) and URL %r (%s) both "
                "want the name %r"
                % (old_url, old_title, url, title, name))
        
        try:
            old_name, old_title = self.name_canon[url]
        except KeyError:
            pass
        else:
            raise CanonConflictError(
                "The resources %r (%s) and %r (%s) both "
                "want the URL %r"
                % (old_name, old_title, name, title, url))
        
        self.url_canon[name] = url, title
        self.name_canon[url] = name, title

def fmt_title(t):
    return "no title" if t is None else "title %r" % t

class RenderingPlugin(jules.plugins.BaseJulesPlugin):
    def get_render_actions(self):
        """Return iterable of (url, canonical, renderer, args)
        
        canonical is either None or (canonical_name, canonical_title),
        where canonical_name is the canonical way to refer to this URL,
        and where canonical_title is the canonical link title for that URL.
        
        renderer has a .render() method which is passed f, *args, where f
        is a file whose content is at the URL.
        """
        raise NotImplementedError
