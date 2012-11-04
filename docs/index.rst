.. Jules documentation master file, created by
   sphinx-quickstart on Wed Jun 27 23:16:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Jules!
=================================

Jules is a static blog generator named after a victorian-ish era literary or
intellectual character, because that's a trendy thing to do.

The design is flexible and plugin-oriented. Much of the built-in functionality
is available through a set of plugins, which creates an architecture very prone
to adaptation and customization. One of the major goals (though not yet reached)
is template impartiality.

Today, Jules is a very capable little static website generator you may find
useful for your personal, project, or organization site.

Jules is maintained by `Calvin Spealman <http://www.ironfroggy.com/>`_ (AKA `@ironfroggy <http://twitter.com/ironfroggy>`_)

You can install Jules easily with

.. code-block:: bash

    pip install jules

Which will install the latest version `from PyPI <http://pypi.python.org/pypi/jules>`_.


Table of Contents
=================

.. toctree::
   :maxdepth: 1

   getting-started
   api
   template
   roadmap

Overview
========

Jules one or more input directories (called `packs`), combines groups of files
(`bundles`) which share their base name. For example, "projects.j2" as a template
and "projects.yaml" as data, may be one bundle. These, after processing and
allowing plugins a chance to extend Jules' abilities, are rendered into yhour final
site.

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
| Blog Starter         | index                 | index.j2          |
+----------------------+                       +-------------------+
| Your site pack       |                       | index.yaml        |
|                      +-----------------------+-------------------+
|                      | site_base             | site_base.j2      |
+----------------------+-----------------------+-------------------+

which might render into the a site like:

::

    /
    ├── index.html
    └── js/
        ├── jquery.min.js
        └── less.min.js


:ref:`Get started <getting-started>` making sites easily today.
