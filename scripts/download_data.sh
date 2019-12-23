#!/bin/sh

set -eu

mkdir -p data

echo "Downloading UD_Finnish-TDT"
git clone --branch r2.4 --single-branch --depth 1 https://github.com/UniversalDependencies/UD_Finnish-TDT data/UD_Finnish-TDT
