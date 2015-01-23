"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class pachyderm(ShutItModule):

	def check_ready(self, shutit):
		return True

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		#https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-kubernetes-on-top-of-a-coreos-cluster
		shutit.send('sleep 30 # wait before trying to log in')
		master_public_ip = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets'][0]['public_ip']
		master_private_ip = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets'][0]['private_ip']
		shutit.login(command='ssh core@' + master_public_ip, expect=' ~ ')
		shutit.send('wget -qO- https://github.com/pachyderm-io/pfs/raw/master/deploy/static/1Node.tar.gz | tar -zxf -')
		shutit.send('fleetctl start 1Node/*')
		shutit.pause_point('')
		return True

	def get_config(self, shutit):
		return True

def module():
	return pachyderm(
		'shutit.tk.pachyderm.pachyderm', 158844783.005,
		description='Pachyderm on CoreOS',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.cluster_config.cluster_config','shutit.tk.coreos_do_setup.coreos_do_setup']
	)

