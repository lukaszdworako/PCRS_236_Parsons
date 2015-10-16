import sys
sys.path.append("/Users/peters43/projects/pcrs/utmandrew/pcrs/")
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pcrs.settings")

from cg_stacktrace import CVisualizer

script = open(sys.argv[1]).read()

cv = CVisualizer('test user', '.')
mod_script = cv.add_printf(script)
print(mod_script)
