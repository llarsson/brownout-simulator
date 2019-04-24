#!/bin/bash

set -eo pipefail

if [ ! -d experiments/$1 ]; then
	echo "Gimme the experiment name!"
	exit 1
fi

experiment=$1

gnuplot <<HERE
set xlabel "Time (s)"
set ylabel "Utilization"

set term "pdf"
set output "experiments/$experiment/utilization.pdf"

set key top center horizontal
set yrange [0:1.5]

set datafile separator ","

set multiplot
plot "experiments/$experiment/never/sim-server1-utilization.csv" using 1:4 with lines title "never" smooth bezier,\
     "experiments/$experiment/0.50/sim-server1-utilization.csv" using 1:4 with lines title "ut=0.50" smooth bezier,\
     "experiments/$experiment/0.95/sim-server1-utilization.csv" using 1:4 with lines title "ut=0.95" smooth bezier,\
     "experiments/$experiment/Brownout-stock/sim-server1-utilization.csv" using 1:4 with lines title "Brownout-stock" smooth bezier,\
     "experiments/$experiment/Brownout-tuned/sim-server1-utilization.csv" using 1:4 with lines title "Brownout-tuned" smooth bezier,\
     "experiments/$experiment/always/sim-server1-utilization.csv" using 1:4 with lines title "always" smooth bezier,\
     "experiments/$experiment/qe/sim-server1-utilization.csv" using 1:4 with lines dashtype "..." linecolor black linewidth 2 title "q-e" smooth bezier
HERE

