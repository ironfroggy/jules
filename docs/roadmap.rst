Roadmap
=======

Plans
^^^^^

Remove bundle status in favor of using source control branches for drafts

  Instead of trying to maintain status of items to keep unpublished things from hitting the listing pages and feeds, just create a branch and write there. Merge back to master to publish. Jules will assume you keep your site in a good version control system, like Git or Mercurial.

  Possibly this might include optional commands to manage the post branches for you.

Change atom feeds to be explicit

  Rather than add every published page to feeds, I'd like feed items to be added as an explicit action. This allows a few useful features.

  * Published posts that aren't in feeds. Good for archive and index pages
  * Can re-post something to a feed when it gets an update
  * Can control better what contents go into a feed

Changelog
^^^^^^^^^

0.2
###

* Added iso8601 filter for Atom complient datetime formats
* Rendered output is UTF8 allows entities defined in ReST
* When adding bundles, check for duplicates (conflicts between real and implied bundles)
* Updated the starter site to improve formatting
* Allow bundle configurations to be defined for collection/tag pages, as long
  as the bundle key matches.
* Added tox tests to ensure packaging, install, site init, and site building work correctly on 2.7 and 3.2

0.1.1
####

* Documentation improvements

0.1
####

* Initial release

