#!/usr/bin/env python
'''
#
# Copyright 2015-2017 Cloudera, Inc.
#
# Collate iperf3 output in JSON files and generate results as CSV or HTML
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
'''
import os
import sys
import json
import argparse
import cgi
import socket

def untar_results(file):
    import tempfile, tarfile
    tmpdir = tempfile.mkdtemp()

    print("Extracting results to " + tmpdir)
    tf = tarfile.open(file)
    tf.extractall(tmpdir)

    return tmpdir

def process_json(server, client, file):    
    if not server in bw_array:
        bw_array[server] = {}

    with open(file) as json_file:
        try:
            json_data = json.load(json_file)
            bwresults = {"received": json_data["result"]["end"]["sum_received"], "sent": json_data["result"]["end"]["sum_sent"]}
            bw_array[server][client] = bwresults

        except ValueError as e:
            bw_array[server][client] = {"error": str(e)}

def process_summary(file):
    if os.path.isfile(file):
        with open(file) as json_file:
            json_data = json.load(json_file)
            summary["start_time"] = json_data["start_time"]
            summary["iperf_client_cmd"] = json_data["iperf_client_cmd"]
            summary["iperf_server_cmd"] = json_data["iperf_server_cmd"]
    else:
        summary["start_time"] = "N/A"
        summary["iperf_client_cmd"] = "N/A"
        summary["iperf_server_cmd"] = "N/A"

def output_html():
    HTMLHEADER = (
        "<html><head><title>iPerf3 bandwidth test results</title>",
        "<style>",
        "table, th, td { border: 1px solid black; }",
        "th, td {",
        "    font-size: 12px;",
        "    width: 40px;",
        "    text-align: center;",
        "    padding: 0px;",
        "    border: 1px solid #e6e6e6;",
        "    border-width: thin;",
        "}",
        "th { background-color: #f2f2f2; }",
        "td.header {",
        "    text-align: left;",
        "    font-weight: bold;",
        "    padding: 2px;",
        "    background-color: #f2f2f2;",
        "}",
        "td.legend { width: 160px; }",
        "td.green  { background-color: #99FF99; }",
        "td.gray   { background-color: #f2f2f2; }",
        "td.yellow { background-color: #FFFF99; }",
        "td.red    { background-color: #FF6666; }",
        "td.error  { background-color: #FF6666; font-size: 10px; font-weight: bold; }",
        "table.result {",
        "    border: 2px solid LightGray;",
        "    border-spacing: 0;",
        "    table-layout : fixed;",
        "    padding: 0px;",
        "    margin-left: 10px;"
        "}",
        "table.legend {",
        "    border: 2px solid LightGray;",
        "    border-spacing: 0;",
        "    padding: 0px;",
        "    margin-top: 20px;",
        "    margin-left: 10px;",
        "}",
        "body {",
        "    font-family: Helvetica Neue,Helvetica,Arial,sans-serif;",
        "    font-size: 14px;",
        "    line-height: 1.42857143;",
        "    color: #333;",
        "    background-color: #fff;",
        "    -webkit-font-smoothing: antialiased;",
        "}",
        "th.rotate {",
        "    height: 110px;",
        "    white-space: nowrap;",
        "}",
        "th.rotate > div {",
        "    transform:",
        "        translate(20px, 50px)",
        "        rotate(270deg);",
        "    width: 0px;",
        "}",
        "div.top-banner {",
        "    margin: 0px;",
        "    padding: 0px;",
        "    background-color: #f8f8f8;",
        "    border-color: #e7e7e7;",
        "    min-height: 50px;",
        "    margin-bottom: 0px;",
        "}",
        "div.horizontal-bar {",
        "    margin: 0px;",
        "    border-top: 1px solid LightGray;",
        "    border-bottom: 1px solid LightGray;",
        "    min-height: 10px;",
        "    background-color: #305673;",
        "}",
        "div.title-bar {",
        "margin: 0px;",
        "margin-bottom: 20px;",
        "min-height: 50px;",
        "background-color:  # f2f2f2;",
        "border-bottom: 1px solid LightGray;",
        "}",
        "h1 {",
        "font-size: 22px;",
        "font-weight: normal;",
        "line-height: 48px;",
        "margin-top: 0;",
        "margin-bottom: 0;",
        "margin-left: 20px;",
        "}",
        "body {",
        "margin: 0px;",
        "padding: 0px;",
        "}",
        "</style></head>",
        "<body>",
    )

    BANNER = (
        "<div class=\"top-banner\">",
        "<img alt=\"Cloudera Logo\" style=\"height: 20px; margin-top: 15px; margin-left: 10px\" src=\"data:image/png",
        ";charset=utf-8;base64,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\">",
        "</div>",
        "<div class=\"horizontal-bar\"></div>",
        "<div class=\"title-bar\"><h1>iPerf3 Network Benchmark Results</h1>",
        "<P><U style=\"padding-left: 50px\">Parameters:</U></P>",
        "<P style=\"padding-left: 50px; font-family: courier\">"
        "Start time: " + cgi.escape(summary["start_time"]) + "<BR>",
        "iperf3 server cmd: " + cgi.escape(summary["iperf_server_cmd"]) + "<BR>",
        "iperf3 client cmd: " + cgi.escape(summary["iperf_client_cmd"]) + "<BR>",
        "max bandwidth: " + str(bw_total) + " Gbit/sec<BR>",
        "</P>",
        "</div>"
    )

    LEGEND = (
        "<div><table class=\"legend\">",
        "    <tr><td colspan=\"2\"><p>Legend</p></td></tr>",
        "<tr>",
        "    <td><div style=\"padding: 5px; margin: 1px; background-color: #99FF99\"></div></td>",
        "	 <td class=\"legend\">Throughput &ge; 80% of max</td>",
        "</tr>",
        "<tr>",
        "	<td><div style=\"padding: 5px; margin: 1px; background-color: #FFFF99\"></td>",
        "	<td class=\"legend\">Throughput &ge; 60% of max</td>",
        "</tr>",
        "<tr>",
        "	<td><div style=\"padding: 5px; margin: 1px; background-color: #ff6666\"></td>",
        "	<td class=\"legend\">Throughput < 60% of max</td>",
        "</tr></table></div>",
        "<P></P>"
    )

    outfile = open("iperf-results.html", "w+")
    for line in HTMLHEADER:
        outfile.writelines(line + "\n")

    for line in BANNER:
        outfile.writelines(line)

    outfile.writelines("\n<!-- Result table below -->\n")
    outfile.writelines("<table class=\"result\">\n")
    outfile.writelines("<tr><th>Values in Gbit/sec</th>\n")
    for desthost in sorted(bw_array.iterkeys()):
        # check if we are using IP address or hostname/FQDN
        try:
            socket.inet_aton(desthost)
            outfile.writelines("<th class=\"rotate\"><div>" + desthost + "</div></th>\n")
        except socket.error:
            outfile.writelines("<th class=\"rotate\"><div>" + desthost.split(".")[0] + "</div></th>\n")
    outfile.writelines("</tr>\n")

    for srchost in sorted(bw_array.iterkeys()):
        row = bw_array[srchost]
        try:
            socket.inet_aton(srchost)
            outfile.writelines("<tr><td class=\"header\">" + srchost + "</td>\n")
        except socket.error:
            outfile.writelines("<tr><td class=\"header\">" + srchost.split(".")[0] + "</td>\n")

        for desthost in sorted(bw_array.iterkeys()):
            if srchost == desthost:
                outfile.writelines("<td class=\"gray\"></td>")

            elif bw_array[srchost][desthost].keys()[0] == "error":
                outfile.writelines("<td class=\"error\"> ERROR </td>")

            else:
                Gbps = bw_array[srchost][desthost]["received"]["bits_per_second"] / 1000000000
                outfile.writelines("<td class=")
                percent = Gbps / bw_total
                if percent > 0.8:
                    outfile.writelines("\"green\"")
                elif percent > 0.5:
                    outfile.writelines("\"yellow\"")
                else:
                    outfile.writelines("\"red\"")
                outfile.writelines(">")
                outfile.writelines(str(round(Gbps, 2)))
                outfile.writelines("</td>")
        outfile.writelines("</td></tr>\n")
    outfile.writelines("</table>\n")

    for line in LEGEND:
        outfile.writelines(line + "\n")

    outfile.writelines("</body></html>\n")
    outfile.close()


def handle_args():
    """Handle command line arguments, returning the options."""

    directory = ""

    if len(sys.argv) == 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":

            sys.exit(1)
        else:
            directory = sys.argv[1]

    if directory == "":
        sys.stderr.write("Usage: " + usage + "\n")
        sys.exit(1)

    return directory


def main():
    """Invoked as a main from the command line, so parse the command line arguments"""
    global parser
    parser = argparse.ArgumentParser(description="iperf3-util result parser.")
    #parser.add_argument('-d', metavar="directory", required=True, help="Directory containing the result json files.")
    parser.add_argument('-f', metavar="tarfile", required=True, help="Zipped tarball of iperf3 test results")
    parser.add_argument('-bw', metavar="bandwidth", type=int, required=True, help="Theoretical maximum bandwidth for each hosts. E.g. 20 for 20Gbps")

    opt=parser.parse_args()

    global bw_array
    global bw_total
    global summary

    summary = {}
    bw_array = {}
    bw_total = opt.bw
    tarfile = opt.f

    if not os.path.isfile(tarfile):
        sys.stderr.write("Error: file " + tarfile + " not found\n")
        sys.exit(2)
    else:
        print("Processing iperf3 output tarfile " + tarfile)
        result_dir=untar_results(tarfile)

        process_summary(result_dir + "/summary.txt")

        # Process each dir which contain iperf3 result for a node
        dirlist = os.listdir(result_dir)
        for src in dirlist:
            if os.path.isdir(result_dir + "/" + src):
                print("Processing result for " + src)
                jsonlist = os.listdir(result_dir + "/" + src)

                for file in jsonlist:
                    if file.endswith(".json"):
                        print("Processing json " + file)
                        process_json(src, os.path.splitext(file)[0],result_dir + "/" + src + "/" + file)

        output_html()
        
        # clean up the temp directory
        import shutil
        shutil.rmtree(result_dir)
        print("Removed temp directory " + result_dir)


if __name__ == "__main__":
    main()
