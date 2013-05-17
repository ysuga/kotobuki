import os, sys, time, subprocess
from rtshell import rtstart, rtresurrect

import wasanbon

def start_cpp_rtcd():
    cpp_env = os.environ.copy()

    if sys.platform == 'win32':
        return subprocess.Popen(['rtcd', '-f', 'conf/rtc_cpp.conf'], env=cpp_env, creationflags=512)
    else:
        return subprocess.Popen(['rtcd', '-f', 'conf/rtc_cpp.conf'], env=cpp_env)


def start_python_rtcd():
    py_env = os.environ.copy()
    if sys.platform == 'win32':
        for path in sys.path:
            if os.path.isfile(os.path.join(path, 'python.exe')):
                cmd = os.path.join(path, 'python.exe')
                file = os.path.join(path, 'rtcd.py')
        p = subprocess.Popen([cmd, file, '-f', 'conf/rtc_py.conf'], env=py_env, creationflags=512, stdin=subprocess.PIPE)
        p.stdin.write('N')
        return p
    else:
        return subprocess.Popen(['rtcd_python', '-f', 'conf/rtc_py.conf'], env=py_env)
 

def start_java_rtcd():
    rtm_java_classpath = os.path.join(wasanbon.rtm_home, 'jar')
    java_env = os.environ.copy()
    if not "CLASSPATH" in java_env.keys():
        java_env["CLASSPATH"]='.'
    if sys.platform == 'win32':
        sep = ';'
    else:
        sep = ':'
    for jarfile in os.listdir(rtm_java_classpath):
        java_env["CLASSPATH"]=java_env["CLASSPATH"] + sep + os.path.join(rtm_java_classpath, jarfile)
    if sys.platform == 'win32':
        return subprocess.Popen([wasanbon.setting['local']['java'], 'rtcd.rtcd', '-f', 'conf/rtc_java.conf'], env=java_env, creationflags=512)
    else:
        return subprocess.Popen([wasanbon.setting['local']['java'], 'rtcd.rtcd', '-f', 'conf/rtc_java.conf'], env=java_env)


def exe_rtresurrect():
    while True:
        ret =  rtresurrect.main([wasanbon.setting['application']['system']])
        if ret == 0:
            break
        time.sleep(1)

def cmd_rtresurrect():
    if sys.platform == 'win32':
        cmd = ['rtresurrect.bat', wasanbon.setting['application']['system']]
    else:
        cmd = ['rtresurrect', wasanbon.setting['application']['system']]
    while True:
        p = subprocess.Popen(cmd)
        if p.wait() == 0:
            break;
        time.sleep(1)

def exe_rtstart():
    while True:
        ret =  rtstart.main([wasanbon.setting['application']['system']])
        if ret == 0:
            break
        time.sleep(1)

def cmd_rtstart():

    if sys.platform == 'win32':
        cmd = ['rtstart.bat', wasanbon.setting['application']['system']]
    else:
        cmd = ['rtstart', wasanbon.setting['application']['system']]
        
    while True:
        p = subprocess.Popen(cmd)
        if p.wait() == 0:
            break;
        time.sleep(1)

