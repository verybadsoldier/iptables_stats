from .iptables_stats import IpTables


def main():
    ip = IpTables()
    ip.getCounts("FIREHOL_BLACKLIST",  'firehol_level2')


if __name__ == '__main__':
    main()
