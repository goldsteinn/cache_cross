#! /usr/bin/env python3

import os

outfile = ".tmp-results"
build_cmd = "gcc -DRUNALL -static -nostartfiles -nodefaultlibs -nostdlib -Wl,--build-id=none cache_cross.S -o cache_cross"
perf_cmd = "perf stat --all-user -x, -e cycles,cpu/event=0xa8,umask=0x01,name=lsd_uops/,cpu/event=0x79,umask=0x08,name=dsb_uops/,cpu/event=0x79,umask=0x04,name=mite_uops/"


class Run():
    def __init__(self, loop_padding, cache_padding, payload):
        self.loop_padding = loop_padding
        self.cache_padding = cache_padding
        self.payload = payload

        self.ev_cycles = None
        self.ev_lsd = None
        self.ev_mite = None
        self.ev_dsb = None
        self.ev_cs = None

    def write_conf(self):
        fpath = "padding.h"
        try:
            f = open(fpath, "w+")
            f.write(
                "#define CACHE_PADDING NOP{}\n#define LOOP_PADDING NOP{}\n#define PAYLOAD {}"
                .format(self.cache_padding, self.loop_padding, self.payload))
            f.flush()
            f.close()
            return True
        except IOError:
            return False
        return False

    def build(self):
        global build_cmd
        return os.system(build_cmd) == 0

    def execute(self):
        if not self.build():
            return False

        global outfile
        global perf_cmd
        exe_cmd = "taskset -c 0 {} ./cache_cross 2> {}".format(
            perf_cmd, outfile)
        if os.system(exe_cmd) != 0:
            return False
        return True

    def get_result(self):
        global outfile
        hit = 0
        try:
            for line in open(outfile, "r"):
                content = line.split(",")
                if "cycles" in line:
                    hit |= 1
                    self.ev_cycles = int(content[0])
                if "lsd_uops" in line:
                    hit |= 2
                    self.ev_lsd = int(content[0])
                if "dsb_uops" in line:
                    hit |= 8
                    self.ev_dsb = int(content[0])
                if "mite_uops" in line:
                    hit |= 4
                    self.ev_mite = int(content[0])

            return hit == 15
        except IOError:
            return False
        return False

    def csv_out(self):
        return "{},{},{},{},{},{},{}".format(self.cache_padding,
                                             self.loop_padding, self.payload,
                                             self.ev_cycles, self.ev_lsd,
                                             self.ev_dsb, self.ev_mite)

    def run(self):
        assert self.write_conf()
        assert self.execute()
        assert self.get_result()
        return self.csv_out()


print("CACHE_PADDING,LOOP_PADDING,PAYLOAD,CYCLES,LSD_UOPS,DSB_UOPS,MITE_UOPS")
lp = 12
while lp < 64:
    cp = 0
    while cp <= 0:
        for pl in ["XOR", "MOV", "DSB0", "DSB1", "DSB2", "DSB3"]:
            r = Run(lp, cp, pl)
            for i in range(0, 5):
                print(r.run())
            r = Run(lp + 1, cp, pl)
            for i in range(0, 5):
                print(r.run())
        cp += 64
    lp += 16
