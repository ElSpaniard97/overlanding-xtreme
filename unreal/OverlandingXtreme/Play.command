#!/bin/zsh
set -eu
project_dir="${0:A:h}"
engine_bin="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
if [[ ! -x "$engine_bin" ]]; then
  print "Unreal Engine 5.8 is required at /Users/Shared/Epic Games/UE_5.8"
  exit 1
fi
exec "$engine_bin" "$project_dir/OverlandingXtreme.uproject" -game -windowed -ResX=1280 -ResY=720
