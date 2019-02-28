import iptc


class IpTables:
    def get_counts(self, chain, rule):
        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, chain)
        for rule in chain.rules:
            (packets, bytes) = rule.get_counters()
            print(packets, bytes)

    def count_rules(self, chain):
        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, chain)
        return len(chain.rules) - 1  # subtract one for RETURN
    