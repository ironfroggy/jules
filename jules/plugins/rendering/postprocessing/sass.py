from scss import Scss

from .. import Renderer
from . import MutatingPostProcessingPlugin

class ScssCompiler(MutatingPostProcessingPlugin):
    input_extension = '.scss'
    output_extension = '.css'
    
    def init(self):
        self.css = Scss()
    
    def process_data(self, data):
        return self.css.compile(data)