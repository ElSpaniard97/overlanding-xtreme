using UnrealBuildTool;
using System.Collections.Generic;
public class OverlandingXtremeEditorTarget : TargetRules
{
    public OverlandingXtremeEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        ExtraModuleNames.Add("OverlandingXtreme");
    }
}
