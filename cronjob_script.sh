#!/bin/bash
source /home/chunkit/.bashrc
source activate trading
screen -XS trading quit
sleep 1
screen -dmS trading \
&& screen -S trading -X stuff \
     "source activate trading \
      && cd /home/chunkit/projects/3xcomtw_socket_crawler \
      && bash /home/chunkit/projects/3xcomtw_socket_crawler/start_crawling_script.sh \n"

