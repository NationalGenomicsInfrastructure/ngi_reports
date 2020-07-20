#
# NGI Reports startup
#
# Adds the scripts directory to the user's PATH so that ngi_reports
# can be executed from the command line easily.
#

ngi_reports_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../ && pwd )
PATH=${ngi_reports_dir}/scripts:$PATH
