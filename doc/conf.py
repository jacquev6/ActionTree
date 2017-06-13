# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

import os
import sys
import glob


master_doc = "index"
project = "ActionTree"
author = '<a href="http://vincent-jacques.net/contact">Vincent Jacques</a>'
copyright = "2013-2017 {}".format(author)
extensions = []


nitpicky = True
# See https://github.com/simpeg/discretize/commit/e1a9cf2352edef9ebf0fdde8a6886db58bf4e90f
nitpick_ignore = [
    ('py:obj', 'list'),
]

# https://github.com/bitprophet/alabaster
# html_theme_path
extensions.append("alabaster")
html_theme = "alabaster"
html_sidebars = {
    "**": ["about.html", "navigation.html", "searchbox.html"],
}
html_theme_options = {
    "github_user": "jacquev6",
    "github_repo": project,
    "github_banner": True,
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


# http://sphinx-doc.org/ext/doctest.html
extensions.append("sphinx.ext.doctest")
# doctest_path
doctest_global_setup = """
import os
os.chdir("doc/user_guide/artifacts")
"""
doctest_global_cleanup = """
import os
os.chdir("../../..")
"""
# doctest_test_doctest_blocks


# http://sphinx-doc.org/latest/ext/intersphinx.html
extensions.append("sphinx.ext.intersphinx")
intersphinx_mapping = {
    "python": ("https://docs.python.org/2/", None),
    "graphviz": ("http://graphviz.readthedocs.io/en/stable/", None),
    "matplotlib": ("http://matplotlib.org/", None),
}
# intersphinx_cache_limit


for input_file in glob.glob("user_guide/*.rst"):
    with open(input_file) as in_f:
        seen = set()
        out_f = None
        output_file = None
        for line in in_f:
            if line.rstrip() == ".. END SECTION {}".format(output_file):
                assert output_file is not None
                out_f.close()
                out_f = None
                output_file = None
            if out_f:
                out_f.write(line[4:])
            if line.startswith(".. BEGIN SECTION "):
                assert output_file is None
                output_file = line[17:].rstrip()
                if output_file in seen:
                    mode = "a"
                else:
                    mode = "w"
                seen.add(output_file)
                out_f = open("user_guide/artifacts/{}".format(output_file), mode)
        assert output_file is None

sys.path.append(os.path.join(os.getcwd(), "user_guide/artifacts"))
