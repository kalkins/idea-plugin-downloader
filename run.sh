#!/bin/sh

user=$(stat -c "%u" .)
group=$(stat -c "%g" .)

if [ -f config.yml ]; then
    config_file=config.yml
elif [ -f config_docker.yml ]; then
    config_file=config_docker.yml
elif [ -f config_example.yml ]; then
    echo "Using example config file"
    config_file=config_example.yml
else
    echo "No config file found. Aborting."
    exit -1
fi

if [ ! -d ./data ]; then
    mkdir ./data
    chown "$user:$group" ./data
fi

USER_ID=$user GROUP_ID=$group docker build -t idea-plugin-downloader . --build-arg CONFIG_FILE=$config_file
USER_ID=$user GROUP_ID=$group docker run --rm --mount "type=bind,src=${PWD}/data,dst=/app/output" idea-plugin-downloader

if [ $? -eq 0 ]; then
    echo "Creating a tarball of the plugins"
    tar zcvf ./jetbrains-plugins.tar.gz -C ./data . 2>/dev/null
    chown "$user:$group" ./jetbrains-plugins.tar.gz

    echo "NEXT: mirror jetbrains-plugins.tar.gz and import into Artifactory."
else
    echo "The download failed, no tarballs created"
    exit 255
fi
