#!/bin/zsh
set -eu
project_dir="${0:A:h}"
engine_bin="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
exec "$engine_bin" "$project_dir/OverlandingXtreme.uproject" /Game/Overlanding/Maps/RedRockRun -game -windowed -ResX=1280 -ResY=720
