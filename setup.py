# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

from setuptools import setup, find_packages
from io import open
import os
import re

import sys

PY2 = sys.version_info[0] == 2  # six is not installed yet

READMEFILE = "README"
VERSIONFILE = os.path.join("mediagoblin", "_version.py")
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"


def get_version():
    with open(VERSIONFILE, "rt") as fobj:
        verstrline = fobj.read()
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." %
                           VERSIONFILE)

pyversion_install_requires = []
if PY2:
    pyversion_install_requires.append('alabaster<=0.7.999') # Tested with 0.7.12
    pyversion_install_requires.append('alembic<=1.4.999') # Tested with 1.4.2
    pyversion_install_requires.append('amqp<=2.5.999') # Tested with 2.5.2
    pyversion_install_requires.append('apipkg<=1.999') # Tested with 1.5
    pyversion_install_requires.append('atomicwrites<=1.4.999') # Tested with 1.4.0
    pyversion_install_requires.append('attrs<=19.3.999') # Tested with 19.3.0
    pyversion_install_requires.append('Babel<=2.8.999') # Tested with 2.8.0
    pyversion_install_requires.append('beautifulsoup4<=4.7.999') # Tested with 4.7.1
    pyversion_install_requires.append('billiard<=3.5.0.999') # Tested with 3.5.0.5
    pyversion_install_requires.append('celery<=4.2.999') # Tested with 4.2.2
    pyversion_install_requires.append('certifi<=2020.4.5.999') # Tested with 2020.4.5.1
    pyversion_install_requires.append('chardet<=3.0.999') # Tested with 3.0.4
    pyversion_install_requires.append('configobj<=5.0.999') # Tested with 5.0.6
    pyversion_install_requires.append('configparser<=5.0.999') # Tested with 5.0.0
    pyversion_install_requires.append('contextlib2<=0.6.999') # Tested with 0.6.0.post1
    pyversion_install_requires.append('decorator<=4.4.999') # Tested with 4.4.2
    pyversion_install_requires.append('dnspython<=1.16.999') # Tested with 1.16.0
    pyversion_install_requires.append('docutils<=0.999') # Tested with 0.16
    pyversion_install_requires.append('email-validator<=1.0.999') # Tested with 1.0.5
    pyversion_install_requires.append('execnet<=1.7.999') # Tested with 1.7.1
    pyversion_install_requires.append('ExifRead<=2.1.999') # Tested with 2.1.2
    pyversion_install_requires.append('funcsigs<=1.0.999') # Tested with 1.0.2
    pyversion_install_requires.append('functools32<=3.2.999') # Tested with 3.2.3.post2
    pyversion_install_requires.append('idna<=2.999') # Tested with 2.9
    pyversion_install_requires.append('imagesize<=1.2.999') # Tested with 1.2.0
    pyversion_install_requires.append('importlib-metadata<=1.6.999') # Tested with 1.6.0
    pyversion_install_requires.append('itsdangerous<=1.1.999') # Tested with 1.1.0
    pyversion_install_requires.append('Jinja2<=2.11.999') # Tested with 2.11.2
    pyversion_install_requires.append('jsonschema<=3.2.999') # Tested with 3.2.0
    pyversion_install_requires.append('kombu<=4.3.999') # Tested with 4.3.0
    pyversion_install_requires.append('Mako<=1.1.999') # Tested with 1.1.2
    pyversion_install_requires.append('Markdown<=3.1.999') # Tested with 3.1.1
    pyversion_install_requires.append('MarkupSafe<=1.1.999') # Tested with 1.1.1
    pyversion_install_requires.append('mock<=1.0.999') # Tested with 1.0.1
    pyversion_install_requires.append('more-itertools<=5.0.999') # Tested with 5.0.0
    pyversion_install_requires.append('oauthlib<=3.1.999') # Tested with 3.1.0
    pyversion_install_requires.append('packaging<=20.999') # Tested with 20.3
    pyversion_install_requires.append('Paste<=3.4.999') # Tested with 3.4.0
    pyversion_install_requires.append('PasteDeploy<=2.1.999') # Tested with 2.1.0
    pyversion_install_requires.append('PasteScript<=3.2.999') # Tested with 3.2.0
    pyversion_install_requires.append('pathlib2<=2.3.999') # Tested with 2.3.5
    pyversion_install_requires.append('pbr<=5.4.999') # Tested with 5.4.5
    pyversion_install_requires.append('pkg-resources<=0.0.999') # Tested with 0.0.0
    pyversion_install_requires.append('pluggy<=0.13.999') # Tested with 0.13.1
    pyversion_install_requires.append('py<=1.8.999') # Tested with 1.8.1
    pyversion_install_requires.append('py-bcrypt<=0.999') # Tested with 0.4
    pyversion_install_requires.append('Pygments<=2.5.999') # Tested with 2.5.2
    pyversion_install_requires.append('PyLD<=1.0.999') # Tested with 1.0.5
    pyversion_install_requires.append('pyparsing<=2.4.999') # Tested with 2.4.7
    pyversion_install_requires.append('pyrsistent<=0.16.999') # Tested with 0.16.0
    pyversion_install_requires.append('pytest<=4.6.999') # Tested with 4.6.9
    pyversion_install_requires.append('pytest-forked<=1.1.999') # Tested with 1.1.3
    pyversion_install_requires.append('pytest-xdist<=1.31.999') # Tested with 1.31.0
    pyversion_install_requires.append('python-dateutil<=2.8.999') # Tested with 2.8.1
    pyversion_install_requires.append('python-editor<=1.0.999') # Tested with 1.0.4
    pyversion_install_requires.append('pytz<=2020.999') # Tested with 2020.1
    pyversion_install_requires.append('requests<=2.23.999') # Tested with 2.23.0
    pyversion_install_requires.append('scandir<=1.10.999') # Tested with 1.10.0
    pyversion_install_requires.append('six<=1.12.999') # Tested with 1.12.0
    pyversion_install_requires.append('snowballstemmer<=2.0.999') # Tested with 2.0.0
    pyversion_install_requires.append('Sphinx<=1.8.999') # Tested with 1.8.5
    pyversion_install_requires.append('sphinxcontrib-websupport<=1.2.999') # Tested with 1.2.2
    pyversion_install_requires.append('SQLAlchemy<=1.3.999') # Tested with 1.3.16
    pyversion_install_requires.append('sqlalchemy-migrate<=0.13.999') # Tested with 0.13.0
    pyversion_install_requires.append('sqlparse<=0.3.999') # Tested with 0.3.1
    pyversion_install_requires.append('Tempita<=0.5.999') # Tested with 0.5.3.dev0
    pyversion_install_requires.append('typing<=3.7.4.999') # Tested with 3.7.4.1
    pyversion_install_requires.append('Unidecode<=1.1.999') # Tested with 1.1.1
    pyversion_install_requires.append('urllib3<=1.25.999') # Tested with 1.25.9
    pyversion_install_requires.append('vine<=1.3.999') # Tested with 1.3.0
    pyversion_install_requires.append('waitress<=1.4.999') # Tested with 1.4.3
    pyversion_install_requires.append('wcwidth<=0.1.999') # Tested with 0.1.9
    pyversion_install_requires.append('WebOb<=1.8.999') # Tested with 1.8.6
    pyversion_install_requires.append('WebTest<=2.0.999') # Tested with 2.0.35
    pyversion_install_requires.append('Werkzeug<=0.16.999') # Tested with 0.16.1
    pyversion_install_requires.append('WTForms<=2.3.999') # Tested with 2.3.1
    pyversion_install_requires.append('zipp<=1.2.999') # Tested with 1.2.0

install_requires = [
    'waitress',
    'alembic>=0.7.5',
    'python-dateutil',
    'wtforms',
    'py-bcrypt',
    'pytest>=2.3.1',
    'pytest-xdist',
    'werkzeug>=0.7,<1.0.0',
    # Celery 4.3.0 drops the "sqlite" transport alias making our tests fail.
    'celery>=3.0,<4.3.0',
    # Jinja2 3.0.0 uses f-strings (Python 3.7 and above) but `pip install` on
    # Debian 9 doesn't seem to respect Jinja2's 'python_requires=">=3.6"' line.
    'jinja2<3.0.0',
    'Babel>=1.3',
    'WebTest>=2.0.18',
    'ConfigObj',
    'Markdown',
    'sqlalchemy',
    'itsdangerous',
    'pytz',
    'sphinx',
    'six>=1.11.0',
    'oauthlib',
    'unidecode',
    'jsonschema',
    'PasteDeploy',
    'PasteScript',
    'requests>=2.6.0',
    'PyLD<2.0.0', # Python 2, but also breaks a Python 3 test if >= 2.0.0.
    'ExifRead>=2.0.0',
    'email-validator', # Seems that WTForms must have dropped this.
    # This is optional:
    # 'translitcodec',
    # For now we're expecting that users will install this from
    # their package managers.
    # 'lxml',
    # 'Pillow',
] + pyversion_install_requires

if not PY2:
    # PyPI version (1.4.2) does not have proper Python 3 support
    install_requires.append('ExifRead>=2.0.0')

with open(READMEFILE, encoding="utf-8") as fobj:
    long_description = fobj.read()

try:
    setup(
    name="mediagoblin",
    version=get_version(),
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    zip_safe=False,
    include_package_data = True,
    # scripts and dependencies
    install_requires=install_requires,
    test_suite='nose.collector',
    entry_points="""\
        [console_scripts]
        gmg = mediagoblin.gmg_commands:main_cli

        [paste.app_factory]
        app = mediagoblin.app:paste_app_factory

        [paste.server_runner]
        paste_server_selector = mediagoblin.app:paste_server_selector

        [paste.filter_app_factory]
        errors = mediagoblin.errormiddleware:mgoblin_error_middleware

        [zc.buildout]
        make_user_dev_dirs = mediagoblin.buildout_recipes:MakeUserDevDirs

        [babel.extractors]
        jinja2 = jinja2.ext:babel_extract
        """,
    license='AGPLv3',
    author='Free Software Foundation and contributors',
    author_email='cwebber@gnu.org',
    url="http://mediagoblin.org/",
    long_description=long_description,
    description='MediaGoblin is a web application for publishing all kinds of media',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
        ],
    )
except TypeError as e:
    import sys

    # Check if the problem is caused by the sqlalchemy/setuptools conflict
    msg_as_str = str(e)
    if not (msg_as_str == 'dist must be a Distribution instance'):
        raise

    # If so, tell the user it is OK to just run the script again.
    print("\n\n---------- NOTE ----------", file=sys.stderr)
    print("The setup.py command you ran failed.\n", file=sys.stderr)
    print("It is a known possible failure. Just run it again. It works the "
          "second time.", file=sys.stderr)
    sys.exit(1)
