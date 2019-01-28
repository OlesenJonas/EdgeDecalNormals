bl_info = {
    "name": "Edge Decal Mesh Normals",
    "description": "Generate Normals for Edge Decal Meshes",
    "author": "Jonas Olesen",
    "version": (1,0),
    "blender": (2, 80, 0),
    "location": "3D View > Toolbar",
    "category": "Object",
}

import bpy
import bmesh
from mathutils import Vector


class clearCustomNormals(bpy.types.Operator):
    """Clear Custom Normal Data"""
    bl_idname = "edit.clearcustomnorm"
    bl_label = "Clear Custom Normals"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode == "EDIT" and context.object.type == "MESH"

    def execute(self, context):
        mesh = bpy.context.object.data
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        mesh.use_auto_smooth = False
        return {"FINISHED"}

class DecalNormalOperator(bpy.types.Operator):
    """Creates Normals for Edge Decal Meshes"""
    bl_idname = "edit.decalnormals"
    bl_label = "Edge Decal Normals"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode == "EDIT" and context.object.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')

        mesh = bpy.context.object.data

        bm = bmesh.new()
        bm.from_mesh(mesh)


        #make list with length as loops in mesh
        def amountLoops(mesh):
            sum = 0
            for face in mesh.faces:
                for loop in face.loops:
                    sum += 1
            return sum

        customNormals = [Vector([0,0,0])]*amountLoops(bm) #initialize empty new list

        selectedVerts = []
        for vert in bm.verts:
            if vert.select:
                selectedVerts.append([vert,vert.normal])   

        for vertAndNormal in selectedVerts:
            vert = vertAndNormal[0]
            cnormal = vertAndNormal[1]
            for edge in vert.link_edges:
                vert2 = edge.other_vert(vert)
                for loop in vert2.link_loops:
                    customNormals[loop.index] = cnormal
                    
        for vertAndNormal in selectedVerts:
            for loop in vertAndNormal[0].link_loops:
                customNormals[loop.index] = vertAndNormal[1]


        bm.free()
        mesh.use_auto_smooth = True
        bpy.ops.mesh.customdata_custom_splitnormals_clear()

        bpy.ops.mesh.customdata_custom_splitnormals_add()
        mesh.normals_split_custom_set(customNormals)
        mesh.free_normals_split()
        return {'FINISHED'}

class customNormalPanel(bpy.types.Panel):
    bl_label = "Edge Decal Normals"
    bl_idname = "VIEW3D_OT_Normaltools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode == "EDIT" and context.object.type == "MESH"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text=" Simple Row:")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("edit.decalnormals")
        row = layout.row()
        row.operator("edit.clearcustomnorm")

classes = (
    DecalNormalOperator,
    clearCustomNormals,
    customNormalPanel
)

def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.packbefore


if __name__ == '__main__':
    register()
