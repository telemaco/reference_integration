#!/bin/bash
# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

set -e

AUTOSD_IMAGE_ROOT_DIR="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)"
AUTOSD_ROOT_DIR="$(cd "$(dirname "${AUTOSD_IMAGE_ROOT_DIR}")" && pwd)"

# Allow override of build config
BUILD_CONFIG="${BUILD_CONFIG:-bl-x86_64-linux-autosd}"

# Output directory for RPMs
RPMS_DIR="${RPMS_DIR:-$AUTOSD_IMAGE_ROOT_DIR/rpms}"

echo "Building RPMs with config: $BUILD_CONFIG"
echo "Output directory: $RPMS_DIR"

# Build all RPM packages
echo "Building lola-demo..."
bazel --quiet build --config="$BUILD_CONFIG" //:lola-demo

echo "Building lifecycle-demo..."
bazel --quiet build --config="$BUILD_CONFIG" //:lifecycle-demo

# Create output directory
mkdir -p "$RPMS_DIR"
rm -fr "${RPMS_DIR}"/repodata
rm -f "${RPMS_DIR}"/*.rpm

# Copy RPMs to output directory
echo "Copying RPMs to $RPMS_DIR..."
cp "${AUTOSD_ROOT_DIR}"/bazel-out/k8-fastbuild/bin/*.rpm "$RPMS_DIR/"

# Create repository metadata
echo "Creating repository metadata..."
createrepo_c -q "$RPMS_DIR/"

echo "Done! RPMs available at: $RPMS_DIR"