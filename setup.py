from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os
import sys
import subprocess

    
# if yaml is not installed, install pyyaml in thirdparty directory
try:
    import yaml
except:
    curdir = os.getcwd()
    if sys.platform == 'win32':
        import urllib
        url = "http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.6.exe"
        filename = os.path.basename(url)
        #wasanbon.util.download(url, dist="thirdparty", force=True)
        file = os.path.join(curdir, 'thirdparty', filename)
        if not os.path.isfile(file):
            class DownloadReport(object):
                def __init__(self):
                    pass
                
                def __call__(self, read_blocks, block_size, total_bytes):
                    end = read_blocks * block_size / float(total_bytes) * 100.0
                    sys.stdout.write('\rProgress %3.2f [percent] ended' % end)
                    sys.stdout.flush()
                    pass

            urllib.urlretrieve(url, file+'.part', DownloadReport())
            os.rename(file+'.part', file)

        os.chdir(os.path.join(curdir, 'thirdparty'))
        subprocess.call([file])
        os.chdir(curdir)
        pass
    else:
        os.chdir(os.path.join(curdir, 'thirdparty', 'PyYAML-3.10'))
        subprocess.call(['python', 'setup.py', 'install'])
        os.chdir(curdir)



class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific fix
    # for this in distutils.command.install_data#306. It fixes install_lib but not
    # install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to the
        # fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
wasanbon_dir = 'wasanbon'

for dirpath, dirnames, filenames in os.walk(wasanbon_dir):
    # Ignore dirnames that start with '.'
    #for i, dirname in enumerate(dirnames):
    #    if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Small hack for working with bdist_wininst.
# See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
    for file_info in data_files:
        file_info[0] = '\\PURELIB\\%s' % file_info[0]

# Dynamically calculate the version based on django.VERSION.
version = __import__('wasanbon').get_version()

scripts = ['wasanbon/bin/wasanbon-admin.py']
if sys.platform == 'win32':
    scripts.append('wasanbon/bin/wasanbon-cd.bat')

setup(
    name = "wasanbon",
    version = version,
    url = 'http://www.sugarsweetrobotics.com/',
    author = 'Sugar Sweet Robotics',
    author_email = 'ysuga@sugarsweetrobotics.com',
    description = '',
    download_url = '',
    packages = packages,
    cmdclass = cmdclasses,
    data_files = data_files,
    scripts = scripts,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: wasanbon',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
   ],
)

try:
    import setuptools
except:
    import wasanbon
    from wasanbon import *
    from wasanbon import util
    from wasanbon.core.management import *
    from wasanbon.core import *
    setting = load_settings()
    util.download_and_install(setting[wasanbon.platform]['packages']['setuptools'],
                              temp=os.getcwd())
    
try:
    import github
except:
    curdir = os.getcwd()
    import subprocess
    os.chdir(os.path.join(curdir, 'thirdparty', 'PyGithub'))
    subprocess.call(['python', 'setup.py', 'install'])
    os.chdir(curdir)

