"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class digital_ocean(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-coreos-cluster-on-digitalocean
		# NEED: an ssh key set up with digital ocean - we take the first one seen from an API request
		# Read in the token
		token = open(shutit.cfg[self.module_id]['oauth_token_file']).read().strip()
		shutit.send('export TOKEN=' + token)
		shutit.send(r'''curl -s -w "\n" https://discovery.etcd.io/new''')
		# Get unique coreos discovery url
		discovery = shutit.get_output().strip()
		cloud_config = open('context/cloud-config').read().strip()
		cloud_config = string.replace(cloud_config,'DISCOVERY',discovery)
		print cloud_config
		if shutit.cfg[self.module_id]['ssh_key_id'] == '':
			shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -u "${TOKEN}:" "https://api.digitalocean.com/v2/account/keys" | jq -M '.ssh_keys[0].id'""")
			ssh_key = shutit.get_output().strip()
		else:
			ssh_key = shutit.cfg[self.module_id]['ssh_key_id']
		for machine in range(1,int(shutit.cfg[self.module_id]['num_machines']) + 1):
			command = '''curl -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"coreos-''' + str(machine) + '''","region":"nyc3","size":"512mb","image":"coreos-stable","ssh_keys":["''' + ssh_key + '''"],"backups":false,"ipv6":true,"user_data":null,"private_networking":null}' "https://api.digitalocean.com/v2/droplets"'''
			shutit.send_file('/tmp/cmd.sh',command)
			shutit.send('sh /tmp/cmd.sh')
			shutit.send('rm -f /tmp/cmd.sh')
			shutit.send('sleep 60',timeout=180)
		return True

	def get_config(self, shutit):
		# oauth access token filename, defaults to context/access_token.dat
		shutit.get_config(self.module_id,'oauth_token_file','context/access_token.dat')
		shutit.get_config(self.module_id,'ssh_key_id','')
		shutit.get_config(self.module_id,'num_machines','1')
		return True
	
	#def finalize(self, shutit):
	#	return True

	#def test(self, shutit):
	#	return True

def module():
	return digital_ocean(
		'shutit.tk.coreos_do_setup.coreos_do_setup', 158844783.001,
		description='Digital Ocean CoreOS setup',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.sd.curl.curl','shutit.tk.sd.jq.jq']
	)

