import iptc


class IpTables:
    def getCounts(self, chain, rule):
        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, chain)
        for rule in chain.rules:
            (packets, bytes) = rule.get_counters()
            print(packets, bytes)
