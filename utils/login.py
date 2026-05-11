from heiter_integration import Heiter

def login_pipeline():
    heiter = Heiter()

    if not heiter.api_token:
        username = input('Enter your username: ')
        password = input('Enter your password: ')

        login = heiter.login(username,
                            password)
        
    return heiter