import platform

from middlewared.utils import run

from middlewared.plugins.service_.services.base import ServiceInterface, ServiceState


class PseudoServiceBase(ServiceInterface):
    plugin = NotImplemented

    async def get_state(self):
        return ServiceState(
            await self.middleware.call(f"{self.plugin}.started"),
            [],
        )

    async def start(self):
        await self.middleware.call(f"{self.plugin}.start")

    async def stop(self):
        await self.middleware.call(f"{self.plugin}.stop")


class ActiveDirectoryService(PseudoServiceBase):
    name = "activedirectory"

    reloadable = True
    restartable = True

    plugin = "activedirectory"

    async def restart(self):
        await self.middleware.call("kerberos.stop")
        await self.middleware.call("activedirectory.start")

    async def reload(self):
        if platform.system() == "FreeBSD":
            await run(["service", "winbindd", "quietreload"])


class LdapService(PseudoServiceBase):
    name = "ldap"

    plugin = "ldap"


class NisService(PseudoServiceBase):
    name = "nis"

    plugin = "nis"
