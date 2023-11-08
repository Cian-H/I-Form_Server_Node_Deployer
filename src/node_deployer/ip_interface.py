from ipaddress import IPv4Address, IPv6Address, ip_address


class IPAddress:
    def __init__(self, *args, **kwargs) -> None:
        self.obj: IPv4Address | IPv6Address = ip_address(*args, **kwargs)

    @property
    def compressed(self) -> str:
        return self.obj.compressed

    @property
    def exploded(self) -> str:
        return self.obj.exploded

    @property
    def is_global(self) -> bool:
        return self.obj.is_global

    @property
    def is_link_local(self) -> bool:
        return self.obj.is_link_local

    @property
    def is_loopback(self) -> bool:
        return self.obj.is_loopback

    @property
    def is_multicast(self) -> bool:
        return self.obj.is_multicast

    @property
    def is_private(self) -> bool:
        return self.obj.is_private

    @property
    def is_reserved(self) -> bool:
        return self.obj.is_reserved

    @property
    def is_unspecified(self) -> bool:
        return self.obj.is_unspecified

    @property
    def max_prefixlen(self) -> int:
        return self.obj.max_prefixlen

    @property
    def packed(self) -> bytes:
        return self.obj.packed

    @property
    def reverse_pointer(self) -> str:
        return self.obj.reverse_pointer

    @property
    def version(self) -> int:
        return self.obj.version

    def __str__(self) -> str:
        return str(self.obj)

    def __repr__(self) -> str:
        return repr(self.obj)

    def __bool__(self) -> bool:
        return not self.obj.is_unspecified
