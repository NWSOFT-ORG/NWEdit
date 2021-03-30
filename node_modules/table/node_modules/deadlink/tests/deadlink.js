'use strict';

var chai = require('chai'),
    expect = chai.expect,
    chaiAsPromised = require('chai-as-promised'),
    nock = require('nock'),
    Sinon = require('sinon'),
    requireNew = require('require-new');

chai.use(chaiAsPromised);

describe('deadlink', function () {
    var Deadlink,
        deadlink,
        sinon;
    beforeEach(function () {
        Deadlink = requireNew('../src/deadlink.js');
        deadlink = Deadlink();
        sinon = Sinon.sandbox.create();
    });
    afterEach(function () {
        sinon.restore();
    });
    describe('.resolveURL()', function () {
        it('Memoizes Deadlink.resolveURL() function', function () {
            var spy = sinon.spy(Deadlink, 'resolveURL');
            nock('http://gajus.com').get('/').reply(200, 'OK', {'content-type': 'text/html'});
            deadlink.resolveURL('http://gajus.com/');
            deadlink.resolveURL('http://gajus.com/');
            deadlink.resolveURL('http://gajus.com/');
            expect(spy.callCount).to.equal(1);
        });
    });
    describe('.resolveFragmentIdentifierDocument()', function () {
        it('promise is resolved with a Deadlink.fragmentIdentifierDocumentResolution', function () {
            return deadlink.resolveFragmentIdentifierDocument('foo', '<div id="foo"></div>')
                .then(function (FragmentIdentifierDocumentResolution) {
                    expect(FragmentIdentifierDocumentResolution).to.instanceof(Deadlink.FragmentIdentifierDocumentResolution);
                });
        });
        it('multiple queries against the same document are cached', function () {
            var spy = sinon.spy(Deadlink, 'getDocumentIDs');
            deadlink.resolveFragmentIdentifierDocument('foo', '<div id="foo"></div>');
            deadlink.resolveFragmentIdentifierDocument('bar', '<div id="foo"></div>');
            deadlink.resolveFragmentIdentifierDocument('baz', '<div id="foo"></div>');
            expect(spy.callCount).to.equal(1);
        });
        describe('Deadlink.FragmentIdentifierDocumentResolution', function () {
            describe('successful resolution of the fragment identifier', function () {
                it('has fragmentIdentifier', function () {
                    return deadlink.resolveFragmentIdentifierDocument('foo', '<div id="foo"></div>')
                        .then(function (FragmentIdentifierDocumentResolution) {
                            expect(FragmentIdentifierDocumentResolution).to.deep.equal({fragmentIdentifier: 'foo'});
                        });
                });
            });
            describe('unsuccessful resolution of the fragment identifier', function () {
                it('has fragmentIdentifier and error', function () {
                    return deadlink.resolveFragmentIdentifierDocument('foo', '<div></div>')
                        .then(function (FragmentIdentifierDocumentResolution) {
                            expect(FragmentIdentifierDocumentResolution).to.deep.equal({fragmentIdentifier: 'foo', error: 'Fragment identifier not found in the document.'});
                        });
                });
            });
        });
    });

    describe('.resolveFragmentIdentifierURL()', function () {
        it('throws an error if URL does not have a fragment identifier', function () {
            var promise = deadlink.resolveFragmentIdentifierURL('http://gajus.com');
            return expect(promise).rejectedWith(Error, 'URL does not have a fragment identifier.');
        });
        it('uses deadlink.resolveURL() to resolve URL', function () {
            var spy = sinon.spy(deadlink, 'resolveURL');
            nock('http://gajus.com').get('/').reply(200, '<div id="foo"></div>', {'content-type': 'text/html'});
            deadlink.resolveFragmentIdentifierURL('http://gajus.com/#foo');
            expect(spy.calledWith('http://gajus.com/#foo')).to.equal(true);
        });
        it('uses deadlink.resolveFragmentIdentifierDocument() to look up the fragment', function () {
            var spy = sinon.spy(deadlink, 'resolveURL');
            nock('http://gajus.com').get('/').reply(200, '<div id="foo"></div>', {'content-type': 'text/html'});
            deadlink.resolveFragmentIdentifierURL('http://gajus.com/#foo');
            expect(spy.calledWith('http://gajus.com/#foo')).to.equal(true);
        });
        describe('successful resolution', function () {
            var promise;
            beforeEach(function () {
                nock('http://gajus.com').get('/').reply(200, '<div id="foo"></div>', {'content-type': 'text/html'});
                promise = deadlink.resolveFragmentIdentifierURL('http://gajus.com/#foo');
            });
            it('is resolved with Deadlink.FragmentIdentifierURLResolution', function () {
                return promise
                    .then(function (Resolution) {
                        expect(Resolution).to.instanceof(Deadlink.FragmentIdentifierURLResolution);
                    });
            });
            describe('Deadlink.FragmentIdentifierURLResolution', function () {
                it('has fragmentIdentifier and url', function () {
                    return promise
                        .then(function (Resolution) {
                            expect(Resolution).to.deep.equal({fragmentIdentifier: 'foo', url: 'http://gajus.com/#foo'});
                        });
                });
            });
        });
        describe('unsuccessful resolution', function () {
            describe('when resource is not loaded', function () {
                var promise;
                beforeEach(function () {
                    nock('http://gajus.com').get('/').reply(404);
                    promise = deadlink.resolveFragmentIdentifierURL('http://gajus.com/#foo');
                });
                it('is resolved with Deadlink.FragmentIdentifierURLResolution', function () {
                    return promise
                        .then(function (Resolution) {
                            expect(Resolution).to.instanceof(Deadlink.FragmentIdentifierURLResolution);
                        });
                });
                describe('Deadlink.FragmentIdentifierURLResolution', function () {
                    it('has error', function () {
                        return promise
                            .then(function (Resolution) {
                                expect(Resolution.error).to.instanceof(Deadlink.URLResolution);
                            });
                    });
                });
            });
            describe('when fragment is not found', function () {
                var promise;
                beforeEach(function () {
                    nock('http://gajus.com').get('/').reply(200, 'OK', {'content-type': 'text/html'});
                    promise = deadlink.resolveFragmentIdentifierURL('http://gajus.com/#foo');
                });
                it('is resolved with Deadlink.FragmentIdentifierURLResolution', function () {
                    return promise
                        .then(function (Resolution) {
                            expect(Resolution).to.instanceof(Deadlink.FragmentIdentifierURLResolution);
                        });
                });
                describe('Deadlink.FragmentIdentifierURLResolution', function () {
                    it('has error', function () {
                        return promise
                            .then(function (Resolution) {
                                expect(Resolution.error).to.instanceof(Deadlink.FragmentIdentifierDocumentResolution);
                            });
                    });
                });
            });
        });
    });
});

describe('Deadlink', function () {
    var Deadlink;
    beforeEach(function () {
        Deadlink = requireNew('../src/deadlink.js');
    });
    describe('.resolveURL()', function () {
        describe('when http:// URL', function () {
            it('promise is resolved with a Deadlink.URLResolution', function () {
                nock('http://gajus.com').get('/').reply(200, 'OK', {'content-type': 'text/html'});
                return Deadlink
                    .resolveURL('http://gajus.com')
                    .then(function (URLResolution) {
                        expect(URLResolution).to.instanceof(Deadlink.URLResolution);
                    });
            });
        });
        describe('when https:// URL', function () {
            it('promise is resolved with a Deadlink.URLResolution', function () {
                nock('https://gajus.com').get('/').reply(200, 'OK', {'content-type': 'text/html'});
                return Deadlink
                    .resolveURL('https://gajus.com')
                    .then(function (URLResolution) {
                        expect(URLResolution).to.instanceof(Deadlink.URLResolution);
                    });
            });
        });
        describe('Deadlink.URLResolution', function () {
            describe('resolution of HTML resource', function () {
                var promise;
                beforeEach(function () {
                    nock('http://gajus.com').get('/').reply(200, 'OK', {'content-type': 'text/html'});
                    promise = Deadlink
                        .resolveURL('http://gajus.com/');
                });
                it('has URL and response body', function () {
                    return promise.then(function (URLResolution) {
                        expect(URLResolution).to.deep.equal({url: 'http://gajus.com/', contentType: 'text/html', body: 'OK'});
                    });
                });
            });
            describe('resolution of resource other than HTML', function () {
                var promise;
                beforeEach(function () {
                    nock('http://gajus.com').get('/').reply(200, 'OK', {'content-type': 'application/json'});
                    promise = Deadlink
                        .resolveURL('http://gajus.com/');
                });
                it('has URL and content type', function () {
                    return promise.then(function (URLResolution) {
                        expect(URLResolution).to.deep.equal({url: 'http://gajus.com/', contentType: 'application/json'});
                    });
                });
            });
            describe('resolution of status code >=400', function () {
                var promise;
                beforeEach(function () {
                    nock('http://gajus.com').get('/').reply(404, 'OK', {'content-type': 'text/html'});
                    promise = Deadlink
                        .resolveURL('http://gajus.com/');
                });
                it('has URL, error and status code', function () {
                    return promise.then(function (URLResolution) {
                        expect(URLResolution).to.deep.equal({url: 'http://gajus.com/', error: 'Resource not resolvable.', statusCode: 404});
                    });
                });
            });
            describe('resolution of HTML resource larger than 5MB', function () {
                var promise;
                beforeEach(function () {
                    nock('http://gajus.com').get('/').reply(200, Array(5 * 1000 * 1000 + 100).join('X'), {'content-type': 'text/html'});
                    promise = Deadlink
                        .resolveURL('http://gajus.com/');
                });
                it('is rejected', function () {
                    return expect(promise).rejectedWith(Error, 'Resource is larger than 1MB.');
                });
            });
        });
    });
    describe('.getDocumentIDs()', function () {
        it('returns IDs from the document', function () {
            return Deadlink.getDocumentIDs('<div id="foo"></div><div id="bar"></div><div id="baz"></div>')
                .then(function (ids) {
                    expect(ids).to.deep.equal(['foo', 'bar', 'baz']);
                });
        });
    });
});
