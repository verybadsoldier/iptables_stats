from ipsetpy import ipset_list


def _count_cidr(cidr_str):
    """resolve IP strings in CIDR syntax (like '192.168.2.0/24') and return number of unique IPs."""
    toks = cidr_str.split('/')
    if len(toks) == 1:
        return 1

    return 2 ** (32 - int(toks[1]))


def get_ip_count(setname: str) -> int:
    ipset = ipset_list(setname)

    num = 0
    in_data = False
    for line in ipset.splitlines():
        if not in_data:
            if line.startswith('Members'):
                in_data = True
            continue
        num += _count_cidr(line)
    return dict(num_unique_ips=num)
