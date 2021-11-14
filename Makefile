start:
	src/rodonesd.py

install:
	sudo apt-get install -y python3-dev
	sudo pip install -r requirements.txt
	sudo cp rodonesd.service /usr/lib/systemd/system/
	sudo ln -s "$(realpath src/rodonesctl.py)" /bin/rodonesctl
	sudo systemctl daemon-reload
	sudo systemctl enable rodonesd
	sudo systemctl start rodonesd

pre-update:
	sudo systemctl stop rodonesd

post-update:
	sudo systemctl start rodonesd

lint:
	flake8 src/