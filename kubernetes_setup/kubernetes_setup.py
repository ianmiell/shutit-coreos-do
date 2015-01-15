"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string

class kubernetes_setup(ShutItModule):

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		#From: https://github.com/bketelsen/coreos-kubernetes-digitalocean
		#shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']
		#Step 4
		#Install Flannel so that each pod in the Kubernetes cluster can have it's own IP address.
		#When you're done you should have flannel installed at /opt/bin/flannel
		for coreos_machine in shutit.cfg['shutit.tk.coreos_do_setup.coreos_do_setup']['created_droplets']:
			public_ip = coreos_machine['public_ip']
			shutit.pause_point(public_ip)
			shutit.login(command='ssh core@' + public_ip)
			shutit.send('git clone https://github.com/coreos/flannel.git')
			shutit.send('cd flannel')
			shutit.send('docker run -v $(pwd):/opt/flannel -i -t google/golang /bin/bash -c "cd /opt/flannel && ./build"')
			shutit.pause_point('/opt/bin/flannel / rudder?')
			shutit.logout()

#
#Step 5
#Configure Rudder on each machine.
#In /etc/systemd/system on each CoreOS machine, create a service file for rudder. Use this one as a template. Replace the line IP address my template with the correct PRIVATE IP address for that machine. Remember you can get that by typing ifconfig. My private IP addresses were on eth1.
#Repeat this process for all three machines, ensuring that you use each machine's private ip address in the rudder.service file.
#Add the service to systemctl: sudo systemctl enable /etc/systemd/system/rudder.service
#Reload systemctl: sudo systemctl daemon-reload
#Start Rudder: sudo systemctl start rudder
#
#Step 6
#Follow this same pattern to add docker, kubelet, and proxy services to all three machines. Remember to use YOUR private IP address in the kubelet.service file. Add each service, reload systemctl and start each service.
#
#Step 7
#On the master, add apiserver and controller-manager. In the apiserver.service file, list the private IP addresses of all three CoreOS machines on Line 15
#
#*** Important - you need to add a scheduler service now, too. I'll try to add a service unit for this shortly. ***
#
#Step 8
#Download kubecfg pre-built binaries by following the instructions at the bottom of Kelsey Hightower's Guide I put mine in /opt/bin
#With any luck you'll now have a fully operational Kubernetes cluster running on Digital Ocean. To test it type kubecfg list minions. You should see all three private ip addresses of your cluster listed in the result.
		return True

	def get_config(self, shutit):
		return True
	
def module():
	return kubernetes_setup(
		'shutit.tk.kubernetes_setup.kubernetes_setup', 158844783.002,
		description='Digital Ocean CoreOS cluster setup',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.coreos_do_setup.coreos_do_setup','shutit.tk.sd.openssh.openssh']
	)

