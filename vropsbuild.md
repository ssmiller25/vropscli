# vROps Build

In order to get this utility to work on a vROps system natively, a custom toolchain must be compiled under the SLES 11
system that vROps uses.  This process will require SLES 11 media or an active SuSE enterprise subscription in order to
download the appropriate packaging:

```
sudo zypper install gcc gcc-c++ make ncurses patch zlib-devel wget tar xz awk netcfg wget-openssl1 curl-openssl1 libtool automake autoconf
```

# Openssl
* Download OpenSSL from https://github.com/openssl/openssl/releases (tar.gz) and scp to vrops system
```
tar -xzvf openssl*
cd openssl-Open*
./config --prefix=/usr --openssldir=/usr/local/openssl shared
make
make install
echo "export LD_LIBRARY_PATH=/usr/local/lib${LD_LIBRARY_PATH}" >> ~/.bash_profile
echo "export LC_ALL=en_US.utf8" >> ~/.bash_profile
echo "export LANG=en_US.utf8" >> ~/.bash_profile
chmod 755 ~/.bash_profile
# Reexecute base_profile, or relogin
cd ~
. ./.bash_profile
echo $LD_LIBRARY_PATH   # Make sure you get output!!!
```


# Curl (Against OpneSSL libs, above)
* Download Curl version 7.52.0 from https://github.com/curl/curl/releases (tar.gz) and scp to vrops system
  * Must be an older version to support the older verion of autoconf on SLES
```
tar -xzvf curl-*.tar.gz
cd curl/
./buildconf
./configure --prefix=/usr/local --with-ssl --disable-shared
make
make install
echo insecure >> $HOME/.curlrc
wget https://raw.githubusercontent.com/curl/curl/curl-7_53_0/lib/mk-ca-bundle.pl
perl mk-ca-bundle.pl -k
export SSL_CERT_FILE=`pwd`/ca-bundle.crt
echo "export SSL_CERT_FILE=`pwd`/ca-bundle.crt" >> ~/.bash_profile
cd ..
```

# Other libraries

```
curl -O https://zlib.net/zlib-1.2.11.tar.gz
tar -xzvf zlib-1.2.11.tar.gz
cd zlib-1.2.11/
./configure
make
make install
cd ..

curl -O https://ftp.gnu.org/gnu/readline/readline-7.0.tar.gz
tar -xzvf readline-7.0.tar.gz
cd readline-7.0/
./configure
make
make install
cd ..

curl -O https://zlib.net/zlib-1.2.11.tar.gz
tar -xzvf zlib-1.2.11.tar.gz
cd zlib-1.2.11/
./configure
make
make install
cd ..
```

# Real Python
* Only was able to get Python 3.6.1 to work (issue with CTypes on 3.7.x)
```
curl -O https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar -xzvf Python-3.6.1.tgz
cd Python-3.6.1/
./configure --enable-shared --prefix=/usr/local --exec-prefix=/usr/local
make
make install
```

# Pipenv for rest of environment buildout
```
pip3 install pipenv
```
