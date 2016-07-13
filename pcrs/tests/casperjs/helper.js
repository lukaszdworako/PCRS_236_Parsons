if ( ! casper.waitForUrlChange) {
    casper.waitForUrlChange = function() {
        var oldUrl;
        //add the check function to the beginning of the arguments...
        Array.prototype.unshift.call(arguments, function check() {
            return oldUrl === this.getCurrentUrl();
        });
        this.then(function(){
            oldUrl = this.getCurrentUrl();
        });
        this.waitFor.apply(this, arguments);
        return this;
    };
}

