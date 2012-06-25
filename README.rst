Jules is a static blog generator named after a victorian-ish era literary or
intellectual character, because apparently that's a trend now.

Jules processes a list of input directories called `packs`. A few `packs` are
included to provide useful parts of a website. As of this time, Jules ship with
HTML5 Boilerplate, LESS CSS, Bootstrap, and Atom XML Feeds.

Files from the source `packs` are grouped by their base name, the filename
without extensions. A bundle could include a YAML configuration file, a Jinja2
template, or other files. The bundles of files are processed together to
output files. By default, the files in the bundle are simply copied.

Restructured text files in a bundle are parsed as the `bundle content`, YAML
files are parsed as the `bundle meta data`, and Jinja2 templates are used to
render output HTML.


+----------------------+-----------------------+-------------------+
| Packs                | Bundles               | Files             |
+======================+=======================+===================+
| HTML5 Boiler Pack    | base                  | base.j2           |
|                      | js/jquery.min         | lib/jquery.min.js |
|                      |                       |                   |
+----------------------+-----------------------+-------------------+
| LESS CSS Pack        | js/less.min           | js/less.min.js    |
+----------------------+-----------------------+-------------------+
| Your site pack       | site_base             | site_base.j2      |
|                      +-----------------------+-------------------+
|                      | index                 | index.j2          |
|                      +                       +-------------------+
|                      |                       | index.rst         |
+----------------------+-----------------------+-------------------+
