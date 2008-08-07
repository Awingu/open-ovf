"""Open-ovf installer"""

import os
from distutils.core import setup

CODE_BASE_DIR = 'py'
SCRIPTS_DIR = 'py/scripts/'

def list_scripts():
    """List all scripts that should go to /usr/bin"""

    file_list = os.listdir(SCRIPTS_DIR)
    return [os.path.join(SCRIPTS_DIR, f) for f in file_list]

setup(name='open-ovf',
        version='0.1',
        description='OVF implementation',
        url='http://open-ovf.sourceforge.net',
        license='EPL',
        packages=['ovf', 'ovf.commands'],
        package_dir = {'': CODE_BASE_DIR},
        scripts=list_scripts(),
      )

