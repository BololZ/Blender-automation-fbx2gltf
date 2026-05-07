#!/usr/bin/bash
set -e

# Get the directory of this script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Blender is available
if ! command -v blender &> /dev/null; then
    echo "ERROR: Blender not found in PATH"
    exit 1
fi

# Default values (can be overridden by arguments)
BASE=""
ANIMATIONS=""
OUTPUT=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --base|-b)
            BASE="$2"
            shift 2
            ;;
        --animations|-a)
            ANIMATIONS="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            echo "Usage: $0 --base <base.fbx> --animations <anim1.fbx,anim2.fbx,...> --output <output.glb|output.gltf>"
            exit 1
            ;;
    esac
done

# Validate required arguments (only --animations and --output are required)
if [[ -z "$ANIMATIONS" || -z "$OUTPUT" ]]; then
    echo "ERROR: Missing required arguments"
    echo "Usage: $0 [--base <base.fbx>] --animations <anim1.fbx,anim2.fbx,...> --output <output.glb|output.gltf>"
    echo "  --base is optional (use if animations don't contain mesh)"
    exit 1
fi

# Validate base file if provided
if [[ -n "$BASE" && ! -f "$BASE" ]]; then
    echo "ERROR: Base file not found: $BASE"
    exit 1
fi

# Validate animation files
for file in ${ANIMATIONS//,/ }; do
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Animation file not found: $file"
        exit 1
    fi
done

# Create output directory if it doesn't exist
OUTPUT_DIR="$(dirname "$OUTPUT")"
if [[ ! -d "$OUTPUT_DIR" && "$OUTPUT_DIR" != "." ]]; then
    mkdir -p "$OUTPUT_DIR"
fi

# Run the conversion
echo "Running Fusion FBX to GLTF2 conversion..."
echo "  Base model: $BASE"
echo "  Animations: $ANIMATIONS"
echo "  Output: $OUTPUT"

blender --background --addons io_scene_gltf2 --python "$DIR/convert_fusion_fbx.py" -- \
    --base "$BASE" \
    --animations "$ANIMATIONS" \
    --output "$OUTPUT"

echo "Conversion complete."
