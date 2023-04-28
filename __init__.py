

bl_info = {
    "name": "unorthodox animation tools",  # The name in the addon search menu
    "author": "chairman xi ",
    "description": "a set of quality of life tools when animating and other bizzarre toughts...",
    "blender": (3, 0, 0),  # Lowest version to use
    "location": "View3D",
    "category": "Animation",
}
import bpy
from . import animationLayers
from . import SemiUniversalSnap


def register():
    animationLayers.register()
    SemiUniversalSnap.register()

def unregister():
    animationLayers.unregister()
    SemiUniversalSnap.unregister()





if __name__ == "__main__":
    register()

