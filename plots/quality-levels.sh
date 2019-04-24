#!/bin/bash

gnuplot="docker run -i --rm --volume $(pwd):/tmp -w /tmp gnuplot gnuplot"

set -eo pipefail

if [ ! -d experiments/$1 ]; then
	echo "Gimme the experiment name!"
	exit 1
fi

experiment=$1

yrange="" # smart enough on its own
if echo "$experiment" | grep "16client"; then
	yrange="set yrange [0:2200]" # ...but not in this case
fi


$gnuplot <<HERE
set ylabel "Requests"

set term "pdf"
set output "experiments/$experiment/quality-levels.pdf"

set datafile separator ","

set key top right horizontal
set auto x
set style data histograms
set style increment default
set style histogram cluster gap 3
set style fill solid border -1
set boxwidth 0.8

$yrange

set xtics nomirror rotate by -45

# reverse the order here to make pretty!
set xtics ("drop" 5, "cached-prior" 4, "equal-tags" 3, "similar-general" 2, "similar-specific" 1, "individual-model" 0)

plot "experiments/$experiment/never/sim-server1-quality.csv" using 4 title "never" smooth frequency,\
     "experiments/$experiment/0.50/sim-server1-quality.csv" using 4 title "ut=0.50" smooth frequency,\
     "experiments/$experiment/0.95/sim-server1-quality.csv" using 4 title "ut=0.95" smooth frequency,\
     "experiments/$experiment/Brownout-stock/sim-server1-quality.csv" using 4 title "Brownout-stock" smooth frequency,\
     "experiments/$experiment/Brownout-tuned/sim-server1-quality.csv" using 4 title "Brownout-tuned" smooth frequency,\
     "experiments/$experiment/always/sim-server1-quality.csv" using 4 title "always" smooth frequency,\
     "experiments/$experiment/qe/sim-server1-quality.csv" using 4 linecolor black fillstyle pattern 10 title "q-e" smooth frequency
HERE
