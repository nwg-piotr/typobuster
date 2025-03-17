<img src="https://github.com/nwg-piotr/typobuster/raw/refs/heads/main/typobuster.svg" width="90" style="margin-right:10px" align=left alt="nwg-shell logo">
<H1>typobuster</H1><br>

This application is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

__Typobuster__ is a simplified text editor with a wide selection of transformations and automatic correction of common typos.

In my daily work I constantly receive texts in various formats (MS Word, LibreOffice, email), which are supposed to be 
published on the web and contain still the same typos: misplaced spaces, multiple spaces and line breaks, German-style 
quotation marks, etc. Up until now, I have used Mousepad to proofread, either manually or via search and replace, but 
that was kind of waste of time. To make life easier, I developed a simple editor that will do it automatically. It is 
supposed to focus on plain text and contain the tools that an average user needs.

[![Packaging status](https://repology.org/badge/vertical-allrepos/typobuster.svg)](https://repology.org/project/typobuster/versions)

## Transformations

![2025-03-17-020853_hypr_screenshot](https://github.com/user-attachments/assets/cff7a05d-55e1-4313-be3e-246b02afefe2)

## View

![image](https://github.com/user-attachments/assets/dfb4cb1a-3968-4095-a5c1-6ca7c4d4a3b5)


## Tools

![image](https://github.com/user-attachments/assets/76dadd29-7446-45e5-a761-ea2a95bfc6bc)


## Web cleanup

![image](https://github.com/user-attachments/assets/1f71960c-552f-4f37-a2c2-3c9ad5f0d842)

## Preferences

![2025-03-17-020940_hypr_screenshot](https://github.com/user-attachments/assets/238f13e8-d210-43f8-9a25-0c3dfa8e04be)

## Syntax highlight

The editor does not detect file types automatically, as it's mostly designed to work with plain text. However,
you can choose a syntax from the View menu manually. I only selected most popular types, and stored them as 
`"id": "description"` dictionary in the `~/.config/typobuster/syntax` JSON file. If you need to add something
I skipped, available ids are:

`'abnf', 'actionscript', 'ada', 'ansforth94', 'asciidoc', 'asp', 'automake', 'awk', 'bennugd', 'bibtex', 'bluespec', 
'boo', 'c', 'c-sharp', 'cpp', 'changelog', 'cmake', 'cobol', 'commonlisp', 'css', 'csv', 'cuda', 'd', 'dart', 'def', 
'desktop', 'diff', 'docbook', 'docker', 'dpatch', 'dtd', 'gdb-log', 'eiffel', 'erb', 'erb-html', 'erb-js', 'erlang', 
'fsharp', 'fcl', 'fish', 'ftl', 'forth', 'fortran', 'gap', 'gdscript', 'genie', 'go', 'gradle', 'dot', 'groovy', 
'gtk-doc', 'gtkrc', 'haddock', 'haskell', 'haxe', 'html', 'idl', 'idl-exelis', 'imagej', 'ini', 'llvm', 'j', 'jade', 
'java', 'js', 'js-val', 'js-expr', 'js-fn', 'js-lit', 'js-mod', 'js-st', 'cg', 'glsl', 'jsdoc', 'json', 'jsx', 'julia', 
'kotlin', 'latex', 'lean', 'less', 'lex', 'libtool', 'haskell-literate', 'logcat', 'logtalk', 'lua', 'm4', 'makefile', 
'mallard', 'markdown', 'matlab', 'maxima', 'mediawiki', 'meson', 'modelica', 'mxml', 'cpphdr', 'chdr', 'nemerle', 
'netrexx', 'nsis', 'objc', 'objj', 'ocaml', 'ocl', 'octave', 'ooc', 'opal', 'opencl', 'pascal', 'perl', 'php', 'pig', 
'pkgconfig', 'rpmspec', 'dosbatch', 'powershell', 'prolog', 'proto', 'puppet', 'python3', 'python', 'r', 'rst', 'ruby', 
'rust', 'scala', 'scheme', 'scilab', 'scss', 'sh', 'solidity', 'sparql', 'spice', 'sql', 'sml', 'star', 'sweave', 
'swift', 'systemverilog', 'dtl', 'tera', 'tcl', 'terraform', 'texinfo', 'thrift', 'gettext-translation', 'toml', 't2t', 
'typescript', 'typescript-js-expr', 'typescript-js-fn', 'typescript-js-lit', 'typescript-js-mod', 'typescript-js-st', 
'typescript-jsx', 'typescript-type-expr', 'typescript-type-gen', 'typescript-type-lit', 'vala', 'vbnet', 'verilog', 
'vhdl', 'xml', 'xslt', 'yacc', 'yaml', 'yara'`

## Dependencies

- `glib2`
- `gtk3`
- `gtksourceview4`
- `python`
- `python-cairo`
- `python-gobject`
- `gspell` (optional) - spell checking plugin
- `hunspel-en_US` (optional) - American English dictionary
- `hunspel-_xx_XX_` (optional) - hunspell dictionaries for languages you use
- for Gspell not to bug you with missing shared libraries warnings, you may also need to install `hspell`, `nuspell`, `aspell` and `libvoikko`, if not yet installed.
- `python-build` (make)
- `python-installer` (make)
- `python-wheel` (make)
- `python-setuptools` (make)

## Installation

```
git clone https://github.com/nwg-piotr/typobuster.git
cd typobuster
sudo ./install.sh
```

## Uninstallation

`sudo ./uninstall.sh`
