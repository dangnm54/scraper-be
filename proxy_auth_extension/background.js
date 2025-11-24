
    var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
        scheme: "http",
        host: "103.99.1.146",
        port: parseInt(8202)
        },
        bypassList: ["localhost"]
    }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "kz00mUFMminhd",
                password: "Hm8fjL77"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    