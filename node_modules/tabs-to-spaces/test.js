
var convert = require('./');

describe('tabs-to-spaces(str)', function () {
  var str = [
    'hello\tworld',
    '\thello\tworld',
    '\t\thello'
  ].join('\n');

  it('should default to two spaces', function () {
    convert(str).should.be.equal([
      'hello  world',
      '  hello  world',
      '    hello'
    ].join('\n'));
  });
});

describe('tabs-to-spaces(str, count)', function () {
  var str = [
    'hello\tworld',
    '\thello\tworld',
    '\t\thello'
  ].join('\n');

  it('should use the given number of spaces', function () {
    convert(str, 4).should.be.equal([
      'hello    world',
      '    hello    world',
      '        hello'
    ].join('\n'));
  });
});

describe('tabs-to-spaces(str, str)', function () {
  var str = [
    'hello\tworld',
    '\thello\tworld',
    '\t\thello'
  ].join('\n');

  it('should use the given number of spaces', function () {
    convert(str, 'abc').should.be.equal([
      'helloabcworld',
      'abchelloabcworld',
      'abcabchello'
    ].join('\n'));
  });
});
