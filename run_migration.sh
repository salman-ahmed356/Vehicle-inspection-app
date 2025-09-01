#!/bin/bash
# Run this script on your VPS server

# If using docker-compose
docker-compose exec web flask db upgrade

# OR if using single container
# docker exec -it <container_name> flask db upgrade

# OR if running directly on VPS without Docker
# cd /path/to/your/app
# source venv/bin/activate
# flask db upgrade