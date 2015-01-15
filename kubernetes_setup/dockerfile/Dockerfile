FROM imiell/sd_shutit

WORKDIR /opt
RUN git clone https://github.com/ianmiell/shutit-coreos-do.git
RUN git clone https://github.com/ianmiell/shutit-distro.git
WORKDIR /opt/shutit-coreos-do/cluster_setup

# replace YOUR_ACCESS_TOKEN with your digital ocean access token
RUN /opt/shutit/shutit build --shutit_module_path /opt/shutit-distro -s shutit.tk.coreos_do_setup.coreos_do_setup oauth_token bb39a0a4593578ec537fa5976c8f0b9b12acd3cc0f108d0b797dcc9ef913730e --delivery bash

# Don't run this - the image's purpose is to set up the coreos cluster
CMD ["/bin/false"] 
