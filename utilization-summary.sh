#!/bin/bash

set -eo pipefail

if [ ! -d experiments/$1 ]; then
	echo "Gimme the experiment name!"
	exit 1
fi

experiment=$1

gnuplot <<HERE
set xlabel "Clients"
set ylabel "Average utilization"

set term "pdf"
set output "experiments/$experiment/utilization-summary.pdf"

set yrange [0:1.5]

set key top center horizontal

set multiplot
plot "experiments/$experiment/utilization_never.dat" with linespoints title "never" ,\
     "experiments/$experiment/utilization_ut=0.50.dat" with linespoints title "ut=0.50" ,\
     "experiments/$experiment/utilization_ut=0.95.dat" with linespoints title "ut=0.95" ,\
     "experiments/$experiment/utilization_Brownout-stock.dat" with linespoints title "Brownout-stock" ,\
     "experiments/$experiment/utilization_Brownout-tuned.dat" with linespoints title "Brownout-tuned" ,\
     "experiments/$experiment/utilization_always.dat" with linespoints title "always" ,\
     "experiments/$experiment/utilization_qe.dat" with linespoints dashtype "..." linecolor black linewidth 2 title "q-e"
HERE
