'use strict';

/* global Promise: true */

var Deadlink = {},
    Promise = require('bluebird'),
    http = require('http'),
    https = require('https'),
    url = require('url'),
    jsdom = require('jsdom'),
    crypto = require('crypto'),
    URLRegExp = require('url-regexp');
    // mmmagic does not work in iojs 3.0.0
    // mmm = require('mmmagic'),
    // Magic = mmm.Magic;

Deadlink = function () {
    var deadlink = {},
        resolvedURLs = {},
        resolvedDocuments = {};

    /**
     * Memoization of Deadlink.resolveURL.
     *
     * @param {String} subjectURL
     * @param {Promise}
     */
    deadlink.resolveURL = function (subjectURL) {
        subjectURL = Deadlink.normaliseURL(subjectURL);

        if (resolvedURLs[subjectURL] === undefined) {
            resolvedURLs[subjectURL] = Deadlink.resolveURL(subjectURL);
        }

        return resolvedURLs[subjectURL];
    };

    /**
     * @param {String} fragmentIdentifier Fragment identifier name (without #).
     * @param {String} subjectDocument HTML document.
     */
    deadlink.resolveFragmentIdentifierDocument = function (fragmentIdentifier, subjectDocument) {
        var hash = crypto.createHash('md5').update(subjectDocument).digest('hex');

        if (resolvedDocuments[hash] === undefined) {
            resolvedDocuments[hash] = Deadlink.getDocumentIDs(subjectDocument);
        }

        return new Promise(function (resolve) {
            resolvedDocuments[hash].then(function (ids) {
                if (ids.indexOf(fragmentIdentifier) !== -1) {
                    resolve(new Deadlink.FragmentIdentifierDocumentResolution({fragmentIdentifier: fragmentIdentifier}));
                } else {
                    resolve(new Deadlink.FragmentIdentifierDocumentResolution({fragmentIdentifier: fragmentIdentifier, error: 'Fragment identifier not found in the document.'}));
                }
            });
        });
    };

    /**
     * @param {String} subjectURL
     */
    deadlink.resolveFragmentIdentifierURL = function (subjectURL) {
        return new Promise(function (resolve) {
            var fragmentIdentifier = Deadlink.getFragmentIdentifier(subjectURL);

            if (!fragmentIdentifier) {
                throw new Error('URL does not have a fragment identifier.');
            }

            deadlink.resolveURL(subjectURL)
                .then(function (URLResolution) {
                    if (URLResolution.body) {
                        deadlink.resolveFragmentIdentifierDocument(fragmentIdentifier, URLResolution.body)
                            .then(function (FragmentIdentifierDocumentResolution) {
                                if (!FragmentIdentifierDocumentResolution.error) {
                                    resolve(new Deadlink.FragmentIdentifierURLResolution({
                                        fragmentIdentifier: FragmentIdentifierDocumentResolution.fragmentIdentifier,
                                        url: subjectURL
                                    }));
                                } else {
                                    resolve(new Deadlink.FragmentIdentifierURLResolution({
                                        fragmentIdentifier: FragmentIdentifierDocumentResolution.fragmentIdentifier,
                                        url: subjectURL,
                                        error: FragmentIdentifierDocumentResolution
                                    }));
                                }
                            });
                    } else {
                        resolve(new Deadlink.FragmentIdentifierURLResolution({
                            fragmentIdentifier: fragmentIdentifier,
                            url: subjectURL,
                            error: URLResolution
                        }));
                    }
                });
        });
    };

    /**
     * Returns a collection of `resolveURL` promises.
     *
     * @param {Array} subjectURLs
     * @return {Array}
     */
    deadlink.resolveURLs = function (subjectURLs) {
        return subjectURLs.map(deadlink.resolveURL);
    };

    /**
     * Returns a collection of `resolveFragmentIdentifierURL` promises.
     *
     * @param {Array} subjectURLs
     * @return {Array}
     */
    deadlink.resolveFragmentIdentifierURLs = function (subjectURLs) {
        return subjectURLs.map(deadlink.resolveFragmentIdentifierURL);
    };

    /**
     * This is a convenience wrapper to resolve a collection of URLs,
     * and resolve the fragment identifier when it is part of the URL in the collection.
     *
     * @param {Array} subjectURLs
     * @return {Array}
     */
    deadlink.resolve = function (subjectURLs) {
        var promises = [],
            normalisedURLs = [];

        subjectURLs.forEach(function (subjectURL) {
            var normalisedURL;

            normalisedURL = Deadlink.normaliseURL(subjectURL);

            if (normalisedURLs.indexOf(normalisedURL) === -1) {
                normalisedURLs.push(normalisedURL);

                promises.unshift(deadlink.resolveURL(subjectURL));
            }

            if (Deadlink.getFragmentIdentifier(subjectURL)) {
                promises.push(deadlink.resolveFragmentIdentifierURL(subjectURL));
            }
        });

        return promises;
    };

    /**
     * Matches URLs in the input document.
     *
     * @param {String} subjectDocument
     * @param {Array}
     */
    deadlink.matchURLs = function (subjectDocument) {
        return URLRegExp.match(subjectDocument);
    };

    return deadlink;
};

/**
 * Treat http://foo.com/ and http://foo.com/#resource-identifier
 * as the same when making a request and looking of the cache.
 *
 * @param {String} subjectURL
 * @return {String}
 */
Deadlink.normaliseURL = function (subjectURL) {
    subjectURL = url.parse(subjectURL);
    delete subjectURL.hash;
    return url.format(subjectURL);
};

/**
 * Makes an HTTP request and responds to the promise.
 * URL is resolved with a promise that in turn resolves to `Deadlink.URLResolution`.
 * `Deadlink.URLResolution` of a successful resolution does not have `error` property.
 *
 * @param {String} subjectURL
 * @param {Promise}
 */
Deadlink.resolveURL = function (subjectURL) {
    return new Promise(function (resolve, reject) {
        var protocol = subjectURL.indexOf('https://') === 0 ? https : http;
        protocol.get(subjectURL, function (response) {
            var request = this,
                magic,
                responseData = '',
                respondeContentType = response.headers['content-type'] || '';

            if (response.statusCode >= 400) {
                return resolve(
                    new Deadlink.URLResolution({
                        error: 'Resource not resolvable.',
                        url: subjectURL,
                        statusCode: response.statusCode
                    })
                );
            }

            if (respondeContentType.toLowerCase().indexOf('text/html') !== 0) {
                return resolve(
                    new Deadlink.URLResolution({
                        url: subjectURL,
                        contentType: respondeContentType
                    })
                );
            }

            response.on('data', function (chunk) {
                responseData += chunk;

                if (responseData.length > 5 * 1000 * 1000) {
                    request.abort();

                    return reject(new Error('Resource is larger than 1MB.'));
                }

                /* magic = new Magic(false, mmm.MAGIC_MIME_TYPE);

                // Make sure that what we are reading is HTML data.
                magic.detect(chunk, function (err, result) {
                    if (err) {
                        throw new Error('Resource type evaluation error.');
                    }

                    if (result.toLowerCase().indexOf('text/') !== 0) {
                        request.abort();

                        return reject(new Error('Resource is not text.'));
                    }
                }); */
            });

            response.on('end', function () {
                resolve(
                    new Deadlink.URLResolution({
                        url: subjectURL,
                        contentType: respondeContentType,
                        body: responseData
                    })
                );
            });
        }).on('error', reject);
    });
};

/**
 * Uses subjectDocument string to construct DOM and get list of all IDs in the document.
 */
Deadlink.getDocumentIDs = function (subjectDocument) {
    return new Promise(function (resolve, reject) {
        var getIDs = function (document) {
            setTimeout(function () {
                var ids;

                ids = []
                    .slice.apply(document.body.getElementsByTagName('*'))
                    .map(function (node) {
                        return node.id;
                    })
                    .filter(Boolean);

                resolve(ids);
            }, 10);
        };
        jsdom.env({
            html: subjectDocument,
            created: function (error) {
                if (error) {
                    return reject(new Error('Document cannot be created.'));
                }
            },
            loaded: function (error) {
                if (error) {
                    return reject(new Error('Document cannot be loaded.'));
                }
            },
            done: function (error, window) {
                // It might be that the fragment identifier on the page are generated using a script
                // such as https://github.com/gajus/contents, in which case IDs won't be available until
                // the document has been loaded and the said script finish processing the document.
                if (window.document.readyState === 'complete') {
                    getIDs(window.document);
                } else {
                    window.document.addEventListener('DOMContentLoaded', function () {
                        getIDs(window.document);
                    });
                }
            }
        });
    });
};

/**
 * Extracts the fragment identifier (hash) from the subjectURL.
 *
 * @param {String} subjectURL
 * @return {String|undefined}
 */
Deadlink.getFragmentIdentifier = function (subjectURL) {
    var fragmentIdentifier = url.parse(subjectURL).hash;

    if (!fragmentIdentifier) {
        return undefined;
    }

    return fragmentIdentifier.slice(1);
};

Deadlink.Resolution = function (data) {
    var resolution = this;
    Object.keys(data).forEach(function (k) {
        resolution[k] = data[k];
    });
};

Deadlink.URLResolution = function () {
    Deadlink.Resolution.apply(this, arguments);
};

Deadlink.URLResolution.prototype = Object.create(Deadlink.Resolution.prototype);

Deadlink.FragmentIdentifierDocumentResolution = function () {
    Deadlink.Resolution.apply(this, arguments);
};

Deadlink.FragmentIdentifierDocumentResolution.prototype = Object.create(Deadlink.Resolution.prototype);

Deadlink.FragmentIdentifierURLResolution = function () {
    Deadlink.Resolution.apply(this, arguments);
};

Deadlink.FragmentIdentifierURLResolution.prototype = Object.create(Deadlink.Resolution.prototype);

module.exports = Deadlink;
