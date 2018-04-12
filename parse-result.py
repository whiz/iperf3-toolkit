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

def process_json(file):
    with open(file) as json_file:
        json_data = json.load(json_file)

        server = json_data[0]["result"]["start"]["connecting_to"]["host"]
        row = {}
        for element in json_data:
            bwresults = {"received": element["result"]["end"]["sum_received"], "sent": element["result"]["end"]["sum_sent"]}
            client = element["client"]
            row[client] = bwresults

        bw_array[server] = row

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
        "td.red    { background-color: #FF6666; }", "",
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
        "    background-color: #0078D9;",
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
        "<img alt=\"Cloudera Logo\" style=\"height: 20px; margin-top: 15px; margin-left: 10px\" src=\"data:image/svg+xml",
        ";charset=utf-8;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkxheWVyX",
        "zEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9",
        "IjBweCIgeT0iMHB4IiB2aWV3Qm94PSIwIDAgMTc1IDMxLjMiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDE3NSAzMS4zOyIgeG1",
        "sOnNwYWNlPSJwcmVzZXJ2ZSI+PHN0eWxlIHR5cGU9InRleHQvY3NzIj4uc3Qwe2ZpbGw6IzAwNTg4NDt9LnN0MXtmaWxsOiMwMDU4ODI7fS5zdD",
        "J7ZmlsbDojMDBBN0UwO308L3N0eWxlPjxnPjxnPjxnPjxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0xNzAuMyw2LjljMS41LDAsMi40LDEuMSwyLjQsM",
        "i40YzAsMS4zLTEsMi40LTIuNCwyLjRjLTEuNSwwLTIuNC0xLjEtMi40LTIuNEMxNjcuOCw4LDE2OC44LDYuOSwxNzAuMyw2Ljl6TTE3MC4zLDEx",
        "LjRjMS4yLDAsMi0wLjksMi0yYzAtMS4xLTAuOS0yLjEtMi0yLjFjLTEuMiwwLTIsMC45LTIsMi4xQzE2OC4yLDEwLjUsMTY5LjEsMTEuNCwxNzA",
        "uMywxMS40eiBNMTcwLjMsOS43aC0wLjV2MS4xaC0wLjVWOGgxYzAuNywwLDEuMSwwLjIsMS4xLDAuOWMwLDAuNC0wLjEsMC43LTAuNSwwLjhsMC",
        "41LDEuMWgtMC42TDE3MC4zLDkuN3ogTTE2OS44LDkuM2gwLjVjMC4zLDAsMC41LTAuMSwwLjUtMC40YzAtMC4zLTAuMi0wLjQtMC42LTAuNGgtM",
        "C40VjkuM3oiLz48L2c+PGc+PGc+PHBhdGggY2xhc3M9InN0MSIgZD0iTTE0My40LDdjLTEuNiwwLTMuMiwwLjItNC44LDAuNmMtMC43LDAuMi0x",
        "LjQsMC40LTIsMC43Yy0wLjEtMC4yLTAuMy0wLjQtMC40LTAuNUMxMzUuNiw3LjMsMTM0LjgsNywxMzQsN2gtMy4zdjIzLjdoNi40VjE4LjRjMC0",
        "yLjQsMC40LTMuMywxLjMtNC4yYzAuOC0wLjgsMi4xLTEuMiwzLjktMS4yaDIuN1Y3SDE0My40Ii8+PHBhdGggY2xhc3M9InN0MSIgZD0iTTI3Lj",
        "MsMGgtMy4zdjI3LjhjMCwwLjgsMC4zLDEuNSwwLjksMi4xYzAuNiwwLjYsMS4zLDAuOCwyLjIsMC44aDMuM1YyLjljMC0wLjgtMC4zLTEuNS0wL",
        "jktMi4xQzI4LjksMC4zLDI4LjIsMCwyNy4zLDAiLz48cGF0aCBjbGFzcz0ic3QxIiBkPSJNNDQsMjUuOWMzLjgsMCw1LTMuOSw1LTcuMWMwLTMu",
        "My0xLjItNy4yLTUtNy4yYy0zLjgsMC00LjksMy45LTQuOSw3LjJDMzksMjIsNDAuMiwyNS45LDQ0LDI1Ljl6IE00NCw2LjRjNy4yLDAsMTEuMiw",
        "0LjYsMTEuMiwxMi4zYzAsNy42LTQsMTIuMi0xMS4yLDEyLjJjLTcuMywwLTExLjEtNC42LTExLjEtMTIuMkMzMi45LDExLDM2LjcsNi40LDQ0LD",
        "YuNHoiLz48cGF0aCBjbGFzcz0ic3QxIiBkPSJNMTEuMSwyNS45Yy0zLjgsMC00LjktMy45LTQuOS03LjFjMC0zLjMsMS4xLTcuMiw0LjktNy4yY",
        "zIsMCwzLjIsMS4xLDQsMi41aDYuNmMtMS4zLTQuOS01LTcuNy0xMC42LTcuN0MzLjgsNi40LDAsMTEsMCwxOC43YzAsNy42LDMuOCwxMi4yLDEx",
        "LjEsMTIuMmM1LjYsMCw5LjMtMi44LDEwLjYtNy43aC00LjNjMCwwLTEuMiwwLTEuOCwwLjZDMTQuNCwyNC45LDEzLjUsMjUuOSwxMS4xLDI1Ljl",
        "6Ii8+PHBhdGggY2xhc3M9InN0MSIgZD0iTTc3LjgsNy45Qzc3LjIsNy4zLDc2LjQsNyw3NS41LDdoLTMuMnYxNC44YzAsMS40LTAuNCwyLjQtMS",
        "4zLDMuMWMtMC45LDAuNi0xLjksMS0zLDFjLTEuMSwwLTIuMS0wLjMtMy0xYy0wLjktMC42LTEuMy0xLjctMS4zLTMuMVYxMGMwLTAuOC0wLjMtM",
        "S41LTAuOS0yLjFDNjIuNCw3LjMsNjEuNiw3LDYwLjcsN2gtMy4ydjEzLjhjMCw0LjIsMS4yLDYuOCwzLjQsOC4yYzIuMSwxLjQsNC41LDEuOSw3",
        "LjIsMS45YzIuNywwLDUtMC41LDcuMi0xLjljMi4yLTEuNCwzLjQtNCwzLjQtOC4yVjEwQzc4LjYsOS4xLDc4LjMsOC40LDc3LjgsNy45eiIvPjx",
        "wYXRoIGNsYXNzPSJzdDEiIGQ9Ik0xMDIuOSwwLjhjLTAuNi0wLjYtMS4zLTAuOC0yLjItMC44aC0zLjJ2OC44Yy0xLTAuOS0zLTIuNC02LjEtMi",
        "40Yy02LjUsMC0xMC4yLDQuNi0xMC4yLDEyLjNjMCw3LjYsMy45LDEyLjIsMTEuMywxMi4yYzcuMywwLDExLjMtNC41LDExLjMtMTIuMWgwVjIuO",
        "UMxMDMuOCwyLjEsMTAzLjUsMS40LDEwMi45LDAuOHogTTkyLjQsMjUuOWMtMy44LDAtNS0zLjktNS03LjFjMC0zLjMsMS4yLTcuMiw1LTcuMmMz",
        "LjgsMCw1LDMuOSw1LjEsNy4xdjAuMWgwQzk3LjUsMjIsOTYuMywyNS45LDkyLjQsMjUuOXoiLz48cGF0aCBjbGFzcz0ic3QxIiBkPSJNMTI4LjQ",
        "sMTcuM2MwLDAuNS0wLjEsMS0wLjMsMS40Yy0wLjEsMC4zLTAuMywwLjUtMC41LDAuN2MtMC42LDAuNi0xLjMsMC45LTIuMSwwLjloLTEyLjljMC",
        "4yLDIuOCwxLjYsNS42LDQuOCw1LjZjMi40LDAsMy4zLTEsNC40LTJjMC43LTAuNiwxLjgtMC42LDEuOC0wLjZoNC4zYy0xLjMsNC45LTUsNy43L",
        "TEwLjYsNy43Yy03LjMsMC0xMS4xLTQuNi0xMS4xLTEyLjJjMC03LjcsMy44LTEyLjMsMTEuMS0xMi4zYzUuNiwwLDkuMywyLjgsMTAuNiw3Ljdj",
        "MC4yLDAuOSwwLjQsMS44LDAuNSwyLjhMMTI4LjQsMTcuM3ogTTExNy4zLDExLjZjLTIuNiwwLTQuNCwxLjktNC42LDQuMWg5LjJDMTIxLjksMTM",
        "uNSwxMTkuOCwxMS42LDExNy4zLDExLjZ6Ii8+PHBhdGggY2xhc3M9InN0MSIgZD0iTTE2Ni4zLDEzYzAtMi4xLTAuOS0zLjctMi42LTQuOWMtMS",
        "43LTEuMS00LjItMS43LTcuNi0xLjdjLTMsMC01LjQsMC43LTcsMmMtMS41LDEuMi0yLjMsMi44LTIuNiw0LjZoNi4xYzAuMy0wLjcsMC44LTEuM",
        "iwxLjUtMS40YzAuNy0wLjIsMS40LTAuNCwyLjMtMC40YzEuMSwwLDEuOCwwLjEsMi42LDAuNGMwLjksMC4zLDEuNCwwLjgsMS40LDEuN2MwLDAu",
        "OS0xLjMsMS44LTQsMi4xYy0zLjIsMC40LTUuNywwLjctOCwyLjRjLTEuNSwxLjEtMi40LDMtMi40LDUuNGMwLDIuNiwwLjgsNC41LDIuNSw1LjZ",
        "jMS40LDEsMy44LDEuOSw3LjYsMS45YzMuNCwwLDUuOS0wLjcsNy42LTEuOGMxLjgtMS4yLDIuNy0yLjUsMi44LTVWMTN6IE0xNTkuNCwyNC41Yy",
        "0xLDAuOS0yLjMsMS40LTQsMS40Yy0wLjUsMC0yLjItMC4xLTIuOS0wLjhjLTAuNS0wLjUtMC44LTEtMC44LTEuOGMwLTAuNiwwLjItMS4yLDAuN",
        "i0xLjZjMC45LTAuOSwxLjktMS4xLDQtMS41YzEuNC0wLjMsMy4xLTAuOCw0LTEuM3YxLjhDMTYwLjQsMjIuMywxNjAuNCwyMy42LDE1OS40LDI0",
        "LjV6Ii8+PC9nPjwvZz48L2c+PC9nPjwvc3ZnPg==\">",
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
    parser.add_argument('-d', metavar="directory", required=True, help="Directory containing the result json files.")
    parser.add_argument('-bw', metavar="bandwidth", type=int, required=True, help="Theoretical maximum bandwidth for each hosts. E.g. 20 for 20Gbps")

    opt=parser.parse_args()

    global bw_array
    global bw_total
    global summary

    summary = {}
    bw_array = {}
    bw_total = opt.bw
    directory = opt.d

    if not os.path.isdir(directory):
        sys.stderr.write("Error: directory " + directory + " not found\n")
        sys.exit(2)
    else:
        print("Processing iperf3 output in " + directory)

        process_summary(directory + "/summary.txt")

        files = os.listdir(directory)
        for file in files:
            if file.endswith(".json"):
                srchost = os.path.splitext(file)[0]
                process_json(directory + "/" + file)
                output_html()


if __name__ == "__main__":
    main()
