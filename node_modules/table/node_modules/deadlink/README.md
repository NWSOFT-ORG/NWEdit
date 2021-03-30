<h2 id="deadlink">Deadlink</h2>

[![Travis build status](http://img.shields.io/travis/gajus/deadlink/master.svg?style=flat)](https://travis-ci.org/gajus/deadlink)
[![NPM version](http://img.shields.io/npm/v/deadlink.svg?style=flat)](https://www.npmjs.org/package/deadlink)

Find dead URLs and fragment identifiers (URLs with a hash and a corresponding ID element in the resulting document).

Deadlink is using a combination of header inspection, [data inspection](https://github.com/mscdex/mmmagic) (2015-08-06: mmmagic has been temporary removed until issues with iojs 3.0.0 are resolved) and content length inspection to determine if the content exists, when to listen for the response, and when to [bail out](#special-case).

Deadlink is using [jsdom](https://github.com/tmpvar/jsdom) to load the document and execute it. Therefore, resolving fragment identifiers will work even if the element IDs of the resulting document are generated dynamically after `DOMContentLoaded` event.

<h2 id="contents">Contents</h2>

* [Deadlink](#deadlink)
* [Contents](#contents)
* [Usage](#usage)
    * [Resolving URLs and Fragment Identifiers](#usage-resolving-urls-and-fragment-identifiers)
    * [Resolving URLs](#usage-resolving-urls)
    * [Resolving Fragment Identifiers](#usage-resolving-fragment-identifiers)
    * [Deadlink.Resolution](#usage-deadlink-resolution)
    * [Matching URLs](#usage-matching-urls)
* [Download](#download)


<h2 id="usage">Usage</h2>

This guide explains the most common use case, without going into details about the properties of the intermediate results. Some of these properties are useful for further analyzes, such as knowing when to load the document to extract the IDs for fragment identification.

Refer to the [test cases](https://github.com/gajus/deadlink/tree/master/tests) for the detail explanation of Deadlink behavior.

```js
var Deadlink = require('deadlink'),
    deadlink = Deadlink();
```

<h3 id="usage-resolving-urls-and-fragment-identifiers">Resolving URLs and Fragment Identifiers</h3>

This is a convenience wrapper to resolve a collection of URLs, including the fragment identifier when it is part of the URL. URL/Fragment Identifier is resolved with a promise that in turn resolves to [`Deadlink.Resolution`](#deadlinkresolution).

```js
var promises = deadlink.resolve([
    'http://gajus.com/foo',
    'http://gajus.com/bar',
    'http://gajus.com/#foo',
    'http://gajus.com/#bar'
]);
```

Use [`Promise.all`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all) to construct a promise that resolves when all of the promises in the collection are resolved. [`Deadlink.Resolution`](#deadlinkresolution) of a successful resolution does not have an `error` property.

```js
Promise.all(promises).then(function () {
    promises.forEach(function (Resolution) {
        if (!Resolution.error) {
            // OK
        }
    });
});
```

<h3 id="usage-resolving-urls">Resolving URLs</h3>

The same as [`deadlink.resolve()`](#resolving-urls-and-fragment-identifiers) but limited to URL resolution.

```js
deadlink.resolveURLs([
    'http://gajus.com/foo',
    'http://gajus.com/bar'
]);
```

<h4 id="usage-resolving-urls-special-case">Special Case</h4>

There is one special case when promise for a valid response can be rejected.

It is rejected if `Content-Type` is `text/html` and content length is larger than 5MB. Deadlink is storing the response of `text/html` in case `resolveFragmentIdentifierURL` will be referring to the said URL in future. If you foresee this as an issue, [raise an issue](https://github.com/gajus/deadlink/issues) stating your use case.

<h3 id="usage-resolving-fragment-identifiers">Resolving Fragment Identifiers</h3>

The same as [`deadlink.resolve()`](#resolving-urls-and-fragment-identifiers) but limited to Fragment Identifier resolution.

```js
deadlink.resolveFragmentIdentifierURLs([
    'http://gajus.com/#foo',
    'http://gajus.com/#bar'
]);
```

<h3 id="usage-deadlink-resolution">Deadlink.Resolution</h3>

The resolution object reflects the type of the resource:

```js
Deadlink.URLResolution
Deadlink.FragmentIdentifierDocumentResolution
Deadlink.FragmentIdentifierURLResolution
```

All of these objects extend from `Deadlink.Resolution`.

The [test cases](https://github.com/gajus/deadlink/tree/master/tests) explain what properties and when do each of these objects have.

<h3 id="usage-matching-urls">Matching URLs</h3>

`deadlink.matchURLs(inputString)` collects all URLs from a string. This function is a wrapper around [URL RegExp](https://github.com/gajus/url-regexp) `match()`.

<h2 id="download">Download</h2>

Download using [NPM](https://www.npmjs.org/):

```sh
npm install deadlink
```
