var io = require('socket.io')(8888);

// the secret key to identify instructors
var secret_key = '3919766206359598592';

io.on('connection', function (socket) {

    // updating problem info such as visibility
    socket.on('itemUpdate', function (data) {
        console.log('I received ', data);
        // broadcast iff the message is signed with the secret key
        if (data['secret_key'] == secret_key) {
            io.emit('itemUpdate', data);
        }
        else {
            console.log('permission denied');
        }
    });

    // updating problem status for user
    socket.on('statusUpdate', function (data) {
        io.emit(data.userhash, data);
    });

});