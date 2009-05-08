import sys,os,string

APPNAME='My Contacts'
VERSION='0.25'
DATE='2nd March 2009'
COPYRIGHT="Copyright \xc2\xa9 2009 Mal Minhas, Oppian Systems Ltd"

GLADEFILE='mycontacts.glade'
HOMEDIR=os.environ.get('HOME')

def determinePlatform():
    """ 1. sys.platform, 2. 'uname -a' """ 
    platform=sys.platform.upper()  # 1. sys.platform: [win32|mac|linux...]
    try:  # 2. "uname -a" using os.system() if it's there
        cmd="uname -a"
        handle=os.popen(cmd,'r')
        unamestr=string.join(handle.readlines())
        handle.close()
        unamestr=unamestr.rstrip('\n')    # IMPORTANT: this is how you chomp in Python
        platform+=" : %s" % unamestr
    except Exception,e:
        print "Exception on uname: %s" % e
    return (os.name,platform)

