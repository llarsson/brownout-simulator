#!/bin/bash

set -eo pipefail

if [ ! -d experiments/$1 ]; then
	echo "Gimme the experiment name!"
	exit 1
fi

experiment=$1

gnuplot <<HERE
set ylabel "Response time (s)"
set xlabel "Simulation time (s)"

set datafile separator ","

set term "pdf"

set yrange [-0.01:2.0]

set key top center horizontal

set output "experiments/$experiment/response-times-95percentile.pdf"
plot "experiments/$experiment/never/sim-server1.csv" using (\$1):(\$3) with lines title "never" smooth bezier, \
     "experiments/$experiment/0.50/sim-server1.csv" using (\$1):(\$3) with lines title "ut=0.50" smooth bezier, \
     "experiments/$experiment/0.95/sim-server1.csv" using (\$1):(\$3) with lines title "ut=0.95" smooth bezier, \
     "experiments/$experiment/Brownout-stock/sim-server1.csv" using (\$1):(\$3) with lines title "Brownout-stock" smooth bezier, \
     "experiments/$experiment/Brownout-tuned/sim-server1.csv" using (\$1):(\$3) with lines title "Brownout-tuned" smooth bezier, \
     "experiments/$experiment/always/sim-server1.csv" using (\$1):(\$3) with lines title "always" smooth bezier, \
     "experiments/$experiment/qe/sim-server1.csv" using (\$1):(\$3) with lines dashtype "..." linecolor black linewidth 2 title "q-e" smooth bezier

set output "experiments/$experiment/response-times-99percentile.pdf"
plot "experiments/$experiment/never/sim-server1.csv" using (\$1):(\$4) with lines title "never" smooth bezier, \
     "experiments/$experiment/0.50/sim-server1.csv" using (\$1):(\$4) with lines title "ut=0.50" smooth bezier, \
     "experiments/$experiment/0.95/sim-server1.csv" using (\$1):(\$4) with lines title "ut=0.95" smooth bezier, \
     "experiments/$experiment/Brownout-stock/sim-server1.csv" using (\$1):(\$4) with lines title "Brownout-stock" smooth bezier, \
     "experiments/$experiment/Brownout-tuned/sim-server1.csv" using (\$1):(\$4) with lines title "Brownout-tuned" smooth bezier, \
     "experiments/$experiment/always/sim-server1.csv" using (\$1):(\$4) with lines title "always" smooth bezier, \
     "experiments/$experiment/qe/sim-server1.csv" using (\$1):(\$4) with lines dashtype "..." linecolor black linewidth 2 title "q-e" smooth bezier
HERE
