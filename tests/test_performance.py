import time


def performance_test():
    start_time = time.time()  # Record the start time

    # Task 1: Measure the time taken to load the homepage
    homepage_start_time = time.time()
    # Simulating homepage load time
    time.sleep(2)  
    homepage_end_time = time.time()
    homepage_execution_time = homepage_end_time - homepage_start_time
    print(f"Homepage load time: {homepage_execution_time} seconds")

    # Task 2: Measure the time taken to load the preferences page
    preferences_start_time = time.time()
    # Simulating preferences page load time
    time.sleep(1.5) 
    preferences_end_time = time.time()
    preferences_execution_time = preferences_end_time - preferences_start_time
    print(f"Preferences page load time: {preferences_execution_time} seconds")

    # Task 3: Measure the time taken to load the profile page
    profile_start_time = time.time()
    # Simulating profile page load time
    time.sleep(1.8) 
    profile_end_time = time.time()
    profile_execution_time = profile_end_time - profile_start_time
    print(f"Profile page load time: {profile_execution_time} seconds")

    # Task 4: Measure the time taken to load the search page
    search_start_time = time.time()
    # Simulating search page load time
    time.sleep(1.2) 
    search_end_time = time.time()
    search_execution_time = search_end_time - search_start_time
    print(f"Search page load time: {search_execution_time} seconds")

    # Task 5: Measure the time taken to load the settings page
    settings_start_time = time.time()
    # Simulating settings page load time
    time.sleep(1.4)  
    settings_end_time = time.time()
    settings_execution_time = settings_end_time - settings_start_time
    print(f"Settings page load time: {settings_execution_time} seconds")

    # Task 6: Measure the time taken to submit a form
    form_start_time = time.time()
    # Simulating form submission time
    time.sleep(3) 
    form_end_time = time.time()
    form_execution_time = form_end_time - form_start_time
    print(f"Form submission time: {form_execution_time} seconds")

    # Task 7: Measure the time taken to fetch data from an API endpoint
    api_start_time = time.time()
    # Simulating API fetch time
    time.sleep(1)
    api_end_time = time.time()
    api_execution_time = api_end_time - api_start_time
    print(f"API fetch time: {api_execution_time} seconds")

    end_time = time.time()  # Record the end time
    execution_time = end_time - start_time 
    print(f"Total execution time: {execution_time} seconds")


if __name__ == '__main__':
    performance_test()
