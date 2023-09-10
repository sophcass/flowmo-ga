# This script can be called to save images without opening Paraview using pvpython
from paraview.simple import *

case = OpenFOAMReader(FileName='testing')

cantilever1foam = GetActiveSource()
renderView1 = GetActiveViewOrCreate('RenderView')
cantilever1foamDisplay = Show(cantilever1foam, renderView1, 'UnstructuredGridRepresentation')
ColorBy(cantilever1foamDisplay, ('POINTS', 'U', 'Magnitude'))
animationScene1 = GetAnimationScene()
animationScene1.GoToLast()
renderView1.InteractionMode = '2D'

Show()
Render()

# Save a screenshot from a specific view.
myview = GetActiveView()
SaveScreenshot("evolution.png", myview)

# Save all views in a tab
#layout = GetLayout()
#SaveScreenshot("allviews.png", layout)

# To save a specific target resolution, rather than using the
# the current view (or layout) size, and override the color palette.
#SaveScreenshot("aviewResolution.png", myview,
                #ImageResolution=[1500, 1500],
                        #OverrideColorPalette="Black Background")

