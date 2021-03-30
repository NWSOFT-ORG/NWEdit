<h2 id="url-regexp">URL RegExp</h2>

[![Travis build status](http://img.shields.io/travis/gajus/url-regexp/master.svg?style=flat)](https://travis-ci.org/gajus/url-regexp)
[![NPM version](http://img.shields.io/npm/v/url-regexp.svg?style=flat)](https://www.npmjs.org/package/url-regexp)

RegExp object to match and validate URL(s).

<h2 id="usage">Usage</h2>

```js
var URLRegExp = require('url-regexp');
```

<h2 id="validate-url">Validate URL</h2>

```js
URLRegExp.validate('input string');
```

<h2 id="match-urls">Match URLs</h2>

`URLRegExp.match()` will return all valid URLs from the string.

```js
URLRegExp.match('input string');
```

<h2 id="download">Download</h2>

Download using [NPM](https://www.npmjs.org/):

```sh
npm install url-regexp
```