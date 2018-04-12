#!/usr/bin/env bash
#
# Copyright 2015-2017 Cloudera, Inc.
#
# Automate running of iperf3 on Cloudera cluster nodes for network throughput tests
#
# DISCLAIMER
#
# Please note: This script is released for use "AS IS" without any warranties
# of any kind, including, but not limited to their installation, use, or
# performance. We disclaim any and all warranties, either express or implied,
# including but not limited to any warranty of noninfringement,
# merchantability, and/ or fitness for a particular purpose. We do not warrant
# that the technology will meet your requirements, that the operation thereof
# will be uninterrupted or error-free, or that any errors will be corrected.
#
# Any use of these scripts and toxxxols is at your own risk. There is no guarantee
# that they have been through thorough testing in a comparable environment and
# we are not responsible for any damage or data loss incurred with their use.
#
# You are responsible for reviewing and testing any scripts you run thoroughly
# before use in any non-testing environment.

VERSION=1.0

function info() {
    echo "$(date) [$(tput setaf 2)INFO $(tput sgr0)] $*"
}

function err() {
    echo "$(date) [$(tput setaf 1)ERROR$(tput sgr0)] $*"
}

function warn() {
    echo "$(date) [$(tput setaf 3)WARN $(tput sgr0)] $*"
}

function debug() {
    if [[ $DEBUG_MODE ]]; then
        echo "$(date) [$(tput setaf 2)DEBUG$(tput sgr0)] $*"
    fi
}

function die() {
    err "$@"
    exit 2
}

function validate_cm_url() {
    local url_test cm_output
    local regex='(http|https?)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]'

    if [[ ${OPT_CMURL} =~ $regex ]]; then
        url_test=$(curl -k --silent --head --fail "${OPT_URL}")
        if [ ! -z "${url_test}" ]; then
            info "Cloudera Manager seems to be running"
        else
            die "Can't connect to Cloudera Manager. Check URL and firewalls."
        fi
    else
        err  "Invalid Cloudera Manager URL '$OPT_URL'"
        exit 1
    fi

    cm_output=$(curl -k -s -u "$OPT_USER:$OPT_PASSWORD" "$OPT_URL/api")
    if grep -q "Error 401 Bad credentials" <<< "$cm_output"; then
        die "Authentication to Cloudera Manager failed. Check username and password."
    fi
}

function cleanup {
    if [ "$COMPLETED" == "1" ]; then
            echo ""
            echo "Tests completed"
    else
            echo ""
            echo "Terminating script... stopping tests"
            echo "Cleaning up iperf3 process on $SERVER"
            ssh "$OPT_USER@$SERVER" "ps aux | grep 'iperf3' | awk '{print \$2}' | xargs kill" > /dev/null 2>&1
            kill SSH_PID > /dev/null 2>&1
    fi
    }

function write_summary {
    cat > "$OUTPUTDIR/summary.txt" <<EOL
{
    "start_time" : "${STARTTIME}",
    "iperf_server_cmd" : "${CMD_IPERF_SERVER}",
    "iperf_client_cmd" : "${CMD_IPERF_CLIENT} <SERVER>"
}
EOL
}

function fetch_cmhost {
    #info "Retrieving hosts from Cloudera Manager server."
    die "Retrieving hosts from CM is not implemented yet. Akan datang."
}

function usage() {
    local SCRIPT_NAME=
    SCRIPT_NAME=$(basename "${BASH_SOURCE[0]}")
    echo
    echo "IPERF Cluster Network Benchmark Utility v$VERSION"
    echo
    echo "$(tput bold)USAGE:$(tput sgr0)"
    echo "  ./${SCRIPT_NAME} [OPTIONS]"
    echo
    echo "$(tput bold)OPTIONS:$(tput sgr0)"
    echo "  $(tput bold)-h, --hostfile $(tput sgr0)<arg>"
    echo "        File containing the list of hosts (default hosts.lst)."
    echo
    echo "  $(tput bold)-u, --sshuser $(tput sgr0)<arg>"
    echo "        User account used for SSH to the hosts. This account must be able to"
    echo "        SSH without specifying a password."
    echo
    echo "$(tput bold)IPERF OPTIONS:$(tput sgr0)"
    echo "  $(tput bold)-p, --port $(tput sgr0)<arg>"
    echo "        Set server port to listen on/connect to (default 5201)"
    echo
    echo "  $(tput bold)-P, --parallel $(tput sgr0)<arg>"
    echo "        Number of parallel client streams to run (default 5)."
    echo
    echo "  $(tput bold)-t, --time $(tput sgr0)<arg>"
    echo "        Time in seconds to transmit for (default 10 secs)."
    echo
    echo "$(tput bold)CLOUDERA MANAGER OPTIONS:$(tput sgr0)"
    echo "  $(tput bold)--cmurl $(tput sgr0)<arg>"
    echo "        Cloudera Manager URL (e.g. http://cm-mycluster.com:7180)."
    echo
    echo "  $(tput bold)--cmuser $(tput sgr0)<arg>"
    echo "        Cloudera Manager username."
    echo
    echo "  $(tput bold)--cmpassword $(tput sgr0)<arg>"
    echo "        Cloudera Manager user password."
    echo
    exit 1
}

OPT_USER="root"     # username for passwordless ssh access
OPT_PORT=5201       # port server will listen on
OPT_THREADS=5       # number of parallel client threads sending data
OPT_DURATION=10     # duration of transmitting data
OPT_HOSTFILE="hosts.lst"

HOSTS=()

if [[ $# -eq 0 ]]; then
    usage
    die
fi

while [[ $# -gt 0 ]]; do
    KEY=$1
    shift
    case ${KEY} in
        -h|--hostfile)      OPT_HOSTFILE="$1";      shift;;
        -u|--sshuser)       OPT_USER="$1";          shift;;
        -p|--port)          OPT_PORT="$1";          shift;;
        -t|--time)          OPT_DURATION="$1";      shift;;
        --cmurl)            OPT_CMURL="$1";         shift;;
        --cmuser)           OPT_CMUSER="$1";        shift;;
	--cmpassword)       OPT_CMPASSWORD="$1";    shift;;
        --help)             OPT_USAGE=true;;
        *)                  OPT_USAGE=true
                            err "Unknown option: ${KEY}"
                            break;;
    esac
done


if [ -z "${OPT_HOSTFILE}" ] && [ -z "${OPT_CMURL}" ]; then
    die "Please specify a hostfile or Cloudera Manager URL."
fi

if ! [ -z "${OPT_CMURL}" ]; then
    validate_cm_url
    if [ -z "${OPT_CMUSER}" ] || [ -z "${OPT_CMPASSWORD}" ]; then
        die "Please specify a Cloudera username and password."
    else
        fetch_cmhost
    fi
else
    if [[ -r "${OPT_HOSTFILE}" ]]; then
        IFS=$'\n' read -d '' -r -a HOSTS < "${OPT_HOSTFILE}"
    else
        die "Unable to read file ${OPT_HOSTFILE}."
    fi
fi

if [ ${#HOSTS[@]} -lt 2 ]; then
    die "Need more than 1 hosts to perform tests, only found ${#HOSTS[@]}."
fi

info "Starting network tests"

STARTTIME=$(date "+%Y-%m-%d %H:%M:%S")
CMD_IPERF_SERVER="iperf3 -s -1 -i 0 -p $OPT_PORT"
CMD_IPERF_CLIENT="iperf3 -t $OPT_DURATION -P $OPT_THREADS -4 -p $OPT_PORT -i 0 -J -c "
COMPLETED=0

OUTPUTDIR="RESULTS-"$(date -d"${STARTTIME}" "+%y%m%d-%H%M%S")

if [ ! -d "$OUTPUTDIR" ]; then
        mkdir "$OUTPUTDIR"
fi

write_summary

trap cleanup EXIT

SERVER=""
CLIENT=""

for i in "${!HOSTS[@]}"; do

        SERVER="${HOSTS[$i]}"
        OUTFILE="$OUTPUTDIR/$SERVER.json"
        echo "[" > "$OUTFILE"

        info "===== Staring iperf3 server on $SERVER ====="

        for j in "${!HOSTS[@]}"; do
                CLIENT="${HOSTS[$j]}"

                if [ "$SERVER" != "$CLIENT" ]; then
                        info "Testing throughput from $CLIENT -> $SERVER"

                        ssh "$OPT_USER@$SERVER" "$CMD_IPERF_SERVER" > /dev/null 2>&1 &

                        sleep 5 #give some time for the server process to load

                        echo "{ \"client\": \"$CLIENT\"," >> "$OUTFILE"
                        echo "  \"result\":" >> "$OUTFILE"

                        clientcmd="$CMD_IPERF_CLIENT $SERVER"
                        ssh "$OPT_USER@$CLIENT" "$clientcmd" >> "$OUTFILE"
			echo "}," >> "$OUTFILE"
                fi
        done
        echo "]" >> "$OUTFILE"
done

# Post-processing - remove last comma from each result json files
for FILE in "$OUTPUTDIR/*.json"; do
	sed -i 'x;${s/,$//;p;x;};1d' $FILE
done
