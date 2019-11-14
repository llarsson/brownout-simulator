import random
from abc import ABC, abstractmethod

class LoadBalancer(ABC):
	def __init__(self):
		self.servers = []

	def setServers(self, servers):
		self.servers = servers

	@abstractmethod
	def request(self, request):
		pass

class RoundRobinLoadBalancer(LoadBalancer):
	def __init__(self):
		super()
		self.server_index = 0
	
	def request(self, request):
		self.server_index = (self.server_index + 1) % len(self.servers)
		return self.servers[self.server_index].request(request)


class RandomLoadBalancer(LoadBalancer):
	def __init__(self):
		super()
	
	def request(self, request):
		return random.choice(self.servers).request(request)
