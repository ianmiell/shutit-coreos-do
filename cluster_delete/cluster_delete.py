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
		import cluster_config
		cluster_config.cluster_config.set_token(shutit)
		shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/" | jq '.droplets[] | .id' -M""")
		droplet_ids = shutit.get_output().strip()
		droplet_id_list = droplet_ids.split()
		for droplet_id in droplet_id_list:
			shutit.send('''curl -s -X DELETE -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '"')
			shutit.log('droplet_id ' + droplet_id + ' deleted.', add_final_message=True)
		return True

	def get_config(self, shutit):
		return True
	
	def finalize(self, shutit):
		return True

def module():
	return cluster_delete(
		'shutit.tk.cluster_delete.cluster_delete', 158844783.003,
		description='Digital Ocean CoreOS deletion',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.cluster_config.cluster_config','shutit.tk.sd.curl.curl','shutit.tk.sd.jq.jq']
	)

