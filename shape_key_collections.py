# TO-DO:
"""
with "All" group selected, show global list of shapekeys for a given object
when assigning a shape key to a group, store the index of the shape key
int he object's key blocks collectionproperty as a "group item"
override the default shape key move up/down functions to also update
the "group item" index
renaming the shape key shouldn't matter in this case
"""

import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel


class MTToolsShapeKeyGroupItem(PropertyGroup):
    # this class holds info on which groups contain which shape key indices
    
    name: StringProperty(
        name="Group Name",
        description="Group name",
        default="",
    )
    
    index: IntProperty()


class MTToolsShapeKeyGroup(PropertyGroup):
    name: StringProperty(
        name="Group Name",
        description="Group name",
        default="",
    )
    
    # index: IntProperty()


class MTToolsShapeKeyGroupUIList(UIList):
    
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        custom_icon = "GROUP"
        # obj = data
        
        # print(index)
        
        # my_index = index
        # print(my_index)
        
        row = layout.row(align=True)
        row.prop(item, "name", icon=custom_icon, emboss=False, text="")
        if item.name != 'All':
            add_op = row.operator("mttools_shape_key_group.assign_to_group", text="", icon="ADD")
            add_op.group_index = index

class MTToolsShapeKeyGroupShapeKeyUIList(UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        custom_icon = 'SHAPEKEY_DATA'

        kbs = data.data.shape_keys.key_blocks
        kb = kbs[item.shape_key]

        row = layout.row()
        row.prop(item, "name", icon=custom_icon, emboss=False, text="")
        row.prop(item, "shape_key", emboss=False, text="")
        row.prop(kb, "name", text="", emboss=False, icon="SHAPEKEY_DATA")
        row.prop(kb, "value", text="", emboss=False)

class MESH_UL_shape_keys_mod_filter(UIList):
    'This is taken and modified from the default UIList definition for shape keys'
    
    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        
        filtered = []
        ordered = []
        
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        
        # data is the mesh object, so this is how you can retrieve the object
        # where the custom properties are stored
        obj = bpy.data.objects[data.user.name]
        # print(obj.mttools_shape_key_group_item.items())
        
        active_group = obj.mttools_shape_key_group_index
        # print(f'active group: {obj.mttools_shape_key_group[active_group].name}, ind: {active_group}')
        
        assignments = [(x[1].name, x[1].index) for x in obj.mttools_shape_key_group_item.items()]

        assignments = [x for x in assignments if x[0] == obj.mttools_shape_key_group[active_group].name]
        # print(assignments)
        assignments_indices = [x[1] for x in assignments]
        # print(assignments_indices)
        
        global_shape_keys = [(kb[0], ind) for ind, kb in enumerate(data.key_blocks.items())]
        global_shape_keys_indices = [x[1] for x in global_shape_keys]
        # print(global_shape_keys_indices)
        
        for x in global_shape_keys_indices:
            if x not in assignments_indices:
                filtered[x] &= ~self.bitflag_filter_item
        
        
        # for x in obj.mttools_shape_key_group_item.items():
        #     print(f'{x}, {x[1].name}, {x[1].index}')
            
        # # the index of a given shape key in the global list and its name
        # for (ind, kb) in enumerate(data.key_blocks.items()):
        #     print(f'{ind} and {kb[0]}')
        
        # assignments = 
        
        # for kb in data.key_blocks.items():
        #     print(kb.name)
        #     pass

        # # filter 1st item test
        # filtered[1] &= ~self.bitflag_filter_item
        # filtered[2] &= ~self.bitflag_filter_item
        
        return filtered, ordered
    
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        # assert(isinstance(item, bpy.types.ShapeKey))
        obj = active_data
        # key = data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.4, align=False)
            split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            row = split.row(align=True)
#            row.emboss = 'NONE_OR_STATUS'
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                split.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text="")
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class MESH_UL_shape_keys_mod(UIList):
    'This is taken and modified from the default UIList definition for shape keys'
    
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        # assert(isinstance(item, bpy.types.ShapeKey))
        obj = active_data
        # key = data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.4, align=False)
            split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            row = split.row(align=True)
#            row.emboss = 'NONE_OR_STATUS'
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                split.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text="")
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class MTToolsShapeKeyGroupAssignToGroup(Operator):
    """Assigns the selected shape key to this group."""
    
    bl_idname = "mttools_shape_key_group.assign_to_group"
    bl_label = "Assign Shape Key to Group"

    group_index: IntProperty(default=0)
    
    def execute(self, context):
        obj = bpy.context.active_object
        
        shape_key_index = obj.active_shape_key_index
        group_index = self.group_index
        
        if shape_key_index == 0:
            print('cannot assign Basis group to shape key group')
            return{'CANCELLED'}
        
        print(f'Shape key: {shape_key_index}, group: {group_index}')
        
        obj = bpy.context.active_object

        current_group_names = [x.name for x in obj.mttools_shape_key_group_item]
        current_group_indices = [x.index for x in obj.mttools_shape_key_group_item]

        name_index = zip(current_group_names, current_group_indices)
        
        if (obj.mttools_shape_key_group[group_index].name, shape_key_index) in name_index:
            print('already assigned')
        else:
            new_group = obj.mttools_shape_key_group_item.add()
            new_group.name = obj.mttools_shape_key_group[group_index].name
            new_group.index = shape_key_index
        
        return {'FINISHED'}


class MTToolsShapeKeyGroupAddGroup(Operator):
    """Adds a new shape key group."""

    bl_idname = "mttools_shape_key_group.add_group"
    bl_label = "Add Shape Key Group"
    
    def execute(self, context):
        
        obj = context.object
        
        num = 1
        groups = [group.name for group in obj.mttools_shape_key_group]
        groups_default_names = [x for x in groups if "Key Group " in x]
        current_indices = [int(x.split()[-1]) for x in groups_default_names]
        
        print(f'Current groups: {groups}')
        
        if current_indices:
            num = max(current_indices) + 1
            
        new_group = context.object.mttools_shape_key_group.add()
        new_group.name = "Key Group " + str(num)
        new_group.index = num

        print(f'Next num value: {num}')
        print("Next group name: Key Group " + str(num))
        
        return{'FINISHED'}


class MTToolsShapeKeyGroupDeleteGroup(Operator):
    """Delete the selected shape key group."""

    bl_idname = "mttools_shape_key_group.delete_group"
    bl_label = "Delete Shape Key Group"

    def execute(self, context):
        obj = context.active_object
        
        index_to_delete = obj.mttools_shape_key_group_index
        group_to_delete = obj.mttools_shape_key_group[index_to_delete].name
        
        # mttools_shape_key_groups = obj.mttools_shape_key_group
        # index = obj.mttools_shape_key_group_index
        if index_to_delete == 0:
            print("don't delete 'ALL'")
            return{'CANCELLED'}

        print(f'delete: group {index_to_delete}')
        print(f'delete: {group_to_delete}')
        
        # mttools_shape_key_groups.remove(index)
        
        assignments = obj.mttools_shape_key_group_item
        remove_list = []
        for ind, x in enumerate(assignments):
            
            if x.name == group_to_delete:
                print(f'DELETE name: {x.name}, index: {x.index}')
                remove_list.append(ind)
            else:
                print(f'KEEP name: {x.name}, index: {x.index}')
                
        print(f'remove_list: {remove_list}')
        
        remove_list.reverse()
        
        print(remove_list)
        
        for x in remove_list:
            obj.mttools_shape_key_group_item.remove(x)
        
        obj.mttools_shape_key_group.remove(index_to_delete)
        
        print(assignments)
        
        # obj.mttools_shape_key_group_index = 
        
        obj.mttools_shape_key_group_index = min(max(0, index_to_delete - 1), len(obj.mttools_shape_key_group) - 1)

        return{'FINISHED'}


class MTToolsShapeKeyGroupPanel(Panel):
    bl_label = "Shape Key Groups"
    bl_idname = "MTTOOLSSHAPEKEYGROUPPANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ""
    bl_category = "MTTools"
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == "MESH" and context.mode == 'OBJECT'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        layout.label(text=obj.name, icon="OUTLINER_OB_MESH")
        col = layout.column()
        row = col.row(align=True)
        row.operator("mttools_shape_key_group.add_group", icon='NEWFOLDER', text="")
        row.operator("mttools_shape_key_group.delete_group", icon='REMOVE', text="")
        col.template_list("MTToolsShapeKeyGroupUIList", "", obj,
            "mttools_shape_key_group", obj, "mttools_shape_key_group_index")
        
        row = layout.row()
        
        key = obj.data.shape_keys
        kb = obj.active_shape_key
        
        if obj.mttools_shape_key_group_index == 0:
            row.template_list("MESH_UL_shape_keys_mod", "", key, "key_blocks", obj, "active_shape_key_index")
        else:
            row.template_list("MESH_UL_shape_keys_mod_filter", "", key, "key_blocks", obj, "active_shape_key_index")
        
        col = row.column()
        
        if obj.mttools_shape_key_group_index != 0:
            col.enabled = False
            
        col.operator("object.shape_key_add", icon='ADD', text="").from_mix = False
        col.operator("object.shape_key_remove", icon='REMOVE', text="").all = False

        col.separator()

        col.menu("MESH_MT_shape_key_context_menu", icon='DOWNARROW_HLT', text="")
        
        kb = obj.active_shape_key
        
        if kb:
            col.separator()

            sub = col.column(align=True)
            sub.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
            sub.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'
        
        
        
        #     enable_edit = obj.mode != 'EDIT'
        #     enable_edit_value = False
        #     enable_pin = False

        #     if enable_edit or (obj.use_shape_key_edit_mode and obj.type == 'MESH'):
        #         enable_pin = True
        #         if obj.show_only_shape_key is False:
        #             enable_edit_value = True

        #     row = layout.row()

        #     rows = 3
        #     if kb:
        #         rows = 5
            
        # else:
            
        #     row.template_list("MTToolsShapeKeyGroupShapeKeyUIList", "", obj,
        #         "mttools_shape_key", obj, "mttools_shape_key_list_index")


classes = [
    MTToolsShapeKeyGroupItem,
    MTToolsShapeKeyGroup,
    MTToolsShapeKeyGroupUIList,
    MTToolsShapeKeyGroupShapeKeyUIList,
    MESH_UL_shape_keys_mod,
    MESH_UL_shape_keys_mod_filter,
    MTToolsShapeKeyGroupAddGroup,
    MTToolsShapeKeyGroupDeleteGroup,
    MTToolsShapeKeyGroupAssignToGroup,
    MTToolsShapeKeyGroupPanel,
]


def initialize_mttools_shape_key_group():
    mesh_objects = [bpy.data.objects[x.name] for x in bpy.data.meshes]

    for obj in mesh_objects:
        if len(obj.mttools_shape_key_group) == 0:
            new_group = obj.mttools_shape_key_group.add()
            new_group.name = "All"


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.mttools_shape_key_group_item = CollectionProperty(type=MTToolsShapeKeyGroupItem)
    bpy.types.Object.mttools_shape_key_group = CollectionProperty(type=MTToolsShapeKeyGroup)
    bpy.types.Object.mttools_shape_key_group_index = IntProperty(name="Active Shape Key Group Index", default=0)


def unregister():
    
    del bpy.types.Object.mttools_shape_key_group_item
    del bpy.types.Object.mttools_shape_key_group
    del bpy.types.Object.mttools_shape_key_group_index
    
    for cls in classes:
        bpy.utils.unregister_class(cls)


register()
initialize_mttools_shape_key_group()  


# if __name__ == "__main__":
#     register()
#     initialize_mttools_shape_key_group()  