#! /bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME=jhbuild

(test -f $srcdir/jhbuild/main.py) || {
	echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
	echo " top-level $PKG_NAME directory"
	exit 1
}

which gnome-autogen.sh || {
    echo "Autotools are only used to build documentation"
    echo "Type make -f Makefile.plain to build or install JhBuild"
    echo ""
    echo "If you want to build documentation, you need to install gnome-common"
    echo "from the GNOME Subversion."
    exit 1
}


REQUIRED_AUTOCONF_VERSION=2.57
REQUIRED_AUTOMAKE_VERSION=1.8
REQUIRED_INTLTOOL_VERSION=0.35.0
REQUIRED_PKG_CONFIG_VERSION=0.16.0
USE_GNOME2_MACROS=1 USE_COMMON_DOC_BUILD=yes . gnome-autogen.sh
