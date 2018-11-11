# coding: utf8

# Copyright 2013-2018 Vincent Jacques <vincent@vincent-jacques.net>

import os
import sys
import glob


project = "ActionTree"
author = '<a href="http://vincent-jacques.net/">Vincent Jacques</a>'
copyright = ('2013-2018 {} <script>var jacquev6_ribbon_github="{}"</script>'.format(author, project) +
             '<script src="https://jacquev6.github.io/ribbon.js"></script>')


master_doc = "index"
extensions = []


nitpicky = True
nitpick_ignore = [
    ('py:class', 'list'),
    ('py:class', 'tuple'),
]

# https://github.com/bitprophet/alabaster
html_sidebars = {
    "**": ["about.html", "navigation.html", "searchbox.html"],
}
html_theme_options = {
    "github_user": "jacquev6",
    "github_repo": project,
    "travis_button": True,
}
html_logo = "logo.png"


# http://sphinx-doc.org/ext/autodoc.html
extensions.append("sphinx.ext.autodoc")
autoclass_content = "both"
autodoc_member_order = "bysource"
autodoc_default_flags = ["members"]
# autodoc_docstring_signature
# autodoc_mock_imports
add_module_names = True
add_class_names = False


# http://sphinx-doc.org/ext/githubpages.html
extensions.append("sphinx.ext.githubpages")


# http://sphinx-doc.org/ext/doctest.html
extensions.append("sphinx.ext.doctest")
# doctest_path
doctest_global_setup = """
from __future__ import print_function

import os

os.chdir("doc/user_guide/artifacts")
"""
doctest_global_cleanup = """
os.chdir("../../..")
"""
# doctest_test_doctest_blocks


# http://sphinx-doc.org/latest/ext/intersphinx.html
extensions.append("sphinx.ext.intersphinx")
intersphinx_mapping = {
    "python": ("https://docs.python.org/2/", None),
    "graphviz": ("https://graphviz.readthedocs.io/en/stable/", None),
    "matplotlib": ("https://matplotlib.org/", None),
}
# intersphinx_cache_limit

sections = []

for file_name in glob.glob("user_guide/*.rst"):
    with open(file_name) as f:
        lines = [line.rstrip() for line in f]

    section_name = None
    for line in lines:
        if line == ".. END SECTION {}".format(section_name):
            sections.append((section_name, section_lines))
            section_name = None
        if section_name:
            if any(line.startswith(prefix) for prefix in ["    ", "... ", ">>> "]):
                section_lines.append(line[4:])
            elif line.strip() in ["", "..."]:
                section_lines.append("")
        if line.startswith(".. BEGIN SECTION "):
            section_name = line[17:].rstrip()
            section_lines = []

for (section_name, section_lines) in sections:
    with open("user_guide/artifacts/{}".format(section_name), "w") as f:
        f.write("\n".join(section_lines).strip() + "\n")

sys.path.append(os.path.join(os.getcwd(), "user_guide/artifacts"))
