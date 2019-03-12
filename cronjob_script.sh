#!/bin/bash
screen -XS trading quit  # kill the current screen
screen -dmS trading  # start a new detached screen
screen -S trading -X stuff "
source activate trading;
cd /home/chunkit/projects/3xcomtw_socket_crawler; 
bash /home/chunkit/projects/3xcomtw_socket_crawler/start_crawling_script.sh
"