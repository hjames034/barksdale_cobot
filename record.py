    #!/usr/bin/env python
# Copyright (c) 2020-2022, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import csv
import logging
import sys
import io
sys.path.append("..")
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import rtde.csv_writer as csv_writer
import rtde.csv_binary_writer as csv_binary_writer
#import rtde_receive
buffer = io.StringIO()
# parameters
parser = argparse.ArgumentParser()
parser.add_argument(
    "--host", default="100.100.100.5", help="name of host to connect to (localhost)"
)
parser.add_argument("--port", type=int, default=30004, help="port number (30004)")
parser.add_argument(
    "--samples", type=int, default=0, help="number of samples to record"
)
parser.add_argument(
    "--frequency", type=int, default=1, help="the sampling frequency in Herz"
)
parser.add_argument(
    "--config",
    default="record_configuration.xml",
    help="data configuration file to use (record_configuration.xml)",
)
parser.add_argument(
    "--output",
    default="robot_data.csv",
    help="data output file to write to (robot_data.csv)",
)
parser.add_argument("--verbose", help="increase output verbosity", action="store_true")
parser.add_argument(
    "--buffered",
    help="Use buffered receive which doesn't skip data",
    action="store_true",
)
parser.add_argument(
    "--binary", help="save the data in binary format", action="store_true"
)
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.INFO)

conf = rtde_config.ConfigFile(args.config)
output_names, output_types = conf.get_recipe("out")

con = rtde.RTDE(args.host, args.port)
con.connect()

# get controller version
con.get_controller_version()

# setup recipes
if not con.send_output_setup(output_names, output_types, frequency=args.frequency):
    logging.error("Unable to configure output")
    sys.exit()

# start data synchronization
if not con.send_start():
    logging.error("Unable to start synchronization")
    sys.exit()

writeModes = "wb" if args.binary else "w"
with open(args.output, writeModes) as csvfile:
    writer = None

    if args.binary:
        writer = csv_binary_writer.CSVBinaryWriter(buffer, output_names, output_types)
    else:
        writer = csv_writer.CSVWriter(buffer, output_names, output_types)

    writer.writeheader()

    i = 1
    keep_running = True
    while keep_running:

        if i % args.frequency == 0:
            if args.samples > 0:
                sys.stdout.write("\r")
                sys.stdout.write("{:.2%} done.".format(float(i) / float(args.samples)))
                sys.stdout.flush()
            else:
                sys.stdout.write("\r")
                sys.stdout.write("{:3d} samples.".format(i))
                sys.stdout.flush()
        if args.samples > 0 and i >= args.samples:
            keep_running = False
        try:
            if args.buffered:
                state = con.receive_buffered(args.binary)
            else:
                state = con.receive(args.binary)
            if state is not None:
                buffer = io.StringIO()
                writer.writerow(state)
                buffer.seek(0)
                csv_reader = csv.reader(buffer)
                data_list = list(csv_reader)
                print(data_list)
                #print(rtde_receive.RTDEProtocol.decode_data(state))
                #if the value is greater than the original value
                if state[2] > state_2:
                    state_2= state[2]
                if state[3] > state_3:
                    state_3 = state[3]
                if state[4] > state_4:
                    state_4 = state[4]
                if state[1] == 1 and state_prev == 0:
                    # reset all values and write test results to file\
                    try:
                        values = [state_0,'empty',state_2,state_3,state_4]
                        #writer.writerow(values) # write values of tests for particular ASV
                    except:
                        pass
                    #reset the values of the test
                    state_0 = state[0]
                    state_1 = 0
                    state_2 = 0
                    state_3 = 0
                    state_4 = 0
                state_prev = state[1]

                i += 1

        except KeyboardInterrupt:
            keep_running = False
        except rtde.RTDEException:
            con.disconnect()
            sys.exit()


sys.stdout.write("\rComplete!            \n")

con.send_pause()
con.disconnect()
