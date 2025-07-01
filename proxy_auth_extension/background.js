
    var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
        scheme: "http",
        host: "171.229.243.144",
        port: parseInt(37495)
        },
        bypassList: ["localhost"]
    }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "sgrgq_minhd",
                password: "XrGsPncf"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    