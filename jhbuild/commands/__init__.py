# jhbuild - a tool to ease building collections of source packages
# Copyright (C) 2001-2006  James Henstridge
#
#   __init__.py: a package holding the various jhbuild subcommands
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

__metaclass__ = type
__all__ = [
    'Command',
    'register_command',
    'run'
    ]

import optparse
import sys

from jhbuild.errors import UsageError, FatalError


class OptionParser(optparse.OptionParser):
    def exit(self, status=0, msg=None):
        if msg:
            sys.stderr.write(uencode(msg))
        sys.exit(status)


class Command:
    """Base class for Command objects"""

    doc = ''
    name = None
    usage_args = N_('[ options ... ]')

    def __init__(self, options=[]):
        self.options = options

    def execute(self, config, args, help):
        options, args = self.parse_args(args)
        return self.run(config, options, args, help)

    def parse_args(self, args):
        self.parser = OptionParser(
            usage='%%prog %s %s' % (self.name, _(self.usage_args)),
            description=_(self.doc))
        self.parser.add_options(self.options)
        return self.parser.parse_args(args)

    def run(self, config, options, args, help=None):
        """The body of the command"""
        raise NotImplementedError

class BuildCommand(Command):
    """Abstract class for commands that build modules"""

    def required_system_dependencies_installed(self, module_state):
        '''Returns true if all required system dependencies are installed for
        modules in module_state.'''
        for pkg_config,(module, req_version, installed_version, new_enough, required_sysdep) in module_state.iteritems():
            if required_sysdep:
                if installed_version is None or not new_enough:
                    return False
        return True

    def print_system_dependencies(self, module_state):
        print _('Required packages:')
        print _('  System installed packages which are too old:')
        have_too_old = False
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


def print_help():
    import os
    thisdir = os.path.abspath(os.path.dirname(__file__))

    # import all available commands
    for fname in os.listdir(os.path.join(thisdir)):
        name, ext = os.path.splitext(fname)
        if not ext == '.py':
            continue
        try:
            __import__('jhbuild.commands.%s' % name)
        except ImportError:
            pass

    uprint(_('JHBuild commands are:'))
    commands = [(x.name, x.doc) for x in get_commands().values()]
    commands.sort()
    for name, description in commands:
        uprint('  %-15s %s' % (name, description))
    print
    uprint(_('For more information run "jhbuild <command> --help"'))

# handle registration of new commands
_commands = {}
def register_command(command_class):
    _commands[command_class.name] = command_class

# special help command, never run
class cmd_help(Command):
    doc = N_('Information about available jhbuild commands')

    name = 'help'
    usage_args = ''

    def run(self, config, options, args, help=None):
        if help:
            return help()

register_command(cmd_help)


def get_commands():
    return _commands

def run(command, config, args, help):
    # if the command hasn't been registered, load a module by the same name
    if command not in _commands:
        try:
            __import__('jhbuild.commands.%s' % command)
        except ImportError:
            pass
    if command not in _commands:
        import jhbuild.moduleset
        module_set = jhbuild.moduleset.load(config)
        try:
            module_set.get_module(command)
            raise FatalError(_('no such command (did you mean "jhbuild build %s"?)' % command))
        except KeyError:
            raise FatalError(_('no such command (did you mean "jhbuild run %s"?)' % command))

    command_class = _commands[command]

    cmd = command_class()
    return cmd.execute(config, args, help)


from jhbuild.commands import base
