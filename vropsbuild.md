# vROps Build

In order to get this utility to work on a vROps system natively, a custom toolchain must be compiled under the SLES 11
system that vROps uses.  This process will require SLES 11 media or an active SuSE enterprise subscription in order to
download the appropriate packaging:

sudo zypper install gcc gcc-c++ make ncurses patch zlib-devel wget tar xz awk netcfg wget-openssl1 curl-openssl1 libtool automake autoconf
sudo zypper install git

# Openssl
cd openssl/
./config --prefix=/usr --openssldir=/usr/local/openssl shared
make
make install


# Curl
cd curl/
./buildconf
./configure --prefix=/usr/local --with-ssl --disable-shared
make
make install
echo insecure >> $HOME/.curlrc
wget https://raw.githubusercontent.com/curl/curl/curl-7_53_0/lib/mk-ca-bundle.pl
perl mk-ca-bundle.pl -k
export SSL_CERT_FILE=`pwd`/ca-bundle.crt

# Other libraries
wget https://zlib.net/zlib-1.2.11.tar.gz
tar -xzvf zlib-1.2.11.tar.gz
cd zlib-1.2.11/
./configure
make
make install

wget https://ftp.gnu.org/gnu/readline/readline-7.0.tar.gz
tar -xzvf readline-7.0.tar.gz
cd readline-7.0/
./configure
make
make install

wget https://ftp.gnu.org/gnu/readline/readline-6.3.tar.gz
tar -xzvf readline-6.3.tar.gz
cd readline-6.3/
./configure
make
make install



# Real Python
cd Python-3.6.1/
./configure --prefix=/usr/local --exec-prefix=/usr/local
make
make install

pip3 install pipenv
