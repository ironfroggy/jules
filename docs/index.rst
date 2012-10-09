.. Jules documentation master file, created by
   sphinx-quickstart on Wed Jun 27 23:16:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Jules's documentation!
=================================

Jules is a static blog generator named after a victorian-ish era literary or
intellectual character, because apparently that's a trend now.

Table of Contents
=================

.. toctree::
   :maxdepth: 1

   getting-started
   api
   template

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
| Your site pack       | site_base             | site_base.j2      |
|                      +-----------------------+-------------------+
|                      | index                 | index.j2          |
|                      +                       +-------------------+
|                      |                       | index.rst         |
|                      +                       +-------------------+
|                      |                       | index.yaml        |
+----------------------+-----------------------+-------------------+

which might render into the a site like:

::

    /
    ├── index.html
    └── js/
        ├── jquery.min.js
        └── less.min.js


