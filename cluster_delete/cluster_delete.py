"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class cluster_delete(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-coreos-cluster-on-digitalocean
		# NEED: an ssh key set up with digital ocean in a file - we take the first one seen from an API request
		# Read in the token
		self._set_token(shutit)
		shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/" | jq '.droplets[] | .id' -M""")
		droplet_ids = shutit.get_output().strip()
		droplet_id_list = droplet_ids.split()
		for droplet_id in droplet_id_list:
			shutit.send('''curl -s -X DELETE -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '"')
            shutit.log('droplet_id ' + droplet_id + ' deleted.', add_final_message=True)
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'oauth_token','')
		shutit.get_config(self.module_id,'oauth_token_file','context/access_token.dat')
		return True
	
	def finalize(self, shutit):
		return True

	def _set_token(self, shutit):
		if shutit.cfg[self.module_id]['oauth_token'] != '':
			token = shutit.cfg[self.module_id]['oauth_token']
		else:
			token = open(shutit.cfg[self.module_id]['oauth_token_file']).read().strip()
		shutit.send('export TOKEN=' + token)

def module():
	return cluster_delete(
		'shutit.tk.cluster_delete.cluster_delete', 158844783.003,
		description='Digital Ocean CoreOS deletion',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.sd.curl.curl','shutit.tk.sd.jq.jq']
	)

