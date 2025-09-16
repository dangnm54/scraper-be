
    var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
        scheme: "http",
        host: "160.25.77.92",
        port: parseInt(8539)
        },
        bypassList: ["localhost"]
    }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "xkNPjzrIminhd",
                password: "kTJnaMBA"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    