#!/usr/bin/env python

#
#    @file  docker_test.py
#    @author Stan Kladko
#    @date 2020
#

import sys, os, subprocess, socket, time
os.chdir("..")
topDir = os.getcwd() + "/sgxwallet"
print("Starting build push")
print("Top directory is:" + topDir)
SCRIPTS_DIR = topDir + "/scripts"

print("Running test");
assert subprocess.call(["docker", "run", "-v", topDir + "/sgx_data:/usr/src/sdk/sgx_data",
                        "-d", "--network=host", "skalenetwork/sgxwalletsim:latest"]) == 0

time.sleep(5);

assert os.path.isdir(topDir + '/sgx_data/sgxwallet.db')
assert os.path.isdir(topDir + 'sgx_data/cert_data');
assert os.path.isdir(topDir + 'sgx_data/CSR_DB');
assert os.path.isdir(topDir + 'sgx_data/CSR_STATUS_DB');
assert os.path.isfile(topDir + 'sgx_data/cert_data/SGXServerCert.crt')
assert os.path.isfile(topDir + 'sgx_data/cert_data/SGXServerCert.key')
assert os.path.isfile(topDir + 'sgx_data/cert_data/rootCA.pem')
assert os.path.isfile(topDir + 'sgx_data/cert_data/rootCA.key')

s1 = socket.socket()
s2 = socket.socket()
s3 = socket.socket()
address = '127.0.0.1'
s1.connect((address, 1026))
s2.connect((address, 1027))
s3.connect((address, 1028))

s1.close()
s2.close()
s3.close()






