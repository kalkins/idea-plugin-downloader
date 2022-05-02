# IDEA plugin downloader
Download Jetbrains plugins from the central repository for use in custom repositories.

## Usage

First, copy the example config file to `config.yml` or `config_docker.yml`, and modify the settings. If you don't create this file, the example config will be used instead.

To run the script, run `run.sh` as a user with access to docker. This will download all plugins, and create the tarball `jetbrains-plugins.tar.gz`. This tarball can then be unpacked in artifactory or a file server.
