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

AUTOSD_IMAGE_SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOSD_IMAGE_ROOT_DIR="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)"
AUTOSD_IMAGE_NAME="score-autosd10-x86_64.qcow2"

AUTOMOTIVE_IMAGE_BUILDER="${AUTOSD_IMAGE_SCRIPTS_DIR}"/automotive-image-builder
AUTOMOTIVE_IMAGE_BUILDER_URL="https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/auto-image-builder.sh"

# Download automotive-image-builder
rm -f "${AUTOMOTIVE_IMAGE_BUILDER}"
curl -s -o "${AUTOMOTIVE_IMAGE_BUILDER}" "${AUTOMOTIVE_IMAGE_BUILDER_URL}"
chmod a+x "${AUTOMOTIVE_IMAGE_BUILDER}"

# Build required rpm packages and the rpm repo
"${AUTOSD_IMAGE_SCRIPTS_DIR}"/build-rpm-repo.sh

# Build image with automotive-image-builder
echo "Build image with automotive-image-builder..."
CURRENT_USER=$USER
(cd "${AUTOSD_IMAGE_ROOT_DIR}" && \
 sudo "${AUTOMOTIVE_IMAGE_BUILDER}" --dev build \
      --progress \
      --define-file vars.yml \
      --define-file vars-devel.yml \
      --target qemu \
      --distro autosd10 \
      image.aib.yml score-autosd10-x86_64.qcow2 && \
 sudo chown "${CURRENT_USER}":"${CURRENT_USER}" ${AUTOSD_IMAGE_NAME})

echo "The score-autosd image is at ${AUTOSD_IMAGE_ROOT_DIR}/${AUTOSD_IMAGE_NAME}"