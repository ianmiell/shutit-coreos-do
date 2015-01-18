"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class cluster_config(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'oauth_token','')
		shutit.get_config(self.module_id,'oauth_token_file','context/access_token.dat')
		return True
	
	@staticmethod
	def set_token(shutit):
		if shutit.cfg['shutit.tk.cluster_config.cluster_config']['oauth_token'] != '':
			token = shutit.cfg['shutit.tk.cluster_config.cluster_config']['oauth_token']
		else:
			token = open(shutit.cfg['shutit.tk.cluster_config.cluster_config']['oauth_token_file']).read().strip()
		shutit.send('export TOKEN=' + token)

def module():
	return cluster_config(
		'shutit.tk.cluster_config.cluster_config', 158844783.0001,
		description='Digital Ocean CoreOS core config',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.setup']
	)

