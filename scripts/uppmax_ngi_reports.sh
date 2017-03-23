#
# NGI Reports startup - UPPMAX
#
# Adds the scripts directory to the user's PATH so that ngi_reports
# can be executed from the command line easily. Also a helper bash
# function to run pandoc easily.
#
# This is a specific file for UPPMAX as it uses the pandoc binary
# designed for the linux distribution. This is because UPPMAX cannot
# install a recent enough version of pandoc system wide.

# Add the scripts directory to the path
ngi_reports_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../ && pwd )
export PATH=${ngi_reports_dir}/scripts:$PATH

# Make an alias so that the main script uses the pandoc binary
alias ngi_reports='ngi_reports --pandoc_binary '

# Function to run pandoc with the correct parameters
function make_report {
    for f in "$@"; do
      fn=${f%.md}
      echo "Converting ${f}.."
      PD_DIR=${ngi_reports_dir}/data/pandoc_templates
      ${PD_DIR}/pandoc --standalone --section-divs ${fn}.md -o ${fn}.html --template=${PD_DIR}/html_pandoc.html --default-image-extension=png --filter ${PD_DIR}/pandoc_filters.py -V template_dir=${PD_DIR}/ 
    done
}
export -f make_report