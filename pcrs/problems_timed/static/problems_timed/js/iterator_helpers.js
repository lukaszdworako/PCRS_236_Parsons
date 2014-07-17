// Helper functions for problems_timed/js_page_iterator.html

function iteratePage(counter, pages, container, intervalId) {
    if (counter >= pages.length) {
        container.innerHTML = '';
        clearInterval(intervalId);
        $('#page_container').toggle();
        $('#submission_block').fadeIn();
    } else {
        container.innerHTML = pages[counter];
        counter++;
    }
    return counter
}

function timeIterator(counter, delay, container, pages, intervalId) {
    if (pages.length == 0) {
        clearInterval(intervalId);
        $('#submission_block').fadeIn();
    } else {
        $('#page_container').toggle();
        container.innerHTML = pages[counter];
        counter++;
        intervalId = setInterval( function () {
            counter = iteratePage(counter, pages, container, intervalId);
        }, delay);
    }
}

function stepIterator(counter, delay, container, pages, intervalId) {
    if (pages.length == 0) {
        $('#submission_block').fadeIn();
    } else {
        $('#next_block').toggle();
        $('#page_container').toggle();
        container.innerHTML = pages[counter];
        counter++;
        
        $('#next_button').click( function() {
            if (counter >= pages.length) {
                $('#next_block').toggle();
            }
            counter = iteratePage(counter, pages, container, intervalId);
        });
    }
}
