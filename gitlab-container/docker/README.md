# Instructions for building and configuring the GitLab Docker image

## `GitLabNoVolume` image definition

The default GitLab container image is configured to use 
persistent volumes for storing data. All the configuration 
files and databases are stored in the volumes and hence are not part of an image. 
For our use case this is an issue since we want to have the image already set up 
with the admin account (and potentially other data) as soon as it is run.

Hence we use a modified version of the default image where we let go of the volumes.
This allows us to include all the configuration (and its changes) into the image itself.

The Dockerfile definition is lifted from the [omnibus-gitlab](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/docker/Dockerfile) repository and modified to remove the volume definitions.

## Files required for the build

As in the omnibus-gitlab repository, the Dockerfile expects a number of files to 
be available in the build context (i.e. the build directory). Most are contained 
in the `assets` folder and are lifted from the omnibus-gitlab repository.

The following files are also lifted into the root of the `docker/` folder: 
- `RELEASE` file (see below)
- `locale.gen`

## The `RELEASE` file

The `Dockerfile` copies a `RELEASE` file into the image (`COPY RELEASE /`). This file is **not** committed to the repository — you must create it in the `docker/` folder before building. It is a plain shell-sourceable file containing version and download metadata for the omnibus package.

### Required variables

| Variable | Description | Example |
|---|---|---|
| `RELEASE_PACKAGE` | Package edition: `gitlab-ce` or `gitlab-ee` | `gitlab-ce` |
| `RELEASE_VERSION` | Package version, with edition suffix | `19.2.0-ce` |
| `DOWNLOAD_URL_amd64` | URL to the `.deb` for amd64 | `https://example.com/gitlab-ce_19.2.0-ce.0_amd64.deb` |
| `DOWNLOAD_URL_arm64` | URL to the `.deb` for arm64 (only needed for arm64 builds) | `https://example.com/gitlab-ce_19.2.0-ce.0_arm64.deb` |

### Example `RELEASE` file

```plaintext
RELEASE_PACKAGE=gitlab-ce
RELEASE_VERSION=19.2.0-ce
DOWNLOAD_URL_amd64=https://example.com/gitlab-ce_19.2.0-ce.0_amd64.deb
DOWNLOAD_URL_arm64=https://example.com/gitlab-ce_19.2.0-ce.0_arm64.deb
```

### How the variables are used

- `assets/setup` sources `/RELEASE` and selects `DOWNLOAD_URL_amd64` or `DOWNLOAD_URL_arm64` based on `TARGETARCH`, then downloads and installs the `.deb`.
- `assets/init-container` re-sources `/RELEASE` at every container start to print the running version.
- The `setup` script strips `DOWNLOAD_URL` lines from `/RELEASE` after install, since the download is no longer needed.


## License

A number of files listed above are lifted from the omnibus-gitlab repository and are licensed under the original [omnibus-gitlab license](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/07ce0895f96fe2eea09137f0a875819dc82cff19/LICENSE). A copy 
has been included in this repository.

## Building and accessing the GitLab image

The `GitLabNoVolume` Dockerfile omits the image's `VOLUME` declarations. From the
`docker/` directory, build the image and then start the container:

```shell
bash ./build_gitlab.sh
bash ./start_gitlab.sh
```

`build_gitlab.sh` builds the image; `start_gitlab.sh` only runs it. The image
exposes ports 443, 80, and 22. Note that `start_gitlab.sh` maps the container's
SSH port (22) to host port 2222, so SSH access is via `localhost:2222`.

After several minutes, the container should be up and running. Note that the 
initial setup of GitLab takes a while, so it is recommended to check the logs of the container to see when it is ready. You can do this by running:

```shell
docker logs -f gitlab-test
```
Once finished, you can access it via a browser at `https://localhost/`.

To access the instance, we need to obtain the initial root password. This can be done by running the following command:

```shell
docker exec -it gitlab-test grep 'Password:' /etc/gitlab/initial_root_password
```

Then you can log in and change the password. 

## Embedding the changes into a new image

Finally, if we are happy with the configuration changes, we need to create a new image with the changes embedded. This can be done by committing the container into a new image:

```shell
docker commit gitlab-test trac2gitlab-gitlab-container:<tag>
```

Before pushing, the image needs to be tagged with the full registry name (see
the top-level `README.md` for the tagging rules). The local image name produced
by `build_gitlab.sh` / `docker commit` does not include the registry prefix, so
an extra `docker tag` step is required:

```shell
docker tag trac2gitlab-gitlab-container:<tag> ghcr.io/cambridge-iccs/trac2gitlab-gitlab-container:<tag>
docker push ghcr.io/cambridge-iccs/trac2gitlab-gitlab-container:<tag>
```

The `<tag>` should follow the `v<major>.<minor>.<patch>` format.

