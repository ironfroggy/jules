import os
import posixpath

class URLWriteConflict(Exception):
    """
    - url: URL in question
    - old: owner of first write
    - new: attempted owner that is being rejected
    """
    def __init__(self, url, old, new):
        self.url = url
        self.old = old
        self.new = new
        super(URLWriteConflict, self).__init__(url, old, new)

# FIXME: pass this into plugins
# FIXME: add shutil wrapping
class URLWriter(object):
    def __init__(self, output_path):
        self.output_path = output_path
        self.ownership = {}
    
    @staticmethod
    def normalize_url(urlpath):
        if posixpath.basename(urlpath) == '':
            return posixpath.join(urlpath, 'index.html')
        return urlpath
    
    @staticmethod
    def split_url(urlpath):
        """
        Convert absolute URL path to an abstract path (list of path components)
        """
        head = urlpath
        reversed_split = []
        while head != '/':
            if not head:
                raise ValueError("relative paths not allowed")
            
            head, tail = posixpath.split(head)
            reversed_split.append(tail)
        return tuple(reversed(reversed_split))
    
    def ensure_directories(self, abstract_path):
        dirs = abstract_path[:-1]
        
        new_dir = '.'
        for dir in dirs:
            new_dir = os.path.join(new_dir, dir)
            # FIXME: race condition precludes parallelism
            if not os.path.isdir(new_dir):
                os.mkdir(new_dir)
        
        
    def urlopen(self, urlpath, owner=None):
        """Open an URL for writing to.
        
        In the case that an URL conflict is found, raise URLWriteConflict
        """
        url = self.normalize_url(urlpath)
        split = (self.output_path,) + self.split_url(url)
        try:
            old_owner = self.ownership[split]
        except KeyError:
            self.ensure_directories(split)
            path = os.path.join(*split)
            f = open(path, 'w')
            self.ownership[split] = owner
            return f
        else:
            raise URLWriteConflict(url, old_owner, owner)


