#!/bin/bash

set -eo pipefail

experimentName=$1

if [ -z $experimentName ]; then
	experimentName=$(date +'%y%m%d.%H%M')
fi

if [ -d experiments/$experimentName ]; then
	rm -rf experiments/$experimentName
fi

for setpoint in 0.05 0.1 0.15 0.2; do # 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1; do
	for pole in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1; do
		sub="sp-${setpoint}-pole-${pole}"
		scenarioFile="scenarios/replica-test-1.py"

		sed -i Server.py -e "s/self.setPoint = .*/self.setPoint = ${setpoint}/g"
		sed -i Server.py -e "s/self.pole = .*/self.pole = ${pole}/g"
	
		for threshold in -1 666 0.50 0.95 200 1337; do
			label=$threshold
			folder=$threshold
		
			individualModel="-1"
			similarSpecific="-1"
			similarGeneral="-1"
			equalTags="-1"
			cachedPrior="-1"
			drop=2
		
			if [ $threshold == "666" ]; then
				label="Brownout"
				folder=$label
				similarGeneral=$threshold
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

		profit=$(grep -A 3 Brownout experiments/${experimentName}/${sub}/summary | tail -n 1 | cut -d ',' -f 9)

		echo "${setpoint} ${pole} ${profit}" >> experiments/${experimentName}/brownout_profit
	done
done
