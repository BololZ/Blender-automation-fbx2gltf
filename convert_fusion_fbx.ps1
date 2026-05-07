<#PSScriptInfo
.VERSION 1.0
.GUID a1b2c3d4-e5f6-7890-abcd-ef1234567890
.AUTHOR Eric
.COPYRIGHT
.DESCRIPTION Converts Fusion FBX animations to GLTF2 format
#>

# Fail on error
$ErrorActionPreference = "Stop"

# Get script directory
$DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Check if Blender is available
try {
    Get-Command blender -ErrorAction Stop | Out-Null
} catch {
    Write-Error "ERROR: Blender not found in PATH"
    exit 1
}

# Default values
$BASE = $null
$ANIMATIONS = $null
$OUTPUT = $null

# Parse command line arguments
for ($i = 0; $i -lt $args.Count; $i++) {
    $arg = $args[$i]
    
    switch ($arg) {
        '--base' { $BASE = $args[++$i]; break }
        '-b' { $BASE = $args[++$i]; break }
        '--animations' { $ANIMATIONS = $args[++$i]; break }
        '-a' { $ANIMATIONS = $args[++$i]; break }
        '--output' { $OUTPUT = $args[++$i]; break }
        '-o' { $OUTPUT = $args[++$i]; break }
        default {
            Write-Error "ERROR: Unknown option: $arg"
            Write-Host "Usage: $($MyInvocation.MyCommand.Name) [--base <base.fbx>] --animations <anim1.fbx,anim2.fbx,...> --output <output.glb|output.gltf>"
            Write-Host "  --base is optional (use if animations don't contain mesh)"
            exit 1
        }
    }
}

# Validate required arguments (only --animations and --output are required)
if (-not $ANIMATIONS -or -not $OUTPUT) {
    Write-Error "ERROR: Missing required arguments"
    Write-Host "Usage: $($MyInvocation.MyCommand.Name) [--base <base.fbx>] --animations <anim1.fbx,anim2.fbx,...> --output <output.glb|output.gltf>"
    Write-Host "  --base is optional (use if animations don't contain mesh)"
    exit 1
}

# Validate base file if provided
if ($BASE -and -not (Test-Path $BASE)) {
    Write-Error "ERROR: Base file not found: $BASE"
    exit 1
}

# Validate animation files
if ($ANIMATIONS) {
    $animationFiles = $ANIMATIONS -split ','
    foreach ($file in $animationFiles) {
        $file = $file.Trim()
        if (-not (Test-Path $file)) {
            Write-Error "ERROR: Animation file not found: $file"
            exit 1
        }
    }
}

# Create output directory if it doesn't exist
$OUTPUT_DIR = Split-Path -Parent $OUTPUT
if ($OUTPUT_DIR -and $OUTPUT_DIR -ne "." -and -not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR -Force | Out-Null
}

# Build Blender command arguments
$blenderArgs = @(
    "--background",
    "--addons", "io_scene_gltf2",
    "--python", "$DIR\convert_fusion_fbx.py",
    "--"
)

if ($BASE) { $blenderArgs += "--base", $BASE }
$blenderArgs += "--animations", $ANIMATIONS
$blenderArgs += "--output", $OUTPUT

# Run the conversion
Write-Host "Running Fusion FBX to GLTF2 conversion..."
Write-Host "  Base model: $BASE"
Write-Host "  Animations: $ANIMATIONS"
Write-Host "  Output: $OUTPUT"

try {
    & blender $blenderArgs
    Write-Host "Conversion complete."
} catch {
    Write-Error "ERROR: Blender failed: $($_.Exception.Message)"
    exit 1
}
