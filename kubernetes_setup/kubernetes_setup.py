"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class kubernetes_setup(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		#https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-kubernetes-on-top-of-a-coreos-cluster
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			private_ip = coreos_machine['private_ip']
			shutit.login(command='ssh core@' + public_ip, expect=' ~ ')
			shutit.send('sudo mkdir -p /opt/shutit')
			shutit.send('docker run -i -t google/golang /bin/bash -c "go get github.com/coreos/flannel"')
			shutit.send('sudo docker cp $(docker ps -l -q):/gopath/bin/flannel /opt/bin/')
			shutit.send('cd ~')
			shutit.send('git clone https://github.com/GoogleCloudPlatform/kubernetes.git')
			shutit.send('cd kubernetes/build')
			shutit.send('./release.sh')
			shutit.send('cd ~/kubernetes/_output/dockerized/bin/linux/amd64')
			shutit.send('sudo cp * /opt/bin')
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

