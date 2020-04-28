.. MediaGoblin Documentation

   Written in 2011, 2012, 2013, 2014, 2015 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

=========================================
Considerations for Production Deployments
=========================================

This document contains a number of suggestions for deploying
MediaGoblin in actual production environments. Consider
":doc:`deploying`" for a basic overview of how to deploy MediaGoblin.


Should I Keep Open Registration Enabled?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unfortunately, in this current release of MediaGoblin we are suffering
from spammers registering to public instances en masse.  As such, you
may want to either:

a) Disable registration on your instance and just make
   accounts for people you know and trust (eg via the `gmg adduser`
   command).  You can disable registration in your mediagoblin.ini
   like so::

     [mediagoblin]
     allow_registration = false

b) Enable a CAPTCHA plugin.  But unfortunately, though some CAPTCHA
   plugins exist, for various reasons we do not have any general
   recommendations we can make at this point.

We hope to have a better solution to this situation shortly.  We
apologize for the inconvenience in the meanwhile.


Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   The directory ``user_dev/crypto/`` contains some very
   sensitive files.
   Especially the ``itsdangeroussecret.bin`` is very important
   for session security. Make sure not to leak its contents anywhere.
   If the contents gets leaked nevertheless, delete your file
   and restart the server, so that it creates a new secret key.
   All previous sessions will be invalidated.


.. _init-script:

Alternative init scripts
------------------------

If your system does not use Systemd, you can use the following command as the
basis for an init script:

.. code-block:: bash

    CELERY_ALWAYS_EAGER=true \
     /srv/mediagoblin.example.org/mediagoblin/bin/paster serve \
     /srv/mediagoblin.example.org/mediagoblin/paste.ini \
     --pid-file=/var/run/mediagoblin.pid \
     --server-name=main

The above configuration places MediaGoblin in "always eager" mode
with Celery, this means that submissions of content will be processed
synchronously, and the user will advance to the next page only after
processing is complete. If we take Celery out of "always eager mode,"
the user will be able to immediately return to the MediaGoblin site
while processing is ongoing. In these cases, use the following command
as the basis for your script:

.. code-block:: bash

    CELERY_ALWAYS_EAGER=false \
     /srv/mediagoblin.example.org/mediagoblin/bin/paster serve \
     /srv/mediagoblin.example.org/mediagoblin/paste.ini \
     --pid-file=/var/run/mediagoblin.pid \
     --server-name=main


Members of the MediaGoblin community have provided init scripts for the
following GNU/Linux distributions:

Arch Linux
  * `MediaGoblin - ArchLinux rc.d scripts
    <http://whird.jpope.org/2012/04/14/mediagoblin-archlinux-rcd-scripts>`_
    by `Jeremy Pope <http://jpope.org/>`_
  * `Mediagoblin init script on Archlinux
    <http://chimo.chromic.org/2012/03/01/mediagoblin-init-script-on-archlinux/>`_
    by `Chimo <http://chimo.chromic.org/>`_

You can reference these scripts to create an init script for your own operating
system. Similar scripts will be in your system's ``/etc/init.d/``
or ``/etc/rc.d/`` directory, but the specifics of an init script will vary from
one distribution to the next.


Separate celery
---------------

":doc:`deploying`" describes a configuration with a separate Celery process, but
the following section covers this in more detail.

MediaGoblin uses `Celery`_ to handle heavy and long-running tasks. Celery can
be launched in two ways:

1.  Embedded in the MediaGoblin WSGI application [#f-mediagoblin-wsgi-app]_.
    This is the way ``./lazyserver.sh`` does it for you. It's simple as you
    only have to run one process. The only bad thing with this is that the
    heavy and long-running tasks will run *in* the webserver, keeping the user
    waiting each time some heavy lifting is needed as in for example processing
    a video. This could lead to problems as an aborted connection will halt any
    processing and since most front-end web servers *will* terminate your
    connection if it doesn't get any response from the MediaGoblin WSGI
    application in a while.

2.  As a separate process communicating with the MediaGoblin WSGI application
    via a `broker`_. This offloads the heavy lifting from the MediaGoblin WSGI
    application and users will be able to continue to browse the site while the
    media is being processed in the background.

.. _`broker`: http://docs.celeryproject.org/en/latest/getting-started/brokers/
.. _`celery`: http://www.celeryproject.org/


.. [#f-mediagoblin-wsgi-app] The MediaGoblin WSGI application is the part that
    of MediaGoblin that processes HTTP requests.

To launch Celery separately from the MediaGoblin WSGI application:

1.  Make sure that the ``CELERY_ALWAYS_EAGER`` environment variable is unset or
    set to ``false`` when launching the MediaGoblin WSGI application.
2.  Start the ``celeryd`` main process with

    .. code-block:: bash

        CELERY_CONFIG_MODULE=mediagoblin.init.celery.from_celery ./bin/celeryd

If you use our example Systemd ``service files``, Celery will be set to the
"CELERY_ALWAYS_EAGER=false" value by default. This will provide your users
with the best user experience, as all media processing will be done in the
background.

.. _sentry:


Set up sentry to monitor exceptions
-----------------------------------

We have a plugin for `raven`_ integration, see the ":doc:`/plugindocs/raven`"
documentation.

.. _`raven`: http://raven.readthedocs.org


.. TODO insert init script here
.. TODO are additional concerns ?
   .. Other Concerns
   .. --------------
