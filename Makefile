BIN_INSTALL_PATH=/usr/local/bin/

all:
	@echo "Execute `make install` to copy the init.d scripts"

install:
	@echo "Installing scripts . . ."
	
	test -e ${BIN_INSTALL_PATH}/x2canvas-server && unlink ${BIN_INSTALL_PATH}/x2canvas-server
	ln -s x2canvas-server ${BIN_INSTALL_PATH}/x2canvas-server
	cp init.d/x2canvas-server.sh /etc/init.d/x2canvas-server
	update-rc.d x2canvas-server defaults 99
	cp logrotate.d/x2canvas-server /etc/logrotate.d/x2canvas-server
	
	@echo "Done. Execute `/etc/init.d/x2canvas-server start`
