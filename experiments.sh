#!/bin/bash

set -eo pipefail

experimentName=$1

if [ -z $experimentName ]; then
	experimentName=$(date +'%y%m%d.%H%M')
fi

if [ -d experiments/$experimentName ]; then
	rm -rf experiments/$experimentName
fi

for sub in spectrum lowfrequency 1client 2client 4client 8client 16client 32client 64client 128client 200client 256client; do
	scenarioFile=""

	if [ $sub == "spectrum" ]; then
		scenarioFile="scenarios/replica-test-1.py"
	elif [ $sub == "lowfrequency" ]; then
		scenarioFile="scenarios/low-frequency.py"
	else
		scenarioFile="scenarios/lowfrequency-$sub.py"
	fi


	for threshold in -1 666-stock 666-tuned 0.50 0.95 200 1337; do
		label=$threshold
		folder=$threshold
	
		individualModel="-1"
		similarSpecific="-1"
		similarGeneral="-1"
		equalTags="-1"
		cachedPrior="-1"
		drop=2
	
		if [ $threshold == "666-stock" ]; then
			label="Brownout-stock"
			folder=$label
			similarGeneral=666
			sed -i Server.py -e "s/self.setPoint = .*/self.setPoint = 1/g"
			sed -i Server.py -e "s/self.pole = .*/self.pole = 0.9/g"
			rm Server.pyc
		elif [ $threshold == "666-tuned" ]; then
			label="Brownout-tuned"
			folder=$label
			similarGeneral=666
			sed -i Server.py -e "s/self.setPoint = .*/self.setPoint = 0.05/g"
			sed -i Server.py -e "s/self.pole = .*/self.pole = 0.7/g"
			rm Server.pyc
		elif [ $threshold == "-1" ]; then
			label="never"
			folder=$label
			similarGeneral=$threshold
		elif [ $threshold == "200" ]; then
			label="always"
			folder=$label
			similarGeneral=$threshold
		elif [ $threshold == "1337" ]; then
			label="qe"
			folder=$label
			individualModel="0.05"
			similarSpecific="0.25"
			similarGeneral="0.35"
			equalTags="0.75"
			cachedPrior="0.99"
			drop=2
		else
			label="ut=$threshold"
			similarGeneral=$threshold
		fi
	
		mkdir -p experiments/$experimentName/$sub/$folder
		echo "$label" >> experiments/$experimentName/$sub/summary
		python replica-simulator.py \
			--individualModel="$individualModel" \
			--similarSpecific="$similarSpecific" \
			--similarGeneral="$similarGeneral" \
			--equalTags="$equalTags" \
			--cachedPrior="$cachedPrior" \
			--drop="$drop" \
			--scenario="$scenarioFile" \
			--outdir experiments/$experimentName/$sub/$folder >> experiments/$experimentName/$sub/summary
	done
	
	for plot in $(ls plots/*.sh); do
		$plot $experimentName/$sub
	done
done

# Average utilization is ~= very special =~
python utilization.py experiments/$experimentName
for file in experiments/$experimentName/utilization_*.dat; do 
	sort $file -n -o $file 
done
./utilization-summary.sh $experimentName
