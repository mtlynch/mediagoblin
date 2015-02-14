#!/bin/bash

# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2015 GNU MediaGoblin Contributors.  See AUTHORS.
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


set -e

# Make sure we have npm available

if ! which npm > /dev/null; then
    echo "Can't find npm, no way to install extlib :(";
    exit 1;
fi

# Install bower if need be
if which bower > /dev/null; then
    BOWER=`which bower`;
elif [ -f ./node_modules/.bin/bower ]; then
    BOWER="./node_modules/.bin/bower";
else
    echo "Bower not found, installing via npm!";
    npm install bower;
    BOWER="./node_modules/.bin/bower";
fi

# Do package/file installs
$BOWER install
