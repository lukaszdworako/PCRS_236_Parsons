$(function() {
    // Fancy extension to store compiled Handlebars templates
    Handlebars.getTemplate = function(name) {
        if (Handlebars.templates === undefined) {
            Handlebars.templates = {};
        }
        if (Handlebars.templates[name] === undefined) {
            var templateCode = $('#' + name).text();
            if ( ! templateCode) {
                throw new Error('Could not load template: ' + name);
            }
            Handlebars.templates[name] = Handlebars.compile(templateCode);
        }

        return Handlebars.templates[name];
    }
});

