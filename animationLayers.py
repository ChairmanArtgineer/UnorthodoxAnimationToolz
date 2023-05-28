import bpy


class ACTION_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "mute", text="", emboss=False, icon='HIDE_OFF' if not item.mute else 'HIDE_ON')
            row.prop(item, "lock", text="", emboss=False, icon='LOCKED' if item.lock else 'UNLOCKED')
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon_value=icon)
            row.prop(item.strips[0], "use_animated_influence", text="", icon='WPAINT_HLT')
            row.prop(item.strips[0], "blend_type", text="")




        elif self.layout_type in {'GRID'}:
            pass

        # upfate the layer list


def update_action_list(self, context):
    obj = bpy.context.object
    nla_tracks = obj.animation_data.nla_tracks
    for track in nla_tracks:
        track.strips[0].action.name = track.name
        if track == nla_tracks[obj.action_list_index]:
            track.select = True
            track.strips[0].select = True

        else:
            track.select = False
            track.strips[0].select = False
        nla_tracks.active = nla_tracks[obj.action_list_index]


# update toggle


def update_function(self, context):
    if self.my_operator_toggle:
        bpy.context.area.type = 'NLA_EDITOR'
        bpy.ops.nla.tweakmode_enter(use_upper_stack_evaluation=True)
        print("enter")
        bpy.context.area.type = 'VIEW_3D'

    else:
        bpy.context.area.type = 'NLA_EDITOR'
        bpy.ops.nla.tweakmode_exit()
        print("exit")
        bpy.context.area.type = 'VIEW_3D'


## tweak action opp


# Define the Blender operator for creating animation layers
class OBJECT_OT_add_animation_layer(bpy.types.Operator):
    """add a new layer to the stack"""
    bl_idname = "object.add_animation_layer"
    bl_label = "Add Animation Layer"
    name: bpy.props.StringProperty(name="NLA Track Name", default="Animation Layer")

    def execute(self, context):
        # Set the active object to the armature
        obj = bpy.context.active_object

        # Create a new action for the NLA track with the track name as the action name
        action = bpy.data.actions.new(self.name)
        obj.animation_data.action = action

        # Create an NLA track
        nla_track = obj.animation_data.nla_tracks.new()
        nla_track.name = self.name

        # Create an action strip for the NLA track
        strip = nla_track.strips.new(self.name, 0, action)
        strip.use_animated_influence = True
        strip.use_sync_length = True
        curFrame = bpy.context.scene.frame_current
        bpy.context.scene.frame_current = 0
        strip.influence = 1
        strip.keyframe_insert(data_path='influence', frame = 0)
        bpy.context.scene.frame_current = curFrame

        # Set the active action to None to avoid conflicts
        bpy.context.object.animation_data.action = None

        return {'FINISHED'}
    ##delete animation layer and its action


class OBJECT_OT_remove_animation_layer(bpy.types.Operator):
    """remove a layer and it's action from the stack"""
    bl_idname = "object.remove_animation_layer"
    bl_label = "remove animation layer"

    def execute(self, context):
        try:
            obj = bpy.context.object
            bpy.data.actions.remove(obj.animation_data.nla_tracks[obj.action_list_index].strips[0].action)
            obj.animation_data.nla_tracks.remove(obj.animation_data.nla_tracks[obj.action_list_index])
        except:
            pass

        return {'FINISHED'}


# Create the Blender panel for the animation layers UI
class OBJECT_PT_animation_layers_panel(bpy.types.Panel):
    bl_label = "Animation Layers"
    bl_idname = "OBJECT_PT_animation_layers_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'animlayer'

    def draw(self, context):

        layout = self.layout
        obj = bpy.context.active_object
        try:
            nla_tracks = obj.animation_data.nla_tracks
            #print("exists")
        except:
            obj.animation_data_create()
            pass

        ## the list
        row = self.layout.row(translate=True)
        row.template_list("ACTION_UL_list", "", bpy.context.object.animation_data, "nla_tracks", obj,
                          "action_list_index")
        ## add and subtract layers
        row = self.layout.row(translate=True)
        row.operator("object.add_animation_layer", text="", icon='ADD')
        bpy.context.view_layer.update()
        row.operator("object.remove_animation_layer", text="", icon='REMOVE')
        ##add layer weight
        try:
            indexStrip = nla_tracks[obj.action_list_index].strips[0]
            if indexStrip.use_animated_influence == True:
                row.prop(indexStrip, "influence", text="weight")
        except:
            pass
        ##tweak toggle
        if len(bpy.context.object.animation_data.nla_tracks) == 0:
            pass
        else:
            wm = context.window_manager
            label = "exit tweak" if wm.my_operator_toggle else "enter tweak"
            layout.prop(wm, 'my_operator_toggle', text=label, toggle=True)

        # Show current action and NLA tracks
        layout.label(
            text="Current Action: " + (obj.animation_data.action.name if obj.animation_data.action else "None"))


# Register the Blender operator and panel


Classes = [
    OBJECT_OT_add_animation_layer,
    OBJECT_PT_animation_layers_panel,
    ACTION_UL_list,
    OBJECT_OT_remove_animation_layer,
]


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_add_animation_layer.bl_idname)


def register():
    bpy.types.Object.action_list_index = bpy.props.IntProperty(update=update_action_list)
    bpy.types.WindowManager.my_operator_toggle = bpy.props.BoolProperty(update=update_function, default=False)
    for cls in Classes:
        bpy.utils.register_class(cls)





def unregister():
    for cls in Classes:
        #del bpy.types.Object.action_list_index
        bpy.utils.unregister_class(cls)


