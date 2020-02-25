import os
import platform
import time

from middlewared.plugins.service_.services.base import ServiceInterface, SimpleService

from middlewared.utils import run


class KmipService(ServiceInterface):
    name = "kmip"

    async def start(self):
        await self.middleware.call("service.start", "ssl")
        await self.middleware.call("etc.generate", "kmip")


class HostnameService(ServiceInterface):
    name = "hostname"

    async def reload(self):
        await run(["hostname", ""])
        await self.middleware.call("etc.generate", "hostname")
        await self.middleware.call("etc.generate", "rc")
        if platform.system() == "FreeBSD":
            await run(["service", "hostname", "start"])
        await self.middleware.call("service.reload", "mdns")
        await self.middleware.call("service.restart", "collectd")


class NetworkService(ServiceInterface):
    name = "network"

    async def start(self):
        await self.middleware.call("interface.sync")
        await self.middleware.call("route.sync")


class NetworkGeneral(ServiceInterface):
    name = "networkgeneral"

    async def reload(self):
        await self.middleware.call("service.reload", "resolvconf")
        if platform.system() == "FreeBSD":
            await run(["service", "routing", "restart"])


class NtpdService(SimpleService):
    name = "ntpd"

    etc = ["ntpd"]
    restartable = True

    freebsd_rc = "ntpd"


class PowerdService(SimpleService):
    name = "powerd"

    etc = ["rc"]

    freebsd_rc = "powerd"


class RcService(ServiceInterface):
    name = "rc"

    etc = ["rc"]
    reloadable = True


class ResolvConfService(ServiceInterface):
    name = "resolvconf"

    async def reload(self):
        await self.middleware.call("service.reload", "hostname")
        await self.middleware.call("dns.sync")


class RoutingService(SimpleService):
    name = "routing"

    etc = ["rc"]

    freebsd_rc = "routing"


class SslService(ServiceInterface):
    name = "ssl"

    etc = ["ssl"]

    async def start(self):
        pass


class SysconsService(SimpleService):
    name = "syscons"

    etc = ["rc"]
    restartable = True

    freebsd_rc = "syscons"


class SysctlService(ServiceInterface):
    name = "sysctl"

    reloadable = True

    async def reload(self):
        await self.middleware.call("etc.generate", "sysctl")


class SyslogdService(SimpleService):
    name = "syslogd"

    etc = ["syslogd"]
    restartable = True
    reloadable = True

    freebsd_rc = "syslog-ng"


class TimeservicesService(ServiceInterface):
    name = "timeservices"

    etc = ["localtime"]
    reloadable = True

    async def reload(self):
        await self.middleware.call("service.restart", "ntpd")

        settings = await self.middleware.call("datastore.config", "system.settings")
        os.environ["TZ"] = settings["stg_timezone"]
        time.tzset()
