const acorn = require('acorn');

let source = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', chunk => { source += chunk; });
process.stdin.on('end', () => {
    try {
        const ast = acorn.parse(source, {
            ecmaVersion: 2025,
            sourceType: 'module',
            locations: true,
            allowHashBang: true,
            allowAwaitOutsideFunction: true,
        });
        process.stdout.write(JSON.stringify(ast));
    } catch (e) {
        process.stdout.write(JSON.stringify({ __parse_error__: e.message }));
    }
});
