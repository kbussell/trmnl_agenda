## Attribution

Source images from [tomorrow.io weather codes](https://github.com/Tomorrow-IO-API/tomorrow-weather-codes).

## Conversion steps

* Clone the tomorrow-weather-codes repo, or just get a copy of the files in the `V1_icons/black` path
* Convert the directory of SVGs to a json file with the encoded PNG data

```
$ python util/convert_images.py <path to svg icons> data/weather_icons.css
```

* Update `TRMNL/src/shared.liquid` with the generated css data