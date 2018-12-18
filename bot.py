#!/usr/bin/python3.7
import telegram.ext, json, os, requests, re, threading, time

'''

To do later:
- Unsubscribe function <-- DONE
- Move to SQLite instead of using reddit.json for better performance.
- Previews of subreddits - using a command (ex. /show /r/<subreddit>) would dump
3 to 5 newest posts from it using private message to the requesting user.
- Listing subscribed subreddits

Last update: 18/12/2018 3:38 AM
if a long time passed after that date we're a lazy

'''

class blopcot:

    def __init__(self):

        self.version = '1.0.18122018'
        self.previous_versions = ['1.0.12122018', '1.0.13122018', '1.0.16122018']

        # Check if configuration file exists.
        if not os.path.isfile('./conf.json'):
            print('File "conf.json" doesn\'t exist. Exiting...')
            raise SystemExit

        # Check if conf.json is readable as Json.
        try:
            with open('./conf.json', 'r') as json_file:
                self.conf = json.load(json_file)
                json_file.close()
        except json.JSONDecodeError:
            print('File "conf.json" seems to be corrupted. Exiting...')
            raise SystemExit

        # Load Reddit
        if self.conf['reddit-enabled']:
            # Check if Telegram group's reddit json file exists
            if os.path.isfile('./reddit.json'):
                self.reddit = open('./reddit.json', 'r')

                try:
                    self.reddit_db = json.load(self.reddit)
                    self.reddit.close()
                    print('Reddit support loaded.')
                    if not self.reddit_db:
                        print('No groups and users have subscribed to any subreddit.')

                except json.JSONDecodeError:
                    print('reddit.json cannot be loaded. Disabling Reddit support.')
                    self.conf['reddit-enabled'] = False


        # Log in to Telegram
        print('Logging in to Telegram...')
        self.updater = telegram.ext.Updater(self.conf['telegram-token'])

        # Register commands
        print('Registering commands...')
        self.updater.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(telegram.ext.CommandHandler('subscribe', self.subscribe))
        self.updater.dispatcher.add_handler(telegram.ext.CommandHandler('unsubscribe', self.unsubscribe))
        self.updater.dispatcher.add_handler(telegram.ext.CommandHandler('listsubscribed', self.listsubscribed))
        self.updater.dispatcher.add_handler(telegram.ext.CommandHandler('startreddit', self.startreddit))

        # Run the bot
        self.updater.start_polling()
        self.updater.idle()


    # -- Commands

    def start(self, bot, update):
        update.message.reply_text('Hello! I\'m BlopCot! I can help you get the newest news, memes or anything else from your favorite websites.\nYou can start by typing /subscribe !')

    def startreddit(self, bot, update):
        # Start a new thread
        self.reddit_auto_update(bot)
        update.message.reply_text('Up and runnin\'!')

    def subscribe(self, bot, update):
        # Find all links in a message
        urls = re.findall('(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',
         update.message.text)

        print('Group with ID ' + str(update.message.chat_id) + ' attemps to subscribe to ' + str(urls).strip('[]'))

        subscribed_success = list()
        subscribed_failed = list()

        for url in urls:

            # Convert chat_id to string since integer can't be the key in the JSON file.
            chat_id = str(update.message.chat_id)

            # Check if the given domain is supported.
            if url[1] in self.conf['eligible-reddit-domains']:

                # Create a list if it doesn't exist yet.
                if not chat_id in self.reddit_db:
                    self.reddit_db[chat_id] = list()

                # Check if the subreddit is already subscribed.
                if not url[2].lower() in self.reddit_db[chat_id]:
                    self.reddit_db[chat_id].append(url[2].lower())
                    subscribed_success.append(url[1] + url[2])

                else:
                    subscribed_failed.append(url[1] + url[2])

            else:
                subscribed_failed.append(url[1] + url[2])

        # Write changes to file
        with open('./reddit.json', 'w') as self.reddit:
            print(self.reddit_db)
            json.dump(self.reddit_db, self.reddit)
            self.reddit.close()


        # Construct a message to return
        subscribed_success = ', '.join(subscribed_success) if subscribed_success else 'None'
        subscribed_failed =  ', '.join(subscribed_failed)  if subscribed_failed  else 'None'
        complete_message = 'Subscribed to: ' + subscribed_success + '\nErrors occured while subscribing to ' + subscribed_failed

        # Return a message to user
        update.message.reply_text(complete_message)

    def unsubscribe(self, bot, update):
        # Find all links in a message
        urls = re.findall('(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',
         update.message.text)

        chat_id = str(update.message.chat_id)
        print('Group with ID ' + chat_id + ' attemps to unsubscribe from ' + str(urls).strip('[]'))


        for url in urls:
            # Check if the given domain is supported.
            print(url[1] + ' in self.conf.eligible-reddit-domains ==> ' + str(url[1] in self.conf['eligible-reddit-domains']))
            if url[1] in self.conf['eligible-reddit-domains']:
                print('AAAAAAAAAAAAAA PENISSSSS JEBANIEEEEEEEEEEEE AAAAAAAAAAAAAAAA DZIAAŁAM')

                # Create a list if it doesn't exist yet.
                print(chat_id + ' in self.reddit_db ==> ' + str(chat_id in self.reddit_db))
                if not chat_id in self.reddit_db:
                    print('Making a list for ' + chat_id)
                    self.reddit_db[chat_id] = list()

                print(chat_id + ' is currently subscribed to: ' + str(self.reddit_db[chat_id]))
                print(chat_id + ' tries to unsubscribe from ' + url[2])

                # Add ending slash to url if it doesn't exist already.
                if not url[2].endswith('/'):
                    print('Adding ending slash to ' + url[2])
                    url[2] = url[2] + '/'

                # Make the smol letters
                subreddit = url[2].lower()
                print('Changed to lowercase -> ' + subreddit)

                print(subreddit + ' in self.reddit_db.chat_id ==> ' + str(subreddit in self.reddit_db[chat_id]))

                # Remove entry from list.
                if subreddit in self.reddit_db[chat_id]:
                    self.reddit_db[chat_id].remove(subreddit)
                    msg = subreddit + ' has been unsubscribed.'
                else:
                    msg = subreddit + ' was never subscribed.'

                print(chat_id + ' ==> "' + msg + '"')

                # Write changes
                # https://i.imgur.com/RcGt5jX.png
                print('Writing to file...')
                with open('./reddit.json', 'w') as self.reddit:
                    json.dump(self.reddit_db, self.reddit)
                    self.reddit.close()

                print('Done unsubscribing.')

                # Return a message
                update.message.reply_text(msg)

    def listsubscribed(self, bot, update):

        chat_id = str(update.message.chat_id)

        # Convert list to string with separator.
        list = ',\n'.join(self.reddit_db[chat_id])

        update.message.reply_text(
            'Your group (' + chat_id + ') is subscribed to:\n' + list
        )







    # -- Services

    @telegram.ext.dispatcher.run_async
    def reddit_auto_update(self, bot):

        while 1:
            print('Searching for new posts...')
            # Loop through groups and fetch new posts for them.
            for group in self.reddit_db.keys():
                print('Looking for new posts for group with ID ' + str(group))
                if group == 'newest_posts': continue;
                self.fetch_newest_from_reddit(bot, group)
            # Delay between fetching new posts.
            print('Ended fetching reddit. Sleeping for ' + str(self.conf['delay-between-fetch']) + ' seconds...')
            time.sleep(self.conf['delay-between-fetch'])


    def fetch_newest_from_reddit(self, bot, group):

        print('Saying hello from self.fetch_newest_from_reddit()')

        # Check if group ID is a integer, and if so convert it to string.
        if isinstance(group, int):
            group = str(group)

        loop_been_run_for_times = 0

        # Loop through subscribed subreddits by chat_id
        for subreddit in self.reddit_db[group]:

            loop_been_run_for_times += 1
            print('Running for loop ' + str(loop_been_run_for_times) + ' time.')

            print('Attempting to get ' + subreddit + ' for the chat with ID ' + str(group) + '...')

            # Construct the URL that we're gonna connect to using the first
            # occurence in "eligible-reddit-domains" in conf.json
            url = 'https://' + self.conf['eligible-reddit-domains'][0] + subreddit + '.json'

            # Send a request with modified User-Agent suitable for using Reddit's API
            response = requests.get(url, headers={'User-Agent': self.conf['user-agent']})
            print(url + ' => ' + str(response.status_code) + ' ' + response.reason)

            # Check if response http code is "200 OK", if not - skip this subreddit
            if not response.status_code == 200:
                bot.send_message(group, 'Could not find new posts in ' + subreddit + ' because it returned an error.')
                continue

            # Parse JSON out of response
            result = response.json()
            print('Got a list of posts of ' + subreddit + ' for group with ID ' + group + ', it contains ' + str(len(result['data']['children'])) + ' children.')

            # Get the last newest posts (Amount of them can be changed in configuration)
            newest_posts = result['data']['children'][:self.conf['saved-posts-amount']]
            print('Saving locally ' + str(len(newest_posts)) + ' children from subreddit ' + subreddit)

            # Check if subreddit exist in self.reddit_db, if it doesn't create it.
            print(subreddit + ' in self.reddit_db => ' + str(subreddit in self.reddit_db))
            if not subreddit in self.reddit_db['newest_posts']:
                print(subreddit + ' not found in self.reddit_db, making an entry...')
                self.reddit_db['newest_posts'][subreddit] = list()
                with open('./reddit.json', 'w') as reddit_file:
                    print('Writing changes to file...')
                    json.dump(self.reddit_db, reddit_file)
                    reddit_file.close()
            else:
                print(subreddit + ' was found in self.reddit_db, skipping creation of new entry...')

            # Skip this subreddit if newest post on Reddit has the same permalink as the newest post locally.
            try:
                # If subreddit was never been fetched.
                if not self.reddit_db['newest_posts'][subreddit]: raise KeyError;
                # If newest post on subreddit has the same permalink as the newest post locally.
                if newest_posts[0]['data']['permalink'] == self.reddit_db['newest_posts'][subreddit][0]:
                    continue
            except KeyError:
                pass


            for post in newest_posts:

                print('Reached "' + post['data']['subreddit_name_prefixed'] + '/' + post['data']['id'] + '"')

                # Check if post has been already sent, if so skip it.
                print('Is already sent => ' + str(post['data']['permalink'] in self.reddit_db['newest_posts'][subreddit]))
                if post['data']['permalink'] in self.reddit_db['newest_posts'][subreddit]: continue
                # Check if post is pinned to the top of the subreddit, if so - skip it.
                if post['data']['stickied']: continue


                # Save permalinks to file to check later if the post was already sent.
                if not post['data']['permalink'] in self.reddit_db['newest_posts'][subreddit]:
                    print('Writing changes to file...')
                    self.reddit_db['newest_posts'][subreddit].append(post['data']['permalink'])
                    with open('./reddit.json', 'w') as self.reddit:
                        json.dump(self.reddit_db, self.reddit)
                        self.reddit.close()


                # Send a message to the subscribers.
                bot.send_message(group,
                post['data']['url'] +
                '\nfrom ' + subreddit
                )

                # Wait a little bit to avoid being ratelimited by Telegram
                time.sleep(self.conf['delay-between-requests'])

            # Wait a little bit before another request to reddit. You can customize it in config.
            print('Sleeping for ' + str(self.conf['delay-between-requests']) + ' second(s)...')
            time.sleep(self.conf['delay-between-requests'])


# end class



# Initialize the class and run the bot if the file is not imported as package
if __name__ == '__main__':
    blopcot()
