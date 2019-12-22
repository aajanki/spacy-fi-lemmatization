#!/bin/sh

set -eu

mkdir -p data

echo "Downloading Joukahainen"
wget --directory-prefix data https://joukahainen.puimula.org/sanastot/joukahainen.xml.gz

echo "Downloading word frequencies"
wget --directory-prefix data http://bionlp-www.utu.fi/.jmnybl/finnish_vocab.txt.gz

echo "Cloning corevoikko"
git clone https://github.com/voikko/corevoikko data/corevoikko

echo "Downloading UD_Finnish-TDT"
git clone --branch r2.4 --single-branch --depth 1 https://github.com/UniversalDependencies/UD_Finnish-TDT data/UD_Finnish-TDT
