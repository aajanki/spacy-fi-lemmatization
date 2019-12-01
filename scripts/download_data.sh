#!/bin/sh

set -eu

mkdir -p data
wget --directory-prefix data https://joukahainen.puimula.org/sanastot/joukahainen.xml.gz
