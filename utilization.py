#!/usr/bin/env python


def gather(experiment_name):
	experiments = ['1client', '2client', '4client', '8client', '16client', '32client', '64client', '128client', '200client', '256client' ]

	results = {}

	for (index, experiment) in enumerate(experiments):
		summary = []

		with open("%s/%s/summary" % (experiment_name, experiment)) as summary_file:
			summary = summary_file.readlines()

		offset = 0

		while offset + 4 <= len(summary):
			approach = summary[offset].strip()
			info = summary[offset+1].strip()
			headers = summary[offset+2].strip()
			data = summary[offset+3].strip()

			avg_utilization = data.split(',')[-1]

			if approach not in results:
				results[approach] = {}

			results[approach][experiment.split('c')[0]] = avg_utilization

			offset += 4

	return results


if __name__=='__main__':
	import sys
	import pprint

	if (len(sys.argv) != 2):
		experiment = 'experiments/lol'
	else:
		experiment = sys.argv[1]

	results = gather(experiment)

	for approach in results:
		with open("%s/utilization_%s.dat" % (experiment, approach), 'w+') as outfile:
			for e in results[approach]:
				outfile.write("%s %s\n" % (e, results[approach][e]))
