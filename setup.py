#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
Explicitly typed attributes for Python.

The Traits project is at the center of all Enthought Tool Suite development
and has changed the mental model used at Enthought for programming in the
already extremely efficient Python programming language. We encourage everyone
to join us in enjoying the productivity gains from using such a powerful
approach.

The Traits project allows Python programmers to use a special kind of type
definition called a *trait*, which gives object attributes some additional
characteristics:

- **Initialization**: A trait has a *default value*, which is
  automatically set as the initial value of an attribute before its
  first use in a program.
- **Validation**: A trait attribute's type is *explicitly declared*. The
  type is evident in the code, and only values that meet a
  programmer-specified set of criteria (i.e., the trait definition) can
  be assigned to that attribute.
- **Delegation**: The value of a trait attribute can be contained either
  in the defining object or in another object *delegated* to by the
  trait.
- **Notification**: Setting the value of a trait attribute can *notify*
  other parts of the program that the value has changed.
- **Visualization**: User interfaces that allow a user to *interactively
  modify* the value of a trait attribute can be automatically
  constructed using the trait's definition. (This feature requires that
  a supported GUI toolkit be installed. If this feature is not used, the
  Traits project does not otherwise require GUI support.)

A class can freely mix trait-based attributes with normal Python attributes,
or can opt to allow the use of only a fixed or open set of trait attributes
within the class. Trait attributes defined by a classs are automatically
inherited by any subclass derived from the class.
"""


import os, zipfile
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import DistributionNotFound, parse_version, require, VersionConflict

from setup_data import INFO
from make_docs import HtmlBuild


ctraits = Extension(
    'enthought.traits.ctraits',
    sources = ['enthought/traits/ctraits.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )
speedups = Extension(
    'enthought.traits.protocols._speedups',
    # fixme: Use the generated sources until Pyrex 0.9.6 and setuptools can play
    # with each other. See #1364
    sources = ['enthought/traits/protocols/_speedups.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Methods to allow us to dynamically build html docs from RST sources.
def generate_docs():
    """ If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = doc_dir

    required_sphinx_version = "0.4.1"
    sphinx_installed = False
    try:
        require("Sphinx>=%s" % required_sphinx_version)
        sphinx_installed = True
    except (DistributionNotFound, VersionConflict):
        log.warn('Sphinx install of version %s could not be verified.'
                    ' Trying simple import...' % required_sphinx_version)
        try:
            import sphinx
            if parse_version(sphinx.__version__) < parse_version(required_sphinx_version):
                log.error("Sphinx version must be >=%s." % required_sphinx_version)
            else:
                sphinx_installed = True
        except ImportError:
            log.error("Sphnix install not found.")

    if sphinx_installed:
        log.info("Generating %s documentation..." % INFO['name'])
        docsrc = source_dir
        target = dest_dir

        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': docsrc,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False
                }, [])
            del build

        except:
            log.error("The documentation generation failed.  Falling back to "
                      "the zip file.")

            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, doc_dir)
    else:
        # Unzip the docs into the 'html' folder.
        log.info("Installing %s documentaion from zip file.\n" % INFO['name'])
        unzip_html_docs(html_zip, doc_dir)

def unzip_html_docs(src_path, dest_dir):
    """ Given a path to a zipfile, extract its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
        else:
            if not os.path.exists(cur_name):
                os.mkdir(cur_name)
    file.close()

class my_develop(develop):
    def run(self):
        develop.run(self)
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        generate_docs()


# Call the setup function.
setup(
    author = 'David C. Morrill, et. al.',
    author_email = 'dmorrill@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: C
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines()],
    cmdclass = {
        'develop': my_develop,
        'build': my_build
        },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = DOCLINES[1],
    extras_require = INFO['extras_require'],
    ext_modules = [ctraits, speedups],
    include_package_data = True,
    install_requires = INFO['install_requires'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'Traits',
    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
        ],
    packages = find_packages(exclude = [
        'docs',
        'docs.*',
        'integrationtests',
        'integrationtests.*',
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/traits',
    version = INFO['version'],
    zip_safe = False,
    )

