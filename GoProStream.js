var http = require("http");

http.createServer(function (request, response) {
   response.writeHead(200, {'Content-Type': 'text/plain'});
   response.end('GoPro Stream\n');
}).listen(8080);

// Console will print the message
console.log('Server running at http://127.0.0.1:8080/');
