CC=gcc
CFLAGS=-static -nostartfiles -nodefaultlibs -nostdlib -Wl,--build-id=none
TARGET=cache_cross

all:
	$(CC) $(CFLAGS) $(TARGET).S -o $(TARGET)

clean:
	rm -f $(TARGET)
