#!/usr/bin/env python3
"""Convert Fusion FBX animations to GLTF2 format.

Usage:
    blender --background --python convert_fusion_fbx.py \
        --base <base_model.fbx> \
        --animations <anim1.fbx,anim2.fbx,...> \
        --output <output.gltf|output.glb>

Features:
    - Auto-converts FBX version 6100 to 7100+ if needed
    - Merges base model with multiple animations
    - Exports to GLTF2 format (GLB or GLTF)
    - OpenColorIO fallback mode compatible
"""
import bpy
import sys
import os
import argparse
import tempfile
import shutil


def parse_arguments():
    """Parse command line arguments."""
    # Get all arguments after the script name
    try:
        script_index = sys.argv.index(__file__)
    except ValueError:
        script_index = sys.argv.index(os.path.basename(__file__))
    
    raw_args = sys.argv[script_index + 1:]
    
    # Filter out the -- separator and any Blender-specific arguments
    # that might have been passed through
    filtered_args = []
    for arg in raw_args:
        if arg == '--':
            continue
        # Skip Blender-specific -- arguments (not our script args)
        if arg.startswith('--') and not any(
            arg.startswith(f'--{x}') or arg.startswith(f'-{x}')
            for x in ['base', 'animations', 'output', 'b', 'a', 'o']
        ):
            continue
        filtered_args.append(arg)
    
    parser = argparse.ArgumentParser(
        description='Convert Fusion FBX animations to GLTF2 format'
    )
    parser.add_argument(
        '--base', '-b',
        required=False,
        default=None,
        help='Path to base model FBX file (optional if animations contain mesh)'
    )
    parser.add_argument(
        '--animations', '-a',
        required=True,
        help='Comma-separated list of animation FBX files'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file path (.glb or .gltf)'
    )
    return parser.parse_args(filtered_args)


def try_import_fbx(filepath, remove_mesh=False):
    """Try to import an FBX file, auto-converting to 7100+ if version is unsupported.
    
    Args:
        filepath: Path to FBX file
        remove_mesh: If True, remove mesh objects after import (keep armatures/animations)
    
    Returns (success, converted_path_or_original, temp_dir_or_None)
    """
    try:
        bpy.ops.import_scene.fbx(filepath=filepath, use_anim=True)
        
        if remove_mesh:
            # Remove mesh objects, keep armatures and animations
            mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
            for obj in mesh_objects:
                bpy.data.objects.remove(obj)
        
        return True, filepath, None
    except RuntimeError as e:
        error_str = str(e)
        if "Version" in error_str and "unsupported" in error_str:
            # Version issue - convert and retry with converted file
            print(f"  FBX version issue detected in {filepath}, converting to 7100...")
            
            temp_dir = tempfile.mkdtemp(prefix='fbx_convert_')
            temp_path = os.path.join(temp_dir, os.path.basename(filepath) + '.v7100.fbx')
            
            # Clear scene, import old, export as 7100
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.fbx(filepath=filepath, use_anim=True)
            bpy.ops.export_scene.fbx(
                filepath=temp_path,
                version='BINARY_7100',
                use_selection=False,
                bake_space_transform=False
            )
            bpy.ops.wm.read_factory_settings(use_empty=True)
            
            # Import converted file
            bpy.ops.import_scene.fbx(filepath=temp_path, use_anim=True)
            
            if remove_mesh:
                # Remove mesh objects
                mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
                for obj in mesh_objects:
                    bpy.data.objects.remove(obj)
            
            print(f"  Converted {filepath} -> {temp_path}")
            return True, temp_path, temp_dir
        else:
            # Re-raise other errors
            raise


def cleanup_temp_dirs(temp_dirs):
    """Remove temporary directories."""
    for temp_dir in temp_dirs:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"  Warning: Could not clean up temp dir {temp_dir}: {e}")


def export_gltf2(filepath, export_animations=True, export_format='GLB'):
    """Export scene to glTF2 format.
    
    In background mode, addon operators may not be auto-registered.
    Check first, then register if needed.
    """
    
    # Now the operator should be available
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_animations=export_animations,
        export_format=export_format,
        export_current_frame=False,
        export_apply=True
    )


def main():
    """Main conversion pipeline."""
    args = parse_arguments()
    
    print(f"Starting Fusion FBX to GLTF2 conversion...")
    if args.base:
        print(f"  Base model: {args.base}")
    else:
        print(f"  Base model: None (using first animation's mesh)")
    print(f"  Animations: {args.animations}")
    print(f"  Output: {args.output}")
    
    # Split animations list
    animation_files = [a.strip() for a in args.animations.split(',')]
    
    # Validate all files exist
    if args.base and not os.path.exists(args.base):
        print(f"ERROR: Base file not found: {args.base}")
        sys.exit(1)
    
    for f in animation_files:
        if not os.path.exists(f):
            print(f"ERROR: File not found: {f}")
            sys.exit(1)
    
    # Track temp directories for cleanup
    temp_dirs = []
    
    # Clear scene before starting
    print("\nClearing scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import logic: with or without base model
    if args.base:
        # Mode 1: Base model provided
        print(f"\nImporting base model: {args.base}")
        try:
            _, base_path, base_temp_dir = try_import_fbx(args.base, remove_mesh=False)
            if base_temp_dir:
                temp_dirs.append(base_temp_dir)
        except RuntimeError as e:
            print(f"ERROR: Failed to import base model: {e}")
            cleanup_temp_dirs(temp_dirs)
            sys.exit(1)
        
        # Import all animations without mesh
        for anim in animation_files:
            print(f"Importing animation (animations only): {anim}")
            try:
                _, anim_path, anim_temp_dir = try_import_fbx(anim, remove_mesh=True)
                if anim_temp_dir:
                    temp_dirs.append(anim_temp_dir)
            except RuntimeError as e:
                print(f"ERROR: Failed to import animation {anim}: {e}")
                cleanup_temp_dirs(temp_dirs)
                sys.exit(1)
    else:
        # Mode 2: No base model - use first animation's mesh
        if not animation_files:
            print("ERROR: No animations provided and no base model")
            cleanup_temp_dirs(temp_dirs)
            sys.exit(1)
        
        print(f"\nImporting first animation (with mesh): {animation_files[0]}")
        try:
            _, first_anim_path, first_temp_dir = try_import_fbx(animation_files[0], remove_mesh=False)
            if first_temp_dir:
                temp_dirs.append(first_temp_dir)
        except RuntimeError as e:
            print(f"ERROR: Failed to import first animation: {e}")
            cleanup_temp_dirs(temp_dirs)
            sys.exit(1)
        
        # Import remaining animations without mesh
        for anim in animation_files[1:]:
            print(f"Importing animation (animations only): {anim}")
            try:
                _, anim_path, anim_temp_dir = try_import_fbx(anim, remove_mesh=True)
                if anim_temp_dir:
                    temp_dirs.append(anim_temp_dir)
            except RuntimeError as e:
                print(f"ERROR: Failed to import animation {anim}: {e}")
                cleanup_temp_dirs(temp_dirs)
                sys.exit(1)
    
    # Determine output format
    export_format = 'GLB' if args.output.lower().endswith('.glb') else 'GLTF'
    
    # Export as GLTF2
    print(f"\nExporting to: {args.output} (format: {export_format})")
    try:
        export_gltf2(
            filepath=args.output,
            export_animations=True,
            export_format=export_format
        )
    except RuntimeError as e:
        print(f"ERROR: Failed to export GLTF2: {e}")
        cleanup_temp_dirs(temp_dirs)
        sys.exit(1)
    
    # Clean up temporary files
    cleanup_temp_dirs(temp_dirs)
    
    print(f"\nSUCCESS: Created {args.output}")


if __name__ == "__main__":
    main()
