#################################################################################
# PRIMO - The P&A Project Optimizer was produced under the Methane Emissions
# Reduction Program (MERP) and National Energy Technology Laboratory's (NETL)
# National Emissions Reduction Initiative (NEMRI).
#
# NOTICE. This Software was developed under funding from the U.S. Government
# and the U.S. Government consequently retains certain rights. As such, the
# U.S. Government has been granted for itself and others acting on its behalf
# a paid-up, nonexclusive, irrevocable, worldwide license in the Software to
# reproduce, distribute copies to the public, prepare derivative works, and
# perform publicly and display publicly, and to permit others to do so.
#################################################################################
"""
A short script to export API documentation as a standalone HTML. To execute, do:
cd app
python3 export_doc.py

An HTML file will be generated in the static folder
static/api-docs.html

that can be shared when documentation is needed without full access to or starting
the API service
"""

# Standard libs
import json

# User-defined libs
from main import app

if __name__ == "__main__":
    with open("static/api-docs.html", "w", encoding="utf-8") as write_file:
        with open("static/html_template", "r", encoding="utf-8") as read_file:
            template_data = read_file.read()
        print(template_data % json.dumps(app.openapi()), file=write_file)
