#!/bin/bash

latexmk -output-directory=./tmp -pdf presentation.tex
mv.exe tmp/presentation.pdf .
