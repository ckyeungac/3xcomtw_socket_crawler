#!/bin/bash
# kill the current screen
screen -XS trading quit  

# restart a new screen
cd /home/chunkit/projects/3xcomtw_socket_crawler
screen -dmS trading bash -c "cd /home/chunkit/projects/3xcomtw_socket_crawler && bash /home/chunkit/projects/3xcomtw_socket_crawler/start_crawling_script.sh"