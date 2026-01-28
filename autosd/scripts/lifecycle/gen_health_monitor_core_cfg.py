#! /usr/bin/env python3

import flatbuffers
import argparse

from HMCOREFlatBuffer import HMCOREEcuCfg, Watchdog, HmConfig

def main():
    parser = argparse.ArgumentParser(
        description="Generate Health Monitor Core Configuration Flatbuffer."
    )
    parser.add_argument(
        "output_filepath", help="Path to the output Flatbuffer binary file."
    )
    args = parser.parse_args()

    builder = flatbuffers.Builder(1024)

    # Build HmConfig objects
    config_offsets = []

    HmConfig.Start(builder)
    HmConfig.AddPeriodicity(builder, 50)
    HmConfig.AddBufferSizeGlobalSupervision(builder, 512)
    config_offsets.append(HmConfig.End(builder))

    # Create the vector of HmConfig offsets
    HMCOREEcuCfg.StartConfigVector(builder, len(config_offsets))
    for offset in reversed(config_offsets):
        builder.PrependUOffsetTRelative(offset)
    config_vector = builder.EndVector()

    # Create an empty vector for Watchdogs
    HMCOREEcuCfg.StartWatchdogsVector(builder, 0)
    watchdogs_vector = builder.EndVector()

    # Build the main HMCOREEcuCfg table
    HMCOREEcuCfg.Start(builder)
    HMCOREEcuCfg.AddVersionMajor(builder, 3)
    HMCOREEcuCfg.AddVersionMinor(builder, 0)
    HMCOREEcuCfg.AddWatchdogs(builder, watchdogs_vector)
    HMCOREEcuCfg.AddConfig(builder, config_vector)
    ecu_cfg = HMCOREEcuCfg.End(builder)

    builder.Finish(ecu_cfg)

    buf = builder.Output()

    with open(args.output_filepath, "wb") as f:
        f.write(buf)

if __name__ == "__main__":
    main()
