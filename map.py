from room import OmegaRoom

room = OmegaRoom()
courses = room.getCourses(11)

for i in range(len(courses)):
    print(courses[i]["name"], i)
#
works = room.getWorks(courses[8]["id"])

if works:

    room.downloadWorks(works, courses[8]["name"])
try:
    posts = room.getPostsMaterials(courses[4]["id"])
except :
    posts = False

if posts:
    room.downloadWorks(posts, courses[4]["name"])




