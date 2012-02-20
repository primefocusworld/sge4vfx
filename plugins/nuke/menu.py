#  menu.py
#  sge4vfx
#
#  Created by Stephen Willey on 04/02/2011.
import nuke
import os.path
import sge4vfx_nuke

m = menubar.addMenu("&Render")
if m and not m.findItem("Render on theQ"):
  m.addCommand("-", "", "")
  m.addCommand("Render on theQ", lambda: sge4vfx_nuke.RenderPanel())
