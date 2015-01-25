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
		master_public_ip = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets'][0]['public_ip']
		master_private_ip = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets'][0]['private_ip']
		shutit.send('sleep 120 # wait before trying to log in')
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			shutit.login(command='ssh core@' + public_ip, expect=' ~ ')
			shutit.login(command='sudo su', expect='coreos')
			for coreos_machine2 in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
				public_ip = coreos_machine2['public_ip']
				private_ip = coreos_machine2['private_ip']
				hostname = coreos_machine2['hostname']
				shutit.send('echo "' + private_ip + ' ' + hostname + '" >> /etc/hosts')
			shutit.logout()
			shutit.logout()
		shutit.login(command='ssh core@' + master_public_ip, expect=' ~ ')
		shutit.send('wget -qO- https://github.com/pachyderm-io/pfs/raw/master/deploy/static/1Node.tar.gz | tar -zxf -')
		shutit.send('fleetctl start 1Node/*')
		shutit.send('git clone https://github.com/pachyderm/chess.git')
		shutit.send('cd chess/data')
		shutit.send('./send_sample chess')
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

