# Modified from https://lindevs.com/install-redis-from-source-code-on-raspberry-pi/
# Download Redis
curl -O  http://download.redis.io/releases/redis-6.2.6.tar.gz
tar xzvf redis-6.2.6.tar.gz
rm -rf redis-6.2.6.tar.gz

# Build and install Redis
cd redis-6.2.6
sudo make install
cd ..

# Configure Redis
sudo mkdir /etc/redis
sudo cp redis-6.2.6/redis.conf /etc/redis
sudo sed -i 's/# supervised auto/supervised systemd/' /etc/redis/redis.conf
sudo sed -i 's/dir .\//dir \/var\/lib\/redis/' /etc/redis/redis.conf
rm -rf redis-6.2.6

# Create user for Redis
sudo adduser --system --group --no-create-home redis
sudo mkdir /var/lib/redis
sudo chown redis:redis /var/lib/redis
sudo chmod 770 /var/lib/redis

# Make Redis a service
sudo tee -a /etc/systemd/system/redis.service > /dev/null <<EOT
[Unit]
Description=In-memory data structure store
After=network.target
 
[Service]
User=redis
Group=redis
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always
 
[Install]
WantedBy=multi-user.target
EOT

# Enable auto start at boot
sudo systemctl enable redis

# Start Redis service
sudo service redis start

# To test installation
# redis-cli -- PING


# To uninstall
# sudo dpkg -r redis
# sudo rm -rf /etc/redis
# sudo rm -rf /var/lib/redis
# sudo deluser redis