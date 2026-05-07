# Fusion FBX to GLTF2 Converter

Convert Fusion 360 FBX animation files to GLTF2 format (GLB/GLTF) using Blender in background mode.

## Overview

This tool converts FBX animation files exported from Fusion 360 into GLTF2 format, combining multiple animation FBX files into a single output file with all animations preserved. It handles FBX version compatibility issues and works with Blender's OpenColorIO fallback mode.

## Features

- Multi-animation merging: Combine multiple FBX animations into one GLTF2 file
- Optional base model: Use separate base mesh or extract from first animation
- Auto FBX conversion: Automatically converts FBX version 6100 to 7100+
- Format flexibility: Output as .glb (binary) or .gltf (text + assets)
- Cross-platform: Works on Linux, macOS, and Windows
- Error handling: Clear error messages with troubleshooting tips
- Temp cleanup: Automatic cleanup of temporary converted files

## Files

| File | Platform | Purpose |
|------|----------|---------|
| convert_fusion_fbx.py | All | Core conversion logic (Blender Python) |
| convert_fusion_fbx.sh | Linux/macOS | Shell wrapper script |
| convert_fusion_fbx.ps1 | Windows | PowerShell wrapper script |

## Requirements

- Blender 5.1+ (tested with Blender 5.1.1)
- glTF2 Addon: io_scene_gltf2 (bundled with Blender)
- Python (included with Blender)

## Installation

No installation required. Simply place all three files in the same directory as your FBX files.

## Usage

### Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| --base / -b | No | Path to base model FBX (optional) |
| --animations / -a | Yes | Comma-separated list of animation FBX files |
| --output / -o | Yes | Output file path (.glb or .gltf) |

### With Base Model (Separate Mesh)

Linux/macOS:
```bash
./convert_fusion_fbx.sh \
    --base character.fbx \
    --animations "idle.fbx,walk.fbx,run.fbx" \
    --output character.glb
```

Windows PowerShell:
```powershell
.\convert_fusion_fbx.ps1 \
    -base character.fbx \
    -animations "idle.fbx,walk.fbx,run.fbx" \
    -output character.glb
```

### Without Base Model (Mesh in Animations)

If your animation FBX files already contain the mesh:

Linux/macOS:
```bash
./convert_fusion_fbx.sh \
    --animations "idle.fbx,walk.fbx,run.fbx" \
    --output character.glb
```

Windows PowerShell:
```powershell
.\convert_fusion_fbx.ps1 \
    -animations "idle.fbx,walk.fbx,run.fbx" \
    -output character.glb
```

## How It Works

1. **FBX Import**: Each FBX file is imported into Blender
2. **Version Handling**: FBX version 6100 files are auto-converted to 7100+
3. **Mesh Handling**: Base model mesh is kept, animation meshes are removed (or first animation's mesh is kept if no base)
4. **Export**: All animations are combined and exported to GLTF2 format
5. **Cleanup**: Temporary converted FBX files are removed

## Output Formats

- **.glb** - Binary GLTF (single file, recommended)
- **.gltf** - Text GLTF (multiple files: JSON + assets)

Format is determined by the file extension in --output argument.

## Troubleshooting

### Blender not found in PATH
Ensure Blender is installed and in your system PATH:
```bash
blender --version
```

### Could not export glTF2
Verify the glTF2 addon exists:
```bash
ls /usr/share/blender/5.1/scripts/addons_core/io_scene_gltf2/
```

### FBX version 6100 unsupported
Handled automatically - the script converts to 7100+.

### OpenColorIO Fallback Mode
Normal with Blender 5.1.1 - script works with fallback mode.

## License

Provided as-is for Fusion 360 FBX to GLTF2 conversion.
