# jhbuild - a tool to ease building collections of source packages
# Copyright (C) 2011 Colin Walters <walters@verbum.org>
#
#   sysdeps.py: Install system dependencies
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from optparse import make_option
import logging

import jhbuild.moduleset
from jhbuild.errors import FatalError
from jhbuild.commands import Command, register_command
from jhbuild.commands.base import cmd_build
from jhbuild.utils.systeminstall import SystemInstall

class cmd_sysdeps(cmd_build):
    doc = N_('Check and install tarball dependencies using system packages')

    name = 'sysdeps'

    def __init__(self):
        Command.__init__(self, [
            make_option('--install',
                        action='store_true', default = False,
                        help=_('Install pkg-config modules via system'))])

    def run(self, config, options, args, help=None):
        config.set_from_cmdline_options(options)

        module_set = jhbuild.moduleset.load(config)
        modules = args or config.modules
        module_list = module_set.get_full_module_list(modules)
        module_state = module_set.get_system_modules(module_list)

        have_new_enough = False
        have_too_old = False

        print _('System installed packages which are new enough:')
        for pkg_config,(module, req_version, installed_version, new_enough, required_sysdep) in module_state.iteritems():
            if (installed_version is not None) and new_enough and (config.partial_build or required_sysdep):
                have_new_enough = True
                print (_("    %(pkg)s (required=%(req)s, installed=%(installed)s)" % {'pkg': pkg_config,
                                                                                      'req': req_version,
                                                                                      'installed': installed_version}))
        if not have_new_enough:
            print _('  (none)')

        print _('Required packages:')
        print _('  System installed packages which are too old:')
        for pkg_config,(module, req_version, installed_version, new_enough, required_sysdep) in module_state.iteritems():
            if (installed_version is not None) and (not new_enough) and required_sysdep:
                have_too_old = True
                print (_("    %(pkg)s (required=%(req)s, installed=%(installed)s)" % {'pkg': pkg_config,
                                                                                      'req': req_version,
                                                                                      'installed': installed_version}))
        if not have_too_old:
            print _('    (none)')

        print _('  No matching system package installed:')
        uninstalled = []
        for pkg_config,(module, req_version, installed_version, new_enough, required_sysdep) in module_state.iteritems():
            if installed_version is None and required_sysdep:
                print (_("    %(pkg)s (required=%(req)s)") % {'pkg': pkg_config,
                                                              'req': req_version})
                uninstalled.append(pkg_config)
        if len(uninstalled) == 0:
            print _('    (none)')

        have_too_old = False

        if config.partial_build:
            print _('Optional packages: (JHBuild will build the missing packages)')
            print _('  System installed packages which are too old:')
            for pkg_config,(module, req_version, installed_version, new_enough, required_sysdep) in module_state.iteritems():
                if (installed_version is not None) and (not new_enough) and (not required_sysdep):
                    have_too_old = True
                    print (_("    %(pkg)s (required=%(req)s, installed=%(installed)s)" % {'pkg': pkg_config,
                                                                                          'req': req_version,
                                                                                          'installed': installed_version}))
            if not have_too_old:
                print _('    (none)')

            print _('  No matching system package installed:')
            for pkg_config,(module, req_version, installed_version, new_enough, required_sysdep) in module_state.iteritems():
                if installed_version is None and (not required_sysdep):
                    print (_("    %(pkg)s (required=%(req)s)") % {'pkg': pkg_config,
                                                                  'req': req_version})
                    uninstalled.append(pkg_config)
            if len(uninstalled) == 0:
                print _('  (none)')

            if options.install:
                installer = SystemInstall.find_best()
                if installer is None:
                    raise FatalError(_("Don't know how to install packages on this system"))

                if len(uninstalled) == 0:
                    logging.info(_("No uninstalled system dependencies to install for modules: %r" % (modules, )))
                else:
                    logging.info(_("Installing dependencies on system: %s" % (' '.join(uninstalled), )))
                    installer.install(uninstalled)

register_command(cmd_sysdeps)
