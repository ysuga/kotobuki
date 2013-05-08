import sys, os
import yaml, types


def get_home_path():
    if sys.platform == 'darwin':
        return os.environ['HOME'] 
    elif sys.platform == 'win32':
        return os.path.join(os.environ['HOMEDRIVE'] , os.environ['HOMEPATH'])
    return ''

tagdict = {'$HOME': get_home_path()}

rtm_temp = ""
rtm_home = ""

def get_version():
    """Get wasabon version.
    """
    return "0.0.1-2"


def load_settings():
    global rtm_root, rtm_home

    root_dir = os.path.join(__path__[0], 'settings')
    setting = __load_subdir(root_dir)
    
    pathdict = setting['common']['path']
    old_len = len(tagdict)
    while True:
        for key in pathdict:
            pathdict[key] = __replace_tag(pathdict[key])
        __update_tagdict(pathdict)
        if len(tagdict) == old_len:
            break
        old_len = len(tagdict)
    
    __replace_tag_recursive(setting)

    return setting

def __update_tagdict(hash):
    for key in hash.keys():
        if hash[key].find('$') < 0:
            tagdict['$'+key] = hash[key]

def __replace_tag_recursive(hash):
    if type(hash) is types.DictType:
        for key in hash.keys():
            hash[key] = __replace_tag_recursive(hash[key])
        return hash
    elif type(hash) is types.ListType:
        new_hash = []
        for v in hash:
            new_hash.append(__replace_tag_recursive(v))
        return new_hash
    else:
        return __replace_tag(hash)

def __replace_tag(str):
    global tagdict
    for tag in tagdict.keys():
        str = str.replace(tag, tagdict[tag])
    return str

def __parse_yaml(hash):
    for key in hash.keys():
        val = hash[key]
        if type(val) is types.DictType:
            hash[key] = __parse_yaml(val)
        elif type(val) is types.StringType:
            hash[key] = __replace_tags(val)
    return hash

def __load_yaml(file):
    dict = yaml.load(open(file, 'r'))
    if type(dict) == types.NoneType:
        return {}
    return dict
    
def __load_subdir(root):
    ret = {}
    for dir in os.listdir(root):
        path = os.path.join(root, dir)
        if os.path.isdir(path):
            ret[dir] = __load_subdir(path)
        elif os.path.isfile(path):
            if dir.endswith('yaml'):
                ret[dir[:len(dir)-5]] = __load_yaml(path)
    return ret

setting = load_settings()
rtm_home = setting['common']['path']['RTM_HOME']
rtm_temp = setting['common']['path']['RTM_TEMP']

repositories = dict(setting['common']['repository'], **setting[sys.platform]['repository'])

__local_setting_file = os.path.join(rtm_home, 'setting.yaml')
if os.path.isfile(__local_setting_file):
    setting['local'] = yaml.load(open(__local_setting_file, 'r'))

__local_repository_file = os.path.join(rtm_home, 'repository.yaml')
if os.path.isfile(__local_repository_file):
    setting['local_repo'] = yaml.load(open(__local_repository_file, 'r'))
    repositories = dict(repositories, **setting['local_repo'])

__application_setting_file = os.path.join(os.getcwd(), 'setting.yaml')
if os.path.isfile(__application_setting_file):
    appsetting = yaml.load(open(__application_setting_file, 'r'))
    if 'application' in appsetting.keys():
        setting['application'] = appsetting['application']

if 'application' in setting.keys():
    __application_repository_file = os.path.join(os.getcwd(), setting['application']['RTC_DIR'], 'repository.yaml')
    if os.path.isfile(__application_repository_file):
        app_repo = yaml.load(open(__application_repository_file, 'r'))
        setting['app_repo'] = app_repo



