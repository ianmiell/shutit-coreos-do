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
$SHUTIT build -m /path/to/shutit-distro
popd

#eg: shutit build --shutit_module_path /space/git/shutit-distro:.. -s shutit.tk.cluster_delete.cluster_delete oauth_token $DO_TOKEN
