import os
import base64 
import logging
from typing import Tuple, List

from selenium import webdriver
from screeninfo import get_monitors, Monitor
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService


try:
    import scraper.tool.utils as utl
    import scraper.tool.log_op as lg
except ImportError:
    import tool.utils as utl
    import tool.log_op as lg


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def crt_proxy_helper_extention(proxy_user: str, proxy_password: str, proxy_ip: str, proxy_port: str) -> str:

    lg.log_divider('Create proxy helper extension')

    # 1. define directory (folder) for the extension
    extension_dir: str = 'proxy_auth_extension'
    if not os.path.exists(extension_dir):
        os.makedirs(extension_dir)
    log.info(f'Created {extension_dir}')

    # 2. crt manifest.json file -> describ extension
    manifest_content: str = """
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
    manifest_path: str = os.path.join(extension_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        f.write(manifest_content)
    log.info(f'Created {manifest_path}')

    # 3. crt background.js file -> the script adds Proxy-Authen header (handles proxy logic)
    proxy_cred: str = f'{proxy_user}:{proxy_password}'
    encoded_cred: str = base64.b64encode(proxy_cred.encode()).decode()

    background_script_content: str = f"""
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

    background_script_path: str = os.path.join(extension_dir, "background.js")
    try:
        with open(background_script_path, "w") as f:
            f.write(background_script_content)
        log.info(f"Created {background_script_path}")
    except IOError as e:
        log.error(f"Error writing {background_script_path} | Cannot proceed with creating extension files.")
        lg.log_detail_error(e)
        

    return extension_dir



def config_basic_driver_setting() -> EdgeOptions:

    lg.log_divider('Config basic driver setting')

    options: EdgeOptions = EdgeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0") # Example Chrome User-Agent

    log.info('Configured basic settings')
    return options



def config_advanced_driver_setting(extension_dir_ipt: str, options_ipt: EdgeOptions) -> EdgeOptions | None:

    lg.log_divider('Config advanced driver setting')

    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
    log.info(f'Configured minimal logging for selenium')

    options: EdgeOptions = options_ipt
    absolute_extension_dir: str = os.path.abspath(extension_dir_ipt)
    try:
        options.add_argument(f'--load-extension={absolute_extension_dir}')
        log.info(f'Configured Edge to load proxy helper extension from: {absolute_extension_dir}')
        return options
    except Exception as e:
        log.error(f'Error loading Proxy Helper Extension | Absolute_extension_dir: {absolute_extension_dir}')
        lg.log_detail_error(e)
        return None



def start_browser(driver_path_ipt: str, option_ipt: EdgeOptions) -> Tuple[WebDriver | None, WebDriverWait | None]:

    lg.log_divider('Start browser')

    driver: WebDriver | None = None
    try:
        service: EdgeService = EdgeService(executable_path = driver_path_ipt, log_output=os.devnull)
        driver = webdriver.Edge(service = service, options = option_ipt)
        log.info(f'Edge browser started | Driver <{driver}> created')

        wait: WebDriverWait = WebDriverWait(driver,20)
        log.info(f'Wait <{wait}> created')


        # open browser in specific screen
        monitor_list: List[Monitor] = get_monitors()
        log.debug(f'Detected {len(monitor_list)} monitors')
            # screen laptop: 1920 x 1080
            # screen monitor: 2560 x 1440

        if len(monitor_list) > 1:
            secondary_monitor: Monitor | None = None
            for monitor in monitor_list:
                if not monitor.is_primary:
                    secondary_monitor = monitor
                    break

            if secondary_monitor:
                log.info(f'Secondary monitor found, open browser on secondary monitor')
                # driver.set_window_rect(x=-1920, y=180, width=1500, height=1010)
                driver.set_window_rect(x=960, y=10, width=960, height=1010)
            else:
                log.info(f'Cannot identify clear secondary monitor, maximizing browser')
                driver.set_window_rect(x=960, y=10, width=960, height=1010)

        else:
            log.info(f'Only 1 monitor, maximizing browser')
            # driver.set_window_rect(x=960, y=10, width=960, height=1010)
            driver.set_window_rect(x=10, y=10, width=1900, height=1010)

        return driver, wait


    except Exception as e:
        log.error(f'Error starting Edge browser with the specified path')
        log.error('Please check driver_path and Edge browser / driver version')
        lg.log_detail_error(e)
        return None, None



def close_browser(driver: WebDriver) -> None:

    lg.log_divider('Close browser')

    driver.quit()
    log.info('Close browser')

