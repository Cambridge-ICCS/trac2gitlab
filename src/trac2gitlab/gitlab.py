import re
import time

import docker
from docker.models.containers import Container


class GitLabInstance:
    """A GitLab CE server running in Docker.

        instance = GitLabInstance().wait_until_ready()
        <do things with the instance>
        instance.stop()

    The container will be automatically removed when stopped.

    Note that we reserve the name "gitlab" for the container ATM.
    If the container with that name already exists. This class will fail
    to instantiate.

    Can also be used as a context manager; the container is then stopped
    and removed automatically on exit::

        with GitLabInstance().wait_until_ready() as gitlab:
            ...
    """

    DEFAULT_IMAGE = "gitlab/gitlab-ce:19.2.0-ce.0"
    DEFAULT_PORTS = {"443/tcp": 443, "80/tcp": 80, "22/tcp": 2222}

    def __init__(
        self,
        name: str = "gitlab",
        hostname: str = "gitlab.example.com",
        image: str = DEFAULT_IMAGE,
        ports: dict[str, int] | None = None,
    ) -> None:
        self._client = docker.from_env()
        self._name = name
        self._hostname = hostname
        self._ports = ports if ports is not None else dict(self.DEFAULT_PORTS)

        self._container = self._start_container(image)

    def _start_container(self, image: str) -> Container:
        return self._client.containers.run(
            image,
            name=self._name,
            hostname=self._hostname,
            ports=self._ports,
            detach=True,
            auto_remove=True,
        )


    def is_ready(self) -> bool:
        """
        True once Docker reports the container's health check as healthy.

        We check using the GitLab's API's `health_check` endpoint. The container
        is supposed to have some build-in health check, but it seems to trigger
        before the web interface is up.

        By default it is not exposed to the world so we enquire it from
        inside the container.

        This is CERTAINLY not an idiomatic way to to this. But must do until
        someone who knows what they are doing has a look at this...
        """
        # TODO:
        #   I unsure about the port and exact settings in the way I launch this command
        output = self._container.exec_run("curl -sS http://localhost/-/health").output

        # I am not sure if I don't get extra things in the response.
        # I assume as long as the magic keyword  is there things should be up
        return bool(re.match(r"GitLab OK", output.decode("utf-8")))

    def wait_until_ready(self, timeout: float = 900, poll_interval: float = 5) -> "GitLabInstance":
        """Block until GitLab has finished its internal configuration.

        Args:
            timeout: In [s]
            poll_interval: Time between subsequent readiness enquiries [s]

        Returns:
            self, once the container is ready.
        """
        deadline = time.monotonic() + timeout
        last_status = None
        while time.monotonic() < deadline:
            ready = self.is_ready()
            if ready:
                return self
            time.sleep(poll_interval)
        raise TimeoutError(
            f"Container '{self._name}' was not healthy within {timeout:.0f}s "
            f"(last health status: {last_status!r}). Logs:\n{self._logs_tail()}"
        )

    def _logs_tail(self, lines: int = 60) -> str:
        """Get lines from the tail of the log.
        """
        return self._container.logs(tail=lines).decode(errors="replace")

    def stop(self) -> None:
        self._container.stop()

    def __enter__(self) -> "GitLabInstance":
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()
