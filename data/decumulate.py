#!/usr/bin/env python3
import os
import fileinput


IFS = os.environ.get('IFS', ';')

with fileinput.input() as infile:
	for line in infile:
		line = line.rstrip('\r\n').split(IFS)

		if line[-1].isdigit():
			cumulated = int(line[-1])
			line[-1] = cumulated

			for i in range(len(line) - 2, 0, -1):
				x = int(line[i]) - cumulated
				cumulated += x
				line[i] = x

		print(*line, sep=IFS)
