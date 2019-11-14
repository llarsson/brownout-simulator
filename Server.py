from collections import defaultdict, deque
import random
import numpy as np

from utils import *

## Represents a brownout compliant server.
# Current implementation simulates processor-sharing with an infinite number of
# concurrent requests and a fixed time-slice.
class Server:
	## Variable used for giving IDs to servers for pretty-printing
	lastServerId = 1

	## Constructor.
	# @param sim Simulator to attach the server to
	# @param minimumServiceTime minimum service-time (despite variance)
	# @param timeSlice time slice; a request longer that this will observe
	# context-switching
	# @param initialTheta initial dimmer value
	# @param controlPeriod control period of brownout controller (0 = disabled)
	# @note The constructor adds an event into the simulator
	def __init__(self, sim, quality_levels, thresholds,
			initialTheta = 0.5, controlPeriod = 5,
			timeSlice = 0.01, minimumServiceTime = 0.0001,
			utilizationReadingInterval = 0):
		self.quality_levels = quality_levels
		## time slice for scheduling requests (server model parameter)
		self.timeSlice = timeSlice
		## minimum service time, despite variance (server model parameter)
		self.minimumServiceTime = minimumServiceTime
		## list of active requests (server model variable)
		self.activeRequests = deque()

		## control period (controller parameter)
		self.controlPeriod = controlPeriod # second
		## setpoint (controller parameter)
		self.setPoint = 1
		## initialization for the RLS estimator (controller variable)
		self.rlsP = 1000
		## RLS forgetting factor (controller parameter)
		self.rlsForgetting = 0.95
		## Current alpha (controller variable)
		self.alpha = 1
		## Pole (controller parameter)
		self.pole = 0.9
		## latencies measured during last control period (controller input)
		self.latestLatencies = []
		## dimmer value (controller output)
		self.theta = initialTheta

		## The amount of time this server is active. Useful to compute utilization
		# Since we are in a simulator, this value is hard to use correctly. Use getActiveTime() instead.
		self.__activeTime = 0
		## The time when the server became last active (None, not currently active)
		self.__activeTimeStarted = None
		## Value used to compute utilization
		self.lastActiveTime = 0

		## Server ID for pretty-printing
		self.name = 'server' + str(Server.lastServerId)
		Server.lastServerId += 1

		## Current utilization
		self.utilization = 0
		self.utilizationReadings = []
		self.cachedUtilizationReading = 0
		self.cachedUtilizationReadingTimestamp = 0
		self.utilizationReadingInterval = utilizationReadingInterval
		self.thresholds = thresholds

		## Reference to simulator
		self.sim = sim
		if self.controlPeriod > 0:
			self.sim.add(0, self.runControlLoop)
	
	def getUtilization(self):
		if not self.utilizationReadingInterval:
			return self.utilization

		if self.sim.now > self.cachedUtilizationReadingTimestamp + self.utilizationReadingInterval:
			self.cachedUtilizationReading = self.utilization
			self.cachedUtilizationReadingTimestamp = self.sim.now
		return self.cachedUtilizationReading


	## Compute the (simulated) amount of time this server has been active.
	# @note In a real OS, the active time would be updated at each context switch.
	# However, this is a simulation, therefore, in order not to waste time on
	# simulating context-switches, we compute this value when requested, as if it
	# were continuously update.
	def getActiveTime(self):
		ret = self.__activeTime
		if self.__activeTimeStarted is not None:
			ret += self.sim.now - self.__activeTimeStarted
		return ret

	## Runs the control loop.
	# Basically retrieves self.lastestLatencies and computes a new self.theta.
	# Ask Martina for details. :P
	def runControlLoop(self):
		if self.latestLatencies:
			# Possible choices: max or avg latency control
			#serviceTime = avg(self.latestLatencies) # avg latency
			# serviceTime = max(self.latestLatencies) # max latency
			serviceTime = np.percentile(self.latestLatencies, 95) # 95 percentile
			serviceLevel = self.theta

			# choice of the estimator:
			# ------- bare estimator
			# self.alpha = serviceTime / serviceLevel # very rough estimate
			# ------- RLS estimation algorithm
			a = self.rlsP*serviceLevel
			g = 1 / (serviceLevel*a + self.rlsForgetting)
			k = g*a
			e = serviceTime - serviceLevel*self.alpha
			self.alpha = self.alpha + k*e
			self.rlsP  = (self.rlsP - g * a*a) / self.rlsForgetting
			# end of the estimator - in the end self.alpha should be set
			
			error = self.setPoint - serviceTime
			# NOTE: control knob allowing slow increase
			#if error > 0:
			#	error *= 0.1
			variation = (1 / self.alpha) * (1 - self.pole) * error
			serviceLevel += self.controlPeriod * variation

			# saturation, it's a probability
			self.theta = min(max(serviceLevel, 0.0), 1.0)
		
		# Compute utilization
		self.utilization = (self.getActiveTime() - self.lastActiveTime) / self.controlPeriod
		self.utilizationReadings.append(self.utilization)
		self.lastActiveTime = self.getActiveTime()

		# Report
		if not self.latestLatencies:
			self.latestLatencies.append(float('nan'))
		valuesToOutput = [ \
			self.sim.now, \
			avg(self.latestLatencies), \
			np.percentile(self.latestLatencies, 95), \
			np.percentile(self.latestLatencies, 99), \
			maxOrNan(self.latestLatencies), \
			self.theta, \
			self.utilization, \
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Re-run later
		self.latestLatencies = []
		self.sim.add(self.controlPeriod, self.runControlLoop)

	## Tells the server to serve a request.
	# @param request request to serve
	# @note When request completes, request.onCompleted() is called.
	# The following attributes are added to the request:
	# <ul>
	#   <li>theta, the current dimmer value</li>
	#   <li>arrival, time at which the request was first <b>scheduled</b>.
	#     May be arbitrary later than when request() was called</li>
	#   <li>completion, time at which the request finished</li>
	# </ul>
	def request(self, request):
		# Activate scheduler, if its not active
		if len(self.activeRequests) == 0:
			self.sim.add(0, self.onScheduleRequests)
		# Add request to list of active requests
		self.activeRequests.append(request)

		# Report queue length
		valuesToOutput = [ \
			self.sim.now, \
			len(self.activeRequests), \
		]
		self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))


	def is_brownout(self):
		threshold = [t for t in self.thresholds if t['name'] == 'similar-general'][0]
		return threshold['level'] > 660


	def quality_level_index(self, name):
		for (index, level) in enumerate(self.thresholds):
			if level['name'] == name:
				return index
		raise KeyError(name)


	def determineServiceTime(self, activeRequest):
		"Returns service time and variance thereof"
		quality_level = 'drop' # sane default :D
		if self.is_brownout():
			# Original from Brownout paper, which understands only
			# two quality levels.
			activeRequest.withOptional = random.random() <= self.theta
			if activeRequest.withOptional:
				quality_level = 'similar-general'
			else:
				quality_level = 'drop'
		else:
			for threshold in self.thresholds:
				if self.getUtilization() <= threshold['level']:
					quality_level = threshold['name']
					break
			activeRequest.withOptional = (quality_level != 'drop')

		activeRequest.qualityLevel = self.quality_level_index(quality_level)

		return (self.quality_levels[quality_level]['service_time'],\
				self.quality_levels[quality_level]['variance']) 


	## Event handler for scheduling active requests.
	# This function is the core of the processor-sharing with time-slice model.
	# This function is called when "context-switching" occurs. There must be at
	# most one such event registered in the simulation.
	# This function is invoked in the following cases:
	# <ul>
	#   <li>By request(), when the list of active requests was previously empty.
	#   </li>
	#   <li>By onCompleted(), to pick a new request to schedule</li>
	#   <li>By itself, when a request is preempted, i.e., context-switched</li>
	# </ul>
	def onScheduleRequests(self):
		#self.sim.log(self, "scheduling")
		# Select next active request
		activeRequest = self.activeRequests.popleft()
		
		# Track utilization
		if self.__activeTimeStarted is None:
			self.__activeTimeStarted = self.sim.now

		# Has this request been scheduled before?
		if not hasattr(activeRequest, 'remainingTime'):
			#self.sim.log(self, "request {0} entered the system", activeRequest)
			# Pick whether to serve it with optional content or not
			activeRequest.arrival = self.sim.now
			activeRequest.theta = self.theta

			serviceTime, variance = self.determineServiceTime(activeRequest)

			activeRequest.remainingTime = \
				max(random.normalvariate(serviceTime, variance), self.minimumServiceTime)

		# Schedule it to run for a bit
		timeToExecuteActiveRequest = min(self.timeSlice, activeRequest.remainingTime)
		activeRequest.remainingTime -= timeToExecuteActiveRequest

		# Will it finish?
		if activeRequest.remainingTime == 0:
			# Leave this request in front (onCompleted will pop it)
			self.activeRequests.appendleft(activeRequest)

			# Run onComplete when done
			self.sim.add(timeToExecuteActiveRequest, \
				lambda: self.onCompleted(activeRequest))
			#self.sim.log(self, "request {0} will execute for {1} to completion", \
			#	activeRequest, timeToExecuteActiveRequest)
		else:
			# Reintroduce it in the active request list at the end for
			# round-robin scheduling
			self.activeRequests.append(activeRequest)

			# Re-run scheduler when time-slice has expired
			self.sim.add(timeToExecuteActiveRequest, self.onScheduleRequests)
			#self.sim.log(self, "request {0} will execute for {1} not to completion",\
			#	activeRequest, timeToExecuteActiveRequest)

	## Event handler for request completion.
	# Marks the request as completed, calls request.onCompleted() and calls
	# onScheduleRequests() to pick a new request to schedule.
	# @param request request that has received enough service time
	def onCompleted(self, request):
		# Track utilization
		self.__activeTime += self.sim.now - self.__activeTimeStarted
		self.__activeTimeStarted = None

		# Remove request from active list
		activeRequest = self.activeRequests.popleft()
		if activeRequest != request:
			raise Exception("Weird! Expected request {0} but got {1} instead". \
				format(request, activeRequest))

		# And completed it
		request.completion = self.sim.now
		self.latestLatencies.append(request.completion - request.arrival)
		request.onCompleted()

		# Report
		valuesToOutput = [ \
			self.sim.now, \
			request.arrival, \
			request.completion - request.arrival, \
		]
		self.sim.output(str(self)+'-rt', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Report queue length
		valuesToOutput = [ \
			self.sim.now, \
			len(self.activeRequests), \
		]
		self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Report quality level
		valuesToOutput = [ \
			self.sim.now, \
			request.arrival, \
			request.completion - request.arrival, \
		]
		self.sim.output(str(self)+'-quality', ','.join(["{0:.5f}".format(value) \
				for value in valuesToOutput]) + "," + str(request.qualityLevel))

		# Report utilization level
		valuesToOutput = [ \
			self.sim.now, \
			request.arrival, \
			request.completion - request.arrival, \
			self.utilization \
		]
		self.sim.output(str(self)+'-utilization', ','.join(["{0:.5f}".format(value) \
				for value in valuesToOutput]))

		# Continue with scheduler
		if len(self.activeRequests) > 0:
			self.sim.add(0, self.onScheduleRequests)

	## Pretty-print server's ID
	def __str__(self):
		return str(self.name)

