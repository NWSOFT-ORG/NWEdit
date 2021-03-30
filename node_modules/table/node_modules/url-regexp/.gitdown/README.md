## URL RegExp

{"gitdown": "badge", "name": "travis"}
{"gitdown": "badge", "name": "npm-version"}

RegExp object to match and validate URL(s).

## Usage

```js
var URLRegExp = require('url-regexp');
```

## Validate URL

```js
URLRegExp.validate('input string');
```

## Match URLs

`URLRegExp.match()` will return all valid URLs from the string.

```js
URLRegExp.match('input string');
```

## Download

Download using [NPM](https://www.npmjs.org/):

```sh
npm install url-regexp
```