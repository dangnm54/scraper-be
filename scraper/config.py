import random

# __Proxy authen data
proxy_user = "sgrgq_minhd"
proxy_password = "XrGsPncf"
proxy_ip = "171.229.224.9"
proxy_port = "37495"


driver_path = r'C:\Users\ADMIN\Pictures\scraper\scraper-be\scraper\msedgedriver.exe'

data_folder_path = r'C:\Users\ADMIN\Pictures\scraper\scraper-be\data'

# __Website links
main_website_url = 'https://www.airbnb.com.vn/homes'
ip_website_url = 'https://nordvpn.com/what-is-my-ip/'


# __Wait random 
wait_time = random.uniform(1, 3) + random.uniform(2, 5) - random.uniform(0.1, 0.5)
# print(wait_time)



# __Library list

# pip install selenium
# pip install screeninfo
# pip install pandas
# pip install requests
# pip install beautifulsoup4
# pip install lxml
# pip install tqdm
# pip install seaborn
# pip install matplotlib

# pip freeze   -> check all lib of venv