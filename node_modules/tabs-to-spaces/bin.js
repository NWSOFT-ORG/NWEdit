#!/usr/bin/env node

var convert = require('./');
var program = require('commander');

program
  .version(require('./package.json').version)
  .usage('[options] [files]')
  .option('-s, --spaces [number]', 'Number of spaces to use, defaults to 2', 2)
  .option('-v, --verbose', 'Verbose output', false)
  .parse(process.argv);

var files = program.args;
var verbose = program.verbose;
var spaces = parseInt(program.spaces, 10);

if (!files.length) {
  process.exit(0);
}

next(0);

function next(index) {
  var file = files[index];
  if (!file) return process.exit(0);
  if (verbose) console.log('converting %s', file);
  convert.file(file, spaces, function (err) {
    if (err) throw err;
    index++;
    next(index);
  });
}
