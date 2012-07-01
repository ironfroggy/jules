.. Jules documentation master file, created by
   sphinx-quickstart on Wed Jun 27 23:16:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Jules's documentation!
=================================

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


An example layout:

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

Getting Started
===============

First, you'll need to install Jules. You can do so with a simple
``pip install Jules``, or you can checkout a copy directly from the GitHub
`repository <http://github.com/ironfroggy/jules>`_. You can quickly begin
your first Jules website with the ``init`` subcommand.

::

    jules init my-new-site


Which will produce and empty site with all the parts a Jules project needs.

::

    my-new-site/
    ├── site.yaml
    ├── contents/
    │   ├── index.yaml
    │   ├── first-post.yaml
    │   └── first-post.rst
    ├── static/
    │   ├── css/
    │   │   └── site.less
    │   ├── img/
    │   └── js/
    └── templates/
        ├── site_base.j2
        ├── tag.j2
        ├── post.j2
        └── index.j2

We can break down the files produced and what all the parts do.

* `site.yaml`
    Provides global configuration for the site
* `contents/`
    All your Restructured Text content goes here; Your blog posts and pages.
* `templates/`
    Jinja2 templates defining your layout are found here.
* `static/`
    Javascript, images, and CSS and Less stylesheets are all located under ``static/``

Your `site.yaml` will contain a basic configuration and a few values will
obviously need customized.

::

    title: "My New Site"
    subtitle: "A Website For Me!"
    google_analytics_id: "UA-XXXXXX-XX"
    domain: "www.example.com"
    default_author: "You <you@example.com>"
    tag_path: "tags/{tag}/"
    packs:
    - "jules:html5boilerplate"
    - "jules:lesscss"
    - "jules:atom"
    - "dir:templates"
    - "dir:static"
    - "dir:contents"

While most of these are self-explainatory, one section you might not guess
the meaning of the list of `packs`. A `pack` is a directory containing
content, assets, or templates and your site is built out of a list of packs,
which are all combined into your final site. This allows Jules to offer
bits of functionality and shortcuts in self-contained pieces for you to use
or skip, as you wish. In our default site, we have three packs from Jules
offering a basic layout based on the excellent HTML5 Boilerplate project,
the assets needed to use LESS CSS for easier site styling, and the atom pack
to provide a template to generate Atom feeds.

The other three packs are the directories you'll find in the site folder,
separated for you into templates, static files, and content.

You'll want to refer to the Jinja2 documentation for everything in the
``templates/`` directory, but if you have a background in Django things
should feel familiar to you.

The part you'll spend most of your time in is the ``contents/`` directory,
where you'll configure your pages and posts and where their content will live.
In the example site provided, there is an ``index.yaml`` configuring the
front page. Our example site's is very simple.

::

    render: jinja2
    template: index.j2

This just tells Jinja this page should be rendered, with Jinja2, and to use
the ``index.j2`` template.

A bigger example is the example blog post, which is actually two files. The
first configures the page (``first-post.yaml``) and the second contains the
contents of the post (``first-post.rst``). The contents are in restructured
text, which is a great mark up language to write plain-text which can be
converted into a number of presentation formats.

::

    title: First Post
    status: published
    publish_time: !!timestamp '2012-06-23 10:00:00'
    render: jinja2
    template: post.j2
    tags:
    - test

The post is configured with a title, a publication status and time, and the
same render and template directives shared by the front page. The post also
has a list of tags, and the templates provided will generate a list of all
the published tags and build index pages for all of them.

Now, to see our site we just need to run ``jules build`` from inside the
site directory. Jules will look for the ``site.yaml`` and then load all the
configured packs, parse your content, collect your posts and tags, and render
the site to ``_build``.

Finally, if you want to see the site in action, just run the serve command
after building.

::

    jules serve

And direct your browser to `<http://localhost:8000/>`_ to see it in action.


Template API
============

Within your templates, you'll have access to a few things that let you access
both the current page being rendered and other pages, as well as information
about the site itself.


``bundle``
^^^^^^^^^^

The current page being rendered.

``bundle.meta``
###############

* ``bundle.meta.title``
* ``bundle.meta.publish_time``
* ``bundle.meta.created_time``
* ``bundle.meta.status``
* ``bundle.meta.tags``

``engine``
^^^^^^^^^^

``config``
^^^^^^^^^^
