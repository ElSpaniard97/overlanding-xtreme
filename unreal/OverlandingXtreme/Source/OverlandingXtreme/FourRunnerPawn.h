#pragma once
#include "CoreMinimal.h"
#include "WheeledVehiclePawn.h"
#include "ChaosVehicleWheel.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "FourRunnerPawn.generated.h"

class UStaticMeshComponent;
class USpringArmComponent;
class UCameraComponent;

UCLASS()
class OVERLANDINGXTREME_API UOverlandingFrontWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public:
    UOverlandingFrontWheel();
};

UCLASS()
class OVERLANDINGXTREME_API UOverlandingRearWheel : public UOverlandingFrontWheel
{
    GENERATED_BODY()
public:
    UOverlandingRearWheel();
};

UCLASS()
class OVERLANDINGXTREME_API AFourRunnerPawn : public AWheeledVehiclePawn
{
    GENERATED_BODY()
public:
    AFourRunnerPawn();
    virtual void Tick(float DeltaSeconds) override;
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Body;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<UStaticMeshComponent>> TireMeshes;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> ChaseArm;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> ChaseCamera;
private:
    FVector StartLocation;
    FRotator StartRotation;
    float Steering = 0;
    float Elapsed = 0;
    float TestDistance = 0;
    float TestSteer = 0;
    float TestSpin = 0;
    float TestReverseSpeed = 0;
    float TestReverseDistance = 0;
    float TestStopSpeed = 0;
    float TestYaw = 0;
    float TestRoll = 0;
    int TestContacts = 0;
    int LastTestSecond = -1;
    bool bDriveTest = false;
    bool bTestComplete = false;
};

UCLASS()
class OVERLANDINGXTREME_API AOverlandingHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};

UCLASS()
class OVERLANDINGXTREME_API AOverlandingGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AOverlandingGameMode();
};
