all: clean build

build:
	gcc -no-pie -static-pie -m32 source.c -o multiple_inputs.elf

clean:
	rm -f multiple_inputs.elf
