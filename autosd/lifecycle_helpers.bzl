"""Helpers for Lifecycle project integration."""

def lifecycle_py_flatbuffer_library():
    """Generates Python flatbuffer bindings for Lifecycle."""
    native.genrule(
        name = "hm_flatcfg_py",
        srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib/config:hm_flatcfg_fbs"],
        outs = [
            "HMFlatBuffer/__init__.py",
            "HMFlatBuffer/HMEcuCfg.py",
            "HMFlatBuffer/Process.py",
            "HMFlatBuffer/HmProcessExecutionError.py",
            "HMFlatBuffer/HmRefProcessGroupStates.py",
            "HMFlatBuffer/HmRefProcess.py",
            "HMFlatBuffer/HmMonitorInterface.py",
            "HMFlatBuffer/HmSupervisionCheckpoint.py",
            "HMFlatBuffer/HmCheckpointTransition.py",
            "HMFlatBuffer/HmAliveSupervision.py",
            "HMFlatBuffer/HmDeadlineSupervision.py",
            "HMFlatBuffer/HmLogicalSupervision.py",
            "HMFlatBuffer/HmLogicalCheckpoint.py",
            "HMFlatBuffer/HmLogicalTransition.py",
            "HMFlatBuffer/HmLocalSupervision.py",
            "HMFlatBuffer/HmRefAliveSupervision.py",
            "HMFlatBuffer/HmRefDeadlineSupervision.py",
            "HMFlatBuffer/HmRefLogicalSupervision.py",
            "HMFlatBuffer/HmGlobalSupervision.py",
            "HMFlatBuffer/HmGlobalSupervisionLocalRef.py",
            "HMFlatBuffer/HmRefProcessGroupStatesGlobal.py",
            "HMFlatBuffer/RecoveryNotification.py",
        ],
        cmd = "$(location @flatbuffers//:flatc) --python -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib/config:hm_flatcfg_fbs)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.genrule(
        name = "lm_flatcfg_py",
        srcs = ["@score_lifecycle_health//src/launch_manager_daemon/config:lm_flatcfg_fbs"],
        outs = [
            "LMFlatBuffer/__init__.py",
            "LMFlatBuffer/LMEcuCfg.py",
            "LMFlatBuffer/ModeGroup.py",
            "LMFlatBuffer/ModeDeclaration.py",
            "LMFlatBuffer/Process.py",
            "LMFlatBuffer/ProcessStartupConfig.py",
            "LMFlatBuffer/ProcessGroupStateDependency.py",
            "LMFlatBuffer/ProcessExecutionDependency.py",
            "LMFlatBuffer/EnvironmentVariable.py",
            "LMFlatBuffer/ProcessArgument.py",
            "LMFlatBuffer/ProcessSgid.py",
            "LMFlatBuffer/ExecutionStateReportingBehaviorEnum.py",
            "LMFlatBuffer/TerminationBehaviorEnum.py",
        ],
        cmd = "$(location @flatbuffers//:flatc) --python -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/config:lm_flatcfg_fbs)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.genrule(
        name = "hmcore_flatcfg_py",
        srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib/config:hmcore_flatcfg_fbs"],
        outs = [
            "HMCOREFlatBuffer/__init__.py",
            "HMCOREFlatBuffer/HMCOREEcuCfg.py",
            "HMCOREFlatBuffer/Watchdog.py",
            "HMCOREFlatBuffer/HmConfig.py",
        ],
        cmd = "$(location @flatbuffers//:flatc) --python -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib/config:hmcore_flatcfg_fbs)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )
