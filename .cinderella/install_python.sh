#!/usr/bin/env bash

VERSION=$1
TMP_FOLDER=/tmp

if [ -d "$HOME/bin/python/$VERSION" ]; then
    echo "Python $VERSION already installed"
    exit 0
fi

wget -O $TMP_FOLDER/Python-$VERSION.tgz https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tgz

if [ $? -ne 0 ]; then
    echo "Could not download Python $VERSION"
    exit 1
fi

tar xf $TMP_FOLDER/Python-$VERSION.tgz -C $TMP_FOLDER
mkdir -p $HOME/bin/python/$VERSION

# Enable SSL
setup=$TMP_FOLDER/Python-$VERSION/Modules/Setup.dist
echo "_socket socketmodule.c" >> $setup
echo "SSL=/usr/include/openssl" >> $setup
echo "_ssl _ssl.c \\" >> $setup
echo '        -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \\' >> $setup
echo '        -L$(SSL)/lib -lssl -lcrypto' >> $setup

cd $TMP_FOLDER/Python-$VERSION \
    && ./configure --prefix=$HOME/bin/python/$VERSION \
    && make && make install \
    && cd $HOME
