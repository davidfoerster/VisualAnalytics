#!/bin/sh
set -e

latexmk -output-directory=./tmp -pdf presentation.tex
cp tmp/presentation.pdf .
