"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string
import re
import sys

class kubernetes_coreos_setup(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		# Read in the token
		import cluster_config
		cluster_config.cluster_config.set_token(shutit)
		if shutit.cfg[self.module_id]['ssh_key_id'] == '':
			shutit.send("""curl -s -X GET -H 'Content-Type: application/json' -u "${TOKEN}:" "https://api.digitalocean.com/v2/account/keys" | jq -M '.ssh_keys[0].id'""")
			ssh_key_id = shutit.get_output().strip()
		else:
			ssh_key_id = shutit.cfg[self.module_id]['ssh_key_id']
		# ssh keys
		shutit.send('mkdir -p /root/.ssh')
		if shutit.cfg[self.module_id]['ssh_key_file'] != '':
			shutit.send_host_file('/root/.ssh/' + shutit.cfg[self.module_id]['ssh_key_filename'],shutit.cfg[self.module_id]['ssh_key_file'])
			shutit.send('chmod 0600 /root/.ssh/' + shutit.cfg[self.module_id]['ssh_key_filename'])
		shutit.cfg[self.module_id]['created_droplets'] = []
		master_private_ip = ''
		master_public_ip = ''
		for machine in range(1,int(shutit.cfg[self.module_id]['num_machines']) + 1):
			# TODO: get these cloud configs direct from github: https://raw.githubusercontent.com/GoogleCloudPlatform/kubernetes/master/docs/getting-started-guides/coreos/cloud-configs/node.yaml and master.yaml
			if machine == 1:
				cloud_config = open('context/master/cloud-config').read().strip()
			else:
				cloud_config = open('context/node/cloud-config').read().strip()
				cloud_config = string.replace(cloud_config,'<master-private-ip>',master_private_ip)
			command = '''curl --stderr /tmp/err -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"coreos-''' + str(machine) + '''","region":"nyc3","size":"512mb","image":"coreos-stable","ssh_keys":["''' + ssh_key_id + '''"],"backups":false,"ipv6":true,"user_data":"''' + cloud_config + '''","private_networking":true}' "https://api.digitalocean.com/v2/droplets"'''
			shutit.send_file('/tmp/cmd.sh',command)
			shutit.send('sh /tmp/cmd.sh > /tmp/out')
			shutit.send('cat /tmp/err') #debug
			shutit.send('cat /tmp/out') #debug
			shutit.send('cat /tmp/out | jq ".droplet.id" -M')
			droplet_id = shutit.get_output().strip()
			shutit.pause_point('')
			shutit.send('rm -f /tmp/out')
			shutit.send('rm -f /tmp/cmd.sh')
			public_ip = 'none'
			private_ip = 'none'
			count = 0
			while not re.match('^[0-9.]+$',public_ip):
				count += 1
				if count > 20:
					print "failed to start a machine?"
					sys.exit(1)
				shutit.send('sleep 60 # Wait a decent amount of time; this seems to be required',timeout=180)
				shutit.send('''curl -s -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '''" > /tmp/out''')
				shutit.send('''cat /tmp/out | jq -M '.droplet.networks.v4[] | select(.type == "public") | .ip_address''' + "'")
				public_ip = shutit.get_output().strip().strip('"')
				shutit.send('''cat /tmp/out | jq -M '.droplet.networks.v4[] | select(.type == "private") | .ip_address''' + "'")
				private_ip = shutit.get_output().strip().strip('"')
				shutit.send('''rm -f /tmp/out''')
			shutit.log('droplet_id: ' + droplet_id + ': ip address: ' + public_ip + '\nLog in with: ssh core@' + public_ip, add_final_message=True)
			shutit.cfg[self.module_id]['created_droplets'].append({"droplet_id":droplet_id,"public_ip":public_ip,"private_ip":private_ip,"ssh_key_id":ssh_key_id})
			if machine == 1:
				master_public_ip = public_ip
				master_private_ip = private_ip
		shutit.send('sleep 100 # Wait a decent amount of time; this seems to be required to allow ssh to start up',timeout=180)
		shutit.login(command='ssh core@' + master_public_ip, expect=' ~ ')
		shutit.send('git clone https://github.com/GoogleCloudPlatform/kubernetes.git')
		shutit.send('cd kubernetes')
		shutit.multisend('hack/dev-build-and-up.sh',{'Download it now':'y'})
		shutit.send('cd ~/kubernetes/_output/dockerized/bin/linux/amd64')
		shutit.send('sudo mkdir -p /opt/bin')
		# Copy all except ones already there
		shutit.send('ls | egrep -v "(kube-apiserver|kube-controller-manager|kube-scheduler)" | xargs -IXXX sudo cp XXX /opt/bin')
		shutit.send('cd /opt/bin')
		shutit.send('tar -cf /tmp/kub.tar .')
		shutit.logout()
		# copy the executables over
		shutit.multisend('scp core@' + master_public_ip + ':/tmp/kub.tar /tmp/kub.tar',{'connecting':'yes'})
		for coreos_machine in shutit.cfg[self.module_id]['created_droplets']:
			public_ip = coreos_machine['public_ip']
			if public_ip == master_public_ip:
				# No need to do this on master!
				continue
			shutit.multisend('scp /tmp/kub.tar core@' + public_ip + ':/tmp/kub.tar',{'connecting':'yes'})
			shutit.login(command='ssh core@' + public_ip, expect=' ~ ')
			shutit.send('cd /opt/bin')
			shutit.send('sudo tar -xf /tmp/kub.tar .')
			shutit.send('rm -f /tmp/kub.tar')
			shutit.logout()
		shutit.send('rm -f /tmp/kub.tar')
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'ssh_key_id','')
		shutit.get_config(self.module_id,'num_machines','3')
		shutit.get_config(self.module_id,'ssh_key_file','')
		shutit.get_config(self.module_id,'ssh_key_filename','id_rsa')
		# Whether to delete machines on finalization.
		shutit.get_config(self.module_id,'delete_machines',False,boolean=True)
		return True
	
	def finalize(self, shutit):
		if shutit.cfg[self.module_id]['delete_machines']:
			cluster_config.set_token(shutit)
			for droplet_data in shutit.cfg[self.module_id]['created_droplets']:
				shutit.send('''curl -X DELETE -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" "https://api.digitalocean.com/v2/droplets/''' + droplet_data['droplet_id'] + '"')
		shutit.send('rm -rf /root/.ssh')
		return True

def module():
	return kubernetes_coreos_setup(
		'shutit.tk.kubernetes_coreos_setup.kubernetes_coreos_setup', 158844783.0015,
		description='Digital Ocean CoreOS kubernetes cluster setup',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.cluster_config.cluster_config','shutit.tk.sd.curl.curl','shutit.tk.sd.jq.jq','shutit.tk.sd.openssh.openssh']
	)

