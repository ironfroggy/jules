Template API
============

Within your templates, you'll have access to a few things that let you access
both the current page being rendered and other pages, as well as information
about the site itself.


``bundle``
^^^^^^^^^^

The current page being rendered.

.. automethod:: jules.Bundle.recent

.. automethod:: jules.Bundle.url


``meta``
###############

The configured metadata for the current bundle is available easily.

* ``meta.title``
* ``meta.publish_time``
* ``meta.created_time``
* ``meta.updated_time``
* ``meta.status``
* ``meta.tags``

This is all the data from the bundle's YAML file.

``engine``
^^^^^^^^^^

The Jules "Engine" usde to process and coordinate the website rendering is
available for access to a lot of useful facilities.

.. automethod:: jules.JulesEngine.get_bundles_by

.. automethod:: jules.JulesEngine.get_bundle

Head to the :ref:`API documentation <api-engine>` for everything available here.

``config``
^^^^^^^^^^

The parsed ``site.yaml`` configuration is available from any
template.

``bundles``
^^^^^^^^^^^

All of the bundles on the site are available through the ``bundles`` variable.
