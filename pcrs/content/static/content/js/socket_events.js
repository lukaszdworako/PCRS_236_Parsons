socket.on('itemUpdate', function (data) {
    window.dispatchEvent(
        new CustomEvent('itemUpdate', {detail: data})
    );
});

socket.on(userhash, function (data) {
    window.dispatchEvent(
        new CustomEvent('statusUpdate', {detail: data})
    );
});


// Listen for updates.
// These events are dispatched by the socket listener.
window.addEventListener('statusUpdate', function (event) {
    var receiver = 'statusUpdate' + event.detail.id;
    window.dispatchEvent(
        new CustomEvent(receiver, {detail: event.detail})
    );
}, false);

window.addEventListener('itemUpdate', function (event) {
    var receiver = 'itemUpdate' + event.detail.item.id;
    window.dispatchEvent(
        new CustomEvent(receiver, {detail: event.detail})
    );
}, false);