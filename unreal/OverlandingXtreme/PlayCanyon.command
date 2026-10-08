#!/bin/zsh
set -eu
project_dir="${0:A:h}"
engine_bin="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
map_path="/Game/Overlanding/Maps/RedRockRun4Runner"
if [[ -f "$project_dir/Content/LocalOnly/Maps/RedRockRun4Runner.umap" ]]; then
  map_path="/Game/LocalOnly/Maps/RedRockRun4Runner"
fi
exec "$engine_bin" "$project_dir/OverlandingXtreme.uproject" "$map_path" -game -windowed -ResX=1280 -ResY=720
