#!/usr/bin/env python

try:
    import yaml
except:
    print "You need to install PyYaml(http://pyyaml.org/)"
    sys.exit( 0 )

import sys
import subprocess

# The default file name for the YAML file
config_file = "settings.yml"

# Let the user override the default file name for the YAML file
if len( sys.argv ) > 1:
    config_file = sys.argv[1]

# Load the yaml file and set the config variable
config = yaml.load( open( config_file ).read() )

# Location of ssh
SSHCMD = '/usr/bin/ssh'

# Parse out the YAML file into a simple dictionary of mappings
def get_tunnels( servers ):
    tunnels = []

    for server, mappings in config['servers'].items():
        for lport, rport in mappings['port_mappings'].items():
            tunnels.append( "-L %s:%s:%s" % (lport,server,rport) )

    return tunnels

# Get a string to use for the ssh
def tunnels_to_string( tunnel_list ):
    return "-L " + " -L ".join( tunnel_list )

# Start the tunnels and return the Popen object
def start_tunnels( tunnel_list, config ):
    ssh_args = ["-l %s" % config['ssh_server']['username'],'-i', config['ssh_server']['ident_file'], '-N']
    args = [SSHCMD] + ssh_args + tunnel_list + [config['ssh_server']['server']]
    print " ".join( args )
    return subprocess.Popen( " ".join( args ), shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.STDOUT )

def start_ADS( ads_options ):
    return subprocess.Popen( ads_options['command_to_open'], shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.STDOUT )

# Start up the tunnels
print "Opening Tunnels"
ssh_process = start_tunnels( get_tunnels( config ), config )
print "Opened with process id of: %s" % ssh_process.pid

print "Opening ADS"
ads_process = start_ADS( config['ADS'] )
print "Opened with process id of: %s" % ads_process.pid

# Wait for Apache Directory Studio to exit
ads_process.wait()

# Close the SSH Tunnels
ssh_process.poll()
if not ssh_process.returncode:
    ssh_process.terminate()
    print "Terminated ssh tunnels"
