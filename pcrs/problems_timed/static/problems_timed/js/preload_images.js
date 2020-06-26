function preloadImages(pages) {
    var images = [];
    var regex = /img.*?src='(.*?)'/g;
    
    for (var i = 0; i < pages.length; i++) {
        var match = regex.exec(pages[i]);
        if (match) {
            images.push(match[1]);
        }
        while (match != null) {
            var match = regex.exec(pages[i]);
            if (match) {
                images.push(match[1]);
            }
        }
    }
    
    for (var i = 0; i < images.length; i++) {
        var img = new Image();
        img.src = images[i]
    }
}
