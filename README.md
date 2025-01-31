# typobuster
Work in progress: a simple text editor designed to automatically fix common typos.

**The program is still quite far from its target functionality. Please check back later.**

![image](https://github.com/user-attachments/assets/409850d3-74b2-4b99-b544-8e9f940eb620)

In my work with Wordpress, every day I receive texts in various formats (MS Word, LibreOffice, email), which constantly 
contain the same errors: misplaced spaces, multiple spaces and line breaks, German-style quotation marks, etc. 
Up until now, I have used Mousepad to proofread, either manually or via search and replace, but that was kind of 
waste of time. To make life easier, I'm writing a simple editor based on gtksourceview4, that will do it automatically. 
Besides, it is supposed to contain only the basic tools that I actually use in my work, (e.g. changing the case of 
characters), and nothing more.

Mousepad on has a lot of options I don't use and a few that drive me crazy (multiple tabs). Since I have to work 
with submitted text and feed it to Wordpress every day, I missed the option to remove the most common typos in 
a single click. I've named the program "Typobuster", as its basic purpose is to correct common mistakes. 
I plan to add only those Mousepad features that I actually use.

## Installation

```
git clone https://github.com/nwg-piotr/typobuster.git
cd typobuster
sudo ./install.sh
```

## Uninstallation

`sudo ./uninstall.sh`
