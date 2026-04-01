---
name: blender
description: 3D modeling and rendering via Blender MCP. Use when creating 3D models, architectural visualization, product renders, or any 3D scene. Requires Blender open with MCP addon connected.
allowed-tools: mcp__blender__execute_blender_code, mcp__blender__get_scene_info, mcp__blender__get_object_info, mcp__blender__get_viewport_screenshot, mcp__blender__search_polyhaven_assets, mcp__blender__get_polyhaven_categories, mcp__blender__download_polyhaven_asset, mcp__blender__set_texture, mcp__blender__search_sketchfab_models, mcp__blender__download_sketchfab_model, mcp__blender__get_sketchfab_model_preview, mcp__blender__generate_hyper3d_model_via_text, mcp__blender__generate_hyper3d_model_via_images, mcp__blender__get_hyper3d_status, mcp__blender__import_generated_asset, Read
---

# Blender — 3D Modeling & Rendering

Create 3D scenes, architectural visualizations, and photorealistic renders via Blender MCP.

## Prerequisites

- Blender open with BlenderMCP addon connected (port 9876)
- MCP server configured: `"blender": {"command": "/path/to/uvx", "args": ["blender-mcp"]}`

## Workflow

```
1. get_scene_info          → understand current state
2. execute_blender_code    → create/modify geometry, materials, lights
3. get_viewport_screenshot → verify visually after each major step
4. execute_blender_code    → render to file
5. Read rendered image     → verify final output
```

**Golden rule:** Screenshot after every major operation. Self-correct from what you see.

## API Rules (Blender 4.2+ / 5.x)

### Prefer bpy.data over bpy.ops

```python
# BAD — requires context, breaks in headless/MCP
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# GOOD — direct data manipulation
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
```

### Context override (when bpy.ops is unavoidable)

```python
# Blender 4.x+ — temp_override (dict override is DEPRECATED)
with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
    bpy.ops.object.modifier_apply(modifier="bool_cut")
```

### bmesh for complex geometry

```python
import bmesh
bm = bmesh.new()
# ... create geometry ...
bm.to_mesh(mesh)
bm.free()  # ALWAYS free bmesh
mesh.update()
```

### Version-specific names (Blender 5.x)

| Old Name | New Name (5.x) |
|----------|-----------------|
| `Transmission` | `Transmission Weight` |
| `Specular` | `Specular IOR Level` |
| `BLENDER_EEVEE` | `BLENDER_EEVEE_NEXT` |
| `Fac` (node I/O) | `Factor` |
| `NISHITA` (sky) | `SINGLE_SCATTERING` |
| `WAVE` (texture) | Does NOT exist — use `WOOD` type with `wave_type='BANDS'` |
| `FAST` (boolean solver) | Does NOT exist — use `EXACT` or `FLOAT` |
| `ShaderNodeMixRGB` | `ShaderNodeMix` with `data_type='RGBA'` |
| `noise_threshold` | Use `adaptive_threshold` with `use_adaptive_sampling = True` |
| Filmic (color mgmt) | `AgX` is default in 5.x, Filmic still works |

Check with: `[i.identifier for i in bsdf.inputs]`

### Critical gotcha: film_transparent

```python
# This causes BLACK BACKGROUND in renders — check FIRST
scene.render.film_transparent = False  # Must be False for visible sky
```

## Render Setup

### Cycles (photorealistic)

```python
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.noise_threshold = 0.01  # adaptive sampling

# GPU if available
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'  # macOS. Use CUDA/OPTIX for NVIDIA
for device in prefs.devices:
    device.use = True
scene.cycles.device = 'GPU'

# Color management
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium Contrast'
```

### EEVEE Next (fast preview)

```python
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 64
scene.eevee.use_raytracing = True
scene.eevee.use_shadows = True
```

### Render to file

```python
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "/tmp/render_output.png"
bpy.ops.render.render(write_still=True)
```

**Speed tiers:**
- Preview: 50% resolution, 32 samples, EEVEE
- Draft: 75% resolution, 64 samples, Cycles + denoise
- Final: 100% resolution, 256+ samples, Cycles + denoise

## Camera

```python
import math
from mathutils import Vector

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 28  # 24=wide, 35=standard, 50=portrait, 85=telephoto
cam_data.sensor_width = 36

cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Point at target
cam_obj.location = (x, y, z)
target = Vector((tx, ty, tz))
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
```

## Lighting

### HDRI (best for archviz) — via Poly Haven

```python
# 1. Search
search_polyhaven_assets(asset_type="hdri", categories="outdoor")
# 2. Download
download_polyhaven_asset(asset_id="clarens_midday", asset_type="hdri", resolution="2k")
```

### HDRI via Python (manual)

```python
world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

env = nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load("/path/to/hdri.hdr")

mapping = nodes.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value = (0, 0, rotation_z)

texcoord = nodes.new('ShaderNodeTexCoord')
bg = nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 1.5
output = nodes.new('ShaderNodeOutputWorld')

links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], env.inputs['Vector'])
links.new(env.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
```

### Sky texture (Blender 5.x)

```python
# BEST: Nishita renamed to SINGLE_SCATTERING in 5.x
sky = nodes.new('ShaderNodeTexSky')
sky.sky_type = 'SINGLE_SCATTERING'  # was 'NISHITA' pre-5.0
sky.sun_elevation = math.radians(45)
sky.sun_rotation = math.radians(45)
sky.altitude = 0.0
sky.air_density = 1.0
sky.dust_density = 1.0

# Also available: 'MULTIPLE_SCATTERING' (slower, more accurate)
# Legacy: 'HOSEK_WILKIE', 'PREETHAM'
```

### Gradient sky (procedural, full hemisphere)

For world shaders, use `Normal` output (not Generated). Z goes -1 (nadir) to +1 (zenith).

```python
n_tc = nodes.new('ShaderNodeTexCoord')
n_sep = nodes.new('ShaderNodeSeparateXYZ')
n_mul = nodes.new('ShaderNodeMath'); n_mul.operation = 'MULTIPLY'; n_mul.inputs[1].default_value = 0.5
n_add = nodes.new('ShaderNodeMath'); n_add.operation = 'ADD'; n_add.inputs[1].default_value = 0.5
n_ramp = nodes.new('ShaderNodeValToRGB')

# 0 = nadir (ground), 0.5 = horizon, 1.0 = zenith
n_ramp.color_ramp.elements[0].color = (0.25, 0.22, 0.18, 1)  # ground
n_ramp.color_ramp.elements[1].color = (0.32, 0.52, 0.82, 1)  # zenith
mid = n_ramp.color_ramp.elements.new(0.5)
mid.color = (0.85, 0.82, 0.76, 1)  # bright horizon

links.new(n_tc.outputs['Normal'], n_sep.inputs['Vector'])
links.new(n_sep.outputs['Z'], n_mul.inputs[0])
links.new(n_mul.outputs['Value'], n_add.inputs[0])
links.new(n_add.outputs['Value'], n_ramp.inputs['Factor'])
```

### Three-point lighting

```python
def add_light(name, light_type, location, energy, rotation=None, size=None):
    light_data = bpy.data.lights.new(name, type=light_type)
    light_data.energy = energy
    if size and light_type == 'AREA':
        light_data.size = size
    obj = bpy.data.objects.new(name, light_data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    if rotation:
        obj.rotation_euler = rotation
    return obj

# Key light
add_light("Key", 'AREA', (5, -5, 8), energy=500, size=3,
    rotation=(math.radians(55), 0, math.radians(45)))
# Fill light
add_light("Fill", 'AREA', (-5, -3, 5), energy=150, size=5,
    rotation=(math.radians(60), 0, math.radians(-30)))
# Rim/back light
add_light("Rim", 'AREA', (0, 6, 6), energy=300, size=2,
    rotation=(math.radians(45), 0, math.radians(180)))
```

## Materials

### Principled BSDF template

```python
def create_material(name, **inputs):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    for key, val in inputs.items():
        inp = bsdf.inputs.get(key)
        if inp:
            inp.default_value = val
    return mat

# Examples
steel = create_material("Steel",
    **{"Base Color": (0.6, 0.6, 0.6, 1), "Metallic": 1.0, "Roughness": 0.3})

concrete = create_material("Concrete",
    **{"Base Color": (0.55, 0.52, 0.48, 1), "Roughness": 0.9})

glass = create_material("Glass",
    **{"Base Color": (0.9, 0.95, 1.0, 1), "Transmission Weight": 1.0,
       "IOR": 1.52, "Roughness": 0.02})

wood = create_material("Wood",
    **{"Base Color": (0.4, 0.25, 0.12, 1), "Roughness": 0.7})
```

### Corten steel (realistic oxide mix)

```python
mat = bpy.data.materials.new("Corten")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
output.location = (800, 0)

mix = nodes.new('ShaderNodeMixShader')
mix.location = (600, 0)

# Clean metal
metal = nodes.new('ShaderNodeBsdfPrincipled')
metal.location = (300, 100)
metal.inputs['Base Color'].default_value = (0.4, 0.25, 0.15, 1)
metal.inputs['Metallic'].default_value = 0.9
metal.inputs['Roughness'].default_value = 0.4

# Rust
rust = nodes.new('ShaderNodeBsdfPrincipled')
rust.location = (300, -100)
rust.inputs['Base Color'].default_value = (0.6, 0.15, 0.05, 1)
rust.inputs['Metallic'].default_value = 0.0
rust.inputs['Roughness'].default_value = 0.85

# Noise mask
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-200, -50)
noise.inputs['Scale'].default_value = 8.0
noise.inputs['Detail'].default_value = 6.0
noise.inputs['Roughness'].default_value = 0.7

ramp = nodes.new('ShaderNodeValToRGB')
ramp.location = (100, -50)
ramp.color_ramp.elements[0].position = 0.4
ramp.color_ramp.elements[1].position = 0.7

# Bump
bump = nodes.new('ShaderNodeBump')
bump.location = (100, -200)
bump.inputs['Strength'].default_value = 0.8

texcoord = nodes.new('ShaderNodeTexCoord')
texcoord.location = (-400, 0)

links.new(texcoord.outputs['Object'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(noise.outputs['Fac'], bump.inputs['Height'])
links.new(ramp.outputs['Fac'], mix.inputs['Fac'])
links.new(bump.outputs['Normal'], metal.inputs['Normal'])
links.new(bump.outputs['Normal'], rust.inputs['Normal'])
links.new(metal.outputs['BSDF'], mix.inputs[1])
links.new(rust.outputs['BSDF'], mix.inputs[2])
links.new(mix.outputs['Shader'], output.inputs['Surface'])
```

### Apply PBR textures from Poly Haven

```python
# Search → download → apply
search_polyhaven_assets(asset_type="texture", categories="concrete")
set_texture(object_name="Floor", texture_id="concrete_wall_008")
```

## Geometry Patterns

### Corrugated panel (modifier-based)

```python
def make_corrugated_panel(name, length, height, location, wall_thickness=0.002):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm,
        x_segments=int(length / 0.05),  # enough subdivisions for wave
        y_segments=4,
        size=1.0)
    bmesh.ops.scale(bm, vec=(length, height, 1), verts=bm.verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)

    # Corrugation via displace
    tex = bpy.data.textures.new(f"{name}_wave", type='WAVE')
    tex.wave_type = 'BANDS'
    disp = obj.modifiers.new("corrugated", type='DISPLACE')
    disp.texture = tex
    disp.strength = 0.018
    disp.direction = 'X'
    disp.texture_coords = 'LOCAL'

    # Thickness
    solid = obj.modifiers.new("thickness", type='SOLIDIFY')
    solid.thickness = wall_thickness
    solid.offset = -1.0
    return obj
```

### Boolean cut (windows, doors)

```python
def boolean_cut(target, cutter):
    mod = target.modifiers.new("cut", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    with bpy.context.temp_override(object=target):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
```

### Bevel edges (realistic metal)

```python
mod = obj.modifiers.new("bevel", type='BEVEL')
mod.width = 0.005
mod.segments = 2
mod.limit_method = 'ANGLE'
mod.angle_limit = math.radians(30)
```

## Asset Pipeline

### Poly Haven (free, no API key)

Enable checkbox in Blender N-panel → BlenderMCP.

```
HDRIs:   search → download → auto-applies as world
Textures: search → set_texture → auto-applies PBR maps
Models:  search → download → imports mesh
```

Resolutions: `1k` (fast), `2k` (archviz standard), `4k` (hero textures)

### Sketchfab (needs API key)

Enable + add key in N-panel. Only downloadable models accessible.

```
search_sketchfab_models(query="barcelona chair", downloadable=true)
get_sketchfab_model_preview(uid="abc123")  → verify before downloading
download_sketchfab_model(uid="abc123", normalize_size=true, target_size=1.5)
```

### Hyper3D Rodin (AI model generation)

Async — 3 steps:
```
1. generate_hyper3d_model_via_text(prompt="oak dining table")  → job ID
2. get_hyper3d_status(job_id)  → poll until Done (~2 min)
3. import_generated_asset(task_uuid, name="table")
```

## ArchViz Quality Checklist

### Camera (biggest impact)
```python
cam.data.lens = 40           # 35-55mm only. NEVER wider than 30mm
cam.location.z = 1.6         # eye-level height (human scale)
cam.data.shift_y = 0.1       # correct framing WITHOUT tilting (two-point perspective)
# NEVER rotate camera X to see more building — use shift_y
```

### Micro-bevels (makes metal look real)
```python
mod = obj.modifiers.new("Bevel", type='BEVEL')
mod.width = 0.002       # 2mm for steel beams
mod.segments = 2         # 2 = double highlight = machined metal
mod.limit_method = 'ANGLE'
mod.angle_limit = math.radians(30)
mod.use_clamp_overlap = True
```

### Render settings (5.x optimized)
```python
scene.render.engine = 'CYCLES'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.adaptive_min_samples = 64
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.sample_clamp_indirect = 10  # kill fireflies
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 8
scene.cycles.caustics_reflective = False
scene.render.film_transparent = False  # CRITICAL for visible sky
scene.view_settings.view_transform = 'AgX'  # better than Filmic in 5.x
scene.view_settings.look = 'AgX - Base Contrast'
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `bpy.ops` in loops | Use `bpy.data` direct manipulation |
| Not freeing bmesh | Always call `bm.free()` |
| Wrong Principled BSDF input names | Check `[i.identifier for i in bsdf.inputs]` |
| `sky.sky_type = 'NISHITA'` | Use `'SINGLE_SCATTERING'` (renamed in 5.0) |
| `'WAVE'` texture type | Does not exist — use `'WOOD'` with `wave_type='BANDS'` |
| `'FAST'` boolean solver | Does not exist — use `'EXACT'` |
| `Fac` node socket name | Renamed to `'Factor'` in 5.x |
| `film_transparent = True` | **#1 cause of black background** — set to False |
| Camera too wide (<30mm) | Use 35-55mm for archviz (40mm = sweet spot) |
| Camera tilted up | Use `cam.data.shift_y` instead of rotation |
| TexCoord `Generated` in world shader | Use `Normal` for procedural sky gradients |
| Dark renders | Boost world strength + add fill light + check film_transparent |
| Giant render times | Use adaptive sampling + OIDN denoiser |

## Execution Pattern

Break complex scenes into sequential steps. Never send giant monolithic scripts.

```
Step 1: Clear scene, set units
Step 2: Create base geometry         → screenshot
Step 3: Add details/modifiers        → screenshot
Step 4: Apply materials              → screenshot
Step 5: Set up lighting (HDRI/lamps) → screenshot
Step 6: Position camera              → screenshot
Step 7: Preview render (EEVEE/low)   → verify
Step 8: Final render (Cycles/high)   → deliver
```
