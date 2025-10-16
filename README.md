export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install google-adk -r requirements.txt

adk run src/

Example conversation:

```
[user]: hello
[steering]: Hello! Do you know where you'd like to travel, or would you like some help deciding?
[user]: I would like to go to Japan.
[attractions_planner]: Great! Japan is a fantastic choice. To help me suggest the best attractions, could you tell me a little more about what you're interested in? For example, are you looking for historical sites, natural beauty, bustling city life, unique cultural experiences, or something else?
[user]: Actually I don't know what country to visit.
[travel_brainstormer]: No problem at all! I can definitely help you with that. To get started, could you tell me a little bit about what you're hoping to get out of your trip? Are you looking for adventure, relaxation and leisure, a chance to learn something new, a great shopping experience, or an opportunity to view art and culture?
[user]: exit
```

or

```
adk web
```