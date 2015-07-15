"""ShutIt module. See http://shutit.tk
"""
from shutit_module import ShutItModule
import string
import time

class deis(ShutItModule):

	def check_ready(self, shutit):
		return True

	def build(self, shutit):
		import cluster_config
		token = cluster_config.cluster_config.get_token(shutit)
		domain = shutit.cfg[self.module_id]['domain']
		ssh_key_name = shutit.cfg[self.module_id]['ssh_key_name']
		shutit.send('mkdir -p /tmp/build/deis_client')
		shutit.send('cd /tmp/build/deis_client')
		shutit.send('curl -sSL http://deis.io/deis-cli/install.sh | sh')
		cmd = ''
		pw = ''
		if shutit.whoami != 'root':
			pw = shutit.get_env_pass(shutit.whoami(),'Input sudo password: ')
			cmd = 'sudo '
		shutit.multisend(cmd + 'ln -fs $PWD/deis /usr/bin/deis',{'assword':pw})
		shutit.install('ruby curl git openssh-client')
		shutit.send('rm -rf /tmp/opt/deis')
		shutit.send('mkdir -p /tmp/opt/deis')
		shutit.send('cd /tmp/opt/deis')
		shutit.send(cmd + 'gem install docl')
		shutit.send('git clone https://github.com/deis/deis.git')
		shutit.send('cd deis')
		shutit.send('make discovery-url')
		shutit.multisend('docl authorize',{'Enter your DO Token:':token})
		shutit.send('docl keys | grep --color=never -w ' + ssh_key_name)
		ssh_key = shutit.send_and_get_output('docl keys | grep --color=never -w ' + ssh_key_name + r""" | sed 's/.*id: \([0-9]*\))/\1/'""")
		ssh_key = ssh_key.strip()
		output = shutit.send_and_get_output('./contrib/digitalocean/provision-do-cluster.sh nyc3 ' + ssh_key + ' 4GB | grep --color=never "^[0-9]"').split()
		if len(output) != 3:
			shutit.fail('unexpected output from cluster provisioning: ' + str(output))
		# delete the domain
		shutit.send('curl -s -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer ' + token + '" "https://api.digitalocean.com/v2/domains/' + domain + '"')
		# create the domain
		shutit.send('curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ' + token + '''" -d '{"name":"''' + domain + '''","ip_address":"''' + output[0] + '''"}' "https://api.digitalocean.com/v2/domains/"''')
		# set up the CNAME record name=* hostname=@
		shutit.send('curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ' + token + '''" -d '{"type":"CNAME","name":"*","data":"@","priority":null,"port":null,"weight":null}' "https://api.digitalocean.com/v2/domains/''' + domain + '''/records"''')
		count = 1
		for addr in output:
			# set up the 3 @ A records
			shutit.send('''curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ''' + token + '''" -d '{"type":"A","name":"@","data":"''' + addr + '''","priority":null,"port":null,"weight":null}' "https://api.digitalocean.com/v2/domains/''' + domain + '''/records"''')
			# set up the 3 deis-1/2/3 A records
			shutit.send('curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ' + token + '''" -d '{"type":"A","name":"deis-''' + str(count) + '''","data":"''' + addr + '''","priority":null,"port":null,"weight":null}' "https://api.digitalocean.com/v2/domains/''' + domain + '''/records"''')
			count += 1
		shutit.send('sleep 120 # pause seems to help here')
		shutit.login(command='ssh core@' + output[0],expect=' ~ ')
		shutit.send('curl -sSL http://deis.io/deisctl/install.sh | sudo sh -s 1.8.0')
		shutit.send('eval `ssh-agent -s`')
		shutit.multisend('ssh-add .ssh/authorized_keys.d/coreos-cloudinit',{'assphrase':''})
		shutit.send('export DEISCTL_TUNNEL=' + output[0])
		shutit.send('deisctl config platform set sshPrivateKey=~/.ssh/authorized_keys.d/coreos-cloudinit')
		shutit.send('deisctl config platform set domain=' + domain)
		shutit.send('deisctl install platform')
		shutit.send('deisctl start platform #takes a while',timeout=10000)
		shutit.logout('ssh core@' + output[1])
		shutit.send('mkdir tmp')
		shutit.send('cd tmp')
		shutit.send('curl -sSL http://deis.io/deis-cli/install.sh | sh')
		shutit.send('mv deis /usr/bin')
		shutit.send('cd ..')
		shutit.send('rm -rf tmp')
		shutit.multisend('deis register http://deis.' + domain,{'username:':'admin','password':'admin','email:':'admin@' + domain})
		shutit.log('Deis cluster has been set up for domain: ' + domain + '\n\nadmin user is "admin" and password is "admin".\n\nSee here for info on what to do next: http://docs.deis.io/en/latest/using_deis/\n\nYou can quit this build now, the work has been done.', add_final_message=True)
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'domain')
		shutit.get_config(self.module_id,'ssh_key_name')
		return True

def module():
	return deis(
		'shutit.tk.deis.deis', 158844783.006,
		description='deis on CoreOS',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.cluster_config.cluster_config']
	)

