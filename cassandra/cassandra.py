"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class cassandra(ShutItModule):

	def check_ready(self, shutit):
		return False

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		import cluster_config
		cluster_config.cluster_config.set_token(shutit)
		shutit.send_host_file('/tmp/cassandra.yaml','context/cassandra.yaml')
		shutit.send_host_file('/tmp/cassandra-service.yaml','context/cassandra-service.yaml')
		shutit.send_host_file('/tmp/cassandra-controller.yaml','context/cassandra-controller.yaml')
		shutit.send('kubectl create -f cassandra.yaml')
		shutit.send('kubectl create -f cassandra-service.yaml')
		shutit.send('kubectl create -f cassandra-controller.yaml')
		return True

	def get_config(self, shutit):
		return True

def module():
	return cassandra(
		'shutit.tk.cassandra.cassandra', 158844783.004,
		description='Cassandra and Kubernetes on CoreOS',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.kubernetes_setup.kubernetes_setup']
	)

