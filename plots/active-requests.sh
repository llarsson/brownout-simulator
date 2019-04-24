#!/bin/bash

set -eo pipefail

if [ ! -d experiments/$1 ]; then
	echo "Gimme the experiment name!"
	exit 1
fi

experiment=$1

gnuplot <<HERE
set xlabel "Time (s)"
set ylabel "Requests"

set key top center horizontal 
set term "pdf"
set output "experiments/$experiment/active-requests.pdf"

set datafile separator ","

set multiplot
plot "experiments/$experiment/never/sim-server1-arl.csv" with lines title "never" smooth bezier,\
     "experiments/$experiment/0.50/sim-server1-arl.csv" with lines title "ut=0.50" smooth bezier,\
     "experiments/$experiment/0.95/sim-server1-arl.csv" with lines title "ut=0.95" smooth bezier,\
     "experiments/$experiment/Brownout-stock/sim-server1-arl.csv" with lines title "Brownout-stock" smooth bezier,\
     "experiments/$experiment/Brownout-tuned/sim-server1-arl.csv" with lines title "Brownout-tuned" smooth bezier,\
     "experiments/$experiment/always/sim-server1-arl.csv" with lines title "always" smooth bezier,\
     "experiments/$experiment/qe/sim-server1-arl.csv" with lines dashtype "..." linecolor black linewidth 2 title "q-e" smooth bezier
HERE
