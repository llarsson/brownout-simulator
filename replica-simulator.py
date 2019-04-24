#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import numpy as np
import random

from Clients import *
from Request import *
from Server import *
from SimulatorKernel import *

## @package simulator Main simulator namespace

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout replica simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--outdir',
		help = 'Destination folder for results and logs',
		default = '.')
	parser.add_argument('--timeSlice',
		type = float,
		help = 'Time-slice of server scheduler',
		default = 0.01)
	parser.add_argument('--controlPeriod',
		help = 'Specify the control period of the replica controller',
		default = 0.5)
	parser.add_argument('--individualModel',
		help = 'Utilization threshold for the individual-model quality',
		default = 2.0)
	parser.add_argument('--similarSpecific',
		help = 'Utilization threshold for the similar-specific quality',
		default = 2.0)
	parser.add_argument('--similarGeneral',
		help = 'Utilization threshold for the similar-general quality',
		default = 0.5)
	parser.add_argument('--equalTags',
		help = 'Utilization threshold for the equal-tags quality',
		default = 2.0)
	parser.add_argument('--cachedPrior',
		help = 'Utilization threshold for the cached-prior quality',
		default = 2.0)
	parser.add_argument('--drop',
		help = 'Utilization threshold for the drop quality',
		default = 2.0)
	parser.add_argument('--scenario',
		help = 'Specify a scenario in which to test the system',
		default = os.path.join(os.path.dirname(sys.argv[0]), 'scenarios', 'replica-test-1.py'))
	args = parser.parse_args()

	quality_levels = {
			'individual-model': {'service_time': 0.03000, 'variance': 0.1000},
			'similar-specific': {'service_time': 0.01400, 'variance': 0.0150},
			'similar-general':  {'service_time': 0.00700, 'variance': 0.0100},
			'equal-tags':       {'service_time': 0.00250, 'variance': 0.0080},
			'cached-prior':     {'service_time': 0.00085, 'variance': 0.0015},
			'drop':             {'service_time': 0.00067, 'variance': 0.0010}
			}

	thresholds = [ 
			{'name': 'individual-model', 'level': float(args.individualModel)},
			{'name': 'similar-specific', 'level': float(args.similarSpecific)},
			{'name': 'similar-general',  'level': float(args.similarGeneral)},
			{'name': 'equal-tags',       'level': float(args.equalTags)},
			{'name': 'cached-prior',     'level': float(args.cachedPrior)},
			{'name': 'drop',             'level': float(args.drop)},
			]

	print(str(thresholds))

	random.seed(1)
	sim = SimulatorKernel(outputDirectory = args.outdir)
	server = Server(sim, quality_levels, thresholds, 
			controlPeriod = args.controlPeriod,
			timeSlice = args.timeSlice)
	clients = []
	openLoopClient = OpenLoopClient(sim, server)

	# Define verbs for scenarios
	def addClients(at, n):
		def addClientsHandler():
			for _ in range(0, n):
				clients.append(ClosedLoopClient(sim, server))
		sim.add(at, addClientsHandler)

	def delClients(at, n):
		def delClientsHandler():
			for _ in range(0, n):
				client = clients.pop()
				client.deactivate()
		sim.add(at, delClientsHandler)

	def changeServiceTime(at, y, n):
		def changeServiceTimeHandler():
			server.serviceTimeY = y
			server.serviceTimeN = n
		sim.add(at, changeServiceTimeHandler)
		
	def setRate(at, rate):
		sim.add(at, lambda: openLoopClient.setRate(rate))

	def endOfSimulation(at):
		otherParams['simulateUntil'] = at

	# Load scenario
	otherParams = {}
	execfile(args.scenario)
	
	if 'simulateUntil' not in otherParams:
		raise Exception("Scenario does not define end-of-simulation")
	sim.run(until = otherParams['simulateUntil'])

	# Report end results
	responseTimes = reduce(lambda x,y: x+y, [client.responseTimes for client in clients]) + openLoopClient.responseTimes

	toReport = []
	toReport.append(("numRequests", len(responseTimes)))
	numRequestsWithOptional = sum([client.numCompletedRequestsWithOptional for client in clients]) + openLoopClient.numCompletedRequestsWithOptional
	toReport.append(("numRequestsWithOptional", numRequestsWithOptional))
	toReport.append(("avgResponseTime", avg(responseTimes)))
	toReport.append(("p95ResponseTime", np.percentile(responseTimes, 95)))
	toReport.append(("p99ResponseTime", np.percentile(responseTimes, 99)))
	toReport.append(("maxResponseTime", max(responseTimes)))
	toReport.append(("optionalRatio", numRequestsWithOptional / len(responseTimes)))
	toReport.append(("stddevResponseTime", np.std(responseTimes)))
	toReport.append(("profit", 1.5 * numRequestsWithOptional + (len(responseTimes) - numRequestsWithOptional)))
	toReport.append(("avgUtilization", float(sum(server.utilizationReadings)) / len(server.utilizationReadings) ))

	print(*[k for k,v in toReport], sep = ',')
	print(*[v for k,v in toReport], sep = ',')

if __name__ == "__main__":
	main()
