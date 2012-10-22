.. _getting-started:
Getting Started
===============

First, you'll need to install Jules. You can do so with a simple
``pip install Jules``, or you can checkout a copy directly from the GitHub
`repository <http://github.com/ironfroggy/jules>`_. You can quickly begin
your first Jules website with the ``init`` subcommand.

::

    jules init my-new-site
    cd my-new-site
    jules build
    jules serve


Which will produce and empty site with all the parts a Jules project needs.
You can view the site, running with the ``jules serve`` command, by visiting
`http://localhost:8000/` on your local machine.

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

Site Configuration
^^^^^^^^^^^^^^^^^^

Your `site.yaml` will contain a basic configuration and a few values will
obviously need customized.

::

    title: "My New Site"
    subtitle: "A Website For Me!"
    google_analytics_id: "UA-XXXXXX-XX"
    domain: "www.example.com"
    default_author: "You <you@example.com>"
    packs:
    - "jules:html5boilerplate"
    - "jules:lesscss"
    - "jules:atom"
    - "jules:pygments"
    - "dir:templates"
    - "dir:static"
    - "dir:contents"
    bundle_defaults:
        output_ext: ""
        render: jinja2
    collections:
        tags:
            key_pattern: "{value}"
            match:
                status: published
            group_by:
                in: tags
            meta:
                render: jinja2
                template: tag.j2


While most of these are self-explainatory, we'll walk through.

::

    title: "My New Site"
    subtitle: "A Website For Me!"
    google_analytics_id: "UA-XXXXXX-XX"
    domain: "www.example.com"
    default_author: "You <you@example.com>"


These basic fields should be the most obvious. These fields, like everything
in ``site.yaml``, will be available in templates through the ``config`` variable.

::

    bundle_defaults:
        output_ext: ""
        render: jinja2

We set a few defaults for pages that will be rendered on our site. We want to
render with no extension, for clean URLs, and we want to render with jinja2
templates.

::

    packs:
    - "jules:html5boilerplate"
    - "jules:lesscss"
    - "jules:atom"
    - "jules:pygments"
    - "dir:templates"
    - "dir:static"
    - "dir:contents"


We configure our site with a list of `packs`. Every pack is a directory
containing content, assets, or templates, which are all combined into your
final site. This allows Jules to offer
bits of functionality and shortcuts in self-contained pieces for you to pick
or skip, as they suit your needs.

In this default site, we have three packs from Jules
offering a basic layout based on the excellent HTML5 Boilerplate project,
the assets needed to use LESS CSS for easier site styling, and the atom pack
to provide a template to generate Atom feeds.

The other three packs are the directories you'll find in the site folder,
separated for you into templates, static files, and content. These are used
in the default starter site, but you can define any packs however you want
to split up your site's input.

::

    collections:
        tags:
            key_pattern: "{value}"
            match:
                status: published
            group_by:
                in: tags
            meta:
                render: jinja2
                template: tag.j2


Collections allow us to group pages on the site with some common attribute,
sharing tags in this case. The collection of pages is itself a page we
can provide a tag for to render into the site, so we'll have pages for
every tag found.

We could group pages by other factors, such as posts made in a series or
separate blogs on a single installation.

Contents
^^^^^^^^

The part you'll spend most of your time in is the ``contents/`` directory.

The files here define all the pages, blog posts, and other types of content
you'll use on your site. Typically, a page consists of a configuration file
(YAML) and a content file (ReST).

In the example site provided, there is an ``index.yaml`` configuring the
front page, and a pair of files ``first-post.yaml`` and ``first-post.rst``
defining a sample blog post. These are grouped into the bundles ``index``
and ``first-post``.

::

    template: index.j2

In the site configuration we set bundle defaults to render with Jinja2, so
all we need to specify for the front page is the name of the template.

A bigger example is the example blog post, which is actually two files. The
first configures the page (``first-post.yaml``) and the second contains the
contents of the post (``first-post.rst``). The contents are in restructured
text, which is a great mark up language to write plain-text which can be
converted into a number of presentation formats.

Other content formats can be added easily by the plugin architecture, and
more will be included out of the box soon.

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

When you're ready to deploy, your complete website is sitting in ``./_build``
waiting to be copied to your webserver.
