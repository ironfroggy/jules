from jules.plugins import BaseJulesPlugin
from jules import add_namespace
add_namespace(__name__)

class MutatingPostProcessingPlugin(BaseJulesPlugin):
    processing_dependencies = ()
    # TODO: support MIME types?
    input_extension = None
    output_extension = None
    
    def process_data(self, data):
        """Process data and return replacement data.
        
        If the extension of the replacement data is different, then the class
        attribute output_extension must be different. A plugin can't currently
        return multiple different extensions depending on the input.
        """
        return data

# TODO:
##BEGINNING = 0
##END = -1
##ANYWHERE = None
##class NonmutatingPostProcessingPlugin(jules.plugins.BaseJulesPlugin):