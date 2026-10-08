using UnrealBuildTool;
public class OverlandingXtreme : ModuleRules
{
    public OverlandingXtreme(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "ChaosVehicles", "PhysicsCore" });
    }
}
