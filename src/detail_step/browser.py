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

import src.tool.log_op as lg
from src.type.data import BrowserMode


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



def config_basic_driver_setting(browser_mode: BrowserMode = 'local') -> EdgeOptions:

    lg.log_divider('Config basic driver setting')

    options: EdgeOptions = EdgeOptions()

    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0") # Example Chrome User-Agent

    if browser_mode == 'headless':
        options.add_argument("--headless=new")  # Use new headless mode (more undetectable)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # Anti-detection arguments
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Enable these for better compatibility (removed images=false for maps)
        options.add_argument("--disable-extensions")


    log.info('Configured basic settings')
    return options



def config_proxy_driver_setting(extension_dir_ipt: str | None, options_ipt: EdgeOptions) -> EdgeOptions:

    lg.log_divider('Config advanced driver setting')

    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
    log.info(f'Configured minimal logging for selenium')

    options: EdgeOptions = options_ipt

    if not extension_dir_ipt:
        log.warning(f'No proxy extension provided -> driver will not use proxy')
        return options

    absolute_extension_dir: str = os.path.abspath(extension_dir_ipt)

    try:
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f'--load-extension={absolute_extension_dir}')
        log.info(f'Configured Edge to load proxy helper extension from: {absolute_extension_dir}')
        return options

    except Exception as e:
        log.error(f'Error loading Proxy Helper Extension | Absolute_extension_dir: {absolute_extension_dir}')
        lg.log_detail_error(e)
        return options



def start_browser(driver_path_ipt: str, option_ipt: EdgeOptions, browser_mode: BrowserMode = 'local') -> Tuple[WebDriver | None, WebDriverWait | None]:

    lg.log_divider('Start browser')

    try:
        service: EdgeService = EdgeService(executable_path = driver_path_ipt, log_output=os.devnull)
        driver: WebDriver = webdriver.Edge(service = service, options = option_ipt)

        # make browser look like come from real Chrome / Edge browser
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'
        })
    
        # return 'undefined' instead of 'true' when airbnb check if webdriver is used
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        log.info(f'Edge browser started | Driver <{driver}> created')

    except Exception as e:
        log.error(f'Error starting Edge browser with the specified path')
        log.error('Please check driver_path and Edge browser-driver version')
        lg.log_detail_error(e)
        return None, None


    wait: WebDriverWait = WebDriverWait(driver,20)
    log.info(f'Wait <{wait}> created')

    # # open browser in specific screen
    if browser_mode == 'local':      
        monitor_list: List[Monitor] = get_monitors()
        log.debug(f'Detected {len(monitor_list)} monitors')
            # screen laptop: 1920 x 1080
            # screen monitor: 2560 x 1440
            # current position: monitor on top laptop vertical

        if len(monitor_list) > 1:
            secondary_monitor: Monitor | None = None
            for monitor in monitor_list:
                if not monitor.is_primary:
                    secondary_monitor = monitor
                    break

            if secondary_monitor:
                log.info(f'Secondary monitor found, open browser on secondary monitor')
                driver.set_window_rect(x=-1920, y=380, width=1500, height=1010)  #monitor
                # driver.set_window_rect(x=1550, y=1450, width=960, height=1010)   #laptop
                # driver.set_window_rect(x=-1920, y=180, width=1700, height=800)  #uat
            else:
                log.info(f'Cannot identify clear secondary monitor, maximizing browser')
                driver.set_window_rect(x=960, y=10, width=960, height=1010)     #laptop - normal 

        else:
            log.info(f'Only 1 monitor, maximizing browser')
            # driver.set_window_rect(x=960, y=10, width=960, height=1010)
            # driver.set_window_rect(x=10, y=10, width=1900, height=1010)   #uat
            driver.set_window_rect(x=10, y=10, width=1900, height=1010)     #laptop - host 

    return driver, wait






def close_browser(driver: WebDriver) -> None:

    lg.log_divider('Close browser')

    driver.quit()
    log.info('Close browser')

