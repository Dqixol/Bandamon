# bandamon - (hopefully) a better pandamon :0

## usage
```
bandamon [-h] [-e EXPRESSIONS [EXPRESSIONS ...]] [-v INVERSES [INVERSES ...]] [-u USER] [-d] [-l]

options:
  -h, --help            show this help message and exit
  -e EXPRESSIONS [EXPRESSIONS ...], --expressions EXPRESSIONS [EXPRESSIONS ...]
  -v INVERSES [INVERSES ...], --inverses INVERSES [INVERSES ...]
  -u USER, --user USER  User interested
  -d, --detail          show job details
  -l, --loop            None stop monitoring
```
## example output
```
$ bandamon -e v1_0530 700587 -l -d
```
![example output](example_output.png)

## credit
Code largely came from the following project
https://pypi.org/project/pandamonium
