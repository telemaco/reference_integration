#! /usr/bin/env python3

import flatbuffers
import argparse
import json

from LMFlatBuffer import (
    LMEcuCfg,
    Process,
    ProcessStartupConfig,
    ProcessGroupStateDependency,
    ProcessExecutionDependency,
    EnvironmentVariable,
    ProcessArgument,
    ProcessSgid,
    ModeGroup,
    ModeDeclaration,
)


def create_process_argument(builder, arg):
    argument = builder.CreateString(arg)
    ProcessArgument.Start(builder)
    ProcessArgument.AddArgument(builder, argument)
    return ProcessArgument.End(builder)


def create_environment_variable(builder, key, value):
    key_str = builder.CreateString(key)
    value_str = builder.CreateString(value)
    EnvironmentVariable.Start(builder)
    EnvironmentVariable.AddKey(builder, key_str)
    EnvironmentVariable.AddValue(builder, value_str)
    return EnvironmentVariable.End(builder)


def create_process_group_state_dependency(builder, state_machine_name, state_name):
    sm_name = builder.CreateString(state_machine_name)
    s_name = builder.CreateString(state_name)
    ProcessGroupStateDependency.Start(builder)
    ProcessGroupStateDependency.AddStateMachineName(builder, sm_name)
    ProcessGroupStateDependency.AddStateName(builder, s_name)
    return ProcessGroupStateDependency.End(builder)


def create_process_execution_dependency(builder, state_name, target_process_identifier):
    s_name = builder.CreateString(state_name)
    tp_id = builder.CreateString(target_process_identifier)
    ProcessExecutionDependency.Start(builder)
    ProcessExecutionDependency.AddStateName(builder, s_name)
    ProcessExecutionDependency.AddTargetProcessIdentifier(builder, tp_id)
    return ProcessExecutionDependency.End(builder)


def create_startup_config(builder, pg_name, proc_index):
    identifier_offset = builder.CreateString(f"demo_app_startup_config_{proc_index}")

    # ExecutionError, SchedulingPolicy, SchedulingPriority strings created before Start
    execution_error_offset = builder.CreateString("1")
    scheduling_policy_offset = builder.CreateString("SCHED_OTHER")
    scheduling_priority_offset = builder.CreateString("0")

    # Environment Variables
    env_vars = [
        create_environment_variable(builder, "LD_LIBRARY_PATH", "/usr/lib"),
        create_environment_variable(
            builder, "PROCESSIDENTIFIER", f"{pg_name}_app{proc_index}"
        ),
        create_environment_variable(
            builder,
            "CONFIG_PATH",
            f"/etc/score-lifecycle-health/health_monitor_process_cfg_{proc_index}_{pg_name}.bin",
        ),
    ]
    ProcessStartupConfig.StartEnvironmentVariableVector(builder, len(env_vars))
    for var in reversed(env_vars):
        builder.PrependUOffsetTRelative(var)
    env_vars_vector = builder.EndVector()

    # Process Arguments
    args = [
        create_process_argument(builder, f"-sdemo/demo_application{proc_index}/Port1")
    ]
    ProcessStartupConfig.StartProcessArgumentVector(builder, len(args))
    for arg in reversed(args):
        builder.PrependUOffsetTRelative(arg)
    args_vector = builder.EndVector()

    # Process Group State Dependencies
    pg_deps = [
        create_process_group_state_dependency(builder, pg_name, f"{pg_name}/Startup")
    ]
    ProcessStartupConfig.StartProcessGroupStateDependencyVector(builder, len(pg_deps))
    for dep in reversed(pg_deps):
        builder.PrependUOffsetTRelative(dep)
    pg_deps_vector = builder.EndVector()

    # Execution Dependencies
    exec_deps = [
        create_process_execution_dependency(
            builder, "Running", "/healthmonitorApp/healthmonitor"
        )
    ]
    ProcessStartupConfig.StartExecutionDependencyVector(builder, len(exec_deps))
    for dep in reversed(exec_deps):
        builder.PrependUOffsetTRelative(dep)
    exec_deps_vector = builder.EndVector()

    ProcessStartupConfig.Start(builder)
    ProcessStartupConfig.AddIdentifier(builder, identifier_offset)
    ProcessStartupConfig.AddExecutionError(builder, execution_error_offset)
    ProcessStartupConfig.AddSchedulingPolicy(builder, scheduling_policy_offset)
    ProcessStartupConfig.AddSchedulingPriority(builder, scheduling_priority_offset)
    ProcessStartupConfig.AddEnterTimeoutValue(builder, 2000)
    ProcessStartupConfig.AddExitTimeoutValue(builder, 2000)
    ProcessStartupConfig.AddTerminationBehavior(
        builder, 0
    )  # ProcessIsNotSelfTerminating
    ProcessStartupConfig.AddEnvironmentVariable(builder, env_vars_vector)
    ProcessStartupConfig.AddProcessArgument(builder, args_vector)
    ProcessStartupConfig.AddProcessGroupStateDependency(builder, pg_deps_vector)
    ProcessStartupConfig.AddExecutionDependency(builder, exec_deps_vector)
    return ProcessStartupConfig.End(builder)


def create_process(builder, pg_name, proc_index):
    identifier_offset = builder.CreateString(f"demo_app{proc_index}_{pg_name}")
    path_offset = builder.CreateString("/usr/bin/cpp_supervised_app")

    startup_configs = [create_startup_config(builder, pg_name, proc_index)]
    Process.StartStartupConfigVector(builder, len(startup_configs))
    for config in reversed(startup_configs):
        builder.PrependUOffsetTRelative(config)
    startup_configs_vector = builder.EndVector()

    Process.Start(builder)
    Process.AddIdentifier(builder, identifier_offset)
    Process.AddUid(builder, 0)
    Process.AddGid(builder, 0)
    Process.AddPath(builder, path_offset)
    Process.AddNumberOfRestartAttempts(builder, 0)
    Process.AddExecutableReportingBehavior(builder, 0)  # ReportsExecutionState
    Process.AddStartupConfig(builder, startup_configs_vector)
    return Process.End(builder)


def create_control_daemon_process(builder):
    identifier_offset = builder.CreateString("control_daemon")
    path_offset = builder.CreateString("/usr/bin/control_daemon")
    function_cluster_affiliation_offset = builder.CreateString("STATE_MANAGEMENT")

    # Startup Config
    startup_config_identifier_offset = builder.CreateString(
        "control_daemon_startup_config"
    )
    execution_error_offset = builder.CreateString("1")
    scheduling_policy_offset = builder.CreateString("SCHED_OTHER")
    scheduling_priority_offset = builder.CreateString("0")

    # Env Vars
    env_vars = [
        create_environment_variable(builder, "LD_LIBRARY_PATH", "/usr/lib"),
        create_environment_variable(builder, "PROCESSIDENTIFIER", "control_daemon"),
    ]
    ProcessStartupConfig.StartEnvironmentVariableVector(builder, len(env_vars))
    for var in reversed(env_vars):
        builder.PrependUOffsetTRelative(var)
    env_vars_vector = builder.EndVector()

    # PG State Deps
    pg_deps = [
        create_process_group_state_dependency(builder, "MainPG", "MainPG/Startup"),
        create_process_group_state_dependency(builder, "MainPG", "MainPG/Recovery"),
    ]
    ProcessStartupConfig.StartProcessGroupStateDependencyVector(builder, len(pg_deps))
    for dep in reversed(pg_deps):
        builder.PrependUOffsetTRelative(dep)
    pg_deps_vector = builder.EndVector()

    ProcessStartupConfig.Start(builder)
    ProcessStartupConfig.AddIdentifier(builder, startup_config_identifier_offset)
    ProcessStartupConfig.AddExecutionError(builder, execution_error_offset)
    ProcessStartupConfig.AddSchedulingPolicy(builder, scheduling_policy_offset)
    ProcessStartupConfig.AddSchedulingPriority(builder, scheduling_priority_offset)
    ProcessStartupConfig.AddEnterTimeoutValue(builder, 1000)
    ProcessStartupConfig.AddExitTimeoutValue(builder, 1000)
    ProcessStartupConfig.AddTerminationBehavior(
        builder, 0
    )  # ProcessIsNotSelfTerminating
    ProcessStartupConfig.AddProcessGroupStateDependency(builder, pg_deps_vector)
    ProcessStartupConfig.AddEnvironmentVariable(builder, env_vars_vector)
    startup_config = ProcessStartupConfig.End(builder)

    Process.StartStartupConfigVector(builder, 1)
    builder.PrependUOffsetTRelative(startup_config)
    startup_config_vector = builder.EndVector()

    Process.Start(builder)
    Process.AddIdentifier(builder, identifier_offset)
    Process.AddUid(builder, 0)
    Process.AddGid(builder, 0)
    Process.AddPath(builder, path_offset)
    Process.AddFunctionClusterAffiliation(builder, function_cluster_affiliation_offset)
    Process.AddNumberOfRestartAttempts(builder, 0)
    Process.AddExecutableReportingBehavior(builder, 0)  # ReportsExecutionState
    Process.AddStartupConfig(builder, startup_config_vector)
    return Process.End(builder)


def create_mode_declaration(builder, identifier_name, _):
    identifier = builder.CreateString(identifier_name)
    ModeDeclaration.Start(builder)
    ModeDeclaration.AddIdentifier(builder, identifier)
    return ModeDeclaration.End(builder)


def create_mode_group(
    builder, group_identifier, initial_mode_name, initial_mode_value, mode_declarations
):
    identifier = builder.CreateString(group_identifier)
    initial_mode_name_str = builder.CreateString(initial_mode_name)
    initial_mode_value_str = builder.CreateString(initial_mode_value)

    ModeGroup.StartModeDeclarationVector(builder, len(mode_declarations))
    for mode in reversed(mode_declarations):
        builder.PrependUOffsetTRelative(mode)
    mode_declarations_vector = builder.EndVector()

    ModeGroup.Start(builder)
    ModeGroup.AddIdentifier(builder, identifier)
    ModeGroup.AddInitialModeName(builder, initial_mode_name_str)
    ModeGroup.AddInitialModeValue(builder, initial_mode_value_str)
    ModeGroup.AddModeDeclaration(builder, mode_declarations_vector)
    return ModeGroup.End(builder)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Launch Manager Configuration Flatbuffer."
    )
    parser.add_argument(
        "output_filepath", help="Path to the output Flatbuffer binary file."
    )
    parser.add_argument(
        "--process-groups",
        required=True,
        type=str,
        help="A JSON string of process groups to configure.",
    )
    args = parser.parse_args()

    output_filepath = args.output_filepath
    process_groups = json.loads(args.process_groups)

    builder = flatbuffers.Builder(1024)

    process_offsets = []

    # Add control_daemon process
    process_offsets.append(create_control_daemon_process(builder))

    proc_index = 0
    for pg_name, pg_data in process_groups.items():
        for i in range(pg_data["process_num"]):
            process_offsets.append(create_process(builder, pg_name, proc_index))
            proc_index += 1

    LMEcuCfg.StartProcessVector(builder, len(process_offsets))
    for offset in reversed(process_offsets):
        builder.PrependUOffsetTRelative(offset)
    process_vector = builder.EndVector()

    # Mode Declarations
    mode_declarations = [create_mode_declaration(builder, "VehicleState", "Running")]

    # Mode Groups
    mode_groups = [
        create_mode_group(
            builder, "VehicleMode", "VehicleState", "Running", mode_declarations
        )
    ]
    LMEcuCfg.StartModeGroupVector(builder, len(mode_groups))
    for group in reversed(mode_groups):
        builder.PrependUOffsetTRelative(group)
    mode_group_vector = builder.EndVector()

    LMEcuCfg.Start(builder)
    LMEcuCfg.AddVersionMajor(builder, 7)
    LMEcuCfg.AddVersionMinor(builder, 0)
    LMEcuCfg.AddProcess(builder, process_vector)
    LMEcuCfg.AddModeGroup(builder, mode_group_vector)
    ecu_cfg = LMEcuCfg.End(builder)

    builder.Finish(ecu_cfg)

    buf = builder.Output()

    with open(output_filepath, "wb") as f:
        f.write(buf)


if __name__ == "__main__":
    main()
