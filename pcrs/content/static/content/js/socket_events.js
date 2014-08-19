socket.on('problems', function (data) {
    console.log('dispatching update');
    window.dispatchEvent(
        new CustomEvent('problemUpdate', {detail: data})
    );
});

socket.on(userhash, function (data) {
    console.log("Socket dispatching update.");

    window.dispatchEvent(
        new CustomEvent('statusUpdate', {detail: data})
    );
});


// Listen for updates.
// These events are dispatched by the socket listener.
window.addEventListener('statusUpdate', function (event) {
    console.log("Update from socket received.");

    var receiver = 'statusUpdate' + event.detail.item.id;
    window.dispatchEvent(
        new CustomEvent(receiver, {detail: event.detail})
    );
}, false);