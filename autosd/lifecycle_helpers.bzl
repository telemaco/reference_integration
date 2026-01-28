"""Helpers for Lifecycle project integration."""

load("@rules_python//python:defs.bzl", "py_binary", "py_library")

def gen_health_monitor_process_cfg(process_groups):
    """Generates HM config binary and JSON for each process in each process group."""
    all_bins = []
    all_jsons = []
    for pg, pg_data in process_groups.items():
        for i in range(pg_data["process_num"]):
            proc_index = i
            rule_suffix = "{}_{}".format(pg, proc_index)
            bin_file = "health_monitor_process_cfg_{}_{}.bin".format(proc_index, pg)
            json_file = "health_monitor_process_cfg_{}_{}.json".format(proc_index, pg)

            # Rule to generate the binary file
            native.genrule(
                name = "gen_health_monitor_process_cfg_" + rule_suffix,
                srcs = [],
                outs = [bin_file],
                cmd = "$(location :gen_health_monitor_process_cfg_py) $(location {}) --process-group {} --process-index {}".format(bin_file, pg, proc_index),
                tools = [":gen_health_monitor_process_cfg_py"],
                visibility = ["//visibility:public"],
            )
            all_bins.append(":" + bin_file)

            # Rule to generate the JSON file from the binary
            native.genrule(
                name = "gen_health_monitor_process_cfg_json_" + rule_suffix,
                srcs = [
                    ":gen_health_monitor_process_cfg_" + rule_suffix,
                    "@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs",
                ],
                outs = [json_file],
                cmd = "$(location @flatbuffers//:flatc) --json --raw-binary -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs) -- $(location :gen_health_monitor_process_cfg_{})".format(rule_suffix),
                tools = ["@flatbuffers//:flatc"],
                visibility = ["//visibility:public"],
            )
            all_jsons.append(":" + json_file)

    native.filegroup(
        name = "all_health_monitor_process_cfg_bins",
        srcs = all_bins,
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "all_health_monitor_process_cfg_jsons",
        srcs = all_jsons,
        visibility = ["//visibility:public"],
    )


def generate_lifecycle_py_bindings():
    """Generates Python flatbuffer bindings for Lifecycle."""
    native.genrule(
        name = "hm_flatcfg_py",
        srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs"],
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
        cmd = "$(location @flatbuffers//:flatc) --python -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.genrule(
        name = "lm_flatcfg_py",
        srcs = ["@score_lifecycle_health//src/launch_manager_daemon:lm_flatcfg_fbs"],
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
        cmd = "$(location @flatbuffers//:flatc) --python -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon:lm_flatcfg_fbs)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.genrule(
        name = "hmcore_flatcfg_py",
        srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hmcore_flatcfg_fbs"],
        outs = [
            "HMCOREFlatBuffer/__init__.py",
            "HMCOREFlatBuffer/HMCOREEcuCfg.py",
            "HMCOREFlatBuffer/Watchdog.py",
            "HMCOREFlatBuffer/HmConfig.py",
        ],
        cmd = "$(location @flatbuffers//:flatc) --python -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hmcore_flatcfg_fbs)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    py_library(
        name = "lifecycle_fbs_py_bindings",
        srcs = [
            ":hm_flatcfg_py",
            ":lm_flatcfg_py",
            ":hmcore_flatcfg_py"
        ],
        imports = ["."],
        visibility = ["//visibility:public"],
    )

    py_binary(
        name = "gen_health_monitor_process_cfg_py",
        srcs = ["scripts/lifecycle/gen_health_monitor_process_cfg.py"],
        deps = [
            ":lifecycle_fbs_py_bindings",
            "@pip_autosd_venv_test//flatbuffers",
        ],
        main = "gen_health_monitor_process_cfg.py",
        visibility = ["//visibility:public"],
    )

def generate_lifecycle_demo_files(process_groups):
    generate_lifecycle_py_bindings()
    gen_health_monitor_process_cfg(process_groups)
    generate_hm_configs(process_groups)
    generate_lm_config(process_groups)
    generate_hm_core_config()


def _process_groups_to_json_str(process_groups):
    items = []
    for pg, data in process_groups.items():
        items.append('"%s": {"process_num": %d}' % (pg, data["process_num"]))
    return "{%s}" % ", ".join(items)


def generate_lm_config(process_groups):
    """Generates lm_demo.bin and lm_demo.json."""

    py_binary(
        name = "gen_launch_manager_cfg_py",
        srcs = ["scripts/lifecycle/gen_launch_manager_cfg.py"],
        deps = [
            ":lifecycle_fbs_py_bindings",
            "@pip_autosd_venv_test//flatbuffers",
        ],
        main = "gen_launch_manager_cfg.py",
        visibility = ["//visibility:public"],
    )

    # genrule to create lm_demo.bin
    native.genrule(
        name = "generate_lm_config_rule",
        outs = ["lm_demo.bin"],
        cmd = "$(location :gen_launch_manager_cfg_py) $@ --process-groups '{}'".format(_process_groups_to_json_str(process_groups)),
        tools = [":gen_launch_manager_cfg_py"],
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "lm_demo_bin",
        srcs = [":lm_demo.bin"],
        visibility = ["//visibility:public"],
    )

    # genrule to create lm_demo.json from lm_demo.bin
    native.genrule(
        name = "generate_lm_config_json_rule",
        srcs = [
            ":generate_lm_config_rule",
            "@score_lifecycle_health//src/launch_manager_daemon:lm_flatcfg_fbs",
        ],
        outs = ["lm_demo.json"],
        cmd = "$(location @flatbuffers//:flatc) --json --defaults-json --raw-binary -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon:lm_flatcfg_fbs) -- $(location :generate_lm_config_rule)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "lm_demo_json",
        srcs = [":lm_demo.json"],
        visibility = ["//visibility:public"],
    )


def generate_hm_configs(process_groups):
    """Generates hm_demo.bin and hm_demo.json."""

    # py_binary for the new script
    py_binary(
        name = "gen_health_monitor_cfg_py",
        srcs = ["scripts/lifecycle/gen_health_monitor_cfg.py"],
        deps = [
            ":lifecycle_fbs_py_bindings",
            "@pip_autosd_venv_test//flatbuffers",
        ],
        main = "gen_health_monitor_cfg.py",
        visibility = ["//visibility:public"],
    )

    # genrule to create hm_demo.bin
    native.genrule(
        name = "generate_hm_configs_rule",
        outs = ["hm_demo.bin"],
        cmd = "$(location :gen_health_monitor_cfg_py) $@ --process-groups '{}'".format(_process_groups_to_json_str(process_groups)),
        tools = [":gen_health_monitor_cfg_py"],
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "hm_demo_bin",
        srcs = [":hm_demo.bin"],
        visibility = ["//visibility:public"],
    )

    # genrule to create hm_demo.json from hm_demo.bin
    native.genrule(
        name = "generate_hm_configs_json_rule",
        srcs = [
            ":generate_hm_configs_rule",
            "@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs",
        ],
        outs = ["hm_demo.json"],
        cmd = "$(location @flatbuffers//:flatc) --json --defaults-json --raw-binary -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs) -- $(location :generate_hm_configs_rule)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "hm_demo_json",
        srcs = [":hm_demo.json"],
        visibility = ["//visibility:public"],
    )


def generate_hm_core_config():
    """Generates hmcore.bin and hmcore.json."""

    # py_binary for the new script
    py_binary(
        name = "gen_health_monitor_core_cfg_py",
        srcs = ["scripts/lifecycle/gen_health_monitor_core_cfg.py"],
        deps = [
            ":lifecycle_fbs_py_bindings",
            "@pip_autosd_venv_test//flatbuffers",
        ],
        main = "gen_health_monitor_core_cfg.py",
        visibility = ["//visibility:public"],
    )

    # genrule to create hmcore.bin
    native.genrule(
        name = "generate_hm_core_config_rule",
        outs = ["hmcore.bin"],
        cmd = "$(location :gen_health_monitor_core_cfg_py) $@",
        tools = [":gen_health_monitor_core_cfg_py"],
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "hmcore_bin",
        srcs = [":hmcore.bin"],
        visibility = ["//visibility:public"],
    )

    # genrule to create hmcore.json from hmcore.bin
    native.genrule(
        name = "generate_hm_core_config_json_rule",
        srcs = [
            ":generate_hm_core_config_rule",
            "@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hmcore_flatcfg_fbs",
        ],
        outs = ["hmcore.json"],
        cmd = "$(location @flatbuffers//:flatc) --json --defaults-json --raw-binary -o $(@D) $(location @score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hmcore_flatcfg_fbs) -- $(location :generate_hm_core_config_rule)",
        tools = ["@flatbuffers//:flatc"],
        visibility = ["//visibility:public"],
    )

    native.filegroup(
        name = "hmcore_json",
        srcs = [":hmcore.json"],
        visibility = ["//visibility:public"],
    )
