# mcm-label

A command line utility to create scannable labels for McMaster parts.
Order Line Item             |  Label
:-------------------------:|:-------------------------:
![image](https://github.com/user-attachments/assets/7c432c1b-a183-4cf9-a4b1-9a14bbb0d1b2) | ![image](https://github.com/user-attachments/assets/5cbb498b-b662-43f1-aed7-17e6aed98d87)



## Installation

`pip install mcm-label`

## Usage

1. From McMaster's website, navigate to your "Order History", then left click on the order you'd like to create labels for. The address should look something like:
   `https://www.mcmaster.com/order-history/order/<a bunch of random numbers and letters>/`
2. Right click anywhere on the page and click "Save Page As..." - confirm the "file type" says something like "Web Page, complete" - then save
3. Run `mcm-label` with the argument of wherever you saved the order webpage; specifically this must be either the html file directly, or the folder it's contained within.
4. The output will be a `label_###.png` file for each part number in the order. These files are located next to the order html file.

### Details

```
$ mcm-label -h
usage: mcm-label [-h] [-d] [FILE]

positional arguments:
  FILE         Path to a McMaster order html file, or the folder containing one

options:
  -h, --help   show this help message and exit
  -d, --debug  Enables outputting raw html and pdfs of labels
```
