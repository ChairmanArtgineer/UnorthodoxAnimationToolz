import bpy
import mathutils
# Set the prefix for the IK bones
ik_bone_prefix = "IK_"

# Set the prefix for the FK bones
fk_bone_prefix = "FK_"




def getPoleBone(ArmatureObject, active):
    #ik constraint bones    
    for bone in ArmatureObject.pose.bones:
        for constraint in bone.constraints:
            if constraint.name == "IK":
                if constraint.subtarget == active:
                    return [bone.parent.name, bone.name,  constraint.subtarget, constraint.pole_subtarget]
                
                
def find_follow(obj,bone):
    """find follow from ik or fk bones"""
    if bone:
        if "IK_" in bone.name or "FK_" in bone.name:
            if bone.name[3:] in obj.pose.bones:
                ogbone = obj.pose.bones[bone.name[3:]]
                if "Follow" in ogbone:
                    return ogbone
    
def ik_to_fk():
        # Loop through each bone in the armature
    armature = bpy.context.active_object
    pbone = armature.pose.bones
    active = bpy.context.active_pose_bone.name
    active = active[len(fk_bone_prefix):]
    active = ik_bone_prefix + active
    ikPoleData = getPoleBone(armature,active)
    ikBone = ikPoleData[1][len(ik_bone_prefix):]
    endBone =  ikPoleData[0][len(ik_bone_prefix):]
    TargetBone = ikPoleData[2][len(ik_bone_prefix):]
    PoleBone = ikPoleData[3][len(ik_bone_prefix):]
    
    
    #get ik triangle in fk bone
    barycenter = (pbone[fk_bone_prefix + endBone].head + pbone[fk_bone_prefix + endBone].tail + pbone[fk_bone_prefix + ikBone].tail)/3 
    fkPole = ( pbone[fk_bone_prefix + endBone].tail - barycenter) * 2 
    #get fk pole vector and convert to matrix
    print(fkPole)
    fkPole =   mathutils.Matrix.Translation(fkPole) @ ( pbone[fk_bone_prefix + ikBone].matrix) 
    pbone[ik_bone_prefix + TargetBone].matrix =  pbone[fk_bone_prefix + TargetBone].matrix
    pbone[ik_bone_prefix + PoleBone].matrix = fkPole
    
    
     
    #print(armature.pose.bones[fk_bone_prefix + ikBone].matrix )
    
        
def fk_to_ik():
    active =  bpy.context.active_pose_bone.name
    active = active[len(fk_bone_prefix):]
    active = ik_bone_prefix + active
    armature = bpy.context.active_object
    IKBones = getPoleBone(armature,active)
    for i in range(3):
       armature.pose.bones[fk_bone_prefix + IKBones[i][len(ik_bone_prefix):]].matrix = armature.pose.bones[IKBones[i]].matrix.copy()
       bpy.context.view_layer.update() 




##/// classes
class OT_Ik_Snap(bpy.types.Operator):
    """snap ik boens to fk """
    bl_idname = "ot.ik_snap"
    bl_label = "Snap ik to fk"

    def execute(self, context):
            ik_to_fk()
            if find_follow(context.object, context.active_pose_bone):
                find_follow(context.object, context.active_pose_bone)["Follow"] = 0.0
                find_follow(context.object, context.active_pose_bone).keyframe_insert('["Follow"]')

            return {'FINISHED'}
class OT_Fk_Snap(bpy.types.Operator):
    """snap fk boens to ik """
    bl_idname = "ot.fk_snap"
    bl_label = "Snap fk to ik"

    def execute(self, context):
            fk_to_ik()
            if find_follow(context.object, context.active_pose_bone):
                find_follow(context.object, context.active_pose_bone)["Follow"] = 1.0
                find_follow(context.object, context.active_pose_bone).keyframe_insert('["Follow"]')

            return {'FINISHED'}
    
class VIEW3D_MT_PIE(bpy.types.Menu):
    # label is displayed at the center of the pie menu.
    
    bl_label = " anim toolkit"
    bl_idname = "VIEW3D_MT_PIE"
    @classmethod
    def poll(cls, context):

        return context.object.mode == 'POSE'
     
    
               
    def draw(self, context):
            
            
            
            layout = self.layout
            
            pie = layout.menu_pie()
            pie = pie.column()
            # operator_enum will just spread all available options
            # for the type enum of the operator on the pie
            if context.selected_pose_bones:
                active = context.active_pose_bone.name
                active_solo = active[len(ik_bone_prefix):]
                active_solo = ik_bone_prefix + active_solo
                print(active_solo)
                armature = context.object
                switch_Bone = getPoleBone(armature, active_solo)
                if switch_Bone == None:
                    pass
                else:
                    if active == switch_Bone[2]:
                        pie.operator('ot.fk_snap', icon = 'EVENT_A', text="switch to ik")
                    if active == (fk_bone_prefix + switch_Bone[2][len(ik_bone_prefix):]):
                        pie.operator('ot.ik_snap', icon = 'EVENT_B', text="switch to fk")
                    #if find_follow(context.object,context.active_pose_bone):
                        #pie.prop(find_follow(context.object,context.active_pose_bone),'["Follow"]',slider= True)


           
            
            
            pie = layout.menu_pie()          
            box = pie.split()
            b = box.box()
            column = b.column()
            self.draw_left_column(bpy.context.scene, b)
            
            b = box.box()
            column = b.column()
            self.draw_center_column(bpy.context.scene, b)

            
            #draw pivor point
    def draw_left_column(self, scene, layout):
        column = layout.column()
        column.label(text="Pivot ")

        column.prop(scene.tool_settings, "transform_pivot_point",text = "", expand=True)
        
        # draw transform type
    def draw_center_column(self, scene, layout):
        slot = scene.transform_orientation_slots[0]
        custom = slot.custom_orientation

        column = layout.column(align=True)
        column.label(text="Orientation")
        column.prop(slot, "type", text = "",expand=True)

        column = layout.column(align=True)
        
        
        
            
   


#####/////
addon_keymaps = []
def register():
    bpy.utils.register_class(VIEW3D_MT_PIE)
    bpy.utils.register_class(OT_Ik_Snap)
    bpy.utils.register_class(OT_Fk_Snap)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc :
        km = kc.keymaps.new(name ='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu_pie", type='E', value = 'PRESS')
        kmi.properties.name = VIEW3D_MT_PIE.bl_idname
        addon_keymaps.append((km,kmi))

def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_PIE)
    bpy.utils.unregister_class(OT_Ik_Snap)
    bpy.utils.unregister_class(OT_Fk_Snap)
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()   





