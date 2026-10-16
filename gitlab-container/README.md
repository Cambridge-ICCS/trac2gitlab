# GitLab test image. Rules and instructions

We currently do not have an automated way to build the GitLab instance image
for testing the migration in an automated, programmatic way. Sadly, it is a manual
process at the moment.

1. Build the initial container
2. Log in to the GitLab instance (via `https://localhost/`) and make the required changes
3. `docker commit` the changes to get a new version of the container
4. Push the new version to the registry

It is not the best system, so we need to follow rules and be disciplined.

The images need to be manually pushed to the `Cambridge-ICCS` container registry:
`docker push ghcr.io/cambridge-iccs/trac2gitlab-gitlab-container:<tag>`

The `<tag>` should be the version of the container, following the `v<major>.<minor>.<patch>` format.
The version should be updated in the `CHANGELOG.md` file, together with the changes with
respect to the prior version. The SHA256 hash of the image must also be included,
since the container is not attached to the repository and we need a way to verify the integrity.


