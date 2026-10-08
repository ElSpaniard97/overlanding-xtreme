using UnrealBuildTool;
using System.Collections.Generic;
public class OverlandingXtremeTarget : TargetRules
{
    public OverlandingXtremeTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        ExtraModuleNames.Add("OverlandingXtreme");
    }
}
