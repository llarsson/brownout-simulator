#!/bin/bash

set -eo pipefail

if [ ! -d experiments/$1 ]; then
	echo "Gimme the experiment name!"
	exit 1
fi

experiment=$1

gnuplot <<HERE
set ylabel "Probability"
set xlabel "Response time (s), logarithmic scale"

set term "pdf"
set output "experiments/$experiment/response-times-cdf.pdf"

set datafile separator ","

set logscale x

set key top left horizontal

plot "experiments/$experiment/never/sim-server1-rt.csv" using (\$3):(1.0/20000.0) smooth cumulative title "never", \
     "experiments/$experiment/0.50/sim-server1-rt.csv" using (\$3):(1.0/20000.0) smooth cumulative title "ut=0.50", \
     "experiments/$experiment/0.95/sim-server1-rt.csv" using (\$3):(1.0/20000.0) smooth cumulative title "ut=0.95", \
     "experiments/$experiment/Brownout-stock/sim-server1-rt.csv" using (\$3):(1.0/20000.0) smooth cumulative title "Brownout-stock", \
     "experiments/$experiment/Brownout-tuned/sim-server1-rt.csv" using (\$3):(1.0/20000.0) smooth cumulative title "Brownout-tuned", \
     "experiments/$experiment/always/sim-server1-rt.csv" using (\$3):(1.0/20000.0) smooth cumulative title "always", \
     "experiments/$experiment/qe/sim-server1-rt.csv" using (\$3):(1.0/20000.0) linecolor black dashtype "..." linewidth 2 smooth cumulative title "q-e"
HERE
