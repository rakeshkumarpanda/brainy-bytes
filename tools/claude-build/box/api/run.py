"""Starts the local stand-in API, then runs the example script exactly as written."""
import runpy
import sys

import standin

standin.start()
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
