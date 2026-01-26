#! /usr/bin/env python3

import flatbuffers
import argparse
import json

from HMFlatBuffer import (
    HMEcuCfg,
    Process,
    HmRefProcessGroupStates,
    HmProcessExecutionError,
    HmAliveSupervision,
    HmDeadlineSupervision,
    HmGlobalSupervision,
    HmLocalSupervision,
    HmLogicalSupervision,
    HmMonitorInterface,
    HmSupervisionCheckpoint,
    HmCheckpointTransition,
    HmLogicalCheckpoint,
    HmLogicalTransition,
    HmRefAliveSupervision,
    HmRefDeadlineSupervision,
    HmRefLogicalSupervision,
    HmRefProcessGroupStatesGlobal,
    RecoveryNotification,
    HmRefProcess,
    HmGlobalSupervisionLocalRef,
)


def create_hm_monitor_interface(builder, index, process_name, process_group_name):
    instance_specifier = builder.CreateString(f"demo/{process_name}/Port1")
    process_short_name = builder.CreateString(process_name)
    port_prototype = builder.CreateString("Port1")
    interface_path = builder.CreateString(f"{process_name}_{process_group_name}")

    HmMonitorInterface.Start(builder)
    HmMonitorInterface.AddInstanceSpecifier(builder, instance_specifier)
    HmMonitorInterface.AddProcessShortName(builder, process_short_name)
    HmMonitorInterface.AddPortPrototype(builder, port_prototype)
    HmMonitorInterface.AddInterfacePath(builder, interface_path)
    HmMonitorInterface.AddRefProcessIndex(builder, index)
    HmMonitorInterface.AddPermittedUid(builder, 0)
    return HmMonitorInterface.End(builder)


def create_hm_supervision_checkpoint(
    builder, index, checkpoint_id, ref_interface_index
):
    short_name = builder.CreateString(f"Checkpoint{index}_{checkpoint_id}")

    HmSupervisionCheckpoint.Start(builder)
    HmSupervisionCheckpoint.AddShortName(builder, short_name)
    HmSupervisionCheckpoint.AddCheckpointId(builder, checkpoint_id)
    HmSupervisionCheckpoint.AddRefInterfaceIndex(builder, ref_interface_index)
    return HmSupervisionCheckpoint.End(builder)


def create_hm_alive_supervision(
    builder, index, ref_checkpoint_index, ref_process_index, pg_name
):
    rule_context_key = builder.CreateString(f"AliveSupervision{index}")
    ref_pgs_identifier_str = f"{pg_name}/Startup"
    ref_pgs_identifier = builder.CreateString(ref_pgs_identifier_str)

    HmRefProcessGroupStates.Start(builder)
    HmRefProcessGroupStates.AddIdentifier(builder, ref_pgs_identifier)
    ref_pgs = HmRefProcessGroupStates.End(builder)

    HmAliveSupervision.StartRefProcessGroupStatesVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_pgs)
    ref_pgs_vector = builder.EndVector()

    HmAliveSupervision.Start(builder)
    HmAliveSupervision.AddRuleContextKey(builder, rule_context_key)
    HmAliveSupervision.AddRefCheckPointIndex(builder, ref_checkpoint_index)
    HmAliveSupervision.AddAliveReferenceCycle(builder, 100.0)
    HmAliveSupervision.AddMinAliveIndications(builder, 1)
    HmAliveSupervision.AddMaxAliveIndications(builder, 3)
    HmAliveSupervision.AddIsMinCheckDisabled(builder, False)
    HmAliveSupervision.AddIsMaxCheckDisabled(builder, False)
    HmAliveSupervision.AddFailedSupervisionCyclesTolerance(builder, 1)
    HmAliveSupervision.AddRefProcessIndex(builder, ref_process_index)
    HmAliveSupervision.AddRefProcessGroupStates(builder, ref_pgs_vector)
    return HmAliveSupervision.End(builder)


def create_hm_checkpoint_transition(builder, ref_source_cp_index, ref_target_cp_index):
    HmCheckpointTransition.Start(builder)
    HmCheckpointTransition.AddRefSourceCpindex(builder, ref_source_cp_index)
    HmCheckpointTransition.AddRefTargetCpindex(builder, ref_target_cp_index)
    return HmCheckpointTransition.End(builder)


def create_hm_deadline_supervision(
    builder, index, ref_source_cp_index, ref_target_cp_index, ref_process_index, pg_name
):
    rule_context_key = builder.CreateString(f"DeadlineSupervision{index}")
    ref_pgs_identifier_str = f"{pg_name}/Startup"
    ref_pgs_identifier = builder.CreateString(ref_pgs_identifier_str)

    HmRefProcessGroupStates.Start(builder)
    HmRefProcessGroupStates.AddIdentifier(builder, ref_pgs_identifier)
    ref_pgs = HmRefProcessGroupStates.End(builder)

    HmDeadlineSupervision.StartRefProcessGroupStatesVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_pgs)
    ref_pgs_vector = builder.EndVector()

    checkpoint_transition = create_hm_checkpoint_transition(
        builder, ref_source_cp_index, ref_target_cp_index
    )

    HmDeadlineSupervision.StartRefProcessIndicesVector(builder, 1)
    builder.PrependUint32(ref_process_index)
    ref_process_indices_vector = builder.EndVector()

    HmDeadlineSupervision.Start(builder)
    HmDeadlineSupervision.AddRuleContextKey(builder, rule_context_key)
    HmDeadlineSupervision.AddMaxDeadline(builder, 80.0)
    HmDeadlineSupervision.AddMinDeadline(builder, 40.0)
    HmDeadlineSupervision.AddCheckpointTransition(builder, checkpoint_transition)
    HmDeadlineSupervision.AddRefProcessIndices(builder, ref_process_indices_vector)
    HmDeadlineSupervision.AddRefProcessGroupStates(builder, ref_pgs_vector)
    return HmDeadlineSupervision.End(builder)


def create_hm_logical_checkpoint(builder, ref_checkpoint_index, is_initial, is_final):
    HmLogicalCheckpoint.Start(builder)
    HmLogicalCheckpoint.AddRefCheckPointIndex(builder, ref_checkpoint_index)
    HmLogicalCheckpoint.AddIsInitial(builder, is_initial)
    HmLogicalCheckpoint.AddIsFinal(builder, is_final)
    return HmLogicalCheckpoint.End(builder)


def create_hm_logical_transition(builder, checkpoint_source_idx, checkpoint_target_idx):
    HmLogicalTransition.Start(builder)
    HmLogicalTransition.AddCheckpointSourceIdx(builder, checkpoint_source_idx)
    HmLogicalTransition.AddCheckpointTargetIdx(builder, checkpoint_target_idx)
    return HmLogicalTransition.End(builder)


def create_hm_logical_supervision(builder, pg_name, process_groups):
    rule_context_key = builder.CreateString(f"LogicalSupervision_{pg_name}")
    ref_pgs_identifier_str = f"{pg_name}/Startup"
    ref_pgs_identifier = builder.CreateString(ref_pgs_identifier_str)

    HmRefProcessGroupStates.Start(builder)
    HmRefProcessGroupStates.AddIdentifier(builder, ref_pgs_identifier)
    ref_pgs = HmRefProcessGroupStates.End(builder)

    HmLogicalSupervision.StartRefProcessGroupStatesVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_pgs)
    ref_pgs_vector = builder.EndVector()

    checkpoints = [
        create_hm_logical_checkpoint(builder, 0, True, False),
        create_hm_logical_checkpoint(builder, 1, False, False),
        create_hm_logical_checkpoint(builder, 2, False, True),
    ]
    HmLogicalSupervision.StartCheckpointsVector(builder, len(checkpoints))
    for offset in reversed(checkpoints):
        builder.PrependUOffsetTRelative(offset)
    checkpoints_vector = builder.EndVector()

    transitions = [
        create_hm_logical_transition(builder, 0, 1),
        create_hm_logical_transition(builder, 1, 2),
    ]
    HmLogicalSupervision.StartTransitionsVector(builder, len(transitions))
    for offset in reversed(transitions):
        builder.PrependUOffsetTRelative(offset)
    transitions_vector = builder.EndVector()

    process_indices = []
    for i in range(process_groups[pg_name]["process_num"]):
        process_indices.append(
            i
            + sum(
                process_groups[p]["process_num"]
                for p in list(process_groups.keys())[
                    : list(process_groups.keys()).index(pg_name)
                ]
            )
        )

    HmLogicalSupervision.StartRefProcessIndicesVector(builder, len(process_indices))
    for index in reversed(process_indices):
        builder.PrependUint32(index)
    ref_process_indices_vector = builder.EndVector()

    HmLogicalSupervision.Start(builder)
    HmLogicalSupervision.AddRuleContextKey(builder, rule_context_key)
    HmLogicalSupervision.AddCheckpoints(builder, checkpoints_vector)
    HmLogicalSupervision.AddTransitions(builder, transitions_vector)
    HmLogicalSupervision.AddRefProcessIndices(builder, ref_process_indices_vector)
    HmLogicalSupervision.AddRefProcessGroupStates(builder, ref_pgs_vector)
    return HmLogicalSupervision.End(builder)


def create_hm_local_supervision(builder, index, logical_supervision_index):
    rule_context_key = builder.CreateString(f"LocalSupervision{index}")
    info_ref_interface_path = builder.CreateString(f"demo_application_{index}")

    HmRefAliveSupervision.Start(builder)
    HmRefAliveSupervision.AddRefAliveSupervisionIdx(builder, index)
    ref_alive_supervision = HmRefAliveSupervision.End(builder)

    HmLocalSupervision.StartHmRefAliveSupervisionVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_alive_supervision)
    ref_alive_supervision_vector = builder.EndVector()

    HmRefDeadlineSupervision.Start(builder)
    HmRefDeadlineSupervision.AddRefDeadlineSupervisionIdx(builder, index)
    ref_deadline_supervision = HmRefDeadlineSupervision.End(builder)

    HmLocalSupervision.StartHmRefDeadlineSupervisionVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_deadline_supervision)
    ref_deadline_supervision_vector = builder.EndVector()

    HmRefLogicalSupervision.Start(builder)
    HmRefLogicalSupervision.AddRefLogicalSupervisionIdx(
        builder, logical_supervision_index
    )
    ref_logical_supervision = HmRefLogicalSupervision.End(builder)

    HmLocalSupervision.StartHmRefLogicalSupervisionVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_logical_supervision)
    ref_logical_supervision_vector = builder.EndVector()

    HmLocalSupervision.Start(builder)
    HmLocalSupervision.AddRuleContextKey(builder, rule_context_key)
    HmLocalSupervision.AddInfoRefInterfacePath(builder, info_ref_interface_path)
    HmLocalSupervision.AddHmRefAliveSupervision(builder, ref_alive_supervision_vector)
    HmLocalSupervision.AddHmRefDeadlineSupervision(
        builder, ref_deadline_supervision_vector
    )
    HmLocalSupervision.AddHmRefLogicalSupervision(
        builder, ref_logical_supervision_vector
    )
    return HmLocalSupervision.End(builder)


def create_hm_global_supervision(
    builder, pg_name, process_groups, expired_supervision_tolerance
):
    rule_context_key = builder.CreateString(f"GlobalSupervision_{pg_name}")

    ref_pgs_global_identifier = builder.CreateString(f"{pg_name}/Startup")
    HmRefProcessGroupStatesGlobal.Start(builder)
    HmRefProcessGroupStatesGlobal.AddIdentifier(builder, ref_pgs_global_identifier)
    HmRefProcessGroupStatesGlobal.AddExpiredSupervisionTolerance(
        builder, expired_supervision_tolerance
    )
    ref_pgs_global = HmRefProcessGroupStatesGlobal.End(builder)

    HmGlobalSupervision.StartRefProcessGroupStatesVector(builder, 1)
    builder.PrependUOffsetTRelative(ref_pgs_global)
    ref_pgs_global_vector = builder.EndVector()

    process_indices = []
    for i in range(process_groups[pg_name]["process_num"]):
        process_indices.append(
            i
            + sum(
                process_groups[p]["process_num"]
                for p in list(process_groups.keys())[
                    : list(process_groups.keys()).index(pg_name)
                ]
            )
        )

    ref_processes_offsets = []
    for index in process_indices:
        HmRefProcess.Start(builder)
        HmRefProcess.AddIndex(builder, index)
        ref_processes_offsets.append(HmRefProcess.End(builder))

    HmGlobalSupervision.StartRefProcessesVector(builder, len(ref_processes_offsets))
    for offset in reversed(ref_processes_offsets):
        builder.PrependUOffsetTRelative(offset)
    ref_processes_vector = builder.EndVector()

    local_supervision_offsets = []
    for index in process_indices:
        HmGlobalSupervisionLocalRef.Start(builder)
        HmGlobalSupervisionLocalRef.AddRefLocalSupervisionIndex(builder, index)
        local_supervision_offsets.append(HmGlobalSupervisionLocalRef.End(builder))

    HmGlobalSupervision.StartLocalSupervisionVector(
        builder, len(local_supervision_offsets)
    )
    for offset in reversed(local_supervision_offsets):
        builder.PrependUOffsetTRelative(offset)
    local_supervision_vector = builder.EndVector()

    HmGlobalSupervision.Start(builder)
    HmGlobalSupervision.AddRuleContextKey(builder, rule_context_key)
    HmGlobalSupervision.AddIsSeverityCritical(builder, False)
    HmGlobalSupervision.AddLocalSupervision(builder, local_supervision_vector)
    HmGlobalSupervision.AddRefProcesses(builder, ref_processes_vector)
    HmGlobalSupervision.AddRefProcessGroupStates(builder, ref_pgs_global_vector)
    return HmGlobalSupervision.End(builder)


def create_recovery_notification(builder, pg_name, global_supervision_index):
    short_name = builder.CreateString(f"RecoveryNotification_{pg_name}")
    pg_meta_model_identifier = builder.CreateString(f"{pg_name}/Recovery")
    instance_specifier = builder.CreateString("")

    RecoveryNotification.Start(builder)
    RecoveryNotification.AddShortName(builder, short_name)
    RecoveryNotification.AddRecoveryNotificationTimeout(builder, 4000.0)
    RecoveryNotification.AddProcessGroupMetaModelIdentifier(
        builder, pg_meta_model_identifier
    )
    RecoveryNotification.AddRefGlobalSupervisionIndex(builder, global_supervision_index)
    RecoveryNotification.AddInstanceSpecifier(builder, instance_specifier)
    RecoveryNotification.AddShouldFireWatchdog(builder, False)
    return RecoveryNotification.End(builder)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Health Monitor Configuration Flatbuffer."
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
    monitor_interface_offsets = []
    supervision_checkpoint_offsets = []
    alive_supervision_offsets = []
    deadline_supervision_offsets = []
    logical_supervision_offsets = []
    local_supervision_offsets = []
    global_supervision_offsets = []
    recovery_notification_offsets = []

    process_index = 0
    checkpoint_index = 0
    logical_supervision_index = 0
    global_supervision_index = 0
    for pg_name, pg_data in process_groups.items():
        for i in range(pg_data["process_num"]):
            short_name_str = f"demo_application{process_index}"

            # Create HmMonitorInterface
            monitor_interface = create_hm_monitor_interface(
                builder, process_index, short_name_str, pg_name
            )
            monitor_interface_offsets.append(monitor_interface)

            # Create HmSupervisionCheckpoints
            for checkpoint_id in range(1, 4):
                checkpoint = create_hm_supervision_checkpoint(
                    builder, process_index, checkpoint_id, process_index
                )
                supervision_checkpoint_offsets.append(checkpoint)

            # Create HmAliveSupervision
            alive_supervision = create_hm_alive_supervision(
                builder, process_index, checkpoint_index, process_index, pg_name
            )
            alive_supervision_offsets.append(alive_supervision)

            # Create HmDeadlineSupervision
            deadline_supervision = create_hm_deadline_supervision(
                builder,
                process_index,
                checkpoint_index,
                checkpoint_index + 1,
                process_index,
                pg_name,
            )
            deadline_supervision_offsets.append(deadline_supervision)

            # Create HmLocalSupervision
            local_supervision = create_hm_local_supervision(
                builder, process_index, logical_supervision_index
            )
            local_supervision_offsets.append(local_supervision)

            checkpoint_index += 3

            identifier_str = f"demo_app{process_index}_{pg_name}"

            short_name = builder.CreateString(short_name_str)
            identifier = builder.CreateString(identifier_str)

            # Create HmRefProcessGroupStates
            ref_pgs_identifier_str = f"{pg_name}/Startup"
            ref_pgs_identifier = builder.CreateString(ref_pgs_identifier_str)
            HmRefProcessGroupStates.Start(builder)
            HmRefProcessGroupStates.AddIdentifier(builder, ref_pgs_identifier)
            ref_pgs = HmRefProcessGroupStates.End(builder)

            Process.StartRefProcessGroupStatesVector(builder, 1)
            builder.PrependUOffsetTRelative(ref_pgs)
            ref_pgs_vector = builder.EndVector()

            # Create HmProcessExecutionError
            HmProcessExecutionError.Start(builder)
            HmProcessExecutionError.AddProcessExecutionError(builder, 1)
            proc_exec_error = HmProcessExecutionError.End(builder)

            Process.StartProcessExecutionErrorsVector(builder, 1)
            builder.PrependUOffsetTRelative(proc_exec_error)
            proc_exec_error_vector = builder.EndVector()

            # Create Process
            Process.Start(builder)
            Process.AddIndex(builder, process_index)
            Process.AddShortName(builder, short_name)
            Process.AddIdentifier(builder, identifier)
            Process.AddProcessType(builder, 0)  # REGULAR_PROCESS
            Process.AddRefProcessGroupStates(builder, ref_pgs_vector)
            Process.AddProcessExecutionErrors(builder, proc_exec_error_vector)
            process = Process.End(builder)
            process_offsets.append(process)

            process_index += 1

        # Create HmLogicalSupervision
        logical_supervision = create_hm_logical_supervision(
            builder, pg_name, process_groups
        )
        logical_supervision_offsets.append(logical_supervision)
        logical_supervision_index += 1

        # Create HmGlobalSupervision
        global_supervision_offsets.append(
            create_hm_global_supervision(builder, pg_name, process_groups, 3)
        )

        # Create RecoveryNotification
        recovery_notification = create_recovery_notification(
            builder, pg_name, global_supervision_index
        )
        recovery_notification_offsets.append(recovery_notification)
        global_supervision_index += 1

    HMEcuCfg.StartProcessVector(builder, len(process_offsets))
    for offset in reversed(process_offsets):
        builder.PrependUOffsetTRelative(offset)
    process_vector = builder.EndVector()

    HMEcuCfg.StartHmMonitorInterfaceVector(builder, len(monitor_interface_offsets))
    for offset in reversed(monitor_interface_offsets):
        builder.PrependUOffsetTRelative(offset)
    monitor_interface_vector = builder.EndVector()

    HMEcuCfg.StartHmSupervisionCheckpointVector(
        builder, len(supervision_checkpoint_offsets)
    )
    for offset in reversed(supervision_checkpoint_offsets):
        builder.PrependUOffsetTRelative(offset)
    supervision_checkpoint_vector = builder.EndVector()

    HMEcuCfg.StartHmAliveSupervisionVector(builder, len(alive_supervision_offsets))
    for offset in reversed(alive_supervision_offsets):
        builder.PrependUOffsetTRelative(offset)
    alive_supervision_vector = builder.EndVector()

    HMEcuCfg.StartHmDeadlineSupervisionVector(
        builder, len(deadline_supervision_offsets)
    )
    for offset in reversed(deadline_supervision_offsets):
        builder.PrependUOffsetTRelative(offset)
    deadline_supervision_vector = builder.EndVector()

    HMEcuCfg.StartHmLogicalSupervisionVector(builder, len(logical_supervision_offsets))
    for offset in reversed(logical_supervision_offsets):
        builder.PrependUOffsetTRelative(offset)
    logical_supervision_vector = builder.EndVector()

    HMEcuCfg.StartHmLocalSupervisionVector(builder, len(local_supervision_offsets))
    for offset in reversed(local_supervision_offsets):
        builder.PrependUOffsetTRelative(offset)
    local_supervision_vector = builder.EndVector()

    HMEcuCfg.StartHmGlobalSupervisionVector(builder, len(global_supervision_offsets))
    for offset in reversed(global_supervision_offsets):
        builder.PrependUOffsetTRelative(offset)
    global_supervision_vector = builder.EndVector()

    HMEcuCfg.StartHmRecoveryNotificationVector(
        builder, len(recovery_notification_offsets)
    )
    for offset in reversed(recovery_notification_offsets):
        builder.PrependUOffsetTRelative(offset)
    recovery_notification_vector = builder.EndVector()

    # Create HMEcuCfg
    HMEcuCfg.Start(builder)
    HMEcuCfg.AddVersionMajor(builder, 8)
    HMEcuCfg.AddVersionMinor(builder, 0)
    HMEcuCfg.AddProcess(builder, process_vector)
    HMEcuCfg.AddHmMonitorInterface(builder, monitor_interface_vector)
    HMEcuCfg.AddHmSupervisionCheckpoint(builder, supervision_checkpoint_vector)
    HMEcuCfg.AddHmAliveSupervision(builder, alive_supervision_vector)
    HMEcuCfg.AddHmDeadlineSupervision(builder, deadline_supervision_vector)
    HMEcuCfg.AddHmLogicalSupervision(builder, logical_supervision_vector)
    HMEcuCfg.AddHmLocalSupervision(builder, local_supervision_vector)
    HMEcuCfg.AddHmGlobalSupervision(builder, global_supervision_vector)
    HMEcuCfg.AddHmRecoveryNotification(builder, recovery_notification_vector)
    ecu_cfg = HMEcuCfg.End(builder)

    builder.Finish(ecu_cfg)

    buf = builder.Output()

    with open(output_filepath, "wb") as f:
        f.write(buf)


if __name__ == "__main__":
    main()
