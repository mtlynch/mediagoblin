.. _openid-chapter:

===================
 OpenID plugin
===================

The OpenID plugin allows user to login to your GNU MediaGoblin instance using
their OpenID URL.

This plugin can be enabled alongside :ref:`basic_auth-chapter` and
:ref:`persona-chapter`.

.. note::
    When :ref:`basic_auth-chapter` is enabled alongside this OpenID plugin, and
    a user creates an account using their OpenID. If they would like to add a
    password to their account, they can use the forgot password feature to do
    so.


Set up the OpenID plugin
============================

1. Install the ``python-openid`` package.

2. Add the following to your MediaGoblin .ini file in the ``[plugins]`` section::

    [[mediagoblin.plugins.openid]]

3. Run::

        gmg dbupdate

   in order to create and apply migrations to any database tables that the
   plugin requires.
