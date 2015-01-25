"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string
import time

class deis(ShutItModule):

	def check_ready(self, shutit):
		return True

	def is_installed(self, shutit):
		return False

	def build(self, shutit):
		import cluster_config
		token = cluster_config.cluster_config.get_token(shutit)
		domain = shutit.cfg[self.module_id]['domain']
		shutit.send('mkdir -p /opt/deis')
		shutit.send('cd /opt/deis')
		shutit.send('gem install docl')
		shutit.send('git clone https://github.com/deis/deis.git')
		shutit.send('cd deis')
		shutit.send('make discovery-url')
		# TODO: give each key a unique name
		ssh_key_name = 'deis_' + str(time.time())
		shutit.send('''ssh-keygen -q -t rsa -f ~/.ssh/''' + ssh_key_name + ''' -N '' -C deis''')
		shutit.multisend('docl authorize',{'Enter your DO Token:':token})
		shutit.send('docl upload_key ' + ssh_key_name + ' ~/.ssh/' + ssh_key_name + '.pub')
		shutit.send('docl keys | grep -w ' + ssh_key_name)
		ssh_key = shutit.send_and_get_output('docl keys | grep -w ' + ssh_key_name + r""" | sed 's/.*id: \([0-9]*\))/\1/'""")
		ssh_key = ssh_key.strip()
		output = shutit.send_and_get_output('./contrib/digitalocean/provision-do-cluster.sh nyc3 ' + ssh_key + ' 4GB | grep "^[0-9]"').split()
		shutit.send('ls ~/.ssh && cat ~/.ssh/deis*')
		# delete the domain
		# set up the CNAME record name=* hostname=@
		# set up the 3 @ A records
		# set up the 3 deis-1/2/3 A records
		#shutit.send('''curl -s -X GET -H 'Content-Type: application/json' -u "${TOKEN}:" "https://api.digitalocean.com/v2/domains/"''' + domain + ''' > /tmp/domain_out''')
		#curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer b7d03a6947b217efb6f3ec3bd3504582' -d '{"type":"A","name":"customdomainrecord.com","data":"162.10.66.0","priority":null,"port":null,"weight":null}' "https://api.digitalocean.com/v2/domains/digitaloceanisthebombdiggity.com/records"
		#cf:            command = '''curl -s -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"coreos-''' + str(machine) + '''","region":"nyc3","size":"512mb","image":"coreos-stable","ssh_keys":["''' + ssh_key_id + '''"],"backups":false,"ipv6":true,"user_data":"''' + cloud_config + '''","private_networking":true}' "https://api.digitalocean.com/v2/droplets"'''


		shutit.pause_point('''================================================================================
Now go here: https://cloud.digitalocean.com/domains
and add:
- An entry for your domain name pointing at ''' + output[0] + ''' 
- A wildcard CNAME record at your top-level domain, i.e. a CNAME record with * as the name, and @ as the canonical hostname
- For each CoreOS machine created, an A-record that points to the TLD, i.e. an A-record named @, with the droplet's public IP address
- For each CoreOS machine created, an A-record that points to the name, ie deis-1, deis-2, deis-3 so you can go to each server directly

Created machines are:

''' + output[0] + '\n' + output[1] + '\n' + output[2] + '\n' + '''

The zone files will have the following entries in it:

*   CNAME   @
@   IN A    ''' + output[0] + '''
@   IN A    ''' + output[1] + '''
@   IN A    ''' + output[2] + '''

For convenience, you can also set up DNS records for each node:

deis-1   IN A    ''' + output[0] + '''
deis-2   IN A    ''' + output[1] + '''
deis-3   IN A    ''' + output[2] + '''

See here if you need more info: https://www.digitalocean.com/community/tutorials/how-to-set-up-a-host-name-with-digitalocean
================================================================================

WHEN FINISHED, HIT "CRTL" THEN "]" AT THE SAME TIME TO CONTINUE

================================================================================ ''')
		shutit.multisend('scp -i /root/.ssh/' + ssh_key_name + ' /root/.ssh/' + ssh_key_name + ' core@' + output[0] + ':.ssh/',{'continue connecting':'yes'})
		shutit.login(command='ssh -i /root/.ssh/' + ssh_key_name + ' core@' + output[0],expect=' ~ ')
		shutit.send('chmod 0600 ~/.ssh/' + ssh_key_name)
		shutit.send('eval `ssh-agent -s`')
		shutit.send('ssh-add ~/.ssh/' + ssh_key_name)
		shutit.send('export DEISCTL_TUNNEL=' + output[0])
		shutit.send('deisctl config platform set sshPrivateKey=~/.ssh/' + ssh_key_name)
		shutit.send('deisctl config platform set domain=' + domain)
		shutit.send('deisctl install platform')
		shutit.send('deisctl start platform #takes a while',timeout=10000)
		shutit.logout('ssh core@' + output[1])
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'domain')
		return True

def module():
	return deis(
		'shutit.tk.deis.deis', 158844783.006,
		description='deis on CoreOS',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.sd.ruby.ruby','shutit.tk.sd.curl.curl','shutit.tk.sd.git.git','shutit.tk.sd.openssh.openssh','shutit.tk.cluster_config.cluster_config','shutit.tk.sd.which.which','shutit.tk.sd.deis_client.deis_client']
	)

