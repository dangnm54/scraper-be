import os
import base64 
import logging

from selenium import webdriver
from screeninfo import get_monitors
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService


# -----------------------------------------------------------------------------------



def crt_proxy_helper_extention(proxy_user, proxy_password, proxy_ip, proxy_port):

    # 1. define directory (folder) for the extension
    extension_dir = 'proxy_auth_extension'
    if not os.path.exists(extension_dir):
        os.makedirs(extension_dir)
    print(f'Created {extension_dir}')
    print('-' * 30)

    # 2. crt manifest.json file -> describ extension
    manifest_content = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Helper",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    manifest_path = os.path.join(extension_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        f.write(manifest_content)
    print(f'Created {manifest_path}')
    print('-' * 30)

    # 3. crt background.js file -> the script adds Proxy-Authen header (handles proxy logic)
    proxy_cred = f'{proxy_user}:{proxy_password}'
    encoded_cred = base64.b64encode(proxy_cred.encode()).decode()

    background_script_content = f"""
    var config = {{
    mode: "fixed_servers",
    rules: {{
        singleProxy: {{
        scheme: "http",
        host: "{proxy_ip}",
        port: parseInt({proxy_port})
        }},
        bypassList: ["localhost"]
    }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_password}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
    );
    """

    background_script_path = os.path.join(extension_dir, "background.js")
    try:
        with open(background_script_path, "w") as f:
            f.write(background_script_content)
        print(f"Created {background_script_path}")
    except IOError as e:
        print(f"Error writing {background_script_path}: {e}")
        print("Cannot proceed with creating extension files.")
    print('-' * 30)

    return extension_dir



def config_basic_driver_setting():
    options = EdgeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0") # Example Chrome User-Agent

    print('Configured basic settings')
    print('-' * 30)
    return options



def config_advanced_driver_setting(extension_dir_ipt, options_ipt):
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
    print(f'Configured minimal logging')

    options = options_ipt
    absolute_extension_dir = os.path.abspath(extension_dir_ipt)
    try:
        options.add_argument(f'--load-extension={absolute_extension_dir}')
        print(f'Configured Edge to load proxy helper extension from: {absolute_extension_dir}')
        return options
    except Exception as e:
        print(f'Error loading Proxy Helper Extension | {e}')
        print(f'Absolute_extension_dir: {absolute_extension_dir}')
    print('-' * 30)

    

def start_browser(driver_path_ipt, option_ipt):
    driver = None
    try:
        service = EdgeService(executable_path = driver_path_ipt, log_output=os.devnull)
        driver = webdriver.Edge(service = service, options = option_ipt)
        print('Edge browser started')

        # open browser in specific screen
        monitor_list = get_monitors()
        print(f'Detected {len(monitor_list)} monitors')
            # screen laptop: 1920 x 1080
            # screen monitor: 2560 x 1440

        if len(monitor_list) > 1:
            secondary_monitor = 0
            for monitor in monitor_list:
                if not monitor.is_primary:
                    secondary_monitor = monitor
                    break

            if secondary_monitor:
                print(f'Secondary monitor found, open browser on secondary monitor')
                # driver.set_window_rect(x=-1920, y=180, width=1500, height=1010)
                driver.set_window_rect(x=960, y=10, width=960, height=1010)
            else:
                print(f'Cannot identify clear secondary monitor, maximizing browser')
                driver.set_window_rect(x=960, y=10, width=960, height=1010)
        else:
            print(f'Only 1 monitor, maximizing browser')
            driver.set_window_rect(x=960, y=10, width=960, height=1010)
        print('-'*30)

        wait = WebDriverWait(driver,20)
        return driver, wait

    except Exception as e:
        print(f'Error starting Edge browser with the specified path | {e}')
        print('Please check driver_path, Edge version, and selenium-stealth installation.')
    
    



def close_browser(driver):
    driver.quit()
    print('Close browser')
    print('-'*30)
    
