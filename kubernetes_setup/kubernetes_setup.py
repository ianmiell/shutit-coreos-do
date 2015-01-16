"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class kubernetes_setup(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		#https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-kubernetes-on-top-of-a-coreos-cluster
		shutit.send('sleep 60 # wait before trying to log in')
		master_public_ip = shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets'][0]['public_ip']
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			private_ip = coreos_machine['private_ip']
			shutit.login(command='ssh -A core@' + public_ip, expect=' ~ ')
			shutit.send('sudo mkdir -p /opt/bin')
			shutit.send('docker run -i -t google/golang /bin/bash -c "go get github.com/coreos/flannel"')
			shutit.send('sudo docker cp $(docker ps -l -q):/gopath/bin/flannel /opt/bin/')
			shutit.logout()
		# Copy over kub binaries
		shutit.login(command='ssh -A core@' + master_public_ip, expect=' ~ ')
		shutit.send('cd ~')
		shutit.send('git clone https://github.com/GoogleCloudPlatform/kubernetes.git')
		shutit.send('cd kubernetes/build')
		shutit.multisend('./release.sh',{'Download it now':'y'})
		shutit.send('cd ~/kubernetes/_output/dockerized/bin/linux/amd64')
		shutit.send('sudo cp * /opt/bin')
		shutit.send('cd /opt/bin')
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			if public_ip == master_public_ip:
				# No need to do this on master!
				continue
			shutit.multisend('tar -czf - . | ssh core@' + public_ip + ' "sudo mkdir -p /opt/bin; cd /opt/bin; sudo tar xzvf -"',{'connecting':'yes'})
			shutit.pause_point('')
		shutit.logout()
		return True

	def get_config(self, shutit):
		return True
	
def module():
	return kubernetes_setup(
		'shutit.tk.kubernetes_setup.kubernetes_setup', 158844783.002,
		description='Kubernetes on CoreOS',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.coreos_do_setup.coreos_do_setup']
	)

