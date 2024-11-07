# Server side sanitizers
Research on fuzzing HTML sanitizers in popular programming languages

## Build

Under `/web` you will find a python script used to build the infrastructure for fuzzing. Place your fuzz targets in a separate directory each under `web/docker/backends`. Each subfolder there will be used as a separate docker image and reachable at `http://localhost/subdir-name` at runtime.