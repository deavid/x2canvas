import sys, os, os.path
# Determine current script directory
SCRIPT_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
LIBRARY_DIR = os.path.realpath(os.path.join(SCRIPT_DIR, "../libraries"))
# Search for libraries . . . 
LIBRARIES = []
for dirname in sorted(os.listdir(LIBRARY_DIR)):
    dirpath = os.path.join(LIBRARY_DIR,dirname)
    if not os.path.isdir(dirpath): continue
    LIBRARIES.append(dirpath)
sys.path[:0] = LIBRARIES 
# ;;

def realdir(*args):
    global SCRIPT_DIR
    path1 = os.path.join(SCRIPT_DIR, *args)
    return os.path.realpath(path1)
