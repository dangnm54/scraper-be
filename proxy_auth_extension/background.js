
    var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
        scheme: "http",
        host: "14.225.63.224",
        port: parseInt(41142)
        },
        bypassList: ["localhost"]
    }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "VN43221",
                password: "lLdQ8l4T"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    