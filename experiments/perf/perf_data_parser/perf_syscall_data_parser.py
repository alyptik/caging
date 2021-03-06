"""
<script name> perf_syscall_data_parser.py
<author> Yiwen Li
<creation date> 10/23/17
<purpose> 
this script is to parse the system call time information generated by the perf_event tool
raw data was generated with the following command:
perf record -m 10M -e syscalls:sys_enter_* -e syscalls:sys_exit_* bash ./script  
the raw data should look like this:
            bash 19066 [001] 329000.701687: syscalls:sys_enter_brk: brk: 0x00000000
            bash 19066 [001] 329000.701690: syscalls:sys_exit_brk: 0xb25000
            bash 19066 [001] 329000.701710: syscalls:sys_enter_access: filename: 0x7f15f5ab98c3, mode: 0x00000000
            bash 19066 [001] 329000.701716: syscalls:sys_exit_access: 0xfffffffffffffffe
<output>
output is directed to both the standard output and the defined output path
output contains a list of system calls, each line has the format of <syscall_name num_of_invoked_times total_execution_time>
output should look like the following:
lseek: 4 4.99992165715e-06
rt_sigaction: 16 1.49999978021e-05
mprotect: 16 0.000879999948665
brk: 18 0.000873999961186
close: 19 1.99999776669e-05
"""

import sys, os, string, getopt

is_syscall_enter = -1
syscall_invoked_times_dict = dict()
syscall_timing_dict = dict()
syscall_time_start = dict()
syscall_time_finish = dict()

def parse_input(infile):
   for line in infile:
      global is_syscall_enter
      global syscall_invoked_times_dict
      global syscall_timing_dict
      global syscall_time_start
      global syscall_time_finish
 
      words = line.split(":") 
      words_0 = words[0].split("] ")
      syscall_status = words[2].split("_")[1]
      if syscall_status == "enter":
         is_syscall_enter = 1 
         syscall_name = words[2][10:]
      if syscall_status == "exit":
         is_syscall_enter = 0
         syscall_name = words[2][9:]

      if is_syscall_enter == 1: 
         syscall_time_start[syscall_name] = float(words_0[1])   
      else: 
         syscall_time_finish[syscall_name] = float(words_0[1])

      if is_syscall_enter == 0:
         if syscall_name in syscall_invoked_times_dict:
            syscall_invoked_times_dict[syscall_name] = syscall_invoked_times_dict[syscall_name] + 1
            syscall_timing_dict[syscall_name] = syscall_timing_dict[syscall_name] + syscall_time_finish[syscall_name] - syscall_time_start[syscall_name]         
         else:
            syscall_invoked_times_dict[syscall_name] = 1
            syscall_timing_dict[syscall_name] = syscall_time_finish[syscall_name] - syscall_time_start[syscall_name]


def main(argv):
   global syscall_invoked_times_dict
   global syscall_timing_dict
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'perf_syscall_data_parser.py -i <input_file> -o <output_file>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'perf_syscall_data_parser.py -i <input_file> -o <output_file>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg   

   if os.path.isfile(inputfile):
      infile = open(inputfile, 'r')
      outfile = open(outputfile, 'w')
      parse_input(infile)
      infile.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)

   syscall_total_time = 0.0
   syscall_total_invoked_times = 0
   for syscall in syscall_invoked_times_dict:
      print syscall + ": " + str(syscall_invoked_times_dict[syscall]) + " " + str(syscall_timing_dict[syscall])
      syscall_total_time = syscall_total_time + syscall_timing_dict[syscall]
      syscall_total_invoked_times = syscall_total_invoked_times + syscall_invoked_times_dict[syscall]
      outfile.write(syscall + ": " + str(syscall_invoked_times_dict[syscall]) + " " + str(syscall_timing_dict[syscall]) + "\n")
   print "syscall_total_time = " + str(syscall_total_time)
   outfile.write("syscall_total_time = " + str(syscall_total_time) + "\n")
   print "syscall_total_invoked_times = " + str(syscall_total_invoked_times)
   outfile.write("syscall_total_invoked_time = " + str(syscall_total_invoked_times) + "\n")
   outfile.close()


if __name__ == "__main__":
   main(sys.argv[1:])
