#!/bin/bash
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="../../shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="~/shutit"
# Fall back to trying directory of shutit when module was first created
[[ ! -a "$SHUTIT" ]] && SHUTIT="/home/imiell/shutit_dev/shutit"
if [[ ! -a "$SHUTIT" ]]
then
    echo "Must supply path to ShutIt dir or have shutit on path"
    exit 1
fi
pushd ..
# eg
$SHUTIT build --shutit_module_path ..:/path/to/shutit-distro::/path/to/shutit/shutit/library/copy_ssh_key -s shutit.tk.coreos_do_setup.coreos_do_setup oauth_token DO_TOKEN -s shutit.tk.copy_ssh_key.copy_ssh_key login $USER
# Found YOUR_TARGET_PASSWORD in your config, you may want to quit and override, eg put the following into your

popd
