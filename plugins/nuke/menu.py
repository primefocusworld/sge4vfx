#  menu.py
#  sge4vfx
#
#  Created by Stephen Willey on 04/02/2011.
import nuke
import os.path
import sge4vfx_nuke

m = menubar.addMenu("&Render")
m.addCommand("-", "", "")
m.addCommand("Render on theQ", "sge4vfx_nuke.RenderPanel()")
