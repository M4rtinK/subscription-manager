#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
#
# Authors: Jeff Ortel <jortel@redhat.com>
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
#

import sys
sys.path.append("/usr/share/rhsm")

from subscription_manager.certlib import CertLib, ActionLock, ConsumerIdentity
from subscription_manager.repolib import RepoLib
from subscription_manager.factlib import FactLib
from subscription_manager.cache import PackageProfileLib, InstalledProductsLib

import rhsm.connection as connection

import gettext
_ = gettext.gettext


class CertManager:
    """
    An object used to update the certficates, yum repos, and facts for
    the system.

    @ivar certlib: The RHSM I{entitlement} certificate management lib.
    @type certlib: L{CertLib}
    @ivar repolib: The RHSM repository management lib.
    @type repolib: L{RepoLib}
    """

    def __init__(self, lock=ActionLock(), uep=None):
        self.lock = lock
        self.uep = uep
        self.certlib = CertLib(self.lock, uep=self.uep)
        self.repolib = RepoLib(self.lock, uep=self.uep)
        self.factlib = FactLib(self.lock, uep=self.uep)
        self.profilelib = PackageProfileLib(self.lock, uep=self.uep)
        self.installedprodlib = InstalledProductsLib(self.lock, uep=self.uep)

    def update(self):
        """
        Update I{entitlement} certificates and corresponding
        yum repositiories.
        @return: The number of updates required.
        @rtype: int
        """
        updates = 0
        lock = self.lock
        try:
            lock.acquire()
            for lib in (self.repolib, self.factlib, self.profilelib,
                    self.installedprodlib):
                updates += lib.update()

            # WARNING
            # Certlib inherits DataLib as well as the above 'lib' objects,
            # but for some reason it's update method returns a tuple instead
            # of an int:
            ret = self.certlib.update()
            updates += ret[0]
            for e in ret[1]:
                print ' '.join(str(e).split('-')[1:]).strip()
        finally:
            lock.release()
        return updates


def main(autoheal_enabled):
    if not ConsumerIdentity.existsAndValid():
        log.error('Either the consumer is not registered or the certificates' +
                  ' are corrupted. Certificate update using daemon failed.')
        sys.exit(-1)
    print _('Updating entitlement certificates & repositories')
    uep = connection.UEPConnection(cert_file=ConsumerIdentity.certpath(),
                                   key_file=ConsumerIdentity.keypath())
    mgr = CertManager(uep=uep)
    updates = mgr.update()
    print _('%d updates required') % updates
    print _('done')
    if autoheal_enabled:
        log.info("performing autoheal check")
        try:
            sub_cmd = managercli.SubscribeCommand()
            sub_cmd.main(['--auto'])
        except Exception, e:
            # most errors are caught/logged inside SubscribeCommand, this
            # is only for certain edge cases
            log.exception(e)
            log.error("Error while running autoheal check")
        else:
            log.info("autoheal check complete")

# WARNING: This is not a block of code used to test, this module is
# actually run as a script via cron to periodically update the system's
# certificates, yum repos, and facts.
if __name__ == '__main__':
    from subscription_manager import managercli
    import logging
    import logutil
    import rhsm
    from ConfigParser import NoOptionError

    cfg = rhsm.config.initConfig()
    autoheal_enabled = False
    try:
        autoheal_enabled = cfg.getboolean('rhsm', 'autoheal')
    except NoOptionError:
        # if we can't read the autoheal directive, assume False
        pass

    logutil.init_logger()
    log = logging.getLogger('rhsm-app.' + __name__)
    try:
        main(autoheal_enabled)
    except SystemExit:
        # sys.exit triggers an exception in older Python versions, which
        # in this case  we can safely ignore as we do not want to log the
        # stack trace.
        pass
    except Exception, e:
        log.error("Error while updating certificates using daemon")
        print _('Unable to update entitlement certificates & repositories')
        log.exception(e)
        sys.exit(-1)
