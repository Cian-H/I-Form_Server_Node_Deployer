from ipaddress import IPv4Address, IPv6Address, ip_address


class IPAddress:
    def __init__(self, *args, **kwargs) -> None:
        self.obj: IPv4Address | IPv6Address = ip_address(*args, **kwargs)
        to_passthrough = (
            "compressed",
            "exploded",
            "is_global",
            "is_link_local",
            "is_loopback",
            "is_multicast",
            "is_private",
            "is_reserved",
            "is_unspecified",
            "max_prefixlen",
            "packed",
            "reverse_pointer",
            "version",
        )
        for attrname in to_passthrough:
            self._passthrough(attrname)

    def _passthrough(self, attrname: str) -> None:
        """Passes through an attribute from the underlying IPv4Address or IPv6Address object

        Args:
            attrname (str): The name of the attribute to pass through

        Raises:
            AttributeError: If the attribute is a method
        """        
        attr = getattr(self.obj, attrname)
        if callable(attr):
            raise AttributeError(f"Passthrough is unavailable for methods ({attrname})")
        setattr(self, attrname, attr)

    def __str__(self) -> str:
        return str(self.obj)

    def __repr__(self) -> str:
        return repr(self.obj)

    def __bool__(self) -> bool:
        return not self.obj.is_unspecified
