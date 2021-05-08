
var fs = require('fs');

exports = module.exports = tabs2spaces;
exports.file = file;

/**
 * Convert tabs in the given `str` to `count` spaces
 *
 * @api public
 * @param {String} str
 * @param {Number|String} count
 * @return {String}
 */

function tabs2spaces(str, count) {
  count = count || 2;
  if (typeof count === 'number') {
    count = new Array(count + 1).join(' ');
  }

  return String(str || '').replace(/\t/g, count);
}


/**
 * Convert tabs in file `path` to `count` spaces
 *
 * @api public
 * @param {String} path
 * @param {Number|String} [count]
 * @param {Function} cb
 */

function file(path, count, cb) {
  if (typeof count === 'function') {
    cb = count;
    count = 2;
  }

  fs.readFile(path, function (err, data) {
    if (err) return cb(err);
    data = tabs2spaces(data, count);
    fs.writeFile(path, data, cb);
  });
}
