// Fancy extension to store compiled Handlebars templates
Handlebars.getTemplate = function(name) {
    if (Handlebars.templates === undefined) {
        Handlebars.templates = {};
    }
    if (Handlebars.templates[name] === undefined) {
        var templateCode = $('#' + name).text();
        Handlebars.templates[name] = Handlebars.compile(templateCode);
    }

    return Handlebars.templates[name];
}

