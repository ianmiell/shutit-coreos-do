"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class kubernetes_setup(ShutItModule):

	def check_ready(self, shutit):
		if shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['ssh_key_file'] == '':
			shutit.log('ssh_key_file in shutit.tk.coreos_do_setup.coreos_do_setup must be set to a filename with the ')
			return False
		return True

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		#https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-kubernetes-on-top-of-a-coreos-cluster
		shutit.send('sleep 60 # wait before trying to log in')
		master_public_ip = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets'][0]['public_ip']
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			private_ip = coreos_machine['private_ip']
			shutit.login(command='ssh core@' + public_ip, expect=' ~ ')
			shutit.send('sudo mkdir -p /opt/bin')
			shutit.send('docker run -i -t google/golang /bin/bash -c "go get github.com/coreos/flannel"')
			shutit.send('sudo docker cp $(docker ps -l -q):/gopath/bin/flannel /opt/bin/')
			shutit.logout()
		shutit.login(command='ssh core@' + master_public_ip, expect=' ~ ')
		shutit.send('git clone https://github.com/GoogleCloudPlatform/kubernetes.git')
		shutit.send('cd kubernetes/build')
		shutit.multisend('./release.sh',{'Download it now':'y'})
		shutit.send('cd ~/kubernetes/_output/dockerized/bin/linux/amd64')
		shutit.send('sudo mkdir -p /opt/bin')
		shutit.send('sudo cp * /opt/bin')
		shutit.send('cd /opt/bin')
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			if public_ip == master_public_ip:
				# No need to do this on master!
				continue
			shutit.multisend('tar -czf - . | ssh core@' + public_ip + ' "sudo mkdir -p /opt/bin; cd /opt/bin; sudo tar xzvf -"',{'connecting':'yes'},timeout=60)
		shutit.logout()
		# set up services by copying files
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			shutit.login(command='ssh core@' + public_ip, expect=' ~ ')
			if public_ip == master_public_ip:
				for filename in ('controller-manager.service','apiserver.service'):
					shutit.send_host_file('/tmp/' + filename,'context/master/' + filename)
					shutit.send('sudo cp /tmp/' + filename + ' /etc/systemd/system/' + filename)
					shutit.send('rm -f /tmp/' + filename)
			for filename in ('kubelet.service','proxy.service','docker.service','flannel.service','scheduler.service'):
				shutit.send_host_file('/tmp/' + filename,'context/all/' + filename)
				shutit.send('sudo cp /tmp/' + filename + ' /etc/systemd/system/' + filename)
				shutit.send('rm -f /tmp/' + filename)
			shutit.logout()
		# Now enable services
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			shutit.login(command='ssh core@' + public_ip, expect=' ~ ')
			shutit.send('cd /etc/systemd/system')
			shutit.send('sudo systemctl enable *')
			shutit.logout()
		# Now reboot
		self._set_token(shutit)
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			droplet_id = coreos_machine['droplet_id']
			shutit.send('''curl -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"type":"reboot"}' "https://api.digitalocean.com/v2/droplets/''' + droplet_id + '''/actions"''')
		# wait for it...
		shutit.send('sleep 120')
		return True

	def get_config(self, shutit):
		return True

	def _set_token(self, shutit):
		if shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['oauth_token'] != '':
			token = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['oauth_token']
		else:
			token = open(shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['oauth_token_file']).read().strip()
		shutit.send('export TOKEN=' + token)


	
def module():
	return kubernetes_setup(
		'shutit.tk.kubernetes_setup.kubernetes_setup', 158844783.002,
		description='Kubernetes on CoreOS',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.coreos_do_setup.coreos_do_setup']
	)

