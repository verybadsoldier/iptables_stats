from .iptables_stats import IpTables
import schedule
from mqtt import Mqtt
from ipset import IpSet

m = Mqtt()

def job():
    ip = IpTables()
    ipset = IpSet()
    c1, c2 ip.get_counts("FIREHOL_BLACKLIST", 'firehol_level2')
    m.publish("ipbans/blacklist", str(c1))

    num_l1 = ipset.get_ip_count("firehol_level1")
    m.publish("ipbans/blacklist_num", str(num_l1))

def main():
    schedule.every(10).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
