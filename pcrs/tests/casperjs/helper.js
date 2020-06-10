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

var rootUrl = 'http://localhost/dev_Java';

function startAsPasswordlessAdmin(test) {
    casper.start(rootUrl, function() {
        var formSelector = 'form#login-form';
        // If it doesn't exist, we are already logged in
        if (this.exists(formSelector)) {
            this.fill(formSelector, {
              'username': 'admin',
            }, true);
        }
    });
}

function deleteProblem(type, name) {
    casper.thenOpen(rootUrl + '/problems/' + type + '/list', function() {
        // Wait since the button may or may _not_ appear.
        this.wait(1000);
        // The 'i' tag has the click listener, not the anchor. Gur.
        var editButtonSelector = 'a[title="Edit ' + name + '"] i';

        if ( ! casper.exists(editButtonSelector)) {
            return;
        }
        this.click(editButtonSelector);
        this.waitForUrlChange();

        // Open the delete page
        this.then(function() {
            var deleteUrl = casper.getCurrentUrl() + '/delete';
            this.thenOpen(deleteUrl);
        });

        this.then(function() {
            this.waitForSelector('form');
        });

        this.then(function() {
            // Actually delete the object!
            this.fill('form', {}, true);
        });
    });
}

function addGenericTestCase(casper, input, output) {
    casper.then(function() {
        this.thenOpen(casper.getCurrentUrl() + '/testcase');
    }).then(function() {
        this.waitForUrlChange();

    }).then(function() {
        this.sendKeys('#id_test_input', input);
        this.sendKeys('#id_expected_output', output);
    }).thenEvaluate(function() {
        // The "submit & go back" button
        $('form input#submit-id-submit:last').click();
    }).then(function() {
        this.waitForUrlChange();
    });
}

