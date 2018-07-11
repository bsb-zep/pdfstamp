# Python3 Tool to stamp text/img on the first page of the PDF
## Installation
1. Save [pdfminer](https://files.pythonhosted.org/packages/57/4f/e1df0437858188d2d36466a7bb89aa024d252bd0b7e3ba90cbc567c6c0b8/pdfminer-20140328.tar.gz) source code into vendor/
2. Run: `python3 vendor/pdfminer/setup.py install`
3. Check if [pdfinfo](https://www.xpdfreader.com/pdfinfo-man.html) installed on your system
3. Create config.json:
```
{
  "stampDataPath":"",
  "files": "",
  "metadata": "",
  "outputPath":"",
  "inputPath":""
}
```

## Usage
### Show help message
```
python3 src/run.py -h
```
### Stamp multiple files
```
python3 src/run.py -c ../config.json
```
### Stamp single file
```
python3 src/run.py -c ../config.json -f filename.pdf
```