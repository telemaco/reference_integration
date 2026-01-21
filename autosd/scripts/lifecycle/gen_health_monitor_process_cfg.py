#! /usr/bin/env python3

import flatbuffers
import sys
import argparse

from HMFlatBuffer import HMEcuCfg, HmMonitorInterface

def main():
    parser = argparse.ArgumentParser(description="Generate Health Monitor Configuration Flatbuffer.")
    parser.add_argument("output_filepath", help="Path to the output Flatbuffer binary file.")
    parser.add_argument("--process-group", default="MainPG", help="The name of the process group to configure (default: MainPG).")
    parser.add_argument("--process-index", required=True, type=int, help="The index of the process.")
    args = parser.parse_args()

    output_filepath = args.output_filepath
    process_group_name = args.process_group

    process_index = args.process_index

    builder = flatbuffers.Builder(1024)

    instance_specifier_str = f"demo/demo_application{process_index}/Port1"
    process_short_name_str = f"demo_application{process_index}"
    port_prototype_str = "Port1"
    interface_path_str = f"demo_application_{process_index}_{process_group_name}"

    instance_specifier = builder.CreateString(instance_specifier_str)
    process_short_name = builder.CreateString(process_short_name_str)
    port_prototype = builder.CreateString(port_prototype_str)
    interface_path = builder.CreateString(interface_path_str)
    hm_monitor_iface_offsets = []

    # Create HmMonitorInterface
    HmMonitorInterface.Start(builder)
    HmMonitorInterface.AddInstanceSpecifier(builder, instance_specifier)
    HmMonitorInterface.AddProcessShortName(builder, process_short_name)
    HmMonitorInterface.AddPortPrototype(builder, port_prototype)
    HmMonitorInterface.AddInterfacePath(builder, interface_path)
    HmMonitorInterface.AddRefProcessIndex(builder, 0)
    hm_monitor_iface = HmMonitorInterface.End(builder)
    hm_monitor_iface_offsets.append(hm_monitor_iface)

    # Create HmMonitorInterface vector
    HMEcuCfg.StartHmMonitorInterfaceVector(builder, len(hm_monitor_iface_offsets))
    for offset in reversed(hm_monitor_iface_offsets):
        builder.PrependUOffsetTRelative(offset)
    hm_monitor_iface_vector_offsets = builder.EndVector()

    # Create HMEcuCfg
    HMEcuCfg.Start(builder)
    HMEcuCfg.AddVersionMajor(builder, 8)
    HMEcuCfg.AddVersionMinor(builder, 0)
    HMEcuCfg.AddHmMonitorInterface(builder, hm_monitor_iface_vector_offsets)

    ecu_cfg = HMEcuCfg.End(builder)
    builder.Finish(ecu_cfg)

    buf = builder.Output()

    with open(output_filepath, "wb") as f:
        f.write(buf)

if __name__ == "__main__":
    main()