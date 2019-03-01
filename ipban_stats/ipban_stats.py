import argparse
import logging
import time
import logging

from ipban_stats.config import load_config
from ipban_stats.sinks import MqttSink
import functools
import schedule

from .reading_modules import ipset
from .reading_modules import iptables


_logger = logging.getLogger()


class JobFactory:
    def __init__(self, sinks):
        self._sinks = sinks

    class Job:
        def __init__(self, sinks, module_name, reading_fnc):
            self._sinks = sinks
            self._module_name = module_name
            self._reading_fnc = reading_fnc

        def __call__(self):
            readings = self._reading_fnc()

            for sink in self._sinks:
                for reading_name, value in readings.items():
                    sink.publish(self._module_name, reading_name, value)

    def build_job(self, module_name, reading_fnc):
        return JobFactory.Job(self._sinks, module_name, reading_fnc)

#
# def job_pkg_count(name, chain, rule_regex):
#     num_packages, num_bytes = iptables_stats.get_counts(chain, rule_regex)
#     m.publish("home/minion/iptables/MYCHAIN/firehol_level2/num_packages", str(num_packages))
#     m.publish("home/minion/iptables/MYCHAIN/firehol_level2/num_bytes", str(num_bytes))
#
#
# def job():
#     logging.info('Running job')
#
#     # iptables
#     num_packages, num_bytes = iptables_stats.get_counts("MYCHAIN", 'firehol_level2')
#     m.publish("home/minion/iptables/MYCHAIN/firehol_level2/num_packages", str(num_packages))
#     m.publish("home/minion/iptables/MYCHAIN/firehol_level2/num_bytes", str(num_bytes))
#
#     # ipset
#     ipset = IpSet()
#     num_l1 = ipset.get_ip_count("myset")
#     m.publish("home/minion/ipset/firehol_level1/count", str(num_l1))
#

def _get_interval(cfg):
    return 1 if 'interval' not in cfg else int(cfg['interval'])


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Publish IP statistic values periodically.')
    parser.add_argument('--config_file', type=str, default='/etc/ipstatistics.yml',
                        help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config_file)

    sinks = []
    if 'mqtt' in config:
        cfg = config['mqtt']
        port = 1883 if 'port' not in cfg else int(cfg['port'])
        topic_root = None if 'topic_root' not in cfg else cfg['topic_root']
        mqtt = MqttSink(cfg['host'], port, topic_root)
        sinks.append(mqtt)

    if len(sinks) == 0:
        _logger.warning('Invalid config! No sinks defined!')

    job_factory = JobFactory(sinks)

    if 'iptables_pkg_count' in config:
        for k, v in config['iptables_pkg_count'].items():
            fnc = functools.partial(iptables.get_rule_counters, v['chain'], v['rule_regex'])
            job = job_factory.build_job('iptables_pkg_count', fnc)
            schedule.every(_get_interval(v)).seconds.do(job)

    if 'iptables_rule_count' in config:
        for k, v in config['iptables_rule_count'].items():
            fnc = functools.partial(iptables.get_num_rules, v['chain'])
            job = job_factory.build_job('iptables_rule_count', fnc)
            schedule.every(_get_interval(v)).seconds.do(job)

    if 'ipset_count' in config:
        for k, v in config['ipset_count'].items():
            fnc = functools.partial(ipset.get_ip_count, v['setname'])
            job = job_factory.build_job('ipset_count', fnc)
            schedule.every(_get_interval(v)).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
