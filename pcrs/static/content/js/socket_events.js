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