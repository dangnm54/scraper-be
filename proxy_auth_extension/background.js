
    var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
        scheme: "http",
        host: "103.145.253.8",
        port: parseInt(8295)
        },
        bypassList: ["localhost"]
    }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "x1Ud4Bfcminhd",
                password: "RpPjJraS"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    