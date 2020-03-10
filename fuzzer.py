#!/usr/bin/python

from pwn import *
import random
import string

def load_file(fname):
    with open(fname, "rb") as f:
        return bytearray(f.read())


def write_to_file(file_name, data):
    with open(file_name, 'w') as f:
        f.write(str(data))
    return

def mutate_bits(data):
    data_copy = data[::]
    count = len(data_copy)*8*0.01
    for i in xrange(int(count)):
        rand_no = random.randint(0, len(data)*8-1)

        flipped = data_copy[rand_no/8]^(1<<(rand_no%8))
        original = data_copy[rand_no/8]   
        data_copy[rand_no/8] = flipped
    return data_copy

def mutate_bytes(data):
    data_copy = data[::]
    rand_no = random.randint(0, len(data)-1)
    random_byte = chr(random.randint(0,255))

    data_copy[rand_no] = random_byte
    return data_copy

def run(exename):
    p = subprocess.Popen(["gdb", "--batch-silent", "-x", "fuzz.gdb", exename],
        stdout=subprocess.PIPE,
        stderr=None)
    # argv = ["--batch-silent", "-x", "fuzz.gdb", exename]
    # s = process(executable="gdb", argv=argv, stderr=None)
    # output = s.recvall(timeout=1)
    output, _ = p.communicate()
    if "Program received signal" in output:
        return output.split("------------------------------")[1]
    return None


def mutate_magic(data):
    numbers = [
        (1, p8(0xff)),
        (1, p8(0x7f)),
        (1, p8(0)),
        (2, p16(0xffff)),
        (2, p16(0)),     
        (4, p32(0xffffffff)),
        (4, p32(0)),
        (4, p32(0x80000000)),
        (4, p32(0x40000000)),
        (4, p32(0x7fffffff)),
    ]

    count = int(len(data) * 0.01)
    if count == 0:
        count = 1
    for _ in range(count):
        n_size, n = random.choice(numbers)
        sz = len(data) - n_size
        if sz < 0:
            continue
    idx = random.randint(0, sz)
    data[idx:idx + n_size] = bytearray(n)

    return data

def mutate(data):
    
    data_copy = random.choice([mutate_bits, mutate_bytes, mutate_magic])(data)
    return data_copy


def main():
    input_samples = [
        load_file("input.sample")
    ]

    i = 0

    while True:
        i += 1
        if True:
            sys.stdout.write(".")
            sys.stdout.flush()
        mutated_sample = mutate(random.choice(input_samples))
        write_to_file("test.sample", mutated_sample)

        output = run("test_bin")
        if output is not None:
            print "CRASH!"
            write_to_file("crash.samples.%i" % i, mutated_sample)
            write_to_file("crash.samples.%i.txt" % i, output)
            print output

if __name__ == '__main__':
    main()
