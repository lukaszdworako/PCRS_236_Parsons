socket.on('problems', function (data) {
    console.log('dispatching update');
    window.dispatchEvent(
        new CustomEvent('problemUpdate', {detail: data})
    );
});

socket.on(userhash, function (data) {
    window.dispatchEvent(
        new CustomEvent('problemStatusUpdate', {detail: data})
    );
});
