#include "FourRunnerPawn.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Canvas.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace
{
    // Measured tire centers in the prepared asset's forward-X coordinate space.
    const FVector Centers[] = {
        FVector(166.6204, -83.8536, 43.8849), FVector(166.5655, 84.1293, 43.9127),
        FVector(-119.9597, -83.9643, 43.8990), FVector(-120.0146, 84.0186, 43.8990)
    };
    const TCHAR* Corners[] = { TEXT("FL"), TEXT("FR"), TEXT("RL"), TEXT("RR") };
    const FName WheelBones[] = { TEXT("PhysWheel_FL"), TEXT("PhysWheel_FR"), TEXT("PhysWheel_BL"), TEXT("PhysWheel_BR") };
}

UOverlandingFrontWheel::UOverlandingFrontWheel()
{
    WheelRadius = 42.1f;
    WheelWidth = 28.f;
    WheelMass = 30.f;
    AxleType = EAxleType::Front;
    bAffectedBySteering = true;
    bAffectedByEngine = true;
    bAffectedByBrake = true;
    bAffectedByHandbrake = false;
    MaxSteerAngle = 34.f;
    MaxBrakeTorque = 2600.f;
    FrictionForceMultiplier = 2.f;
    SuspensionMaxRaise = 18.f;
    SuspensionMaxDrop = 22.f;
    // Chaos converts this exposed spring value into centimeter force units;
    // use the same scale as its 250 default, rather than SI stiffness here.
    SpringRate = 650.f;
    SpringPreload = 100.f;
    SuspensionDampingRatio = .65f;
    RollbarScaling = .25f;
    SweepType = ESweepType::ComplexSweep;
    bABSEnabled = true;
    bTractionControlEnabled = true;
}

UOverlandingRearWheel::UOverlandingRearWheel()
{
    AxleType = EAxleType::Rear;
    bAffectedBySteering = false;
    bAffectedByHandbrake = true;
    MaxHandBrakeTorque = 4000.f;
}

AFourRunnerPawn::AFourRunnerPawn()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostPhysics;
    auto* Mesh = GetMesh();
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> PhysicsSkeleton(TEXT("/Game/Vehicles/OffroadCar/SKM_Offroad.SKM_Offroad"));
    Mesh->SetSkeletalMesh(PhysicsSkeleton.Object);
    Mesh->SetCollisionProfileName(TEXT("Vehicle"));
    Mesh->SetSimulatePhysics(true);
    Mesh->SetHiddenInGame(true);
    Mesh->SetCastShadow(false);

    Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FourRunnerBody"));
    Body->SetupAttachment(Mesh);
    Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> BodyAsset(TEXT("/Game/Licensed/Toyota4Runner/Prepared/FourRunner_Body/StaticMeshes/FourRunner_Body.FourRunner_Body"));
    Body->SetStaticMesh(BodyAsset.Object);
    for (int Index = 0; Index < 4; ++Index)
    {
        auto* Tire = CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("Tire_%s"), Corners[Index]));
        Tire->SetupAttachment(Mesh);
        Tire->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Tire->SetRelativeLocation(Centers[Index]);
        const FString Path = FString::Printf(TEXT("/Game/Licensed/Toyota4Runner/Prepared/FourRunner_%s/StaticMeshes/FourRunner_%s.FourRunner_%s"), Corners[Index],Corners[Index],Corners[Index]);
        Tire->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*Path));
        TireMeshes.Add(Tire);
    }

    auto* Movement = CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    Movement->Mass = 2200.f;
    Movement->bEnableCenterOfMassOverride = true;
    Movement->CenterOfMassOverride = FVector(15,0,72);
    Movement->bReverseAsBrake = false;
    Movement->WheelSetups.SetNum(4);
    for (int Index = 0; Index < 4; ++Index)
    {
        Movement->WheelSetups[Index].WheelClass = Index<2 ? UOverlandingFrontWheel::StaticClass() : UOverlandingRearWheel::StaticClass();
        Movement->WheelSetups[Index].BoneName = WheelBones[Index];
        const FVector ReferencePosition = PhysicsSkeleton.Object->GetComposedRefPoseMatrix(WheelBones[Index]).GetOrigin();
        Movement->WheelSetups[Index].AdditionalOffset = Centers[Index]-ReferencePosition;
    }
    Movement->EngineSetup.MaxTorque = 450.f;
    Movement->EngineSetup.MaxRPM = 5500.f;
    auto* Torque = Movement->EngineSetup.TorqueCurve.GetRichCurve();
    Torque->AddKey(0,.6f); Torque->AddKey(1500,.85f); Torque->AddKey(3000,1.f); Torque->AddKey(5500,.7f);
    Movement->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
    Movement->DifferentialSetup.FrontRearSplit = .5f;
    Movement->TransmissionSetup.bUseAutomaticGears = true;
    Movement->TransmissionSetup.bUseAutoReverse = false;
    Movement->TransmissionSetup.FinalRatio = 4.1f;
    Movement->TransmissionSetup.ForwardGearRatios = {3.5f,2.1f,1.4f,1.f,.8f};
    Movement->TransmissionSetup.ReverseGearRatios = {3.2f};
    Movement->TransmissionSetup.ChangeUpRPM = 4300.f;
    Movement->TransmissionSetup.ChangeDownRPM = 1800.f;

    ChaseArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("ChaseArm"));
    ChaseArm->SetupAttachment(Mesh);
    ChaseArm->SetRelativeLocation(FVector(0,0,145));
    ChaseArm->SetRelativeRotation(FRotator(-14,0,0));
    ChaseArm->TargetArmLength = 850;
    ChaseArm->bInheritPitch = false;
    ChaseArm->bInheritRoll = false;
    ChaseArm->bEnableCameraLag = true;
    ChaseArm->CameraLagSpeed = 6;
    ChaseArm->bEnableCameraRotationLag = true;
    ChaseArm->CameraRotationLagSpeed = 7;
    ChaseCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ChaseCamera"));
    ChaseCamera->SetupAttachment(ChaseArm, USpringArmComponent::SocketName);
    ChaseCamera->FieldOfView = 75;
}

void AFourRunnerPawn::BeginPlay()
{
    Super::BeginPlay();
    // Reuse Epic's skeleton as a Chaos chassis carrier, with a correctly sized
    // single SUV collision body. No template wheel geometry is rendered.
    auto* Physics = NewObject<UPhysicsAsset>(this);
    auto* Setup = NewObject<USkeletalBodySetup>(Physics);
    Setup->BoneName = GetMesh()->GetSkeletalMeshAsset()->GetRefSkeleton().GetBoneName(0);
    Setup->PhysicsType = PhysType_Simulated;
    Setup->bConsiderForBounds = true;
    Setup->CollisionTraceFlag = CTF_UseSimpleAsComplex;
    FKBoxElem Box;
    Box.Center = FVector(15,0,112);
    Box.X = 465; Box.Y = 195; Box.Z = 135;
    Setup->AggGeom.BoxElems.Add(Box);
    Physics->SkeletalBodySetups.Add(Setup);
    Physics->UpdateBodySetupIndexMap();
    Physics->UpdateBoundsBodiesArray();
    GetMesh()->SetPhysicsAsset(Physics,true);
    GetMesh()->SetSimulatePhysics(true);
    GetVehicleMovementComponent()->RecreatePhysicsState();
    Body->SetHiddenInGame(false);
    for (const auto& Tire : TireMeshes) Tire->SetHiddenInGame(false);
    StartLocation = GetActorLocation();
    StartRotation = GetActorRotation();
    bDriveTest = FParse::Param(FCommandLine::Get(), TEXT("OverlandingDriveTest"));
    if (auto* PC = Cast<APlayerController>(GetController()))
    {
        PC->bShowMouseCursor = true;
        FInputModeGameAndUI InputMode;
        InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        InputMode.SetHideCursorDuringCapture(false);
        PC->SetInputMode(InputMode);
    }
    auto* Movement = CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    UE_LOG(LogTemp,Display,TEXT("FOURRUNNER_READY wheels=%d body=%s simulation=%d physics_wheels=%d output=%d root=%s"),TireMeshes.Num(),Body->GetStaticMesh()?TEXT("loaded"):TEXT("MISSING"),GetMesh()->IsSimulatingPhysics(),Movement->Wheels.Num(),Movement->PhysicsVehicleOutput().IsValid(),*Setup->BoneName.ToString());
}

void AFourRunnerPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    auto* Movement = CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    auto* PC = Cast<APlayerController>(GetController());
    Elapsed += DeltaSeconds;
    float Forward = 0, Turn = 0;
    bool Handbrake = false;
    if (PC)
    {
        Forward = (PC->IsInputKeyDown(EKeys::W)||PC->IsInputKeyDown(EKeys::Up)?1.f:0.f)
                - (PC->IsInputKeyDown(EKeys::S)||PC->IsInputKeyDown(EKeys::Down)?1.f:0.f);
        Turn = (PC->IsInputKeyDown(EKeys::D)||PC->IsInputKeyDown(EKeys::Right)?1.f:0.f)
             - (PC->IsInputKeyDown(EKeys::A)||PC->IsInputKeyDown(EKeys::Left)?1.f:0.f);
        Handbrake = PC->IsInputKeyDown(EKeys::SpaceBar);
        if (PC->WasInputKeyJustPressed(EKeys::Escape))
            UKismetSystemLibrary::QuitGame(this,PC,EQuitPreference::Quit,false);
        if (PC->WasInputKeyJustPressed(EKeys::F10))
            UGameplayStatics::OpenLevel(this,FName(*GetWorld()->GetName()));
    }
    if (bDriveTest)
    {
        Forward = Elapsed>2 && Elapsed<7 ? 1 : (Elapsed>=10 && Elapsed<13 ? -1 : 0);
        // Brief left turn follows the canyon's first bend; a prolonged right
        // turn would intentionally leave the road and test cliff collisions.
        Turn = Elapsed>4 && Elapsed<4.7f ? -.35f : 0;
        Handbrake = (Elapsed>=7 && Elapsed<10) || Elapsed>=13;
    }
    const float Speed = Movement->GetForwardSpeed();
    TestDistance = FMath::Max(TestDistance,static_cast<float>(FVector::Dist2D(StartLocation,GetActorLocation())));
    TestYaw = FMath::Max(TestYaw,FMath::Abs(FMath::FindDeltaAngleDegrees(StartRotation.Yaw,GetActorRotation().Yaw)));
    TestRoll = FMath::Max(TestRoll,FMath::Abs(GetActorRotation().Roll));
    if (bDriveTest && Elapsed>=9 && Elapsed<10) TestStopSpeed = FMath::Abs(Speed);
    if (bDriveTest && Elapsed>=10 && Elapsed<13)
    {
        TestReverseSpeed = FMath::Min(TestReverseSpeed,Speed);
        TestReverseDistance += FMath::Max(0.f,-Speed)*DeltaSeconds;
    }
    const bool ChangingDirection = (Forward>0 && Speed < -30) || (Forward<0 && Speed>30);
    if (Forward!=0 && !ChangingDirection)
        Movement->SetTargetGear(Forward>0 ? FMath::Max(1,Movement->GetCurrentGear()) : -1,true);
    Movement->SetThrottleInput(ChangingDirection?0:FMath::Abs(Forward));
    Movement->SetBrakeInput(ChangingDirection?1.f:0.f);
    Movement->SetHandbrakeInput(Handbrake);
    Steering = FMath::FInterpTo(Steering,Turn,DeltaSeconds,5.f);
    Movement->SetSteeringInput(Steering);
    if (bDriveTest && static_cast<int>(Elapsed)!=LastTestSecond)
    {
        LastTestSecond = static_cast<int>(Elapsed);
        UE_LOG(LogTemp,Display,TEXT("FOURRUNNER_TEST_STEP time=%.1f dt=%.3f speed=%.1f gear=%d target=%d throttle=%.1f yaw=%.1f roll=%.1f z=%.1f"),Elapsed,DeltaSeconds,Speed,Movement->GetCurrentGear(),Movement->GetTargetGear(),Forward,GetActorRotation().Yaw,GetActorRotation().Roll,GetActorLocation().Z);
    }
    if (Movement->PhysicsVehicleOutput() && Movement->Wheels.Num()==4)
    {
        int Contacts = 0;
        for (int Index=0; Index<4; ++Index)
        {
            auto* Wheel = Movement->Wheels[Index].Get();
            const float Spin = Wheel->GetRotationAngle();
            const float Steer = Wheel->GetSteerAngle();
            TireMeshes[Index]->SetRelativeLocation(Centers[Index]+FVector(0,0,Wheel->GetSuspensionOffset()));
            TireMeshes[Index]->SetRelativeRotation(FRotator(Spin,Steer,0));
            TestSpin = FMath::Max(TestSpin,FMath::Abs(Spin));
            TestSteer = FMath::Max(TestSteer,FMath::Abs(Steer));
            if (!Wheel->IsInAir()) ++Contacts;
        }
        TestContacts = FMath::Max(TestContacts,Contacts);
    }
    if (bDriveTest && !bTestComplete && Elapsed>=16)
    {
        bTestComplete = true;
        const float CameraError = FMath::Abs(FMath::FindDeltaAngleDegrees(ChaseArm->GetComponentRotation().Yaw,GetActorRotation().Yaw));
        // The short steering pulse is reduced by the speed-sensitive steering
        // curve. Require both wheel deflection and an actual heading change.
        const bool Passed = TestDistance>300 && TestSpin>45 && TestSteer>2 && TestContacts==4 && TestYaw>5 && TestReverseSpeed < -100 && TestReverseDistance>200 && TestStopSpeed<100 && CameraError<5 && TestRoll<30;
        UE_LOG(LogTemp,Display,TEXT("FOURRUNNER_DRIVE_TEST %s distance_cm=%.1f spin_deg=%.1f steer_deg=%.1f contacts=%d yaw_deg=%.1f reverse_cm_s=%.1f reverse_distance_cm=%.1f stop_cm_s=%.1f camera_error_deg=%.1f max_roll_deg=%.1f"),Passed?TEXT("PASS"):TEXT("FAIL"),TestDistance,TestSpin,TestSteer,TestContacts,TestYaw,TestReverseSpeed,TestReverseDistance,TestStopSpeed,CameraError,TestRoll);
        if (PC) UKismetSystemLibrary::QuitGame(this,PC,EQuitPreference::Quit,false);
    }
}

void AOverlandingHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas) return;
    DrawText(TEXT("OVERLAND XTREME  |  TOYOTA 4RUNNER"),FLinearColor(1,.75,.3),32,28,nullptr,1.3f);
    DrawText(TEXT("W / S or arrows: drive & reverse     A / D: steer     SPACE: handbrake"),FLinearColor::White,32,Canvas->SizeY-64);
    DrawText(TEXT("ESC: exit     F10: restart trail"),FLinearColor::White,32,Canvas->SizeY-40);
    if (auto* Pawn = Cast<AFourRunnerPawn>(GetOwningPawn()))
    {
        auto* Movement = Pawn->GetVehicleMovementComponent();
        DrawText(FString::Printf(TEXT("%.0f MPH   %s"),FMath::Abs(Movement->GetForwardSpeed())*.0223694f,
                 Movement->GetCurrentGear()<0?TEXT("REVERSE"):TEXT("4WD")),FLinearColor::White,32,Canvas->SizeY-110,nullptr,1.6f);
    }
}

AOverlandingGameMode::AOverlandingGameMode()
{
    DefaultPawnClass = AFourRunnerPawn::StaticClass();
    HUDClass = AOverlandingHUD::StaticClass();
}
