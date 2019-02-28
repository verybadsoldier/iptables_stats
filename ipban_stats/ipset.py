from ipsetpy import ipset_list
from types import int

class IpSet:

    @staticmethod
    def _count_cidr(cidr_str):
        """resolve IP strings in CIDR syntax (like '192.168.2.0/24') and return number of unique IPs."""
        toks = ipstr.split('/')
        if len(toks) == 1:
            return 1

        return 2 ** (32 - int(toks[1]))

    def get_ip_count(self, setname: str): -> int
        ipset = ipset_list(setname)

        num = 0
        for i in ipset:
            num += IpSet._count_cidr(i)
        return num