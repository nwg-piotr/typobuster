# Typobuster
Simplified text editor with a wide selection of transformations and automatic correction of common typos.

In my daily work I constantly receive texts in various formats (MS Word, LibreOffice, email), which are supposed to be published
on the web and contain still the same typos: misplaced spaces, multiple spaces and line breaks, German-style quotation marks, etc. 
Up until now, I have used Mousepad to proofread, either manually or via search and replace, but that was kind of 
waste of time. To make life easier, I developed a simple editor that will do it automatically. It is supposed to contain 
only the tools that I actually need in my work (mostly various text transformations), and case-insensitive sorting.

## Transformations

![image](https://github.com/user-attachments/assets/8f7ac350-2156-49ea-b2be-a4a55cdd1185)

## Tools

![image](https://github.com/user-attachments/assets/bb7a23c4-9da5-4beb-b55e-c0bcd7b1c595)


## Web cleanup

![image](https://github.com/user-attachments/assets/1f71960c-552f-4f37-a2c2-3c9ad5f0d842)

## Preferences

![image](https://github.com/user-attachments/assets/530174a9-91ad-430f-af7f-a42648525c38)

## Syntax highlight

The editor does not detect file types automatically, as it's mostly designed to work with plain text. However,
you can choose a syntax from the View menu manually. I only selected most popular types, and stored them as 
`"id": "description"` dictionary in the `~/.config/typobuster/syntax` JSON file. If you need to add something
I skipped, available ids are:

`'abnf', 'actionscript', 'ada', 'ansforth94', 'asciidoc', 'asp', 'automake', 'awk', 'bennugd', 'bibtex', 'bluespec', 'boo', 'c', 'c-sharp', 'cpp', 'changelog', 'cmake', 'cobol', 'commonlisp', 'css', 'csv', 'cuda', 'd', 'dart', 'def', 'desktop', 'diff', 'docbook', 'docker', 'dpatch', 'dtd', 'gdb-log', 'eiffel', 'erb', 'erb-html', 'erb-js', 'erlang', 'fsharp', 'fcl', 'fish', 'ftl', 'forth', 'fortran', 'gap', 'gdscript', 'genie', 'go', 'gradle', 'dot', 'groovy', 'gtk-doc', 'gtkrc', 'haddock', 'haskell', 'haxe', 'html', 'idl', 'idl-exelis', 'imagej', 'ini', 'llvm', 'j', 'jade', 'java', 'js', 'js-val', 'js-expr', 'js-fn', 'js-lit', 'js-mod', 'js-st', 'cg', 'glsl', 'jsdoc', 'json', 'jsx', 'julia', 'kotlin', 'latex', 'lean', 'less', 'lex', 'libtool', 'haskell-literate', 'logcat', 'logtalk', 'lua', 'm4', 'makefile', 'mallard', 'markdown', 'matlab', 'maxima', 'mediawiki', 'meson', 'modelica', 'mxml', 'cpphdr', 'chdr', 'nemerle', 'netrexx', 'nsis', 'objc', 'objj', 'ocaml', 'ocl', 'octave', 'ooc', 'opal', 'opencl', 'pascal', 'perl', 'php', 'pig', 'pkgconfig', 'rpmspec', 'dosbatch', 'powershell', 'prolog', 'proto', 'puppet', 'python3', 'python', 'r', 'rst', 'ruby', 'rust', 'scala', 'scheme', 'scilab', 'scss', 'sh', 'solidity', 'sparql', 'spice', 'sql', 'sml', 'star', 'sweave', 'swift', 'systemverilog', 'dtl', 'tera', 'tcl', 'terraform', 'texinfo', 'thrift', 'gettext-translation', 'toml', 't2t', 'typescript', 'typescript-js-expr', 'typescript-js-fn', 'typescript-js-lit', 'typescript-js-mod', 'typescript-js-st', 'typescript-jsx', 'typescript-type-expr', 'typescript-type-gen', 'typescript-type-lit', 'vala', 'vbnet', 'verilog', 'vhdl', 'xml', 'xslt', 'yacc', 'yaml', 'yara'`

## Installation

```
git clone https://github.com/nwg-piotr/typobuster.git
cd typobuster
sudo ./install.sh
```

## Uninstallation

`sudo ./uninstall.sh`
