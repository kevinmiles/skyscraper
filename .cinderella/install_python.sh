#!/usr/bin/env bash

VERSION=$1
TMP_FOLDER=/tmp

wget -O $TMP_FOLDER/Python-$VERSION.tgz https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tgz

if [ $? -ne 0 ]; then
    echo "Could not download Python $VERSION"
    exit 1
fi

tar xf $TMP_FOLDER/Python-$VERSION.tgz -C $TMP_FOLDER
mkdir -p $HOME/bin/python/$VERSION

cd $TMP_FOLDER/Python-$VERSION \
    && ./configure --prefix=$HOME/bin/python/$VERSION \
    && make && make install \
    && cd $HOME
