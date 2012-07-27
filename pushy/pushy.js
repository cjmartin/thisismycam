var crypto = require('crypto');

var pushy_secret = "super secret secret";
var pushy_salt = "super salty salt";

var app = require('express').createServer()
  , io = require('socket.io').listen(app);

app.listen(8888);

app.get('/', function (req, res) {
    res.send("I'm a teapot", 418);
});

app.post('/', function (req, res) {

    if (req.body.secret && req.body.secret == pushy_secret) {
        
        var user_id = req.body.user_id;
        
        var shasum = crypto.createHash('sha1');
        shasum.update(user_id + pushy_salt);
        
        var channel = user_id + '_' + shasum.digest('hex');
        
        io.sockets.emit(channel, { msg: req.body.message });

        res.send('OK');
    
    } else {
        
        res.send("I'm a teapot", 418);
        
    }

});

app.get('/test', function (req, res) {
  res.sendfile(__dirname + '/test.html');
});

io.sockets.on('connection', function (socket) {
  socket.emit('test', { hello: 'world' });
});