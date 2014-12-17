#
# NGI Reports startup
#
# Adds the scripts directory to the user's PATH so that ngi_reports
# can be executed from the command line easily. Also a helper bash
# function to run pandoc easily.
#
# Note that this requires pandoc to be installed separately.
# If you're running on Linux with RPM x86_64 you can use the
# uppmax_ngi_reports.sh script instead, which runs the bundled
# pandoc binary.

ngi_reports_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../ && pwd )
PATH=${ngi_reports_dir}/scripts:$PATH
function make_report {
    for f in "$@"; do
      fn=${f%.md}
      echo "Converting ${f}.."
      PD_DIR=${ngi_reports_dir}/data/pandoc_templates
      pandoc --standalone --section-divs ${fn}.md -o ${fn}.html --template=${PD_DIR}/html_pandoc.html --default-image-extension=png --filter ${PD_DIR}/pandoc_filters.py -V template_dir=${PD_DIR}/ 
      pandoc --standalone ${fn}.md -o ${fn}.pdf --template=${PD_DIR}/latex_pandoc.tex --latex-engine=xelatex --default-image-extension=pdf --filter ${PD_DIR}/pandoc_filters.py -V template_dir=${PD_DIR}/ 
    done
}
export -f make_report