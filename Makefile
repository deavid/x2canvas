BIN_INSTALL_PATH=/usr/local/bin
CPATH=$$(pwd)

all:
	@echo "Execute 'make install' to copy the init.d scripts"

install:
	@echo "Installing scripts . . ."
	
	test -h ${BIN_INSTALL_PATH}/x2canvas-server && unlink ${BIN_INSTALL_PATH}/x2canvas-server || echo -n
	ln -s $(CPATH)/x2canvas-server ${BIN_INSTALL_PATH}/x2canvas-server
	cp init.d/x2canvas-server.sh /etc/init.d/x2canvas-server
	update-rc.d x2canvas-server defaults 99
	cp logrotate.d/x2canvas-server /etc/logrotate.d/x2canvas-server
	test -e config.ini || cp config.template.ini config.ini
	
	@echo "Done. Execute '/etc/init.d/x2canvas-server start'"
