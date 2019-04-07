# Space Instagram

This small projects shows you how to get rid or routine when you are working on your Instagram blog
You can see how to download photos from "printshop" collection of Hubble or photo report from last Space X launch

### How to install

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

You should have Instagram account. If you don't have instagram credentials, register on [instagram.com](http://instagram.com)

In the root of the project create file `.env` and add your credentials.

```.env
SPACE_INSTAGRAM_LOGIN=<YOUR_LOGIN>
SPACE_INSTAGRAM_PASSWORD=<YOUR_PASSWORD>
```


### How to use
* Download SpaceX last launch photos

```bash
python3 fetch_spacex.py
``` 

* Download Hubble photo collection

```bash
python3 fetch_hubble.py
``` 

Before upload action check `images/` folder, please

* Uplpad your photos to your account

```bash
python3 publish_to_instagram.py
``` 


### Future improvements

1. Add argparse to `fetch_hubble.py` to get collection argument from command line
1. Make internal method private

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).