AUXD = auxiliary/ubuntu-hardy

DISKS = $(AUXD)/root.qcow2 $(AUXD)/swap.qcow2
OVF = $(AUXD)/httpd.ovf
OVF_ENV = $(AUXD)/ovf-env.iso
QEMU_SCRIPT = $(AUXD)/ubuntu.qemu

OUTPUT = $(DISKS) $(OVF) $(OVF_ENV) $(QEMU_SCRIPT)

all: $(OUTPUT)

$(DISKS) $(QEMU_SCRIPT): createimg
	@echo "making $@"
	[ ! -e $(AUXD) ] || rmdir $(AUXD)
	sudo ./createimg

$(OVF): mk-httpd-ovf $(QEMU_SCRIPT)
	./mk-httpd-ovf $(AUXD)

$(OVF_ENV): ovf-env.xml
	mkisofs -JR -o $@ ovf-env.xml

clean:
	rm -f $(OUTPUT)
