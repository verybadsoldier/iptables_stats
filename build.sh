set -ex
USERNAME=verybadsoldier
IMAGE=iptables_stats
docker build -t $USERNAME/$IMAGE:latest .
