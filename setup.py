#!/usr/bin/python

#
# Copyright (c) 2014 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
from setuptools import setup

setup(name="subscription-manager",
      version='1.12.7',
      url="http://candlepinproject.org",
      description="Manage subscriptions for Red Hat products.",
      license="GPLv2",
      author="Adrian Likins",
      author_email="alikins@redhat.com",
      packages=['src/subscription_manager',
                'src/subscription_manager/gui',
                'src/subscription_manager/plugin',
                'src/subscription_manager/plugin/ostree',
                'src/rhsm_debug',
                'src/rct'],
      test_suite='nose.collector',
      dependency_links=['git+https://github.com/alikins/pyqver.git#egg=pyqver'],
      tests_require=['mock', 'nose', 'coverage',
                     'freezegun', 'polib', 'pep8', 'pyflakes',
                     'pyqver'])
