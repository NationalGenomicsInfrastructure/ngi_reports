#
# NGI Reports startup - UPPMAX
#
# Adds the scripts directory to the user's PATH so that ngi_reports
# can be executed from the command line easily.

# Add the scripts directory to the path
ngi_reports_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../ && pwd )
export PATH=${ngi_reports_dir}/scripts:$PATH

# Alias to regenerate project summary with changes
alias make_report='ngi_reports project_summary --regenerate_html_from_md --markdown_file '
