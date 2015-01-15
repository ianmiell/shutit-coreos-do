"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class coreos_do_setup(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-coreos-cluster-on-digitalocean
		# NEED: an ssh key set up with digital ocean in a file - we take the first one seen from an API request
		# Read in the token
		self._set_token(shutit)
		# Get unique coreos discovery url
		shutit.send(r'''curl -s -w "\n" https://discovery.etcd.io/new''')
		discovery = shutit.get_output().strip()
		cloud_config = open('context/cloud-config').read().strip()
		cloud_config = string.replace(cloud_config,'DISCOVERY',discovery)
		if shutit.cfg[self.module_id]['ssh_key_id'] == '':
			shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -u "${TOKEN}:" "https://api.digitalocean.com/v2/account/keys" | jq -M '.ssh_keys[0].id'""")
			ssh_key_id = shutit.get_output().strip()
		else:
			ssh_key_id = shutit.cfg[self.module_id]['ssh_key_id']
		# Created droplets, in order
		shutit.cfg[self.module_id]['created_droplets'] = []
		for machine in range(1,int(shutit.cfg[self.module_id]['num_machines']) + 1):
			command = '''curl -s -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"coreos-''' + str(machine) + '''","region":"nyc3","size":"512mb","image":"coreos-stable","ssh_keys":["''' + ssh_key_id + '''"],"backups":false,"ipv6":true,"user_data":"''' + cloud_config + '''","private_networking":true}' "https://api.digitalocean.com/v2/droplets"'''
			shutit.send_file('/tmp/cmd.sh',command)
			shutit.send('cat /tmp/cmd.sh')
			shutit.send('sh /tmp/cmd.sh | jq ".droplet.id" -M')
			droplet_id = shutit.get_output().strip()
			shutit.send('rm -f /tmp/cmd.sh')
			shutit.send('sleep 60 #Wait a decent amount of time; this seems to be required',timeout=180)
			shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '''" | jq -M '.droplet.networks.v4[] | select(.type == "public") | ".ip_address"'""")
			public_ip = shutit.get_output().strip().strip('"')
			shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '''" | jq -M '.droplet.networks.v4[] | select(.type == "private") | ".ip_address"'""")
			private_ip = shutit.get_output().strip().strip('"')
			shutit.cfg['build']['report_final_messages'] += 'droplet_id: ' + droplet_id + ': ip address: ' + public_ip + '\nLog in with: ssh core@' + ip + '\n'
			if machine == 1:
				coreos_type = "master"
			else:
				coreos_type = "minion"
			shutit.cfg[self.module_id]['created_droplets'].append({"droplet_id":droplet_id,"coreos_type":coreos_type,"public_ip":public_ip,"private_ip":private_ip,"ssh_key_id":ssh_key_id})
		return True

	def get_config(self, shutit):
		# oauth access token filename, defaults to context/access_token.dat
		shutit.get_config(self.module_id,'oauth_token','')
		shutit.get_config(self.module_id,'oauth_token_file','context/access_token.dat')
		shutit.get_config(self.module_id,'ssh_key_id','')
		shutit.get_config(self.module_id,'num_machines','3')
		# Whether to delete machines on finalization.
		shutit.get_config(self.module_id,'delete_machines',False,boolean=True)
		return True
	
	def finalize(self, shutit):
		if shutit.cfg[self.module_id]['delete_machines']:
			self._set_token(shutit)
			for droplet_id in shutit.cfg[self.module_id]['droplet_ids']:
				shutit.send('''curl -X DELETE -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '"')
		return True

	def _set_token(self, shutit):
		if shutit.cfg[self.module_id]['oauth_token'] != '':
			token = shutit.cfg[self.module_id]['oauth_token']
		else:
			token = open(shutit.cfg[self.module_id]['oauth_token_file']).read().strip()
		shutit.send('export TOKEN=' + token)

def module():
	return coreos_do_setup(
		'shutit.tk.coreos_do_setup.coreos_do_setup', 158844783.001,
		description='Digital Ocean CoreOS cluster setup',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.sd.curl.curl','shutit.tk.sd.jq.jq']
	)

