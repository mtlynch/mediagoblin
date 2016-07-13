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

Deploy with paste
-----------------

The MediaGoblin WSGI application instance you get with ``./lazyserver.sh`` is
not ideal for a production MediaGoblin deployment. Ideally, you should be able
to use a systemd service file or an init script to launch and restart the
MediaGoblin process.

We will explore setting up MediaGoblin systemd service files and init scripts,
but first we need to create the directory that will store the MediaGoblin logs.


.. _create-log-file-dir:

Create the directory for your log file:
---------------------------------------

Production logs for the MediaGoblin application are kept in the
``/var/log/mediagoblin`` directory.  Create the directory and give it the
proper permissions::

    sudo mkdir -p /var/log/mediagoblin && sudo chown -hR mediagoblin:mediagoblin /var/log/mediagoblin


.. _systemd-service-files:

Use systemd service files
-------------------------

If your operating system uses systemd, you can use systemd ``service files``
to manage both the Celery and Paste processes. Place the following service
files in the ``/etc/systemd/system/`` directory.

The first file should be named ``mediagoblin-celeryd.service``. Be sure to
modify it to suit your environment's setup:

.. code-block:: bash

    # Set the WorkingDirectory, Environment and ExecStart values to match your environment.
    # If using Debian/*buntu, mkdir and chown are located in /bin/mkdir and /bin/chown, respectively.
    # If using Fedora/CentOS/Red Hat, mkdir and chown are located in /usr/bin/mkdir and /usr/bin/chown, respectively.

    [Unit]
    Description=Mediagoblin Celeryd

    [Service]
    User=mediagoblin
    Group=mediagoblin
    Type=simple
    WorkingDirectory=/srv/mediagoblin.example.org/mediagoblin
    # Start mg-celeryd process as root, then switch to mediagoblin user/group
    # (This is needed to run the ExecStartPre commands)
    PermissionsStartOnly=true
    # Create directory for PID (if needed) and set ownership
    ExecStartPre=/bin/mkdir -p /run/mediagoblin
    ExecStartPre=/bin/chown -hR mediagoblin:mediagoblin /run/mediagoblin
    # Celery process will run as the `mediagoblin` user after start.
    Environment=MEDIAGOBLIN_CONFIG=/srv/mediagoblin.example.org/mediagoblin/mediagoblin_local.ini \
                CELERY_CONFIG_MODULE=mediagoblin.init.celery.from_celery
    ExecStart=/srv/mediagoblin.example.org/mediagoblin/bin/celery worker \
                  --logfile=/var/log/mediagoblin/celery.log \
                  --loglevel=INFO
    PIDFile=/run/mediagoblin/mediagoblin-celeryd.pid
    
    [Install]
    WantedBy=multi-user.target


The second file should be named ``mediagoblin-paster.service``:


.. code-block:: bash

    # Set the WorkingDirectory, Environment and ExecStart values to match your environment.
    # If using Debian/*buntu, mkdir and chown are located in /bin/mkdir and /bin/chown, respectively.
    # If using Fedora/CentOS/Red Hat, mkdir and chown are located in /usr/bin/mkdir and /usr/bin/chown, respectively.
    [Unit]
    Description=Mediagoblin
    
    [Service]
    Type=forking
    User=mediagoblin
    Group=mediagoblin
    Environment=CELERY_ALWAYS_EAGER=false
    WorkingDirectory=/srv/mediagoblin.example.org/mediagoblin
    # Start mg-paster process as root, then switch to mediagoblin user/group
    PermissionsStartOnly=true
    ExecStartPre=-/bin/mkdir -p /run/mediagoblin
    ExecStartPre=/bin/chown -hR mediagoblin:mediagoblin /run/mediagoblin
    
    ExecStart=/srv/mediagoblin.example.org/mediagoblin/bin/paster serve \
                  /srv/mediagoblin.example.org/mediagoblin/paste_local.ini \
                  --pid-file=/var/run/mediagoblin/mediagoblin.pid \
                  --log-file=/var/log/mediagoblin/mediagoblin.log \
                  --daemon \
                  --server-name=fcgi fcgi_host=127.0.0.1 fcgi_port=26543
    ExecStop=/srv/mediagoblin.example.org/mediagoblin/bin/paster serve \
                 --pid-file=/var/run/mediagoblin/mediagoblin.pid \
                 /srv/mediagoblin.example.org/mediagoblin/paste_local.ini stop
    PIDFile=/var/run/mediagoblin/mediagoblin.pid
    
    [Install]
    WantedBy=multi-user.target



Enable these processes to start at boot by entering::

    sudo systemctl enable mediagoblin-celeryd.service && sudo systemctl enable mediagoblin-paster.service


Start the processes for the current session with::

    sudo systemctl start mediagoblin-paster.service
    sudo systemctl start mediagoblin-celeryd.service


If either command above gives you an error, you can investigate the cause of
the error by entering::

    sudo systemctl status mediagoblin-celeryd.service  or
    sudo systemctl status mediagoblin-paster.service

The above ``systemctl status`` command is also useful if you ever want to
confirm that a process is still running. If you make any changes to the service
files, you can reload the service files by entering::

    sudo systemctl daemon-reload

After entering that command, you can attempt to start the Celery or Paste
processes again.

.. _init-script:

Use an init script
------------------

If your system does not use systemd, you can use the following command as the
basis for an init script:

.. code-block:: bash

    CELERY_ALWAYS_EAGER=true \
     /srv/mediagoblin.example.org/mediagoblin/bin/paster serve \
     /srv/mediagoblin.example.org/mediagoblin/paste.ini \
     --pid-file=/var/run/mediagoblin.pid \
     --server-name=fcgi fcgi_host=127.0.0.1 fcgi_port=26543

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
     --server-name=fcgi fcgi_host=127.0.0.1 fcgi_port=26543


Members of the MediaGoblin community have provided init scripts for the
following GNU/Linux distributions:

Debian
  * `GNU MediaGoblin init scripts
    <https://github.com/joar/mediagoblin-init-scripts>`_
    by `Joar Wandborg <http://wandborg.se>`_

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

If you use our example systemd ``service files``, Celery will be set to the
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
