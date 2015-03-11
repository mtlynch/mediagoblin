dnl configure.ac
dnl
dnl Copyright 2012, 2013 Brandon Invergo <brandon@invergo.net>
dnl           2014 MediaGoblin contributors (see MediaGoblin's AUTHORS)
dnl
dnl Copying and distribution of this file, with or without modification,
dnl are permitted in any medium without royalty provided the copyright
dnl notice and this notice are preserved.  This file is offered as-is,
dnl without any warranty.

dnl#########
dnl README #
dnl#########
dnl
dnl This is a basic Autoconf configure.ac file for Python-based
dnl projects. It is not intended to be used as-is, but rather to be
dnl modified to the specific needs of the project.
dnl
dnl Lines prefixed with "dnl" are comments that are automatically
dnl removed by Autoconf/M4, thus they will not appear in the generated
dnl configure script (see the M4 documentation for more information). 
dnl Such comments are used in this file to communicate information to 
dnl you, the developer. In some cases, the comments contain extra 
dnl macros that you might consider including in your configure script. 
dnl If you wish to include them, simply remove the "dnl" from the 
dnl beginning of the line.
dnl
dnl Lines prefixed with "#" are comments that will appear in the 
dnl generated configure script. These comments are thus used to clarify
dnl to the user what is happening in that script
dnl
dnl Wherever pyconfigure-specific macros are used, extra comments are
dnl included to describe the macros.

dnl######################
dnl Package Information #
dnl######################

dnl----
dnl Initialize Autoconf with the package metadata
dnl The arguments have been set via the project's PKG-INFO file
dnl and correspond to:
dnl
dnl 1) package name (i.e. foo)
dnl 2) package version (i.e. 1.2)
dnl 3) bug/info/project email address (i.e. bug-foo@gnu.org)
dnl----
dnl

dnl # valid version formats:
dnl # * x.y      - final release
dnl # * x.ya1    - alpha 1
dnl # * x.yb1    - beta 1
dnl # * x.yrc1   - release candidate 1
dnl # * x.y.dev  - dev
dnl 
dnl # see http://www.python.org/dev/peps/pep-0386/

AC_INIT([mediagoblin], [0.8.0.dev], [cwebber@gnu.org])


dnl----
dnl Load macros from the m4/ directory. If you plan to write new 
dnl macros, put them in files in this directory.
dnl----
dnl
dnl AC_CONFIG_MACRO_DIR([m4])


dnl # The default prefix should be changed from /usr/local. Set it, as in
dnl # the documentation, to /srv/mediagoblin.example.org/mediagoblin/
dnl AC_PREFIX_DEFAULT([`pwd`])


dnl###########################
dnl Program/command support  #
dnl###########################
dnl
dnl In this section, we check for the presence of important commands
dnl and programs.

dnl--A bit simpler python init----------------------------------------
dnl Expect python2.7 or python2.6 unless --with-python3 is given.
dnl----


AC_ARG_WITH([python3],
	[AS_HELP_STRING([--with-python3], [Set up to use Python 3 by default.])],
	[],
	[with_python3=no])
AS_IF([test "x$with_python3" != xno],
        AC_CHECK_PROGS([PYTHON], [python3.3], [none])
        AC_SUBST([USE_PYTHON3], [true])
	AS_IF([test "x$PYTHON" = xnone],
              [AC_MSG_FAILURE(
		[--with-python3 given but no acceptable python3 (3.3) could be found])]),
      AC_CHECK_PROGS([PYTHON], [python2.7], [none])
      AC_SUBST([USE_PYTHON3], [false])
      AS_IF([test "x$PYTHON" = xnone],
              [AC_MSG_FAILURE(
		[No acceptable python (2.7) could be found])]))

dnl----
dnl With the following set of macros, we implement an option 
dnl "--with-virtualenv", which the user can pass to the configure 
dnl script in order to install to a Virtualenv (AC_ARG_WITH). If the 
dnl option is specified by the user, then we check if the program is
dnl available, checking both for "virtualenv" and "virtualenv2" 
dnl (AC_CHECK_PROGS)
dnl----
dnl
# Support doing development in a virtualenv via the --with-virtualenv 
# configure flag
AC_ARG_WITH([virtualenv],
	[AS_HELP_STRING([--without-virtualenv], [install to a Python virtualenv])],
	[],
	[with_virtualenv=yes])
AS_IF([test "x$with_virtualenv" != xno],
	    AC_CHECK_PROGS([VIRTUALENV], [virtualenv virtualenv3 virtualenv2], [no])
	    AS_IF([test "x$VIRTUALENV" = xno],
	    [AC_MSG_FAILURE(
		[--with-virtualenv given but virtualenv could not be found])]),
	AC_SUBST([VIRTUALENV], [no]))
AC_ARG_VAR([VIRTUALENV_FLAGS], [flags to pass to the virtualenv command])

dnl----
dnl If the program uses sphinx-build to build documentation, uncomment 
dnl this to create a SPHINXBUILD variable in the Makefile pointing to 
dnl the program. Thus, the user would specify 
dnl SPHINXBUILD=/path/to/sphinx-build as an argument to the configure
dnl script. Since building the documentation should be optional, just
dnl print a warning. If the program uses some other documentation
dnl system, you can do something similar with it.
dnl----
dnl
dnl # Check for sphinx-build
dnl AC_CHECK_PROGS([SPHINXBUILD], [sphinx-build sphinx-build3 sphinx-build2], [no])
dnl AS_IF([test "x$SPHINXBUILD" = xno], 
dnl     AC_MSG_WARN(sphinx-build is required to build documentation))


dnl----
dnl These two are standard Autoconf macros which check for the 
dnl presence of some programs that we will use in the Makefile.
dnl----
dnl
AC_PROG_MKDIR_P
AC_PROG_INSTALL	    

dnl--MediaGoblin specific commands/variables ------------------------


dnl#########
dnl Finish #
dnl#########

dnl Define the files to be configured
AC_CONFIG_FILES([Makefile] [mediagoblin/_version.py])

dnl Generate config.status
AC_OUTPUT
