# sgxwallet: SKALE SGX-based hardware crypto wallet

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## Intro

**sgxwallet** is a next generation hardware secure crypto wallet that is based on **Intel SGX** technology. It currently supports **Ethereum** and **SKALE**, and will support **Bitcoin** in the future.

**sgxwallet** runs as a network server.  Clients connect to the server, authenticate to it using 
TLS 1.0 protocol with client certificates, and then issue requests to the server to generate crypto 
keys and perform cryptographic operations. The keys are generated inside the secure SGX enclave and never
leave the enclave unencrypted.  

The server provides an initial registration service to issue client certificates to the clients.
The administrator manually approves each registration.

**sgxwallet** has been tested on **Ubuntu Linux 18.04**.

## An important note about production readiness

The sgxwallet server is still in active development and therefore should be regarded as _alpha software_. The development is still subject to security hardening, further testing, and breaking changes.  **This library has not yet been reviewed or audited for security.**

# Running sgxwallet 

## Clone this repository and its submodules

`git clone --recurse-submodules  https://github.com/skalenetwork/sgxwallet.git`

## Try instantly in simulation mode


The easiest way to try the sgxwallet server is to run in in  
insecure simulation mode that emulates an SGX processor. Once you are familiar with the server,
you can enable sgx on your machine and run it in secure production mode.

To try the server:

Install docker-compose if you do not have it.

```
sudo apt-get install docker.io docker-compose
```

And then do 

 ```
cd run_sgx_sim; 
sudo docker-compose up
``` 

Voila! You should see the "SGX Server started" message.

## Starting, stopping and upgrading the sgxwallet server.

As any docker-compose application sgxwallet server is super easy to use. 

To run the server as a daemon, do

``` 
sudo docker-compose up -d
```

To stop/start server do 

``` 
sudo docker-compose stop
sudo docker-compose start
```

To view server logs do 

``` 
sudo docker-compose logs
```

To upgrade the server to the latest version do 

``` 
sudo docker-compose stop
sudo docker-compose pull
sudo docker-compose up
```

Note: all docker-compose commands need to be issued from run_sgx_sim directory.

Note: sgxwallet places all its data into the sgx_data directory, which is created the first time you run sgxwallet.
Do not remove this directory!

Note: Sgxwallet operates on network ports 1026 (https) and 1027 (http for initial registration). 
If you have a firewall on your network, please make sure these ports are open so clients are able to
connect to the server. 


## Enable SGX on your machine

Once your tried sgxwallet in the simulation mode, you can enable sgx on your machine, and run the server in production
mode.  First, remove the simulation mode wallet by doing 

``` 
sudo docker-compose rm
```

To run **sgxwallet**, you'll need **Intel SGX** capable hardware. Most Intel chips that were produced after 2015 support **SGX**.

-   Enter **BIOS** of you machine by pressing and holding **Del** or **F2** on boot-up and verify that **BIOS** includes **SGX options**.
    If not, your machine cant run **SGX**.
-   Set SGX in BIOS as `enabled` or `software-controlled`.
-   If you can set SGX to `enabled` you are done! Proceed with "Install SGX Driver" section
-   If not, set SGX in BIOS to `software-controlled` and then enable by running a sgx-enable utility, as described below.

## Enable "software-controlled" SGX

To enable SGX using a software utility:

-   Build `sgx-enable` utility by typing `cd  sgx-software-enable; make`
-   Run `./sgx_enable`.  Verify that it says that **SGX** is successfully enabled

## Install SGX driver

```bash
cd scripts; sudo ./sgx_linux_x64_driver_2.5.0_2605efa.bin; cd ..
```

Reboot you machine after driver install.  Do `ls /dev/isgx` to check that `isgx` device is properly installed.
If you do not see the `isgx` device, you need to troubleshoot your driver installation.


## Run the latest sgxwallet docker container from dockerhub

```
cd run_sgx; 
sudo docker-compose up -d
```

You should see "SGX Server started message".

# Development

## Install Prerequisites

```bash
sudo apt-get install build-essential make cmake gcc g++ yasm  python libprotobuf10 flex bison automake libtool texinfo libgcrypt20-dev libgnutls28-dev
```

## Install SGX sdk

```bash
cd scripts; sudo ./sgx_linux_x64_sdk_2.5.100.49891.bin; cd ..

```

## Install required debian packages

```bash
cd scripts; sudo ./install_packages.sh; cd ..

```

## Build dependencies

Dependencies only need to be built once.

```bash
cd scripts; ./build.py; cd ..

```

## Configure and build sgxwallet

Go to the project's top directory, then run

```bash
libtoolize --force
aclocal
autoheader
automake --force-missing --add-missing
autoconf
./configure
make
```

Note: to run in simulation mode, add --enable-sgx-simulation flag when you run configure.

```
./configure --enable-sgx-simulation
```

## Run sgxwallet

Type:

```bash
./sgxwallet
```

## Build Docker container

```bash
sudo docker build -t sgxcontainer .
```

## Build Docker container in simulation mode

```bash
sudo docker build -t sgxcontainersim -f ./DockerfileSimulation .
```

## Run Docker container


```bash
sudo docker run -di --network host --device /dev/isgx --device /dev/mei0 --name sgxwallet sgxcontainer
```

This will run the server in a Docker container named sgxwallet

You can start and stop running sgxwallet container by doing

```bash
docker stop sgxwallet
docker start sgxwallet
```

## Run Docker container in simulation mode

```bash
sudo docker run -di --network host --name sgxwalletsim sgxcontainersim
```


## Adding new source files

Note that `configure, Makefile` and `Makefile.in` files are created by `automake` tools on the fly.  
Please do not add these files to the source tree!

To add new source and include files to app and enclave, edit the corresponding **Makefile.am** file and then re-run configure.

If you change **.edl** file, you need to re-run configure too.

## Example of client certificate instantiation

Go to the project's top directory, then run

```bash
export CSR_FILE=a.csr
export KEY_FILE=k.key
export CERT_NAME_UNIQUE=someVeryUniqueName
openssl req -new -sha256 -nodes -out $CSR_FILE -newkey rsa:2048 -keyout $KEY_FILE -subj /CN=$CERT_NAME_UNIQUE
cat $CSR_FILE
cat $KEY_FILE
export KEY_PEM_FILE=k.pem
openssl rsa -in $KEY_FILE -text > $KEY_PEM_FILE
cat $KEY_PEM_FILE
```

Next, send content of `a.csr` as single line (by replacing real end of lines with `\n`) to port `1027`.

Example:

```bash
export URL_SGX_WALLET="http://127.0.0.1:1027"
curl -X POST --data '{ "jsonrpc": "2.0", "id": 2, "method": "SignCertificate", "params": { "certificate": "-----BEGIN CERTIFICATE REQUEST-----\nMIICYjCCAUoCAQAwHTEbMBkGA1UEAwwSc29tZVZlcnlVbmlxdWVOYW1lMIIBIjAN\nBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3C4ceRhzMAZnG87PwlkzMROHsm3B\ncPydIeiqs1dieuuvVETJqbXAcOENNsGA+AdXjZwFkDuIS24p2yZ8AwuIMAwdMsGa\n5Hzk0ugOy52iPyGEuooqV94nnL6eWw/zryTvkk7j239wMWn5our5Ia1/CBQlXXo2\n4IWTWfWYOz26SWUh4DuvzMOheMVSxg3KLaxpx7Bq09p32lR9xpl53+HqxSDIMYh9\nC3y3kA6NdkKsGE/Jt4WoZ5S5LlrhYjw+PFTeX2lbGDZpn/sxQIM16Pxo2LCfefIa\nik+aZBEAlpn22ljLZ5sEcVgBmOlL+v3waq9u0AaSYzdGFRA+0ceVwU/QTQIDAQAB\noAAwDQYJKoZIhvcNAQELBQADggEBAJXodL69Q/8zDt24AySXK0ksV3C3l5l10Hno\nfF6zKypsYev33CFbZu6HweSgK2f21+DeI9TsGKJxI7K6MUqyH0pJhwlFSeMB5/qP\nJueqXMuvStZSp0GGTaNy7Al/jzOKYNf0ePsv/Rx8NcOdy7RCZE0gW998B5jKb66x\nPgy6QvD8CkZULiRScYlOC8Ex6nc+1Z54pRC1NFWs/ugGyFgLJHy0J2gNkOv6yfsl\nH3V/ocCYSoF4ToUQAxwx+dcy4PXrL9vKzRNJgWzsI/LzCZkglo8iis9YZQawDOUf\nGmDMDkr0Fx1W1tSEpvkw0flkAXZ8PhIGCC0320jkuPeClt7OWNs=\n-----END CERTIFICATE REQUEST-----\n" } }' -H 'content-type:application/json;' $URL_SGX_WALLET

```

The above example produces on success:

```
{"id":2,"jsonrpc":"2.0","result":{"errorMessage":"","result":true,"status":0}}

```

Next, generate the client certificate signed by root ones:

```bash
cd cert
./create_client_cert
ls -1
cat client.crt
openssl x509 -inform PEM -in client.crt > client.pem
cat client.pem
cd ..

```

Finally, execute a test call such as importing BLS key. 

Example:

```bash
export URL_SGX_WALLET="https://127.0.0.1:1026"
curl \
    -X POST --data '{ "jsonrpc": "2.0", "id": 1, "method": "importBLSKeyShare", "params": { "keyShareName": "nBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3C4ceRhzMAZnG87PwlkzMROHsm3B", "n": 2, "t": 2, "index" : 1, "keyShare": "21043165427057050523208250969869713544622230829814517880078280390613973680760" } }' -H 'content-type:application/json;' \
    -v --cacert ./cert/rootCA.pem --key $KEY_PEM_FILE --cert ./cert/client.pem $URL_SGX_WALLET -k

```

The above example produces on success:

```
{"id":1,"jsonrpc":"2.0","result":{"encryptedKeyShare":"0400020000000000040effffff02000000000000000000000b000000000000ff0000000000000000cecb5d7bd507cb936464fdb6b88cfe80e38eae963af6a39b6b05cdfba5521c60000000f0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000080000000000000000000000000000000875c0520e8d6739c440e0e5073633861769fc1d31d627e9a72c66d43871c62bce2cc48e821341e10784242c4c8aad6ca73a491cbf7453c2ff012b6b3d9d96823c0256992d9792ea60269789b2d51ae87c75fe522dbcb8053458c1bca421cbc57f4a58e4e5689d534ca0303db83c7a9e88cd23afe3a39e1a3801371c95e7ffa54e834c6be8853983dcaa1fa9f5e6959a5","errorMessage":"","status":0}}

```

If you change .edl file, you need to re-run configure too.

## Libraries

-   [Intel-SGX-SSL by Intel](https://github.com/intel/intel-sgx-ssl)
-   [LevelDB by Google](https://github.com/google/leveldb)
-   [libBLS by SKALE Labs](https://github.com/skalenetwork/libBLS)
-   [libff by SCIPR-LAB](http://www.scipr-lab.org/)
-   [Linux SGX Driver by Intel](https://github.com/intel/linux-sgx-driver)
-   [SGX-GMP by Intel](https://github.com/intel/sgx-gmp)
-   [SGX Software Enable by Intel](https://github.com/intel/sgx-software-enable)

## License

[![License](https://img.shields.io/github/license/skalenetwork/sgxwallet.svg)](LICENSE)

All contributions to sgxwallet are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).

Copyright (C) 2019-Present SKALE Labs.
